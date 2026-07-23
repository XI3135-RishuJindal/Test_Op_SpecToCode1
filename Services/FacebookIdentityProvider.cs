using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Validates Facebook-issued tokens and normalizes the resulting identity.
    /// In production, call the Facebook Graph API to inspect the token.
    /// The stub implementation accepts any non-empty token for development/testing.
    /// </summary>
    public class FacebookIdentityProvider : IExternalIdentityProvider
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<FacebookIdentityProvider> _logger;

        public string ProviderName => "facebook";

        public FacebookIdentityProvider(IConfiguration configuration, ILogger<FacebookIdentityProvider> logger)
        {
            _configuration = configuration;
            _logger = logger;
        }

        /// <inheritdoc/>
        public Task<ExternalIdentity?> ValidateTokenAsync(string providerToken, CancellationToken cancellationToken = default)
        {
            _logger.LogInformation("FacebookIdentityProvider: validating provider token (token value not logged)");

            if (string.IsNullOrWhiteSpace(providerToken))
            {
                _logger.LogWarning("FacebookIdentityProvider: received empty provider token");
                return Task.FromResult<ExternalIdentity?>(null);
            }

            // TODO: Replace stub with real Facebook token validation:
            //   1. Call https://graph.facebook.com/debug_token?input_token={providerToken}&access_token={appId}|{appSecret}
            //   2. Verify app_id matches _configuration["Authentication:Providers:Facebook:AppId"].
            //   3. Map user_id → ProviderUserId, then fetch /me?fields=email,name.
            var identity = new ExternalIdentity
            {
                Provider = ProviderName,
                ProviderUserId = $"facebook-stub-{providerToken.GetHashCode():X}",
                Email = "stub-facebook-user@example.com",
                Name = "Facebook Stub User"
            };

            return Task.FromResult<ExternalIdentity?>(identity);
        }
    }
}
