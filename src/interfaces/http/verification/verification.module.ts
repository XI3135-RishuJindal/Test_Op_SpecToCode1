import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { VerificationController } from './verification.controller';
import { VerifyEmailUseCase } from '../../../application/use-cases/verify-email.use-case';
import { TypeOrmUserRepository } from '../../../infrastructure/persistence/repositories/typeorm-user.repository';
import { TypeOrmVerificationTokenRepository } from '../../../infrastructure/persistence/repositories/typeorm-verification-token.repository';
import { TypeOrmOutboxWriter } from '../../../infrastructure/persistence/repositories/typeorm-outbox-writer.repository';
import { UserEntity } from '../../../infrastructure/persistence/entities/user.entity';
import { VerificationTokenEntity } from '../../../infrastructure/persistence/entities/verification-token.entity';
import { OutboxEventEntity } from '../../../infrastructure/persistence/entities/outbox-event.entity';
import { USER_REPOSITORY } from '../../../domain/ports/user-repository.port';
import { VERIFICATION_TOKEN_REPOSITORY } from '../../../domain/ports/verification-token-repository.port';
import { OUTBOX_WRITER } from '../../../domain/ports/outbox-writer.port';

@Module({
  imports: [
    TypeOrmModule.forFeature([UserEntity, VerificationTokenEntity, OutboxEventEntity]),
  ],
  controllers: [VerificationController],
  providers: [
    VerifyEmailUseCase,
    { provide: USER_REPOSITORY, useClass: TypeOrmUserRepository },
    { provide: VERIFICATION_TOKEN_REPOSITORY, useClass: TypeOrmVerificationTokenRepository },
    { provide: OUTBOX_WRITER, useClass: TypeOrmOutboxWriter },
  ],
})
export class VerificationModule {}
