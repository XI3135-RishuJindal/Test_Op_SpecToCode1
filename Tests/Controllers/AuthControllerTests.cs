```csharp
using ApiGateway.Controllers;
using ApiGateway.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
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
            _controller = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Fact]
        public void InitiateSSOLogin_ShouldReturnOk_WhenSSOSuccessful()
        {
            // Act
            var result = _controller.InitiateSSOLogin();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            Assert.Equal("SSO login successful", ((dynamic)okResult.Value).Message);
        }

        [Fact]
        public void InitiateSSOLogin_ShouldLogWarning_WhenSSOTakesTooLong()
        {
            // Arrange
            // Simulate long delay by overriding SimulateSSORedirect method locally
            var controller = new AuthController(_mockConfiguration.Object, _mockLogger.Object)
            {
                SimulateSSORedirect = () =>
                {
                    System.Threading.Thread.Sleep(3100); // Simulate delay
                    return true;
                }
            };

            // Act
            var result = controller.InitiateSSOLogin();

            // Assert
            _mockLogger.Verify(logger => logger.LogWarning(It.IsAny<string>(), It.IsAny<object[]>()), Times.Once);
        }
    }
}
```