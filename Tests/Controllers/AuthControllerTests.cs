using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using ApiGateway.Controllers;
using ApiGateway.Models;
using ApiGateway.Services;
using Xunit;

namespace ApiGateway.Tests.Controllers
{
    /// <summary>
    /// Unit tests for <see cref="AuthController"/>, covering both the legacy token endpoint
    /// and the new SSO provider listing and login endpoints.
    /// </summary>
    public class AuthControllerTests
    {
        // -----------------------------------------------------------------------
        // Helpers
        // -----------------------------------------------------------------------

        /// <summary>
        /// Builds an in-memory IConfiguration with JWT settings and all three SSO
        /// providers enabled under Authentication:Providers.
        /// </summary>
        private static IConfiguration BuildConfigurationWithAllProviders()
        {
            var settings = new Dictionary<string, string?>
            {
                ["Jwt:Key"]      = "test-secret-key-for-unit-tests-must-be-long-enough",
                ["Jwt:Issuer"]   = "TestIssuer",
                ["Jwt:Audience"] = "TestAudience",
                // All three providers enabled
                ["Authentication:Providers:Google:Enabled"]   = "true",
                ["Authentication:Providers:Facebook:Enabled"] = "true",
                ["Authentication:Providers:Apple:Enabled"]    = "true"
            };

            return new ConfigurationBuilder()
                .AddInMemoryCollection(settings)
                .Build();
        }

        /// <summary>
        /// Creates an AuthController that has only IConfiguration and ILogger injected
        /// (used for endpoints that do not require ISsoAuthenticationService).
        /// </summary>
        private static AuthController CreateControllerWithConfig(IConfiguration configuration)
        {
            var logger = new Mock<ILogger<AuthController>>().Object;
            return new AuthController(configuration, logger);
        }

        /// <summary>
        /// Creates an AuthController with all three dependencies injected.
        /// </summary>
        private static AuthController CreateControllerWithSsoService(
            IConfiguration configuration,
            ISsoAuthenticationService ssoService)
        {
            var logger = new Mock<ILogger<AuthController>>().Object;
            return new AuthController(configuration, logger, ssoService);
        }

        // -----------------------------------------------------------------------
        // GET /api/auth/providers
        // -----------------------------------------------------------------------

        [Fact]
        public void GetProviders_ReturnsConfiguredProviders()
        {
            // Arrange
            var configuration = BuildConfigurationWithAllProviders();
            var controller = CreateControllerWithConfig(configuration);

            // Act
            var actionResult = controller.GetProviders();

            // Assert – must be 200 OK
            var okResult = Assert.IsType<OkObjectResult>(actionResult);
            Assert.Equal(200, okResult.StatusCode);

            // Assert – body must be a list of AuthProviderInfo
            var providers = Assert.IsAssignableFrom<IEnumerable<AuthProviderInfo>>(okResult.Value);
            var providerList = providers.ToList();

            // All three providers should be present and enabled
            Assert.Contains(providerList, p =>
                p.Id == "google" && p.IsEnabled == true);
            Assert.Contains(providerList, p =>
                p.Id == "facebook" && p.IsEnabled == true);
            Assert.Contains(providerList, p =>
                p.Id == "apple" && p.IsEnabled == true);
        }

        // -----------------------------------------------------------------------
        // POST /api/auth/sso/login – success
        // -----------------------------------------------------------------------

        [Fact]
        public async Task SsoLogin_ValidRequest_ReturnsToken()
        {
            // Arrange
            var expectedResponse = new SsoLoginResponse
            {
                Token       = "eyJhbGciOiJIUzI1NiJ9.test.token",
                ExpiresAt   = DateTime.UtcNow.AddHours(1),
                UserId      = "user-123",
                IsNewUser   = false,
                Provider    = "google",
                RedirectUrl = "/home"
            };

            var ssoServiceMock = new Mock<ISsoAuthenticationService>();
            ssoServiceMock
                .Setup(s => s.LoginWithProviderAsync(
                    It.IsAny<SsoLoginRequest>(),
                    It.IsAny<CancellationToken>()))
                .ReturnsAsync(expectedResponse);

            var controller = CreateControllerWithSsoService(
                BuildConfigurationWithAllProviders(),
                ssoServiceMock.Object);

            var request = new SsoLoginRequest
            {
                Provider      = "google",
                ProviderToken = "valid-google-token"
            };

            // Act
            var actionResult = await controller.SsoLogin(request);

            // Assert – 200 OK
            var okResult = Assert.IsType<OkObjectResult>(actionResult);
            Assert.Equal(200, okResult.StatusCode);

            // Assert – body matches mocked values
            var response = Assert.IsType<SsoLoginResponse>(okResult.Value);
            Assert.False(string.IsNullOrEmpty(response.Token));
            Assert.Equal(expectedResponse.Token,       response.Token);
            Assert.Equal(expectedResponse.UserId,      response.UserId);
            Assert.Equal(expectedResponse.Provider,    response.Provider);
            Assert.Equal(expectedResponse.IsNewUser,   response.IsNewUser);
            Assert.Equal(expectedResponse.RedirectUrl, response.RedirectUrl);
        }

