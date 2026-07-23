namespace ApiGateway.Services
{
    /// <summary>
    /// Represents a normalized external identity returned by an SSO provider after token validation.
    /// </summary>
    public class ExternalIdentity
    {
        /// <summary>
        /// The lowercase provider identifier (e.g., <c>google</c>, <c>facebook</c>, <c>apple</c>).
        /// </summary>
        public string Provider { get; set; } = string.Empty;

        /// <summary>
        /// The unique user identifier as issued by the external provider (subject / user id).
        /// </summary>
        public string ProviderUserId { get; set; } = string.Empty;

        /// <summary>
        /// The user's email address as returned by the provider, if available.
        /// </summary>
        public string? Email { get; set; }

        /// <summary>
        /// The user's display name as returned by the provider, if available.
        /// </summary>
        public string? Name { get; set; }
    }
}
