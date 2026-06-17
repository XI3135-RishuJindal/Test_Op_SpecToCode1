namespace ApiGateway.Models
{
    /// <summary>
    /// Request model for initiating MFA setup for a user account.
    /// The caller must be authenticated (JWT) before requesting MFA setup.
    /// </summary>
    public class MfaSetupRequest
    {
        /// <summary>
        /// The username for which MFA is being enabled.
        /// </summary>
        public string Username { get; set; } = string.Empty;
    }
}
