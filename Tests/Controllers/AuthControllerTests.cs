```csharp
using System.Net;
using System.Net.Http.Json;
using Xunit;
using ApiGateway.Models;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly HttpClient _client;

        public AuthControllerTests(WebApplicationFactory<Program> factory)
        {
            _client = factory.CreateClient();
        }

        [Fact]
        public async Task GenerateToken_ValidCredentials_ReturnsOk()
        {
            // Arrange
            var request = new { Username = "validUser", Password = "validPassword" };

            // Act
            var response = await _client.PostAsJsonAsync("/api/auth/token", request);

            // Assert
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        }

        [Fact]
        public async Task GenerateToken_InvalidCredentials_ReturnsBadRequest()
        {
            // Arrange
            var request = new { Username = "", Password = "validPassword" };

            // Act
            var response = await _client.PostAsJsonAsync("/api/auth/token", request);

            // Assert
            Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
            var errorResponse = await response.Content.ReadFromJsonAsync<ErrorResponse>();
            Assert.NotNull(errorResponse);
            Assert.Equal("InvalidCredentials", errorResponse!.Error);
        }

        // Additional test cases based on historical SAML-related incidents can be added here
    }
}
```