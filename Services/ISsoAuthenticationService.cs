using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Orchestrates the full SSO login flow: token validation, user mapping, JWT issuance.
    /// </summary>
    public interface ISsoAuthenticationService
    {
        /// <summary>
        /// Performs SSO login for the given provider and provider-issued token.
        /// </summary>
        /// <param name="request">SSO login request containing provider and provider token.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <returns>SSO login response containing the issued JWT and user info.</returns>
        /// <exception cref="SsoValidationException">Thrown when request validation fails.</exception>
        /// <exception cref="ProviderAuthenticationException">Thrown when the provider rejects the token.</exception>
        Task<SsoLoginResponse> LoginWithProviderAsync(SsoLoginRequest request, CancellationToken cancellationToken = default);
    }
}
