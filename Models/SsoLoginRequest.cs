namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a request to perform Single Sign-On (SSO) using a third-party provider.
    /// </summary>
    /// <remarks>
    /// The client should obtain a provider-issued token or authorization code
    /// (for example from Google, Facebook, or Apple) and send it to this API
    /// along with the selected provider identifier.
    /// </remarks>
    public class SsoLoginRequest
    {
        /// <summary>
        /// The identifier of the external authentication provider to use.
        /// </summary>
        /// <example>google</example>
        public string Provider { get; set; } = string.Empty;

        /// <summary>
        /// The provider-issued access token or authorization code obtained after the user authenticates with the provider.
        /// </summary>
        /// <remarks>
        /// This value is treated as a secret and is never logged by the API.
        /// For this implementation, provider validation is stubbed and does not call real provider endpoints.
        /// </remarks>
        /// <example>sample-provider-token-or-auth-code</example>
        public string ProviderToken { get; set; } = string.Empty;

        /// <summary>
        /// Optional client-supplied information about the device or platform initiating the login.
        /// </summary>
        /// <remarks>
        /// This field is used only for logging and analytics and does not affect authentication behavior.
        /// </remarks>
        /// <example>iOS 17 - iPhone 14 Pro</example>
        public string? DeviceInfo { get; set; }
    }
}