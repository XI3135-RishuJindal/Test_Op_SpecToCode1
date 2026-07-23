using System;
using System.Threading;
using System.Threading.Tasks;
using ApiGateway.Models;
using ApiGateway.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace ApiGateway.Tests.Services
{
    public class SsoAuthenticationServiceTests
    {
        private static IConfiguration CreateConfiguration(string redirectUrl = "/profile")
        {
            var inMemorySettings = new System.Collections.Generic.Dictionary<string, string?>
            {
                { "Authentication:PostLoginRedirectUrl", redirectUrl }
            };

            return new ConfigurationBuilder()
                .AddInMemoryCollection(inMemorySettings)
                .Build();
        }

        private static ExternalIdentity CreateExternalIdentity(
            string provider = "google",
            string providerUserId = "external-user-123",
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

        private static SsoLoginRequest CreateRequest(
            string provider = "google",
            string providerToken = "token-123")
        {
            return new SsoLoginRequest
            {
                Provider = provider,
                ProviderToken = providerToken,
                DeviceInfo = "unit-test-device"
            };
        }

        private (SsoAuthenticationService service,
                Mock<IExternalIdentityProviderRegistry> registryMock,
                Mock<IUserProfileStore> userProfileStoreMock,
                Mock<IJwtTokenGenerator> jwtGeneratorMock) CreateService(
                    ExternalIdentity externalIdentity,
                    UserProfile userProfile,
                    bool isNewUser,
                    string token = "jwt-token",
                    DateTime? expiresAt = null)
        {
            var loggerMock = new Mock<ILogger<SsoAuthenticationService>>();
            var configuration = CreateConfiguration("/home");

            var externalProviderMock = new Mock<IExternalIdentityProvider>();
            externalProviderMock
                .Setup(p => p.ValidateTokenAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(externalIdentity);

            var registryMock = new Mock<IExternalIdentityProviderRegistry>();
            registryMock
                .Setup(r => r.GetProvider(externalIdentity.Provider))
                .Returns(externalProviderMock.Object);

            var userProfileStoreMock = new Mock<IUserProfileStore>();
            userProfileStoreMock
                .Setup(s => s.GetOrCreateByExternalIdentityAsync(It.IsAny<ExternalIdentity>()))
                .ReturnsAsync((externalIdentity arg) => (userProfile, isNewUser));

            var jwtGeneratorMock = new Mock<IJwtTokenGenerator>();
            var expiry = expiresAt ?? DateTime.UtcNow.AddHours(1);
            jwtGeneratorMock
                .Setup(g => g.GenerateToken(userProfile, externalIdentity, out expiry))
                .Returns(token);

            var service = new SsoAuthenticationService(
                registryMock.Object,
                userProfileStoreMock.Object,
                jwtGeneratorMock.Object,
                configuration,
                loggerMock.Object);

            return (service, registryMock, userProfileStoreMock, jwtGeneratorMock);
        }

        [Fact]
        public async Task LoginWithProviderAsync_NewUser_FlagIsTrue()
        {
            var externalIdentity = CreateExternalIdentity(provider: "google", providerUserId: "new-user-1");
            var userProfile = new UserProfile
            {
                UserId = "internal-123",
                Email = externalIdentity.Email,
            };
            var expiresAt = DateTime.UtcNow.AddMinutes(30);
            var (service, registryMock, userProfileStoreMock, jwtGeneratorMock) =
                CreateService(externalIdentity, userProfile, isNewUser: true, token: "fixed-jwt-token", expiresAt: expiresAt);

            var request = CreateRequest(provider: externalIdentity.Provider, providerToken: "provider-token");

            var response = await service.LoginWithProviderAsync(request, CancellationToken.None);

            Assert.NotNull(response);
            Assert.Equal("fixed-jwt-token", response.Token);
            Assert.Equal(userProfile.UserId, response.UserId);
            Assert.True(response.IsNewUser);
            Assert.Equal(externalIdentity.Provider, response.Provider);
            Assert.Equal("/home", response.RedirectUrl);
            Assert.True(response.ExpiresAt > DateTime.UtcNow.AddMinutes(25));

            registryMock.Verify(r => r.GetProvider(externalIdentity.Provider), Times.Once);
            userProfileStoreMock.Verify(s => s.GetOrCreateByExternalIdentityAsync(It.Is<ExternalIdentity>(
                e => e.Provider == externalIdentity.Provider && e.ProviderUserId == externalIdentity.ProviderUserId)), Times.Once);
            jwtGeneratorMock.VerifyAll();
        }

        [Fact]
        public async Task LoginWithProviderAsync_ExistingUser_FlagIsFalse()
        {
            var externalIdentity = CreateExternalIdentity(provider: "facebook", providerUserId: "existing-user-1");
            var userProfile = new UserProfile
            {
                UserId = "internal-456",
                Email = externalIdentity.Email,
            };

            var (service, _, userProfileStoreMock, _) =
                CreateService(externalIdentity, userProfile, isNewUser: false, token: "existing-user-token");

            var request = CreateRequest(provider: externalIdentity.Provider, providerToken: "provider-token");

            var response = await service.LoginWithProviderAsync(request, CancellationToken.None);

            Assert.NotNull(response);
            Assert.Equal("existing-user-token", response.Token);
            Assert.Equal(userProfile.UserId, response.UserId);
            Assert.False(response.IsNewUser);
            Assert.Equal(externalIdentity.Provider, response.Provider);

            userProfileStoreMock.Verify(s => s.GetOrCreateByExternalIdentityAsync(It.IsAny<ExternalIdentity>()), Times.Once);
        }

        [Theory]
        [InlineData(null, "token")]
        [InlineData("", "token")]
        [InlineData("   ", "token")]
        [InlineData("google", null)]
        [InlineData("google", "")]
        [InlineData("google", "   ")]
        public async Task LoginWithProviderAsync_InvalidInput_ThrowsValidationException(string? provider, string? providerToken)
        {
            var registryMock = new Mock<IExternalIdentityProviderRegistry>(MockBehavior.Strict);
            var userProfileStoreMock = new Mock<IUserProfileStore>(MockBehavior.Strict);
            var jwtGeneratorMock = new Mock<IJwtTokenGenerator>(MockBehavior.Strict);
            var configuration = CreateConfiguration();
            var loggerMock = new Mock<ILogger<SsoAuthenticationService>>();

            var service = new SsoAuthenticationService(
                registryMock.Object,
                userProfileStoreMock.Object,
                jwtGeneratorMock.Object,
                configuration,
                loggerMock.Object);

            var request = new SsoLoginRequest
            {
                Provider = provider ?? string.Empty,
                ProviderToken = providerToken ?? string.Empty
            };

            await Assert.ThrowsAsync<ValidationException>(() =>
                service.LoginWithProviderAsync(request, CancellationToken.None));
        }
    }
}