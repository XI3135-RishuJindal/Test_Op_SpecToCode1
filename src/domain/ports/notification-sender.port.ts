/**
 * Output port — notification sender (email dispatch).
 */
export interface INotificationSender {
  sendVerificationEmail(to: string, token: string): Promise<void>;
}

export const NOTIFICATION_SENDER = Symbol('INotificationSender');
