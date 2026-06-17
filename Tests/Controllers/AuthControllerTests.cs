```csharp
using Xunit;
using Moq;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using ApiGateway.Controllers;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Models;
using System.Threading.Tasks;

namespace Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly AuthController _authController;
        private readonly Mock<ILogger<AuthController>> _mockLogger;
        private readonly Mock<IConfiguration> _mockConfiguration;

        public AuthControllerTests()
        {
            _mockLogger = new Mock<ILogger<AuthController>>();
            _mockConfiguration = new Mock<IConfiguration>();
            _mockConfiguration.Setup(config => config["Jwt:Key"]).Returns("default-secret-key-for-development");
            _mockConfiguration.Setup(config => config["Jwt:Issuer"]).Returns("ApiGateway");
            _mockConfiguration.Setup(config => config["Jwt:Audience"]).Returns("ApiGatewayUsers");

            _authController = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Fact]
        public void GenerateToken_WithValidRequest_ReturnsOkResult()
        {
            // Arrange
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "testpassword"
            };

            // Act
            var result = _authController.GenerateToken(request) as OkObjectResult;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(200, result.StatusCode);
            Assert.IsType<string>(result.Value);
        }

        [Fact]
        public void GenerateToken_WithInvalidRequest_ReturnsBadRequest()
        {
            // Arrange
            var request = new LoginRequest
            {
                Username = "",
                Password = ""
            };

            // Act
            var result = _authController.GenerateToken(request) as BadRequestObjectResult;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(400, result.StatusCode);
            var errorResponse = Assert.IsType<ErrorResponse>(result.Value);
            Assert.Equal("InvalidCredentials", errorResponse.Error);
        }

        [Fact]
        public async Task ValidatePhoneNumber_ValidNumber_ReturnsTrue()
        {
            // Arrange
            var validNumber = "+1234567890";
            // Assuming ValidatePhoneNumber is a method in your actual implementation
            // Mock the method here if needed

            // Act
            var isValid = _authController.ValidatePhoneNumber(validNumber);

            // Assert
            Assert.True(isValid);
        }

        [Fact]
        public async Task ValidatePhoneNumber_InvalidNumber_ReturnsFalse()
        {
            // Arrange
            var invalidNumber = "invalid";

            // Act
            var isValid = _authController.ValidatePhoneNumber(invalidNumber);

            // Assert
            Assert.False(isValid);
        }

        [Fact]
        public async Task SendVerificationSms_ValidNumber_SendsSms()
        {
            // Arrange
            var validNumber = "+1234567890";
            // Mock your SMS service method if needed

            // Act
            var result = await _authController.SendVerificationSms(validNumber);

            // Assert
            Assert.True(result);
        }

        [Fact]
        public async Task SendVerificationSms_InvalidNumber_DoesNotSendSms()
        {
            // Arrange
            var invalidNumber = "invalid";

            // Act
            var result = await _authController.SendVerificationSms(invalidNumber);

            // Assert
            Assert.False(result);
        }
    }
}
```