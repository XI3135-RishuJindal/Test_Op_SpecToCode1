using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Orchestrates the full SSO login flow:
    /// 1. Validate the request.
    /// 2. Resolve the provider implementation.
    /// 3. Validate the provider token → obtain <see cref="ExternalIdentity"/>.
    /// 4. Map or create an internal <see cref="UserProfile"/>.
    /// 5. Issue a signed JWT via <see cref="IJwtTokenGenerator"/>.
    /// 6. Return a populated <see cref="SsoLoginResponse"/>.
    /// </summary>
    public class SsoAuthenticationService : ISsoAuthenticationService
    {
        private readonly IExternalIdentityProviderRegistry _providerRegistry;
        private readonly IUserProfileStore _profileStore;
        private readonly IJwtTokenGenerator _tokenGenerator;
        private readonly IConfiguration _configuration;
        private readonly ILogger<SsoAuthenticationService> _logger;

        public SsoAuthenticationService(
            IExternalIdentityProviderRegistry providerRegistry,
            IUserProfileStore profileStore,
            IJwtTokenGenerator tokenGenerator,
            IConfiguration configuration,
            ILogger<SsoAuthenticationService> logger)
        {
            _providerRegistry = providerRegistry;
            _profileStore = profileStore;
            _tokenGenerator = tokenGenerator;
            _configuration = configuration;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<SsoLoginResponse> LoginWithProviderAsync(
            SsoLoginRequest request,
            CancellationToken cancellationToken = default)
        {
            // --- 1. Validate request ---
            if (string.IsNullOrWhiteSpace(request.Provider))
                throw new ArgumentException("Provider must be specified.", nameof(request));

            if (string.IsNullOrWhiteSpace(request.ProviderToken))
                throw new ArgumentException("ProviderToken must be specified.", nameof(request));

            _logger.LogInformation(
                "SsoAuthenticationService: SSO login attempt for provider '{Provider}'",
                request.Provider);

            // --- 2. Resolve provider ---
            var provider = _providerRegistry.GetProvider(request.Provider);
            if (provider is null)
            {
                _logger.LogWarning(
                    "SsoAuthenticationService: unknown provider '{Provider}'", request.Provider);
                throw new ArgumentException($"Unknown SSO provider: '{request.Provider}'.", nameof(request));
            }

            // --- 3. Validate provider token ---
            _logger.LogInformation(
                "SsoAuthenticationService: validating token with provider '{Provider}'", request.Provider);

            ExternalIdentity? externalIdentity;
            try
            {
                externalIdentity = await provider.ValidateTokenAsync(request.ProviderToken, cancellationToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex,
                    "SsoAuthenticationService: provider '{Provider}' threw an exception during token validation",
                    request.Provider);
                throw new UnauthorizedAccessException(
                    $"Token validation with provider '{request.Provider}' failed.", ex);
            }

            if (externalIdentity is null)
            {
                _logger.LogWarning(
                    "SsoAuthenticationService: provider '{Provider}' rejected the token", request.Provider);
                throw new UnauthorizedAccessException(
                    $"Provider '{request.Provider}' rejected the supplied token.");
            }

            // --- 4. Map / create user profile ---
            _logger.LogInformation(
                "SsoAuthenticationService: looking up profile for {Provider}:{ProviderUserId}",
                externalIdentity.Provider, externalIdentity.ProviderUserId);

            var existingProfile = await _profileStore.FindByExternalIdentityAsync(
                externalIdentity.Provider, externalIdentity.ProviderUserId);

            bool isNewUser = existingProfile is null;

            var profile = await _profileStore.CreateOrUpdateForExternalIdentityAsync(externalIdentity);

            _logger.LogInformation(
                "SsoAuthenticationService: profile resolved – UserId={UserId}, IsNewUser={IsNewUser}",
                profile.UserId, isNewUser);

            // --- 5. Issue JWT ---
            var token = _tokenGenerator.GenerateToken(profile, externalIdentity, out var expiresAt);

            // --- 6. Build response ---
            var redirectUrl = _configuration["Authentication:DefaultRedirectUrl"] ?? "/";

            return new SsoLoginResponse
            {
                Token = token,
                ExpiresAt = expiresAt,
                UserId = profile.UserId,
                IsNewUser = isNewUser,
                Provider = externalIdentity.Provider,
                RedirectUrl = redirectUrl
            };
        }
    }
}
