import { Inject, Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { VerifyEmailCommand } from '../commands/verify-email.command';
import { VerifyEmailResult } from '../results/verify-email.result';
import { IUserRepository, USER_REPOSITORY } from '../../domain/ports/user-repository.port';
import {
  IVerificationTokenRepository,
  VERIFICATION_TOKEN_REPOSITORY,
} from '../../domain/ports/verification-token-repository.port';
import { ITokenGenerator, TOKEN_GENERATOR } from '../../domain/ports/token-generator.port';
import { IOutboxWriter, OUTBOX_WRITER } from '../../domain/ports/outbox-writer.port';

@Injectable()
export class VerifyEmailUseCase {
  constructor(
    @Inject(USER_REPOSITORY) private readonly userRepository: IUserRepository,
    @Inject(VERIFICATION_TOKEN_REPOSITORY)
    private readonly tokenRepository: IVerificationTokenRepository,
    @Inject(TOKEN_GENERATOR) private readonly tokenGenerator: ITokenGenerator,
    @Inject(OUTBOX_WRITER) private readonly outboxWriter: IOutboxWriter,
  ) {}

  async execute(command: VerifyEmailCommand): Promise<VerifyEmailResult> {
    // 1. Hash the raw token to look it up
    const tokenHash = this.tokenGenerator.hash(command.token);

    // 2. Retrieve token record — use generic error to prevent enumeration
    const verificationToken = await this.tokenRepository.findByTokenHash(tokenHash);
    if (!verificationToken || !verificationToken.isValid()) {
      throw new BadRequestException('Invalid or expired verification token.');
    }

    // 3. Retrieve user
    const user = await this.userRepository.findById(verificationToken.userId);
    if (!user) {
      throw new NotFoundException('User not found.');
    }

    // 4. Activate user (domain method enforces state machine)
    user.activate();

    // 5. Mark token as used
    verificationToken.markUsed();

    // 6. Persist changes
    await this.userRepository.update(user);
    await this.tokenRepository.update(verificationToken);

    // 7. Write outbox event
    await this.outboxWriter.write({
      eventType: 'USER_ACTIVATED',
      aggregateId: user.id,
      occurredAt: new Date(),
      payload: {
        userId: user.id,
        email: user.email,
      },
    });

    return { userId: user.id, status: user.status };
  }
}
