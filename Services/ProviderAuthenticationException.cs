namespace ApiGateway.Services
{
    /// <summary>
    /// Thrown when the external provider rejects the supplied token or credential.
    /// Maps to HTTP 401 Unauthorized.
    /// </summary>
    public class ProviderAuthenticationException : Exception
    {
        public ProviderAuthenticationException(string message) : base(message) { }
        public ProviderAuthenticationException(string message, Exception innerException) : base(message, innerException) { }
    }
}
