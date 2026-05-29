```csharp
using Xunit;
using Moq;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using ApiGateway.Controllers;
using ApiGateway.Models;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly Mock<ILogger<AuthController>> _mockLogger;
        private readonly Mock<IConfiguration> _mockConfiguration;
        private readonly AuthController _controller;

        public AuthControllerTests()
        {
            _mockLogger = new Mock<ILogger<AuthController>>();
            _mockConfiguration = new Mock<IConfiguration>();
            _mockConfiguration.Setup(config => config["Jwt:Key"]).Returns("development-secret-key-for-testing-only-256-bits");
            _mockConfiguration.Setup(config => config["Jwt:Issuer"]).Returns("ApiGateway");
            _mockConfiguration.Setup(config => config["Jwt:Audience"]).Returns("ApiGatewayUsers");
            _controller = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Fact]
        public void GenerateToken_WithValidRequest_ShouldReturnOkResult()
        {
            var loginRequest = new LoginRequest
            {
                Username = "testuser",
                Password = "testpassword"
            };

            var result = _controller.GenerateToken(loginRequest);

            Assert.IsType<OkObjectResult>(result);
            _mockLogger.Verify(logger => logger.LogInformation(It.IsAny<string>(), It.IsAny<object[]>()), Times.AtLeast(1));
        }

        [Fact]
        public void GenerateToken_WithInvalidCredentials_ShouldReturnBadRequest()
        {
            var loginRequest = new LoginRequest
            {
                Username = "testuser",
                Password = ""
            };

            var result = _controller.GenerateToken(loginRequest);

            Assert.IsType<BadRequestObjectResult>(result);
            _mockLogger.Verify(logger => logger.LogWarning(It.IsAny<string>(), It.IsAny<object[]>()), Times.Once);
        }
    }
}
```