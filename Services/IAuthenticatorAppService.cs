namespace ApiGateway.Services
{
    /// <summary>
    /// Defines the contract for authenticator-app-based MFA operations.
    /// </summary>
    public interface IAuthenticatorAppService
    {
        /// <summary>
        /// Generates a new Base32-encoded shared secret for a user.
        /// </summary>
        /// <param name="userId">The unique identifier of the user.</param>
        /// <returns>A Base32-encoded secret string.</returns>
        string GenerateSecret(string userId);

        /// <summary>
        /// Generates a provisioning URI (otpauth://) that can be encoded as a QR code
        /// for import into an authenticator app (e.g. Google Authenticator, Authy).
        /// </summary>
        /// <param name="secret">The Base32-encoded shared secret.</param>
        /// <param name="userEmail">The user's e-mail address shown in the app.</param>
        /// <param name="issuer">The application / issuer name shown in the app.</param>
        /// <returns>An otpauth:// URI string.</returns>
        string GenerateQrCodeUri(string secret, string userEmail, string issuer);

        /// <summary>
        /// Validates a TOTP code supplied by the user against the stored shared secret.
        /// </summary>
        /// <param name="secret">The Base32-encoded shared secret for the user.</param>
        /// <param name="code">The 6-digit TOTP code entered by the user.</param>
        /// <returns><c>true</c> if the code is valid; otherwise <c>false</c>.</returns>
        bool ValidateCode(string secret, string code);
    }
}
