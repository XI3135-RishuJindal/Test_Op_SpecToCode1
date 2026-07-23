using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;
using ApiGateway.Services;
using Xunit;

namespace ApiGateway.Tests.Services
{
    public class InMemoryUserProfileStoreTests
    {
        private static ExternalIdentity CreateExternalIdentity(
            string provider = "google",
            string providerUserId = "user-123",
            string? email = "user@example.com",
            string? name = "Test User")
        {
            return new ExternalIdentity
            {
                Provider = provider,
                ProviderUserId = providerUserId,
                Email = email,
                Name = name
            };
        }

        [Fact]
        public async Task FirstLogin_CreatesNewUserProfile()
        {
            var store = new InMemoryUserProfileStore();
            var externalIdentity = CreateExternalIdentity();

            var (profile, isNewUser) = await store.GetOrCreateByExternalIdentityAsync(externalIdentity);

            Assert.True(isNewUser);
            Assert.NotNull(profile);
            Assert.False(string.IsNullOrWhiteSpace(profile.UserId));
            Assert.Equal(externalIdentity.Email, profile.Email);
            Assert.True(profile.ExternalIds.TryGetValue(externalIdentity.Provider, out var mappedProviderUserId));
            Assert.Equal(externalIdentity.ProviderUserId, mappedProviderUserId);
        }

        [Fact]
        public async Task SubsequentLogin_ReusesExistingUserProfile()
        {
            var store = new InMemoryUserProfileStore();
            var externalIdentity = CreateExternalIdentity();

            var (firstProfile, firstIsNewUser) = await store.GetOrCreateByExternalIdentityAsync(externalIdentity);
            var (secondProfile, secondIsNewUser) = await store.GetOrCreateByExternalIdentityAsync(externalIdentity);

            Assert.True(firstIsNewUser);
            Assert.False(secondIsNewUser);
            Assert.Equal(firstProfile.UserId, secondProfile.UserId);
        }

        [Fact]
        public void ParallelAccess_DoesNotCreateDuplicateUsers()
        {
            var store = new InMemoryUserProfileStore();
            var externalIdentity = CreateExternalIdentity();
            var userIds = new ConcurrentBag<string>();
            var isNewUserFlags = new ConcurrentBag<bool>();

            Parallel.For(0, 50, _ =>
            {
                var (profile, isNewUser) = store.GetOrCreateByExternalIdentityAsync(externalIdentity).GetAwaiter().GetResult();
                userIds.Add(profile.UserId);
                isNewUserFlags.Add(isNewUser);
            });

            string? firstUserId = null;
            foreach (var id in userIds)
            {
                if (firstUserId == null)
                {
                    firstUserId = id;
                }
                else
                {
                    Assert.Equal(firstUserId, id);
                }
            }

            Assert.NotNull(firstUserId);

            var newUserCount = 0;
            foreach (var isNew in isNewUserFlags)
            {
                if (isNew)
                {
                    newUserCount++;
                }
            }

            Assert.Equal(1, newUserCount);
        }
    }
}