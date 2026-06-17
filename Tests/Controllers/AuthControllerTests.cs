```csharp
using ApiGateway.Controllers;
using ApiGateway.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly Mock<IAuthenticatorAppService> _mockAuthenticatorAppService;
        private readonly AuthController _authController;

        public AuthControllerTests()
        {
            var config = new ConfigurationBuilder().AddInMemoryCollection().Build();
            var logger = Mock.Of<ILogger<AuthController>>();

            _mockAuthenticatorAppService = new Mock<IAuthenticatorAppService>();
            _authController = new AuthController(config, logger, _mockAuthenticatorAppService.Object);
        }

        [Fact]
        public void GenerateMfaSetupCode_ReturnsValidUrl()
        {
            // Arrange
            var expectedUrl = "some-otp-url";
            _mockAuthenticatorAppService
                .Setup(s => s.GenerateSetupCode(It.IsAny<string>(), It.IsAny<string>()))
                .Returns(expectedUrl);

            // Act
            var result = _authController.GenerateMfaSetupCode() as OkObjectResult;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(expectedUrl, result.Value);
        }

        [Theory]
        [InlineData(true)]
        [InlineData(false)]
        public void ValidateMfaToken_ReturnsExpectedResult(bool expectedValidationResult)
        {
            // Arrange
            var secret = "some-secret";
            var token = "123456";
            _mockAuthenticatorAppService
                .Setup(s => s.ValidateToken(secret, token))
                .Returns(expectedValidationResult);

            // Act
            var result = _authController.ValidateMfaToken(token);

            // Assert
            if (expectedValidationResult)
            {
                var okResult = Assert.IsType<OkObjectResult>(result);
                Assert.True((bool)okResult.Value);
            }
            else
            {
                var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
                var errorResponse = Assert.IsType<ErrorResponse>(badRequestResult.Value);
                Assert.Equal("InvalidToken", errorResponse.Error);
            }
        }
    }
}
```