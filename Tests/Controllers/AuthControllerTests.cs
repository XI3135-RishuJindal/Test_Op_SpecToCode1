```csharp
using ApiGateway.Controllers;
using ApiGateway.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly AuthController _controller;
        private readonly Mock<ILogger<AuthController>> _loggerMock;
        private readonly IConfiguration _configuration;

        public AuthControllerTests()
        {
            _loggerMock = new Mock<ILogger<AuthController>>();
            var configData = new Dictionary<string, string>
            {
                { "Jwt:Key", "test-key" },
                { "Jwt:Issuer", "issuer" },
                { "Jwt:Audience", "audience" }
            };

            _configuration = new ConfigurationBuilder()
                .AddInMemoryCollection(configData)
                .Build();

            _controller = new AuthController(_configuration, _loggerMock.Object);
        }

        [Fact]
        public async Task RegisterPhoneNumber_InvalidNumber_ShouldReturnBadRequest()
        {
            // Arrange
            var request = new PhoneRegistrationRequest { PhoneNumber = "InvalidNumber" };

            // Act
            var result = await _controller.RegisterPhoneNumber(request) as ObjectResult;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(StatusCodes.Status400BadRequest, result.StatusCode);

            var errorResponse = Assert.IsType<ErrorResponse>(result.Value);
            Assert.Equal("InvalidPhoneNumber", errorResponse.Error);
        }

        [Fact]
        public async Task RegisterPhoneNumber_ValidNumber_ShouldReturnOk()
        {
            // Arrange
            var request = new PhoneRegistrationRequest { PhoneNumber = "+12345678901" };

            // Act
            var result = await _controller.RegisterPhoneNumber(request) as ObjectResult;

            // Assert
            Assert.NotNull(result);
            Assert.Equal(StatusCodes.Status200OK, result.StatusCode);
        }
    }
}
```