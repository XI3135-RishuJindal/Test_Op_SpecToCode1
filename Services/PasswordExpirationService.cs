using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Default implementation of <see cref="IPasswordExpirationService"/>.
    ///
    /// Policy constants (configurable via appsettings under "PasswordPolicy"):
    ///   MaxPasswordAgeDays       – days before a password is considered expired  (default 90)
    ///   ExpirationWarningDays    – days before expiry at which warnings begin     (default 14)
    /// </summary>
    public class PasswordExpirationService : IPasswordExpirationService
    {
        private readonly ILogger<PasswordExpirationService> _logger;
        private readonly int _maxPasswordAgeDays;
        private readonly int _expirationWarningDays;

        public PasswordExpirationService(
            ILogger<PasswordExpirationService> logger,
            IConfiguration configuration)
        {
            _logger = logger;
            _maxPasswordAgeDays      = configuration.GetValue<int>("PasswordPolicy:MaxPasswordAgeDays",      90);
            _expirationWarningDays   = configuration.GetValue<int>("PasswordPolicy:ExpirationWarningDays",   14);
        }

        /// <inheritdoc />
        public PasswordExpirationResult CheckPasswordExpiration(string username, DateTime passwordLastChanged)
        {
            var now = DateTime.UtcNow;
            var daysSinceLastChange = (int)(now - passwordLastChanged).TotalDays;
            var daysUntilExpiration = _maxPasswordAgeDays - daysSinceLastChange;

            var isExpired          = daysSinceLastChange >= _maxPasswordAgeDays;
            var isNearingExpiration = !isExpired && daysUntilExpiration <= _expirationWarningDays;

            string? message = null;
            if (isExpired)
            {
                message = $"Your password has expired. It was last changed {daysSinceLastChange} days ago " +
                          $"(maximum allowed: {_maxPasswordAgeDays} days). " +
                          "You must change your password before you can log in.";

                _logger.LogWarning(
                    "Password for user '{Username}' is expired ({DaysSinceLastChange} days old).",
                    username, daysSinceLastChange);
            }
            else if (isNearingExpiration)
            {
                message = $"Your password will expire in {daysUntilExpiration} day(s). " +
                          "Please change it soon to avoid being locked out.";

                _logger.LogInformation(
                    "Password for user '{Username}' expires in {DaysUntilExpiration} day(s).",
                    username, daysUntilExpiration);
            }

            return new PasswordExpirationResult
            {
                IsExpired            = isExpired,
                IsNearingExpiration  = isNearingExpiration,
                DaysSinceLastChange  = daysSinceLastChange,
                DaysUntilExpiration  = daysUntilExpiration,
                NotificationMessage  = message
            };
        }

        /// <inheritdoc />
        public async Task NotifyUserAsync(string username, PasswordExpirationResult result)
        {
            // Integration point: replace the log statement below with calls to the
            // organisation's notification framework (e.g. email, SMS, push notification).
            // The ILogger sink acts as the existing communication framework for this service.
            if (result.IsExpired)
            {
                _logger.LogWarning(
                    "[NOTIFICATION] User '{Username}': {Message}",
                    username, result.NotificationMessage);
            }
            else if (result.IsNearingExpiration)
            {
                _logger.LogInformation(
                    "[NOTIFICATION] User '{Username}': {Message}",
                    username, result.NotificationMessage);
            }

            // Yield to allow async notification pipelines to be plugged in without
            // changing the method signature.
            await Task.CompletedTask;
        }
    }
}
