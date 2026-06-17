namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a standardized error response returned by the API.
    /// </summary>
    /// <remarks>
    /// <para>
    /// All error responses use this format, including client errors (e.g., validation failures) and server errors.
    /// </para>
    /// <para>
    /// Do not rely on the <c>Details</c> field to be present in all responses; it is included for debugging or deeper error diagnostics (never sensitive info).
    /// </para>
    /// </remarks>
    public class ErrorResponse
    {
        /// <summary>
        /// A short error code or identifier (e.g., "InvalidEmailFormat", "InternalServerError").
        /// </summary>
        public string Error { get; set; } = string.Empty;

        /// <summary>
        /// Human-readable description of the error.
        /// </summary>
        public string Message { get; set; } = string.Empty;

        /// <summary>
        /// HTTP status code corresponding to the error.
        /// </summary>
        public int StatusCode { get; set; }

        /// <summary>
        /// Time at which the error occurred (UTC).
        /// </summary>
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Additional details for debugging (may be null, not intended for production exposure).
        /// </summary>
        public string? Details { get; set; }
    }
}