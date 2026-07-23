using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Abstracts validation of a provider-issued token and normalization of the resulting identity.
    /// Each SSO provider (Google, Facebook, Apple) has a dedicated implementation.
    /// </summary>
    public interface IExternalIdentityProvider
    {
        /// <summary>
        /// The provider identifier this implementation handles (e.g., "google", "facebook", "apple").
        /// Used by <see cref="IExternalIdentityProviderRegistry"/> to route requests.
        /// </summary>
        string ProviderName { get; }

        /// <summary>
        /// Validates the provider-issued token and returns a normalized <see cref="ExternalIdentity"/>.
        /// Returns <c>null</c> if the token is invalid or the provider rejects it.
        /// </summary>
        /// <param name="providerToken">The opaque provider token – never log this value.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        Task<ExternalIdentity?> ValidateTokenAsync(string providerToken, CancellationToken cancellationToken = default);
    }
}
