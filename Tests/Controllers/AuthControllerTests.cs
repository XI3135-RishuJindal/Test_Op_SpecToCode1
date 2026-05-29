```csharp
using ApiGateway.Controllers;
using ApiGateway.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Security.Claims;
using System.Text;
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
            _mockConfiguration.Setup(config => config["Jwt:Key"]).Returns("your-secret-key-here-must-be-at-least-256-bits");
            _mockConfiguration.Setup(config => config["Jwt:Issuer"]).Returns("ApiGateway");
            _mockConfiguration.Setup(config => config["Jwt:Audience"]).Returns("ApiGatewayUsers");

            _mockLogger = new Mock<ILogger<AuthController>>();
            _controller = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Fact]
        public void GenerateToken_WithValidCredentials_ReturnsToken()
        {
            // Arrange
            var loginRequest = new LoginRequest
            {
                Username = "testuser",
                Password = "password"
            };

            // Act
            var result = _controller.GenerateToken(loginRequest) as OkObjectResult;
            var token = result?.Value as JwtSecurityToken;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(StatusCodes.Status200OK, result.StatusCode);
            Assert.NotNull(token);
            Assert.Equal("ApiGateway", token.Issuer);
            Assert.Contains(token.Claims, c => c.Type == ClaimTypes.Name && c.Value == "testuser");
        }

        [Fact]
        public void GenerateToken_WithInvalidCredentials_ReturnsBadRequest()
        {
            // Arrange
            var loginRequest = new LoginRequest
            {
                Username = "",
                Password = "password"
            };

            // Act
            var result = _controller.GenerateToken(loginRequest) as BadRequestObjectResult;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(StatusCodes.Status400BadRequest, result.StatusCode);
            Assert.Equal("InvalidCredentials", ((ErrorResponse)result.Value).Error);
        }

        [Fact]
        public void LinkAccounts_WithEmailMatch_ReturnsLinkingPrompt()
        {
            // Arrange
            var email = "existinguser@example.com";
            // Simulate an email that matches existing account

            // Act
            var result = _controller.LinkAccount(email) as OkObjectResult;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(StatusCodes.Status200OK, result.StatusCode);
        }

        [Fact]
        public void LinkAccounts_WithNoEmailMatch_ReturnsNotFound()
        {
            // Arrange
            var email = "newuser@example.com";
            // Simulate an email that does not match existing accounts

            // Act
            var result = _controller.LinkAccount(email) as NotFoundResult;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(StatusCodes.Status404NotFound, result.StatusCode);
        }

        [Fact]
        public void LinkAccounts_WithSuccessfulVerification_ChangesAuthorization()
        {
            // Arrange
            var email = "verifieduser@example.com";
            // Simulate successful account verification

            // Act
            var result = _controller.VerifyAndLinkAccount(email) as OkObjectResult;
            var token = result?.Value as JwtSecurityToken;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(StatusCodes.Status200OK, result.StatusCode);
            Assert.NotNull(token);
            Assert.Contains(token.Claims, c => c.Type == ClaimTypes.Name && c.Value == "verifieduser@example.com");
            Assert.True(result.Value is JwtSecurityToken);
        }
    }
}
```