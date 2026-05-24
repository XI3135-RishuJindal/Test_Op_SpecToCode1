```csharp
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ApiGateway.Controllers;
using ApiGateway.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;
using Moq;
using Xunit;

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

            _mockConfiguration.SetupGet(c => c["Jwt:Key"]).Returns("development-secret-key-for-testing-only-256-bits");
            _mockConfiguration.SetupGet(c => c["Jwt:Issuer"]).Returns("ApiGateway");
            _mockConfiguration.SetupGet(c => c["Jwt:Audience"]).Returns("ApiGatewayUsers");

            _controller = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Fact]
        public void GenerateToken_ValidCredentials_ReturnsToken()
        {
            // Arrange
            var request = new LoginRequest { Username = "testuser", Password = "validpassword" };

            // Act
            var result = _controller.GenerateToken(request) as OkObjectResult;
            var token = result?.Value as string;

            // Assert
            Assert.NotNull(token);

            // Token Validation
            var tokenHandler = new JwtSecurityTokenHandler();
            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuer = true,
                ValidateAudience = true,
                ValidateLifetime = true,
                ValidateIssuerSigningKey = true,
                ValidIssuer = "ApiGateway",
                ValidAudience = "ApiGatewayUsers",
                IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes("development-secret-key-for-testing-only-256-bits"))
            };

            try
            {
                tokenHandler.ValidateToken(token, validationParameters, out SecurityToken validatedToken);
                _mockLogger.Verify(log => log.LogInformation("Token generated successfully"), Times.Once);
            }
            catch
            {
                Assert.True(false, "Token is invalid");
            }
        }

        [Fact]
        public void GenerateToken_MissingUsernameOrPassword_ReturnsBadRequest()
        {
            // Arrange
            var request = new LoginRequest { Username = "", Password = "" };

            // Act
            var result = _controller.GenerateToken(request) as BadRequestObjectResult;
            var errorResponse = result?.Value as ErrorResponse;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(400, result.StatusCode);
            Assert.Equal("InvalidCredentials", errorResponse?.Error);
            Assert.Equal("Username and password are required", errorResponse?.Message);
            _mockLogger.Verify(log => log.LogInformation("Token generation requested for user: {Username}", It.IsAny<string>()), Times.Once);
        }

        [Fact]
        public void GenerateToken_InvalidClaims_ReturnsError()
        {
            // Arrange
            var request = new LoginRequest { Username = "invaliduser", Password = "wrongpassword" };

            // Act
            var result = _controller.GenerateToken(request) as UnauthorizedObjectResult;
            var errorResponse = result?.Value as ErrorResponse;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(401, result.StatusCode);
            Assert.StartsWith("Authentication failed", errorResponse?.Message);
            _mockLogger.Verify(log => log.LogWarning(It.IsAny<string>(), request.Username), Times.AtLeastOnce);
        }
    }
}
```