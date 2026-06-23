import { Inject, Injectable, Logger } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import { IUserRepository, USER_REPOSITORY } from '../../domain/ports/user-repository.port';
import {
  IVerificationTokenRepository,
  VERIFICATION_TOKEN_REPOSITORY,
} from '../../domain/ports/verification-token-repository.port';
import {
  IOutboxEventRepository,
  OUTBOX_EVENT_REPOSITORY,
} from '../../domain/ports/outbox-event-repository.port';
import { IPasswordHasher, PASSWORD_HASHER } from '../../domain/ports/password-hasher.port';
import { ITokenGenerator, TOKEN_GENERATOR } from '../../domain/ports/token-generator.port';
import {
  INotificationSender,
  NOTIFICATION_SENDER,
} from '../../domain/ports/notification-sender.port';
import { User } from '../../domain/entities/user.entity';
import { VerificationToken } from '../../domain/entities/verification-token.entity';
import { OutboxEvent } from '../../domain/entities/outbox-event.entity';
import { Email } from '../../domain/value-objects/email.vo';
import { Password } from '../../domain/value-objects/password.vo';
import { AccountStatus } from '../../domain/enums/account-status.enum';
import { UserAlreadyExistsException } from '../../domain/exceptions/domain.exceptions';

export interface RegisterUserCommand {
  idempotencyKey: string;
  email: string;
  password: string;
  captchaToken?: string;
}

export interface RegisterUserResult {
  /** Generic message — never reveals whether email exists */
  message: string;
}

@Injectable()
export class RegisterUserUseCase {
  private readonly logger = new Logger(RegisterUserUseCase.name);

  constructor(
    @Inject(USER_REPOSITORY) private readonly userRepo: IUserRepository,
    @Inject(VERIFICATION_TOKEN_REPOSITORY)
    private readonly tokenRepo: IVerificationTokenRepository,
    @Inject(OUTBOX_EVENT_REPOSITORY) private readonly outboxRepo: IOutboxEventRepository,
    @Inject(PASSWORD_HASHER) private readonly hasher: IPasswordHasher,
    @Inject(TOKEN_GENERATOR) private readonly tokenGen: ITokenGenerator,
    @Inject(NOTIFICATION_SENDER) private readonly notifier: INotificationSender,
  ) {}

  async execute(command: RegisterUserCommand): Promise<RegisterUserResult> {
    // Idempotency check
    const existing = await this.userRepo.findByIdempotencyKey(command.idempotencyKey);
    if (existing) {
      this.logger.log(`Idempotent replay for key ${command.idempotencyKey}`);
      return { message: 'Registration received. Please check your email to verify your account.' };
    }

    // Validate value objects (throws on invalid input)
    const email = new Email(command.email);
    new Password(command.password); // validate policy only

    // Enumeration-safe: always return generic response even if email exists
    const emailExists = await this.userRepo.findByEmail(email);
    if (emailExists) {
      this.logger.warn(`Registration attempt for existing email (suppressed)`);
      return { message: 'Registration received. Please check your email to verify your account.' };
    }

    // Hash password
    const passwordHash = await this.hasher.hash(command.password);

    // Create user aggregate
    const user = User.create({
      id: uuidv4(),
      email,
      passwordHash,
      status: AccountStatus.PENDING_VERIFICATION,
      idempotencyKey: command.idempotencyKey,
    });

    const savedUser = await this.userRepo.save(user);

    // Generate verification token
    const { raw, hash } = await this.tokenGen.generate();
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 h

    const token = VerificationToken.create({
      id: uuidv4(),
      userId: savedUser.id,
      tokenHash: hash,
      expiresAt,
    });
    await this.tokenRepo.save(token);

    // Write outbox event transactionally
    const outboxEvent = OutboxEvent.create({
      id: uuidv4(),
      aggregateId: savedUser.id,
      aggregateType: 'User',
      eventType: 'user.registered',
      payload: {
        userId: savedUser.id,
        email: email.value,
        idempotencyKey: command.idempotencyKey,
      },
    });
    await this.outboxRepo.save(outboxEvent);

    // Send verification email (fire-and-forget; failures are non-fatal here)
    try {
      await this.notifier.sendVerificationEmail(email.value, raw);
    } catch (err) {
      this.logger.error('Failed to send verification email', err);
    }

    return { message: 'Registration received. Please check your email to verify your account.' };
  }
}
