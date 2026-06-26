import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { VerifyEmailUseCase } from './use-cases/verify-email.use-case';
import { UserEntity } from '../../infrastructure/persistence/entities/user.entity';
import { OutboxEventEntity } from '../../infrastructure/persistence/entities/outbox-event.entity';
import { VerificationTokenEntity } from '../../infrastructure/persistence/entities/verification-token.entity';
import { TypeOrmUserRepository } from '../../infrastructure/persistence/repositories/typeorm-user.repository';
import { TypeOrmVerificationTokenRepository } from '../../infrastructure/persistence/repositories/typeorm-verification-token.repository';
import { TypeOrmOutboxEventRepository } from '../../infrastructure/persistence/repositories/typeorm-outbox-event.repository';
import { Argon2PasswordHasher } from '../../infrastructure/security/argon2-password-hasher';
import { USER_REPOSITORY } from '../../domain/ports/user-repository.port';
import { VERIFICATION_TOKEN_REPOSITORY } from '../../domain/ports/verification-token-repository.port';
import { OUTBOX_EVENT_REPOSITORY } from '../../domain/ports/outbox-event-repository.port';
import { PASSWORD_HASHER } from '../../domain/ports/password-hasher.port';

@Module({
  imports: [
    TypeOrmModule.forFeature([UserEntity, OutboxEventEntity, VerificationTokenEntity]),
  ],
  providers: [
    VerifyEmailUseCase,
    { provide: USER_REPOSITORY, useClass: TypeOrmUserRepository },
    { provide: VERIFICATION_TOKEN_REPOSITORY, useClass: TypeOrmVerificationTokenRepository },
    { provide: OUTBOX_EVENT_REPOSITORY, useClass: TypeOrmOutboxEventRepository },
    { provide: PASSWORD_HASHER, useClass: Argon2PasswordHasher },
  ],
  exports: [VerifyEmailUseCase],
})
export class VerificationModule {}
