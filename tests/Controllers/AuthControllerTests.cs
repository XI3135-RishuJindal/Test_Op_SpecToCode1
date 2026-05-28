```csharp
using Xunit;
using Moq;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using ApiGateway.Controllers;
using ApiGateway.Models;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;

public class AuthControllerTests
{
    private readonly Mock<IConfiguration> _mockConfiguration;
    private readonly Mock<IRoleMappingService> _mockRoleMappingService;
    private readonly Mock<ILogger<AuthController>> _mockLogger;

    public AuthControllerTests()
    {
        _mockConfiguration = new Mock<IConfiguration>();
        _mockRoleMappingService = new Mock<IRoleMappingService>();
        _mockLogger = new Mock<ILogger<AuthController>>();

        _mockConfiguration.Setup(config => config["Jwt:Key"]).Returns("your-secret-key-here-must-be-at-least-256-bits");
        _mockConfiguration.Setup(config => config["Jwt:Issuer"]).Returns("ApiGateway");
        _mockConfiguration.Setup(config => config["Jwt:Audience"]).Returns("ApiGatewayUsers");
    }

    [Fact]
    public void GenerateToken_ValidCredentials_ReturnsToken()
    {
        // Arrange
        var controller = new AuthController(_mockConfiguration.Object, _mockRoleMappingService.Object, _mockLogger.Object);
        var loginRequest = new LoginRequest { Username = "testuser", Password = "testpassword" };

        _mockRoleMappingService.Setup(service => service.GetRolesForUser(It.IsAny<string>()))
            .Returns(new List<string> { "User" });

        // Act
        var result = controller.GenerateToken(loginRequest);

        // Assert
        Assert.IsType<OkObjectResult>(result);
        var okResult = result as OkObjectResult;
        Assert.NotNull(okResult);
        Assert.Contains("Token", (okResult.Value as dynamic).Token);
    }
}
```