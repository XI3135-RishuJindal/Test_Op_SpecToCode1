import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { TerminusModule } from '@nestjs/terminus';
import { HealthModule } from './interfaces/http/health/health.module';
import { RegistrationModule } from './interfaces/http/registration/registration.module';
import { VerificationModule } from './interfaces/http/verification/verification.module';
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
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        host: config.get<string>('database.host'),
        port: config.get<number>('database.port'),
        username: config.get<string>('database.username'),
        password: config.get<string>('database.password'),
        database: config.get<string>('database.name'),
        entities: [UserEntity, OutboxEventEntity, VerificationTokenEntity],
        synchronize: config.get<boolean>('database.synchronize'),
        ssl: config.get<boolean>('database.ssl') ? { rejectUnauthorized: false } : false,
      }),
      inject: [ConfigService],
    }),

    TerminusModule,
    HealthModule,
    RegistrationModule,
    VerificationModule,
  ],
})
export class AppModule {}
