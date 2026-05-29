using Xunit;
using ApiGateway.Controllers;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using Moq;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Models;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly Mock<IConfiguration> _mockConfiguration;
        private readonly Mock<ILogger<AuthController>> _mockLogger;
        private readonly AuthController _authController;

        public AuthControllerTests()
        {
            _mockConfiguration = new Mock<IConfiguration>();
            _mockLogger = new Mock<ILogger<AuthController>>();
            _authController = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Fact]
        public void GenerateToken_ReturnsBadRequest_WhenCredentialsAreInvalid()
        {
            var loginRequest = new LoginRequest { Username = "", Password = "" };
            var result = _authController.GenerateToken(loginRequest) as BadRequestObjectResult;

            Assert.NotNull(result);
            Assert.Equal(400, result.StatusCode);
            _mockLogger.Verify(logger => logger.Log(
                It.Is<LogLevel>(l => l == LogLevel.Information),
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString().Contains("requested for user: ")),
                It.IsAny<Exception>(),
                It.Is<Func<It.IsAnyType, Exception, string>>((v, t) => true)), Times.Once);
        }

        [Fact]
        public void GenerateToken_ReturnsOk_WhenCredentialsAreValid()
        {
            var loginRequest = new LoginRequest { Username = "testuser", Password = "password123" };
            _mockConfiguration.SetupGet(x => x["Jwt:Key"]).Returns("your-secret-key-here-must-be-at-least-256-bits");
            _mockConfiguration.SetupGet(x => x["Jwt:Issuer"]).Returns("ApiGateway");
            _mockConfiguration.SetupGet(x => x["Jwt:Audience"]).Returns("ApiGatewayUsers");

            var result = _authController.GenerateToken(loginRequest) as OkObjectResult;

            Assert.NotNull(result);
            Assert.Equal(200, result.StatusCode);
            _mockLogger.Verify(logger => logger.Log(
                It.Is<LogLevel>(l => l == LogLevel.Information),
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString().Contains("Token generated successfully for user: ")),
                It.IsAny<Exception>(),
                It.Is<Func<It.IsAnyType, Exception, string>>((v, t) => true)), Times.Once);
        }
    }
}
```