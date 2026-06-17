namespace ApiGateway.Models
{
    /// <summary>
    /// Response model returned after MFA setup is initiated.
    /// Contains the shared secret and a QR code URI so the user can
    /// register the account in their authenticator app (e.g. Google Authenticator).
    /// </summary>
    public class MfaSetupResponse
    {
        /// <summary>
        /// Base32-encoded shared secret that the authenticator app uses to generate TOTP codes.
        /// </summary>
        public string SharedSecret { get; set; } = string.Empty;

        /// <summary>
        /// otpauth:// URI that can be encoded as a QR code for easy scanning.
        /// Format: otpauth://totp/{Issuer}:{Username}?secret={SharedSecret}&issuer={Issuer}
        /// </summary>
        public string QrCodeUri { get; set; } = string.Empty;

        /// <summary>
        /// Human-readable issuer label shown in the authenticator app.
        /// </summary>
        public string Issuer { get; set; } = string.Empty;

        /// <summary>
        /// The username associated with this MFA setup.
        /// </summary>
        public string Username { get; set; } = string.Empty;
    }
}
