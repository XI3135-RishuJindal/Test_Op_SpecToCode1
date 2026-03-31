using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using ApiGateway.Controllers;

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
            
            // Setup configuration
            _mockConfiguration.Setup(x => x["Jwt:Key"]).Returns("test-secret-key-for-unit-tests-256-bits");
            _mockConfiguration.Setup(x => x["Jwt:Issuer"]).Returns("TestIssuer");
            _mockConfiguration.Setup(x => x["Jwt:Audience"]).Returns("TestAudience");
            
            _controller = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Fact]
        public void GenerateToken_ValidCredentials_ReturnsToken()
        {
            // Arrange
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "testpassword"
            };

            // Act
            var result = _controller.GenerateToken(request);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var tokenResponse = okResult.Value;
            Assert.NotNull(tokenResponse);
            
            // Use reflection to check the anonymous object properties
            var tokenProperty = tokenResponse.GetType().GetProperty("Token");
            Assert.NotNull(tokenProperty);
            var token = tokenProperty.GetValue(tokenResponse) as string;
            Assert.NotNull(token);
            Assert.NotEmpty(token);
        }

        [Fact]
        public void GenerateToken_EmptyUsername_ReturnsBadRequest()
        {
            // Arrange
            var request = new LoginRequest
            {
                Username = "",
                Password = "testpassword"
            };

            // Act
            var result = _controller.GenerateToken(request);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            Assert.NotNull(badRequestResult.Value);
        }

        [Fact]
        public void GenerateToken_EmptyPassword_ReturnsBadRequest()
        {
            // Arrange
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = ""
            };

            // Act
            var result = _controller.GenerateToken(request);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            Assert.NotNull(badRequestResult.Value);
        }
    }
}