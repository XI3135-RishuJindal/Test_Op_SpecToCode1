namespace ApiGateway.Services.Exceptions
{
    /// <summary>
    /// Thrown when the SSO login request is invalid (e.g., missing provider or providerToken).
    /// Maps to HTTP 400 Bad Request.
    /// </summary>
    public class SsoValidationException : Exception
    {
        public SsoValidationException(string message) : base(message) { }

        public SsoValidationException(string message, Exception innerException)
            : base(message, innerException) { }
    }
}
