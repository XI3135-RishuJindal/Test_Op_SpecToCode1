using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Validates Apple-issued identity tokens and normalizes the resulting identity.
    /// In production, verify the JWT signed by Apple's public keys (Sign in with Apple).
    /// The stub implementation accepts any non-empty token for development/testing.
    /// </summary>
    public class AppleIdentityProvider : IExternalIdentityProvider
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<AppleIdentityProvider> _logger;

        public string ProviderName => "apple";

        public AppleIdentityProvider(IConfiguration configuration, ILogger<AppleIdentityProvider> logger)
        {
            _configuration = configuration;
            _logger = logger;
        }

        /// <inheritdoc/>
        public Task<ExternalIdentity?> ValidateTokenAsync(string providerToken, CancellationToken cancellationToken = default)
        {
            _logger.LogInformation("AppleIdentityProvider: validating provider token (token value not logged)");

            if (string.IsNullOrWhiteSpace(providerToken))
            {
                _logger.LogWarning("AppleIdentityProvider: received empty provider token");
                return Task.FromResult<ExternalIdentity?>(null);
            }

            // TODO: Replace stub with real Apple token validation:
            //   1. Fetch Apple's public keys from https://appleid.apple.com/auth/keys.
            //   2. Validate the id_token JWT signature, issuer (https://appleid.apple.com),
            //      and audience (_configuration["Authentication:Providers:Apple:ClientId"]).
            //   3. Map sub → ProviderUserId, email (only available on first login from Apple).
            var identity = new ExternalIdentity
            {
                Provider = ProviderName,
                ProviderUserId = $"apple-stub-{providerToken.GetHashCode():X}",
                Email = "stub-apple-user@privaterelay.appleid.com",
                Name = "Apple Stub User"
            };

            return Task.FromResult<ExternalIdentity?>(identity);
        }
    }
}
