using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace ApiGateway.Services
{
    /// <summary>
    /// Mock implementation of IEmailSender for development/testing.
    /// Writes verification requests to the log and simulates async email delivery.
    /// </summary>
    public class MockEmailSender : IEmailSender
    {
        private readonly ILogger<MockEmailSender> _logger;
        public MockEmailSender(ILogger<MockEmailSender> logger)
        {
            _logger = logger;
        }

        public Task SendVerificationEmailAsync(string email)
        {
            _logger.LogInformation("Simulated send: Verification email would be sent to: {Email}", email);

            // Simulate short delay
            return Task.CompletedTask;
        }
    }
}