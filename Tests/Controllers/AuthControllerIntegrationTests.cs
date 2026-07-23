```csharp
using Microsoft.AspNetCore.Mvc.Testing;
using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text;
using Xunit;
using ApiGateway.Models;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly WebApplicationFactory<Program> _factory;
        private readonly HttpClient _client;

        public AuthControllerIntegrationTests(WebApplicationFactory<Program> factory)
        {
            _factory = factory;
            _client = factory.CreateClient();
        }

        [Theory]
        [InlineData("mock-idp-okta", "http://mock-okta.com/token", HttpStatusCode.OK)]
        [InlineData("mock-idp-auth0", "http://mock-auth0.com/token", HttpStatusCode.OK)]
        [InlineData("mock-idp-failure", "http://mock-failure.com/token", HttpStatusCode.BadRequest)]
        public async Task SSO_Flow_Integration_Tests(string provider, string tokenUrl, HttpStatusCode expectedStatusCode)
        {
            // Arrange
            var requestContent = new 
            {
                Provider = provider,
                RedirectUri = "http://localhost/callback",
                Code = "authCodeFromIdP"
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(requestContent), 
                Encoding.UTF8, 
                "application/json");

            // Act
            var response = await _client.PostAsync("/api/auth/sso", jsonContent);
            
            // Assert
            Assert.Equal(expectedStatusCode, response.StatusCode);

            if (response.IsSuccessStatusCode)
            {
                var responseBody = JsonSerializer.Deserialize<TestResponse>(
                    await response.Content.ReadAsStringAsync(), 
                    new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                Assert.NotNull(responseBody);
                Assert.Equal("Success", responseBody.Status);
            }
            else
            {
                var errorResponse = JsonSerializer.Deserialize<ErrorResponse>(
                    await response.Content.ReadAsStringAsync(), 
                    new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                Assert.NotNull(errorResponse);
                Assert.Equal(400, errorResponse.StatusCode);
            }
        }
    }
}
```