        // -----------------------------------------------------------------------
        // POST /api/auth/sso/login – SsoValidationException → 400
        // -----------------------------------------------------------------------

        [Fact]
        public async Task SsoLogin_InvalidRequest_ReturnsBadRequest()
        {
            // Arrange – service throws SsoValidationException
            var ssoServiceMock = new Mock<ISsoAuthenticationService>();
            ssoServiceMock
                .Setup(s => s.LoginWithProviderAsync(
                    It.IsAny<SsoLoginRequest>(),
                    It.IsAny<CancellationToken>()))
                .ThrowsAsync(new SsoValidationException("Provider token is missing or invalid."));

            var controller = CreateControllerWithSsoService(
                BuildConfigurationWithAllProviders(),
                ssoServiceMock.Object);

            var request = new SsoLoginRequest
            {
                Provider      = "google",
                ProviderToken = string.Empty   // intentionally invalid
            };

            // Act
            var actionResult = await controller.SsoLogin(request);

            // Assert – 400 Bad Request
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(actionResult);
            Assert.Equal(400, badRequestResult.StatusCode);

            // Assert – ErrorResponse.Error == "InvalidRequest"
            var errorResponse = Assert.IsType<ErrorResponse>(badRequestResult.Value);
            Assert.Equal("InvalidRequest", errorResponse.Error);
        }

        // -----------------------------------------------------------------------
        // POST /api/auth/sso/login – ProviderAuthenticationException → 401
        // -----------------------------------------------------------------------

        [Fact]
        public async Task SsoLogin_ProviderFailure_ReturnsUnauthorized()
        {
            // Arrange – service throws ProviderAuthenticationException
            var ssoServiceMock = new Mock<ISsoAuthenticationService>();
            ssoServiceMock
                .Setup(s => s.LoginWithProviderAsync(
                    It.IsAny<SsoLoginRequest>(),
                    It.IsAny<CancellationToken>()))
                .ThrowsAsync(new ProviderAuthenticationException("The provider rejected the supplied token."));

            var controller = CreateControllerWithSsoService(
                BuildConfigurationWithAllProviders(),
                ssoServiceMock.Object);

            var request = new SsoLoginRequest
            {
                Provider      = "facebook",
                ProviderToken = "expired-facebook-token"
            };

            // Act
            var actionResult = await controller.SsoLogin(request);

            // Assert – 401 Unauthorized
            var unauthorizedResult = Assert.IsType<UnauthorizedObjectResult>(actionResult);
            Assert.Equal(401, unauthorizedResult.StatusCode);

            // Assert – ErrorResponse.Error == "ProviderAuthenticationFailed"
            var errorResponse = Assert.IsType<ErrorResponse>(unauthorizedResult.Value);
            Assert.Equal("ProviderAuthenticationFailed", errorResponse.Error);
        }

        // -----------------------------------------------------------------------
        // Legacy token endpoint – ensure existing behaviour is preserved
        // -----------------------------------------------------------------------

        [Fact]
        public void GenerateToken_EmptyCredentials_ReturnsBadRequest()
        {
            // Arrange
            var controller = CreateControllerWithConfig(BuildConfigurationWithAllProviders());
            var request = new LoginRequest { Username = "", Password = "" };

            // Act
            var actionResult = controller.GenerateToken(request);

            // Assert
            var badRequest = Assert.IsType<BadRequestObjectResult>(actionResult);
            Assert.Equal(400, badRequest.StatusCode);

            var error = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("InvalidCredentials", error.Error);
        }

        [Fact]
        public void GenerateToken_ValidCredentials_Returns200WithToken()
        {
            // Arrange
            var controller = CreateControllerWithConfig(BuildConfigurationWithAllProviders());
            var request = new LoginRequest { Username = "testuser", Password = "anypassword" };

            // Act
            var actionResult = controller.GenerateToken(request);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(actionResult);
            Assert.Equal(200, okResult.StatusCode);
            // The anonymous object should have a non-null "token" property
            Assert.NotNull(okResult.Value);
        }
    }
}
