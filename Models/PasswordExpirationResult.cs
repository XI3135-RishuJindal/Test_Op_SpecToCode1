namespace ApiGateway.Models
{
    /// <summary>
    /// Represents the outcome of a password expiration check.
    /// </summary>
    public class PasswordExpirationResult
    {
        /// <summary>Whether the password has passed the 90-day expiration threshold.</summary>
        public bool IsExpired { get; set; }

        /// <summary>
        /// Whether the password is approaching expiration (within a configurable warning window,
        /// default 14 days before expiry).
        /// </summary>
        public bool IsNearingExpiration { get; set; }

        /// <summary>Number of days since the password was last changed.</summary>
        public int DaysSinceLastChange { get; set; }

        /// <summary>Number of days remaining before the password expires (negative when already expired).</summary>
        public int DaysUntilExpiration { get; set; }

        /// <summary>Human-readable notification message to surface to the user.</summary>
        public string? NotificationMessage { get; set; }
    }
}
