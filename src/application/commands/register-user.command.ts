export interface RegisterUserCommand {
  /** Idempotency key supplied by the caller (e.g. client-generated UUID). */
  idempotencyKey: string;
  email: string;
  password: string;
  /** Optional CAPTCHA / risk-score token from the client. */
  captchaToken?: string;
}
