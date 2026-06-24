namespace ApiGateway.Models
{
    /// <summary>
    /// Represents the outcome of an MFA code delivery attempt.
    /// </summary>
    public class MfaResult
    {
        /// <summary>Whether the delivery request succeeded.</summary>
        public bool Success { get; init; }

        /// <summary>Human-readable message describing the outcome.</summary>
        public string Message { get; init; } = string.Empty;

        /// <summary>
        /// Optional provider-specific reference ID returned by the external API.
        /// Useful for tracing / support.
        /// </summary>
        public string? ProviderReferenceId { get; init; }

        /// <summary>UTC timestamp of the delivery attempt.</summary>
        public DateTime AttemptedAt { get; init; } = DateTime.UtcNow;

        // ── Factory helpers ──────────────────────────────────────────────────

        /// <summary>Creates a successful result.</summary>
        public static MfaResult Ok(string message, string? referenceId = null) =>
            new() { Success = true, Message = message, ProviderReferenceId = referenceId };

        /// <summary>Creates a failed result.</summary>
        public static MfaResult Fail(string message) =>
            new() { Success = false, Message = message };
    }
}
