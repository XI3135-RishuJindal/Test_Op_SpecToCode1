using Xunit;
using Moq;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;
using System.IO;
using ApiGateway.Middleware;

public class TokenValidationFallbackMiddlewareTests
{
    [Fact]
    public async Task Test_TokenValidation_Passes_When_ValidToken()
    {
        // Arrange
        var loggerMock = new Mock<ILogger<TokenValidationFallbackMiddleware>>();
        var middleware = new TokenValidationFallbackMiddleware((innerHttpContext) => Task.CompletedTask, loggerMock.Object);

        var context = new DefaultHttpContext();
        context.Request.Headers["Authorization"] = "Bearer valid-token";

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        Assert.Equal(StatusCodes.Status200OK, context.Response.StatusCode);
    }

    [Fact]
    public async Task Test_TokenValidation_Fails_When_InvalidToken()
    {
        // Arrange
        var loggerMock = new Mock<ILogger<TokenValidationFallbackMiddleware>>();
        var middleware = new TokenValidationFallbackMiddleware((innerHttpContext) => Task.CompletedTask, loggerMock.Object);

        var context = new DefaultHttpContext();

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        Assert.Equal(StatusCodes.Status401Unauthorized, context.Response.StatusCode);
    }
}
