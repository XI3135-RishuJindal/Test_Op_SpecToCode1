import { Inject, Injectable, Logger } from '@nestjs/common';
import { createHash } from 'crypto';
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
import { AccountStatus } from '../../domain/enums/account-status.enum';
import {
  InvalidVerificationTokenException,
  UserNotFoundException,
  AccountNotPendingVerificationException,
} from '../../domain/exceptions/domain.exceptions';
import { OutboxEvent } from '../../domain/entities/outbox-event.entity';

export interface VerifyEmailCommand {
  token: string;
}

export interface VerifyEmailResult {
  message: string;
}

@Injectable()
export class VerifyEmailUseCase {
  private readonly logger = new Logger(VerifyEmailUseCase.name);

  constructor(
    @Inject(USER_REPOSITORY) private readonly userRepo: IUserRepository,
    @Inject(VERIFICATION_TOKEN_REPOSITORY)
    private readonly tokenRepo: IVerificationTokenRepository,
    @Inject(OUTBOX_EVENT_REPOSITORY) private readonly outboxRepo: IOutboxEventRepository,
  ) {}

  async execute(command: VerifyEmailCommand): Promise<VerifyEmailResult> {
    // Derive SHA-256 hash of the raw token to look up stored hash
    const tokenHash = createHash('sha256').update(command.token).digest('hex');
    const verificationToken = await this.tokenRepo.findByTokenHash(tokenHash);

    if (!verificationToken || verificationToken.isExpired() || verificationToken.isUsed()) {
      throw new InvalidVerificationTokenException();
    }

    const user = await this.userRepo.findById(verificationToken.userId);
    if (!user) throw new UserNotFoundException();

    if (user.status !== AccountStatus.PENDING_VERIFICATION) {
      throw new AccountNotPendingVerificationException();
    }

    // Transition account to ACTIVE
    user.activate();
    await this.userRepo.update(user);

    // Mark token as used
    verificationToken.markUsed();
    await this.tokenRepo.update(verificationToken);

    // Write outbox event
    const outboxEvent = OutboxEvent.create({
      id: uuidv4(),
      aggregateId: user.id,
      aggregateType: 'User',
      eventType: 'user.email_verified',
      payload: { userId: user.id, email: user.email.value },
    });
    await this.outboxRepo.save(outboxEvent);

    this.logger.log(`User ${user.id} email verified successfully`);
    return { message: 'Email verified successfully. Your account is now active.' };
  }
}
