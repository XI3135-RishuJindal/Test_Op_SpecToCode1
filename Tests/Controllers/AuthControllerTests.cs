using System;
using System.Threading.Tasks;
using ApiGateway.Controllers;
using ApiGateway.Models;
using ApiGateway.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly Mock<IEmailSender> _emailSenderMock;
        private readonly Mock<ILogger<AuthController>> _loggerMock;
        private readonly Mock<IConfiguration> _configMock;

        public AuthControllerTests()
        {
            _emailSenderMock = new Mock<IEmailSender>();
            _loggerMock = new Mock<ILogger<AuthController>>();
            _configMock = new Mock<IConfiguration>();
            // Only needed for token endpoint, but harmless for register tests.
        }

        private AuthController CreateController()
        {
            return new AuthController(_configMock.Object, _loggerMock.Object, _emailSenderMock.Object);
        }

        [Fact]
        public async Task Register_ValidEmail_ReturnsOk_And_EmailSenderCalled()
        {
            // Arrange
            var controller = CreateController();
            var validEmail = "user.test+foo@example-domain.com";
            var request = new RegisterEmailRequest { Email = validEmail };

            _emailSenderMock
                .Setup(e => e.SendVerificationEmailAsync(It.Is<string>(email => email == validEmail)))
                .Returns(Task.CompletedTask)
                .Verifiable();

            // Act
            var actionResult = await controller.Register(request);

            // Assert
            var okResult = Assert.IsType<OkResult>(actionResult);
            Assert.Equal(StatusCodes.Status200OK, okResult.StatusCode);
            _emailSenderMock.Verify(e => e.SendVerificationEmailAsync(validEmail), Times.Once);
        }

        [Theory]
        [InlineData("")]
        [InlineData(" ")]
        [InlineData(null)]
        [InlineData("plainaddress")]
        [InlineData("missing@tld")]
        [InlineData("@no-local-part.com")]
        [InlineData("Joe Smith <email@domain.com>")]
        [InlineData("email.domain.com")]
        [InlineData("email@domain..com")]
        [InlineData("user@.com")]
        [InlineData("user@com")]
        public async Task Register_InvalidEmail_ReturnsBadRequest_ErrorResponse(string? invalidEmail)
        {
            // Arrange
            var controller = CreateController();
            var request = new RegisterEmailRequest { Email = invalidEmail ?? "" };

            // Act
            var actionResult = await controller.Register(request);

            // Assert
            var badReq = Assert.IsType<BadRequestObjectResult>(actionResult);
            Assert.Equal(StatusCodes.Status400BadRequest, badReq.StatusCode);

            var error = Assert.IsType<ErrorResponse>(badReq.Value);
            Assert.False(string.IsNullOrWhiteSpace(error.Error));
            Assert.False(string.IsNullOrWhiteSpace(error.Message));
            Assert.Equal(400, error.StatusCode);
            Assert.True(error.Timestamp <= DateTime.UtcNow.AddSeconds(1));
        }

        [Fact]
        public async Task Register_EmailSenderThrows_ReturnsInternalServerErrorWithErrorResponse()
        {
            // Arrange
            var controller = CreateController();
            var request = new RegisterEmailRequest { Email = "some.valid-address@example.org" };
            _emailSenderMock
                .Setup(e => e.SendVerificationEmailAsync(It.IsAny<string>()))
                .ThrowsAsync(new Exception("Simulated email send failure"));

            // Act
            var actionResult = await controller.Register(request);

            // Assert
            var objResult = Assert.IsType<ObjectResult>(actionResult);
            Assert.Equal(StatusCodes.Status500InternalServerError, objResult.StatusCode);

            var error = Assert.IsType<ErrorResponse>(objResult.Value);
            Assert.False(string.IsNullOrWhiteSpace(error.Error));
            Assert.False(string.IsNullOrWhiteSpace(error.Message));
            Assert.Equal(500, error.StatusCode);
        }

        [Fact]
        public async Task Register_NullRequest_ReturnsBadRequest_ErrorResponse()
        {
            // Arrange
            var controller = CreateController();

            // Act
            var actionResult = await controller.Register(null);

            // Assert
            var badReq = Assert.IsType<BadRequestObjectResult>(actionResult);
            Assert.Equal(StatusCodes.Status400BadRequest, badReq.StatusCode);

            var error = Assert.IsType<ErrorResponse>(badReq.Value);
            Assert.Contains("required", error.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(400, error.StatusCode);
        }
    }
}