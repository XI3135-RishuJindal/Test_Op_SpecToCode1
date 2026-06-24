```csharp
using Xunit;
using Microsoft.AspNetCore.Mvc;
using Moq;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using ApiGateway.Controllers;
using ApiGateway.Models;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly Mock<IConfiguration> _mockConfiguration;
        private readonly Mock<ILogger<AuthController>> _mockLogger;
        private readonly AuthController _controller;

        public AuthControllerTests()
        {
            _mockConfiguration = new Mock<IConfiguration>();
            _mockLogger = new Mock<ILogger<AuthController>>();
            _controller = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Fact]
        public void GenerateToken_ReturnsBadRequest_OnInvalidCredentials()
        {
            // Arrange
            var loginRequest = new LoginRequest
            {
                Username = string.Empty,
                Password = string.Empty
            };

            // Act
            var result = _controller.GenerateToken(loginRequest) as BadRequestObjectResult;

            // Assert
            Assert.NotNull(result);
            var errorResponse = result.Value as ErrorResponse;
            Assert.NotNull(errorResponse);
            Assert.Equal("InvalidCredentials", errorResponse.Error);
            Assert.Equal("Username and password are required", errorResponse.Message);
        }

        [Fact]
        public void GenerateToken_ReturnsToken_OnValidRequest()
        {
            // Arrange
            var loginRequest = new LoginRequest
            {
                Username = "testuser",
                Password = "testpassword"
            };

            _mockConfiguration.Setup(c => c["Jwt:Key"]).Returns("your-secret-key-here-must-be-at-least-256-bits");
            _mockConfiguration.Setup(c => c["Jwt:Issuer"]).Returns("ApiGateway");
            _mockConfiguration.Setup(c => c["Jwt:Audience"]).Returns("ApiGatewayUsers");

            // Act
            var result = _controller.GenerateToken(loginRequest) as OkObjectResult;

            // Assert
            Assert.NotNull(result);
            Assert.IsType<ObjectResult>(result);
        }
    }
}
```