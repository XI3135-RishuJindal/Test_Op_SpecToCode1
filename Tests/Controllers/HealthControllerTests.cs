using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using ApiGateway.Controllers;

namespace ApiGateway.Tests.Controllers
{
    public class HealthControllerTests
    {
        private readonly Mock<ILogger<HealthController>> _mockLogger;
        private readonly HealthController _controller;

        public HealthControllerTests()
        {
            _mockLogger = new Mock<ILogger<HealthController>>();
            _controller = new HealthController(_mockLogger.Object);
        }

        [Fact]
        public void Get_ReturnsHealthStatus()
        {
            // Act
            var result = _controller.Get();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var healthResponse = okResult.Value;
            Assert.NotNull(healthResponse);
            
            // Use reflection to check the anonymous object properties
            var statusProperty = healthResponse.GetType().GetProperty("Status");
            Assert.NotNull(statusProperty);
            var status = statusProperty.GetValue(healthResponse) as string;
            Assert.Equal("Healthy", status);
        }
    }
}