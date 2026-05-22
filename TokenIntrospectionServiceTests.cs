using Xunit;
using Moq;
using System.Net.Http;
using System.Threading.Tasks;
using ApiGateway.Services;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;

public class TokenIntrospectionServiceTests
{
    [Fact]
    public async Task Test_Introspection_Returns_Active_When_TokenIsValid()
    {
        // Arrange
        var httpClientMock = new Mock<HttpClient>();
        var configMock = new Mock<IConfiguration>();
        var loggerMock = new Mock<ILogger<TokenIntrospectionService>>();

        configMock.SetupGet(x => x["TokenValidation:Fallback:Introspection:Endpoint"]).Returns("https://idp.example.com/introspect");
        configMock.SetupGet(x => x["TokenValidation:Fallback:Introspection:ClientId"]).Returns("client-id");
        configMock.SetupGet(x => x["TokenValidation:Fallback:Introspection:ClientSecret"]).Returns("client-secret");

        var service = new TokenIntrospectionService(httpClientMock.Object, configMock.Object, loggerMock.Object);

        // Act
        var response = await service.IntrospectTokenAsync("valid-token");

        // Assert
        Assert.True(response.Active);
    }

    [Fact]
    public async Task Test_Introspection_Returns_Inactive_When_TokenIsInvalid()
    {
        // Arrange
        var httpClientMock = new Mock<HttpClient>();
        var configMock = new Mock<IConfiguration>();
        var loggerMock = new Mock<ILogger<TokenIntrospectionService>>();

        configMock.SetupGet(x => x["TokenValidation:Fallback:Introspection:Endpoint"]).Returns("https://idp.example.com/introspect");
        configMock.SetupGet(x => x["TokenValidation:Fallback:Introspection:ClientId"]).Returns("client-id");
        configMock.SetupGet(x => x["TokenValidation:Fallback:Introspection:ClientSecret"]).Returns("client-secret");

        var service = new TokenIntrospectionService(httpClientMock.Object, configMock.Object, loggerMock.Object);

        // Act
        var response = await service.IntrospectTokenAsync("invalid-token");

        // Assert
        Assert.False(response.Active);
    }
}
