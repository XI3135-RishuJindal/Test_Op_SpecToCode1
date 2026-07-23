using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Generates a signed JWT for an authenticated internal user, including SSO-specific claims.
    /// Uses the same JWT configuration (issuer, audience, key) as the existing JwtBearer setup.
    /// </summary>
    public interface IJwtTokenGenerator
    {
        /// <summary>
        /// Creates a signed JWT for the given <paramref name="user"/> and <paramref name="externalIdentity"/>.
        /// </summary>
        /// <param name="user">The internal user profile.</param>
        /// <param name="externalIdentity">The external identity used for this login.</param>
        /// <param name="expiresAt">Output: the UTC expiry time of the generated token.</param>
        /// <returns>The serialized JWT string.</returns>
        string GenerateToken(UserProfile user, ExternalIdentity externalIdentity, out DateTime expiresAt);
    }
}
