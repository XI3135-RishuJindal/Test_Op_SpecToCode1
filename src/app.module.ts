import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { TerminusModule } from '@nestjs/terminus';
import { RegistrationModule } from './application/registration/registration.module';
import { VerificationModule } from './application/verification/verification.module';
import { HealthModule } from './interfaces/http/health/health.module';
import { RegistrationController } from './interfaces/http/registration/registration.controller';
import { VerificationController } from './interfaces/http/verification/verification.controller';
import appConfig from './infrastructure/config/app.config';
import databaseConfig from './infrastructure/config/database.config';
import { UserEntity } from './infrastructure/persistence/entities/user.entity';
import { OutboxEventEntity } from './infrastructure/persistence/entities/outbox-event.entity';
import { VerificationTokenEntity } from './infrastructure/persistence/entities/verification-token.entity';

@Module({
  imports: [
    // Configuration
    ConfigModule.forRoot({
      isGlobal: true,
      load: [appConfig, databaseConfig],
      envFilePath: ['.env'],
    }),

    // Database
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => ({
        type: 'postgres',
        host: configService.get<string>('database.host'),
        port: configService.get<number>('database.port'),
        username: configService.get<string>('database.username'),
        password: configService.get<string>('database.password'),
        database: configService.get<string>('database.name'),
        entities: [UserEntity, OutboxEventEntity, VerificationTokenEntity],
        synchronize: configService.get<boolean>('database.synchronize', false),
        ssl: configService.get<boolean>('database.ssl', false)
          ? { rejectUnauthorized: false }
          : false,
      }),
      inject: [ConfigService],
    }),

    // Feature modules
    RegistrationModule,
    VerificationModule,
    HealthModule,
    TerminusModule,
  ],
  controllers: [RegistrationController, VerificationController],
})
export class AppModule {}
