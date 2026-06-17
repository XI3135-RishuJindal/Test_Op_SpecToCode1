namespace ApiGateway.Models
{
    /// <summary>
    /// Response model returned after a TOTP code validation attempt.
    /// On success the caller receives a full JWT; on failure the response
    /// indicates the reason so the client can surface an appropriate message.
    /// </summary>
    public class MfaValidationResponse
    {
        /// <summary>
        /// Indicates whether the TOTP code was accepted and access is granted.
        /// </summary>
        public bool Success { get; set; }

        /// <summary>
        /// Full JWT bearer token issued on successful second-factor validation.
        /// Null when <see cref="Success"/> is false.
        /// </summary>
        public string? Token { get; set; }

        /// <summary>
        /// Human-readable message describing the outcome (e.g. "MFA validation successful"
        /// or "Invalid or expired TOTP code").
        /// </summary>
        public string Message { get; set; } = string.Empty;

        /// <summary>
        /// UTC timestamp of the validation attempt, useful for audit logging.
        /// </summary>
        public DateTime ValidatedAt { get; set; } = DateTime.UtcNow;
    }
}
