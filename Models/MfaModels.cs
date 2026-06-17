namespace ApiGateway.Models
{
    /// <summary>
    /// Request model for initiating MFA setup or challenge for a user.
    /// </summary>
    public class MfaInitiateRequest
    {
        /// <summary>The username for which MFA is being initiated.</summary>
        public string Username { get; set; } = string.Empty;
    }

    /// <summary>
    /// Response returned when MFA is initiated.
    /// Contains the shared secret and a QR code URI for authenticator app setup.
    /// </summary>
    public class MfaInitiateResponse
    {
        /// <summary>Base32-encoded shared secret for the authenticator app.</summary>
        public string SharedSecret { get; set; } = string.Empty;

        /// <summary>
        /// otpauth:// URI that can be encoded as a QR code and scanned by an authenticator app.
        /// </summary>
        public string QrCodeUri { get; set; } = string.Empty;

        /// <summary>Informational message for the client.</summary>
        public string Message { get; set; } = string.Empty;
    }

    /// <summary>
    /// Request model for verifying a TOTP code supplied by the user's authenticator app.
    /// </summary>
    public class MfaVerifyRequest
    {
        /// <summary>The username whose MFA code is being verified.</summary>
        public string Username { get; set; } = string.Empty;

        /// <summary>The 6-digit TOTP code from the authenticator app.</summary>
        public string Code { get; set; } = string.Empty;
    }

    /// <summary>
    /// Response returned after MFA code verification.
    /// </summary>
    public class MfaVerifyResponse
    {
        /// <summary>Whether the supplied code was valid.</summary>
        public bool Success { get; set; }

        /// <summary>Informational message for the client.</summary>
        public string Message { get; set; } = string.Empty;

        /// <summary>
        /// Short-lived JWT token issued only after successful MFA verification.
        /// Null when verification fails.
        /// </summary>
        public string? Token { get; set; }
    }
}
