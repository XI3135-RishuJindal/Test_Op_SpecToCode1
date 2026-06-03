using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Provides password-expiration tracking and notification capabilities.
    /// </summary>
    public interface IPasswordExpirationService
    {
        /// <summary>
        /// Checks whether the password for the given user is expired or nearing expiration.
        /// </summary>
        /// <param name="username">The user whose password age is being evaluated.</param>
        /// <param name="passwordLastChanged">UTC timestamp of the last password change.</param>
        /// <returns>A <see cref="PasswordExpirationResult"/> describing the current expiration state.</returns>
        PasswordExpirationResult CheckPasswordExpiration(string username, DateTime passwordLastChanged);

        /// <summary>
        /// Sends an expiration notification to the user via the existing communication framework.
        /// </summary>
        /// <param name="username">The user to notify.</param>
        /// <param name="result">The expiration result that triggered the notification.</param>
        Task NotifyUserAsync(string username, PasswordExpirationResult result);
    }
}
