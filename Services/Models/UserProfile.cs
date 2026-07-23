namespace ApiGateway.Services.Models
{
    /// <summary>
    /// Represents an internal user profile within the API gateway.
    /// </summary>
    public class UserProfile
    {
        /// <summary>
        /// Gets or sets the internal user identifier.
        /// </summary>
        public string UserId { get; set; } = string.Empty;

        /// <summary>
        /// Gets or sets the primary email associated with the user, if known.
        /// </summary>
        public string? Email { get; set; }
    }
}