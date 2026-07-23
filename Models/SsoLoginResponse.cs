namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a successful Single Sign-On (SSO) login response.
    /// </summary>
    /// <remarks>
    /// The returned <see cref="Token"/> is a JWT issued by this API gateway and can be
    /// used to access protected endpoints such as <c>/api/test</c>.
    /// </remarks>
    public class SsoLoginResponse
    {
        /// <summary>
        /// The JSON Web Token (JWT) issued by this API gateway that represents the authenticated session.
        /// </summary>
        /// <example>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</example>
        public string Token { get; set; } = string.Empty;

        /// <summary>
        /// The UTC date and time when the issued JWT expires.
        /// </summary>
        /// <example>2024-01-01T12:34:56Z</example>
        public DateTime ExpiresAt { get; set; }

        /// <summary>
        /// The internal user identifier assigned by this API gateway.
        /// </summary>
        /// <remarks>
        /// This ID is stable for a given external identity (provider + provider user id)
        /// across multiple SSO logins.
        /// </remarks>
        /// <example>c4a1b8fc-5b7a-4e4a-9f3e-1d2a4c6e9f01</example>
        public string UserId { get; set; } = string.Empty;

        /// <summary>
        /// Indicates whether this is the first time the external identity has logged in through SSO.
        /// </summary>
        /// <remarks>
        /// <c>true</c> means a new internal profile was created for this external identity.
        /// Subsequent logins for the same identity will return <c>false</c>.
        /// </remarks>
        public bool IsNewUser { get; set; }

        /// <summary>
        /// The identifier of the external provider that was used for this SSO login.
        /// </summary>
        /// <example>google</example>
        public string Provider { get; set; } = string.Empty;

        /// <summary>
        /// Suggested relative URL that the client can navigate to after successful login.
        /// </summary>
        /// <remarks>
        /// This value is device-agnostic and is intended for web, mobile, and desktop clients alike.
        /// Typical values are <c>/home</c> or <c>/profile</c>.
        /// </remarks>
        /// <example>/profile</example>
        public string RedirectUrl { get; set; } = string.Empty;
    }
}