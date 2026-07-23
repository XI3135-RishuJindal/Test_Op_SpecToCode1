using System.Collections.Concurrent;
using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Thread-safe in-memory implementation of <see cref="IUserProfileStore"/>.
    /// Registered as a singleton so the store survives across scoped requests.
    /// Replace with a database-backed implementation when persistence is required.
    /// </summary>
    public class InMemoryUserProfileStore : IUserProfileStore
    {
        // Key: (provider, providerUserId) → internal UserId
        private readonly ConcurrentDictionary<(string Provider, string ProviderUserId), string> _externalIdIndex
            = new();

        // Key: internal UserId → UserProfile
        private readonly ConcurrentDictionary<string, UserProfile> _profiles
            = new(StringComparer.OrdinalIgnoreCase);

        private readonly ILogger<InMemoryUserProfileStore> _logger;

        public InMemoryUserProfileStore(ILogger<InMemoryUserProfileStore> logger)
        {
            _logger = logger;
        }

        /// <inheritdoc/>
        public Task<UserProfile?> FindByExternalIdentityAsync(string provider, string providerUserId)
        {
            var key = (provider.ToLowerInvariant(), providerUserId);
            if (_externalIdIndex.TryGetValue(key, out var userId) &&
                _profiles.TryGetValue(userId, out var profile))
            {
                _logger.LogInformation(
                    "UserProfileStore: found existing profile {UserId} for {Provider}:{ProviderUserId}",
                    userId, provider, providerUserId);
                return Task.FromResult<UserProfile?>(profile);
            }

            return Task.FromResult<UserProfile?>(null);
        }

        /// <inheritdoc/>
        public Task<UserProfile> CreateOrUpdateForExternalIdentityAsync(ExternalIdentity externalIdentity)
        {
            var providerKey = externalIdentity.Provider.ToLowerInvariant();
            var indexKey = (providerKey, externalIdentity.ProviderUserId);

            // Idempotent: GetOrAdd ensures only one UserId is ever assigned per (provider, providerUserId).
            var userId = _externalIdIndex.GetOrAdd(indexKey, _ => Guid.NewGuid().ToString());

            var profile = _profiles.AddOrUpdate(
                userId,
                // Add: create a new profile
                _ =>
                {
                    _logger.LogInformation(
                        "UserProfileStore: creating new profile {UserId} for {Provider}:{ProviderUserId}",
                        userId, externalIdentity.Provider, externalIdentity.ProviderUserId);
                    return new UserProfile
                    {
                        UserId = userId,
                        Email = externalIdentity.Email,
                        Name = externalIdentity.Name,
                        ExternalIds = new Dictionary<string, string>
                        {
                            [providerKey] = externalIdentity.ProviderUserId
                        }
                    };
                },
                // Update: refresh mutable fields, keep existing UserId and external id mapping
                (_, existing) =>
                {
                    _logger.LogInformation(
                        "UserProfileStore: updating profile {UserId} for {Provider}:{ProviderUserId}",
                        userId, externalIdentity.Provider, externalIdentity.ProviderUserId);
                    existing.Email = externalIdentity.Email ?? existing.Email;
                    existing.Name = externalIdentity.Name ?? existing.Name;
                    existing.ExternalIds[providerKey] = externalIdentity.ProviderUserId;
                    return existing;
                });

            return Task.FromResult(profile);
        }
    }
}
