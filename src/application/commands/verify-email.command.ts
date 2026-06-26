export interface VerifyEmailCommand {
  /** Raw (un-hashed) verification token from the email link. */
  token: string;
}
