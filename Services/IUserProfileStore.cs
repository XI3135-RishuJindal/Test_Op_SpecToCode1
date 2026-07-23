using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Abstracts persistence of internal user profiles mapped to external SSO identities.
    /// The in-memory implementation is the default; swap for a database-backed one later.
    /// </summary>
    public interface IUserProfileStore
    {
        /// <summary>
        /// Finds an existing user profile by external provider identity.
        /// Returns <c>null</c> if no profile exists for the given provider + providerUserId combination.
        /// </summary>
        Task<UserProfile?> FindByExternalIdentityAsync(string provider, string providerUserId);

        /// <summary>
        /// Creates a new profile for the external identity, or updates an existing one.
        /// This operation must be idempotent: concurrent calls for the same identity must not
        /// create duplicate logical users.
        /// </summary>
        Task<UserProfile> CreateOrUpdateForExternalIdentityAsync(ExternalIdentity externalIdentity);
    }
}
