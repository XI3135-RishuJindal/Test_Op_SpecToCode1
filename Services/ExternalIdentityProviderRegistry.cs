namespace ApiGateway.Services
{
    /// <summary>
    /// Resolves the correct <see cref="IExternalIdentityProvider"/> by provider name.
    /// All <see cref="IExternalIdentityProvider"/> implementations registered in DI are
    /// injected as an <see cref="IEnumerable{T}"/>, making new providers available automatically
    /// when registered in <c>Program.cs</c>.
    /// </summary>
    public class ExternalIdentityProviderRegistry : IExternalIdentityProviderRegistry
    {
        private readonly Dictionary<string, IExternalIdentityProvider> _providers;
        private readonly ILogger<ExternalIdentityProviderRegistry> _logger;

        public ExternalIdentityProviderRegistry(
            IEnumerable<IExternalIdentityProvider> providers,
            ILogger<ExternalIdentityProviderRegistry> logger)
        {
            _logger = logger;
            _providers = providers.ToDictionary(
                p => p.ProviderName.ToLowerInvariant(),
                p => p,
                StringComparer.OrdinalIgnoreCase);

            _logger.LogInformation(
                "ExternalIdentityProviderRegistry: registered providers: {Providers}",
                string.Join(", ", _providers.Keys));
        }

        /// <inheritdoc/>
        public IExternalIdentityProvider? GetProvider(string providerName)
        {
            _providers.TryGetValue(providerName.ToLowerInvariant(), out var provider);
            return provider;
        }

        /// <inheritdoc/>
        public IEnumerable<IExternalIdentityProvider> GetAllProviders() => _providers.Values;
    }
}
