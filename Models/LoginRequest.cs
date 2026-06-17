namespace ApiGateway.Models
{
    /// <summary>
    /// Request model for the primary (username/password) authentication step.
    /// When MFA is enabled for the account the response will contain an
    /// <c>MfaRequired</c> flag and a short-lived <c>MfaSessionToken</c> instead
    /// of a full JWT, prompting the client to complete the second-factor challenge
    /// via <see cref="MfaValidationRequest"/>.
    /// </summary>
    public class LoginRequest
    {
        /// <summary>
        /// The user's login name.
        /// </summary>
        public string Username { get; set; } = string.Empty;

        /// <summary>
        /// The user's password (plain-text over TLS; hashed server-side).
        /// </summary>
        public string Password { get; set; } = string.Empty;
    }

    /// <summary>
    /// Response model for the primary authentication step.
    /// </summary>
    public class LoginResponse
    {
        /// <summary>
        /// Full JWT bearer token. Populated only when MFA is not required or
        /// has already been completed.
        /// </summary>
        public string? Token { get; set; }

        /// <summary>
        /// When true the client must complete the MFA challenge using
        /// <see cref="MfaValidationRequest"/> before a full token is issued.
        /// </summary>
        public bool MfaRequired { get; set; }

        /// <summary>
        /// Short-lived opaque token that ties the pending MFA challenge to this
        /// login attempt. Passed back in <see cref="MfaValidationRequest.MfaSessionToken"/>.
        /// Null when <see cref="MfaRequired"/> is false.
        /// </summary>
        public string? MfaSessionToken { get; set; }

        /// <summary>
        /// Human-readable status message.
        /// </summary>
        public string Message { get; set; } = string.Empty;
    }
}
