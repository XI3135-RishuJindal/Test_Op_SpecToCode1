export interface RegisterUserResult {
  /** Opaque user identifier — safe to return to the caller. */
  userId: string;
  /** Always PENDING_VERIFICATION at registration time. */
  status: string;
}
