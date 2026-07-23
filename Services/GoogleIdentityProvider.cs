using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Validates Google-issued tokens and normalizes the resulting identity.
    /// In production, exchange/validate the token against Google's tokeninfo or userinfo endpoint.
    /// The stub implementation accepts any non-empty token for development/testing.
    /// </summary>
    public class GoogleIdentityProvider : IExternalIdentityProvider
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<GoogleIdentityProvider> _logger;

        public string ProviderName => "google";

        public GoogleIdentityProvider(IConfiguration configuration, ILogger<GoogleIdentityProvider> logger)
        {
            _configuration = configuration;
            _logger = logger;
        }

        /// <inheritdoc/>
        public Task<ExternalIdentity?> ValidateTokenAsync(string providerToken, CancellationToken cancellationToken = default)
        {
            _logger.LogInformation("GoogleIdentityProvider: validating provider token (token value not logged)");

            if (string.IsNullOrWhiteSpace(providerToken))
            {
                _logger.LogWarning("GoogleIdentityProvider: received empty provider token");
                return Task.FromResult<ExternalIdentity?>(null);
            }

            // TODO: Replace stub with real Google token validation:
            //   1. Call https://oauth2.googleapis.com/tokeninfo?id_token={providerToken}
            //      (or use Google.Apis.Auth NuGet package for server-side validation).
            //   2. Verify audience matches _configuration["Authentication:Providers:Google:ClientId"].
            //   3. Map sub → ProviderUserId, email, name.
            var identity = new ExternalIdentity
            {
                Provider = ProviderName,
                ProviderUserId = $"google-stub-{providerToken.GetHashCode():X}",
                Email = "stub-google-user@example.com",
                Name = "Google Stub User"
            };

            return Task.FromResult<ExternalIdentity?>(identity);
        }
    }
}
