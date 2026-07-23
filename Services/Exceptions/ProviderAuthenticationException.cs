namespace ApiGateway.Services.Exceptions
{
    /// <summary>
    /// Thrown when the SSO provider rejects the supplied token or authorization code.
    /// Maps to HTTP 401 Unauthorized.
    /// </summary>
    public class ProviderAuthenticationException : Exception
    {
        /// <summary>
        /// The provider identifier that rejected the token (e.g., "google").
        /// </summary>
        public string Provider { get; }

        public ProviderAuthenticationException(string provider, string message)
            : base(message)
        {
            Provider = provider;
        }

        public ProviderAuthenticationException(string provider, string message, Exception innerException)
            : base(message, innerException)
        {
            Provider = provider;
        }
    }
}
