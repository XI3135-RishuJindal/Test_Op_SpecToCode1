namespace ApiGateway.Services
{
    /// <summary>
    /// Internal domain model representing an application user profile with linked external identities.
    /// This is NOT an API contract or DTO — it is used only within the service layer for in-memory SSO mapping.
    /// </summary>
    public class UserProfile
    {
        /// <summary>
        /// The internal application user identifier.
        /// </summary>
        public string UserId { get; set; } = string.Empty;

        /// <summary>
        /// The user's email address, if known.
        /// </summary>
        public string? Email { get; set; }

        /// <summary>
        /// Maps external provider names to their corresponding provider-issued user IDs.
        /// Key: provider name (e.g., "Google"), Value: provider user ID.
        /// Supports associating multiple external identity providers with a single internal profile.
        /// This collection is intended for in-memory use only and is not persisted.
        /// </summary>
        public Dictionary<string, string> ExternalIds { get; }

        /// <summary>
        /// Initializes a new <see cref="UserProfile"/> with an empty external identity mapping.
        /// </summary>
        public UserProfile()
        {
            ExternalIds = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        }
    }
}
