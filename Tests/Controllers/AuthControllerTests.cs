```csharp
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using ApiGateway.Controllers;
using FluentAssertions;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly Mock<IConfiguration> _configurationMock;
        private readonly Mock<ILogger<AuthController>> _loggerMock;
        private readonly AuthController _controller;

        public AuthControllerTests()
        {
            _configurationMock = new Mock<IConfiguration>();
            _loggerMock = new Mock<ILogger<AuthController>>();
            _controller = new AuthController(_configurationMock.Object, _loggerMock.Object);
        }

        [Fact]
        public async Task OAuthLogin_ShouldRedirectToAuthorizationEndpoint()
        {
            // Arrange
            _configurationMock.SetupGet(x => x["OAuth:ClientId"]).Returns("test-client-id");
            _configurationMock.SetupGet(x => x["OAuth:RedirectUri"]).Returns("https://localhost/callback");
            _configurationMock.SetupGet(x => x["OAuth:Authority"]).Returns("https://test-authority.com");
            _configurationMock.SetupGet(x => x["OAuth:ResponseType"]).Returns("code");

            // Act
            var result = _controller.OAuthLogin() as RedirectResult;

            // Assert
            result.Should().NotBeNull();
            result!.Url.Should().StartWith("https://test-authority.com/authorize?client_id=test-client-id");
        }
    }
}
```