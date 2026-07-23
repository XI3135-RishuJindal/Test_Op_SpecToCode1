namespace ApiGateway.Services.Models
{
    /// <summary>
    /// Represents a normalized external identity returned by a third-party SSO provider.
    /// </summary>
    public class ExternalIdentity
    {
        /// <summary>
        /// Gets or sets the SSO provider identifier (e.g., <c>google</c>, <c>facebook</c>, <c>apple</c>).
        /// </summary>
        public string Provider { get; set; } = string.Empty;

        /// <summary>
        /// Gets or sets the provider-specific user identifier or subject.
        /// </summary>
        public string ProviderUserId { get; set; } = string.Empty;

        /// <summary>
        /// Gets or sets the email address associated with the external identity, if available.
        /// </summary>
        public string? Email { get; set; }
    }
}