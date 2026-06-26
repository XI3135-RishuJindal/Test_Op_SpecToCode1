import { Injectable, Logger } from '@nestjs/common';
import { INotificationSender } from '../../domain/ports/notification-sender.port';

/**
 * Stub notification sender — logs to console.
 * Replace with SMTP / SES adapter in production.
 */
@Injectable()
export class LogNotificationSender implements INotificationSender {
  private readonly logger = new Logger(LogNotificationSender.name);

  async sendVerificationEmail(to: string, token: string): Promise<void> {
    this.logger.log(`[STUB] Sending verification email to ${to} with token ${token}`);
    // TODO: integrate with real email provider (SES, SendGrid, etc.)
  }
}
