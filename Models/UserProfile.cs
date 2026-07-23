namespace ApiGateway.Models
{
    /// <summary>
    /// Represents an internal user profile that maps one or more external SSO identities
    /// to a single internal user identifier.
    /// </summary>
    public class UserProfile
    {
        /// <summary>Internal user identifier (GUID string).</summary>
        public string UserId { get; set; } = string.Empty;

        /// <summary>User's email address (from the most recent SSO login).</summary>
        public string? Email { get; set; }

        /// <summary>User's display name (from the most recent SSO login).</summary>
        public string? Name { get; set; }

        /// <summary>
        /// Maps provider name -> providerUserId for all linked external identities.
        /// </summary>
        public Dictionary<string, string> ExternalIds { get; set; } = new();
    }
}
