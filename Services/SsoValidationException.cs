namespace ApiGateway.Services
{
    /// <summary>
    /// Thrown when the SSO login request fails client-side validation
    /// (e.g., missing provider, missing token, unsupported provider).
    /// Maps to HTTP 400 Bad Request.
    /// </summary>
    public class SsoValidationException : Exception
    {
        public SsoValidationException(string message) : base(message) { }
        public SsoValidationException(string message, Exception innerException) : base(message, innerException) { }
    }
}
