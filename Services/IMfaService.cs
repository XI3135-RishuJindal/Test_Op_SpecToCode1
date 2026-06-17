namespace ApiGateway.Services
{
    /// <summary>
    /// Contract for multi-factor authentication operations.
    /// Implementations handle TOTP secret generation and code validation.
    /// </summary>
    public interface IMfaService
    {
        /// <summary>
        /// Generates a new Base32-encoded shared secret for the given user and
        /// returns an otpauth:// URI suitable for QR-code display.
        /// </summary>
        /// <param name="username">The user for whom the secret is generated.</param>
        /// <param name="issuer">The application/issuer name shown in the authenticator app.</param>
        /// <returns>Tuple of (sharedSecret, qrCodeUri).</returns>
        (string SharedSecret, string QrCodeUri) GenerateSecret(string username, string issuer);

        /// <summary>
        /// Validates a TOTP code against the stored shared secret for the user.
        /// Allows a ±1 time-step window to account for clock skew.
        /// </summary>
        /// <param name="username">The user whose secret is used for validation.</param>
        /// <param name="code">The 6-digit TOTP code to validate.</param>
        /// <returns>True if the code is valid within the allowed window; otherwise false.</returns>
        bool ValidateCode(string username, string code);

        /// <summary>
        /// Stores (or replaces) the shared secret for a user.
        /// In production this would persist to a secure store; here it uses an in-memory dictionary.
        /// </summary>
        void StoreSecret(string username, string secret);
    }
}
