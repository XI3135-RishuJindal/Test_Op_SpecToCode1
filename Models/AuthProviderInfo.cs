namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a third-party authentication provider that can be used for Single Sign-On (SSO).
    /// </summary>
    public class AuthProviderInfo
    {
        /// <summary>
        /// Machine-readable identifier of the provider.
        /// </summary>
        /// <remarks>
        /// This value is used when calling the SSO login endpoint.
        /// </remarks>
        /// <example>google</example>
        public string Id { get; set; } = string.Empty;

        /// <summary>
        /// Human-friendly display name for the provider.
        /// </summary>
        /// <example>Google</example>
        public string DisplayName { get; set; } = string.Empty;

        /// <summary>
        /// Indicates whether this provider is currently enabled for SSO.
        /// </summary>
        /// <remarks>
        /// Disabled providers are still returned by the providers endpoint but marked as unavailable
        /// so that clients can choose not to display them.
        /// </remarks>
        public bool IsEnabled { get; set; }
    }
}