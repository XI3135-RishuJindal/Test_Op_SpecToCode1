using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using ApiGateway.Controllers;
using ApiGateway.Models;

namespace ApiGateway.Tests.Controllers
{
    public class TestControllerTests
    {
        private readonly Mock<ILogger<TestController>> _mockLogger;
        private readonly TestController _controller;

        public TestControllerTests()
        {
            _mockLogger = new Mock<ILogger<TestController>>();
            _controller = new TestController(_mockLogger.Object);
        }

        [Fact]
        public async Task Post_ValidRequest_ReturnsOkResult()
        {
            // Arrange
            var request = new TestRequest
            {
                Message = "Test message",
                Medication = new MedicationDTO
                {
                    Id = 1,
                    Name = "Test Medication",
                    Description = "Test Description",
                    Dosage = 10.5m,
                    Unit = "mg",
                    CreatedAt = DateTime.UtcNow
                }
            };

            // Act
            var result = await _controller.Post(request);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var response = Assert.IsType<TestResponse>(okResult.Value);
            Assert.Equal("Success", response.Status);
            Assert.Contains("Test message", response.Message);
            Assert.NotNull(response.ProcessedMedication);
            Assert.Equal("Test Medication", response.ProcessedMedication.Name);
        }

        [Fact]
        public async Task Post_NullRequest_ReturnsBadRequest()
        {
            // Act
            var result = await _controller.Post(null!);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequestResult.Value);
            Assert.Equal("InvalidRequest", errorResponse.Error);
            Assert.Equal(400, errorResponse.StatusCode);
        }

        [Fact]
        public async Task Post_EmptyMessage_ReturnsBadRequest()
        {
            // Arrange
            var request = new TestRequest
            {
                Message = ""
            };

            // Act
            var result = await _controller.Post(request);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequestResult.Value);
            Assert.Equal("InvalidMessage", errorResponse.Error);
            Assert.Equal(400, errorResponse.StatusCode);
        }

        [Fact]
        public async Task Post_RequestWithoutMedication_ReturnsOkResult()
        {
            // Arrange
            var request = new TestRequest
            {
                Message = "Test message without medication"
            };

            // Act
            var result = await _controller.Post(request);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var response = Assert.IsType<TestResponse>(okResult.Value);
            Assert.Equal("Success", response.Status);
            Assert.Null(response.ProcessedMedication);
        }
    }
}