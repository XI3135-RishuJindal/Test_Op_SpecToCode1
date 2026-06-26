import { Inject, Injectable, ConflictException } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import { RegisterUserCommand } from '../commands/register-user.command';
import { RegisterUserResult } from '../results/register-user.result';
import { IUserRepository, USER_REPOSITORY } from '../../domain/ports/user-repository.port';
import {
  IVerificationTokenRepository,
  VERIFICATION_TOKEN_REPOSITORY,
} from '../../domain/ports/verification-token-repository.port';
import { IPasswordHasher, PASSWORD_HASHER } from '../../domain/ports/password-hasher.port';
import { ITokenGenerator, TOKEN_GENERATOR } from '../../domain/ports/token-generator.port';
import { IOutboxWriter, OUTBOX_WRITER } from '../../domain/ports/outbox-writer.port';
import { User } from '../../domain/entities/user.entity';
import { VerificationToken } from '../../domain/entities/verification-token.entity';
import { AccountStatus } from '../../domain/enums/account-status.enum';
import { Email } from '../../domain/value-objects/email.vo';
import { Password } from '../../domain/value-objects/password.vo';

@Injectable()
export class RegisterUserUseCase {
  /** Token TTL in minutes */
  private static readonly TOKEN_TTL_MINUTES = 60;

  constructor(
    @Inject(USER_REPOSITORY) private readonly userRepository: IUserRepository,
    @Inject(VERIFICATION_TOKEN_REPOSITORY)
    private readonly tokenRepository: IVerificationTokenRepository,
    @Inject(PASSWORD_HASHER) private readonly passwordHasher: IPasswordHasher,
    @Inject(TOKEN_GENERATOR) private readonly tokenGenerator: ITokenGenerator,
    @Inject(OUTBOX_WRITER) private readonly outboxWriter: IOutboxWriter,
  ) {}

  async execute(command: RegisterUserCommand): Promise<RegisterUserResult> {
    // 1. Validate and normalise email
    const email = Email.create(command.email);

    // 2. Validate password policy
    Password.validate(command.password);

    // 3. Idempotency — return early if user already exists (generic response)
    const existing = await this.userRepository.findByEmail(email.value);
    if (existing) {
      // Return a generic response to prevent email enumeration
      return { userId: existing.id, status: existing.status };
    }

    // 4. Hash password
    const passwordHash = await this.passwordHasher.hash(command.password);

    // 5. Create user aggregate
    const now = new Date();
    const user = new User({
      id: uuidv4(),
      email: email.value,
      passwordHash,
      status: AccountStatus.PENDING_VERIFICATION,
      createdAt: now,
      updatedAt: now,
    });

    // 6. Persist user
    await this.userRepository.save(user);

    // 7. Generate verification token
    const rawToken = await this.tokenGenerator.generate();
    const tokenHash = this.tokenGenerator.hash(rawToken);
    const expiresAt = new Date(
      now.getTime() + RegisterUserUseCase.TOKEN_TTL_MINUTES * 60 * 1000,
    );

    const verificationToken = new VerificationToken({
      id: uuidv4(),
      userId: user.id,
      tokenHash,
      expiresAt,
    });

    await this.tokenRepository.save(verificationToken);

    // 8. Write outbox event transactionally
    await this.outboxWriter.write({
      eventType: 'USER_REGISTERED',
      aggregateId: user.id,
      occurredAt: now,
      payload: {
        userId: user.id,
        email: user.email,
        status: user.status,
      },
    });

    return { userId: user.id, status: user.status };
  }
}
