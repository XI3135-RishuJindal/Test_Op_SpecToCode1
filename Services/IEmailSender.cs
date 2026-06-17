using System.Threading.Tasks;

namespace ApiGateway.Services
{
    /// <summary>
    /// Abstraction for sending verification emails asynchronously.
    /// </summary>
    public interface IEmailSender
    {
        /// <summary>
        /// Sends a verification email for account registration.
        /// </summary>
        /// <param name="email">Destination email address.</param>
        /// <returns>A task representing the asynchronous operation.</returns>
        Task SendVerificationEmailAsync(string email);
    }
}