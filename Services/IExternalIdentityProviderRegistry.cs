namespace ApiGateway.Services
{
    /// <summary>
    /// Resolves the correct <see cref="IExternalIdentityProvider"/> implementation by provider name.
    /// All registered providers are visible through this registry.
    /// </summary>
    public interface IExternalIdentityProviderRegistry
    {
        /// <summary>
        /// Returns the provider implementation for the given <paramref name="providerName"/>,
        /// or <c>null</c> if no matching provider is registered.
        /// </summary>
        IExternalIdentityProvider? GetProvider(string providerName);

        /// <summary>
        /// Returns all registered provider implementations.
        /// </summary>
        IEnumerable<IExternalIdentityProvider> GetAllProviders();
    }
}
