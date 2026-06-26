import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { RegistrationController } from './registration.controller';
import { RegisterUserUseCase } from '../../../application/use-cases/register-user.use-case';
import { TypeOrmUserRepository } from '../../../infrastructure/persistence/repositories/typeorm-user.repository';
import { TypeOrmVerificationTokenRepository } from '../../../infrastructure/persistence/repositories/typeorm-verification-token.repository';
import { TypeOrmOutboxWriter } from '../../../infrastructure/persistence/repositories/typeorm-outbox-writer.repository';
import { Argon2PasswordHasher } from '../../../infrastructure/security/argon2-password-hasher.adapter';
import { CryptoTokenGenerator } from '../../../infrastructure/security/crypto-token-generator.adapter';
import { UserEntity } from '../../../infrastructure/persistence/entities/user.entity';
import { VerificationTokenEntity } from '../../../infrastructure/persistence/entities/verification-token.entity';
import { OutboxEventEntity } from '../../../infrastructure/persistence/entities/outbox-event.entity';
import {
  USER_REPOSITORY,
} from '../../../domain/ports/user-repository.port';
import {
  VERIFICATION_TOKEN_REPOSITORY,
} from '../../../domain/ports/verification-token-repository.port';
import { OUTBOX_WRITER } from '../../../domain/ports/outbox-writer.port';
import { PASSWORD_HASHER } from '../../../domain/ports/password-hasher.port';
import { TOKEN_GENERATOR } from '../../../domain/ports/token-generator.port';

@Module({
  imports: [
    TypeOrmModule.forFeature([UserEntity, VerificationTokenEntity, OutboxEventEntity]),
  ],
  controllers: [RegistrationController],
  providers: [
    RegisterUserUseCase,
    { provide: USER_REPOSITORY, useClass: TypeOrmUserRepository },
    { provide: VERIFICATION_TOKEN_REPOSITORY, useClass: TypeOrmVerificationTokenRepository },
    { provide: OUTBOX_WRITER, useClass: TypeOrmOutboxWriter },
    { provide: PASSWORD_HASHER, useClass: Argon2PasswordHasher },
    { provide: TOKEN_GENERATOR, useClass: CryptoTokenGenerator },
  ],
})
export class RegistrationModule {}
