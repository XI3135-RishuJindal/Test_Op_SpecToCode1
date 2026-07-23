namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a normalized identity returned by an external SSO provider.
    /// </summary>
    public class ExternalIdentity
    {
        /// <summary>The provider identifier (e.g., "google", "facebook", "apple").</summary>
        public string Provider { get; set; } = string.Empty;

        /// <summary>The user's unique identifier within the external provider.</summary>
        public string ProviderUserId { get; set; } = string.Empty;

        /// <summary>The user's email address as reported by the provider (may be null).</summary>
        public string? Email { get; set; }

        /// <summary>The user's display name as reported by the provider (may be null).</summary>
        public string? Name { get; set; }
    }
}
