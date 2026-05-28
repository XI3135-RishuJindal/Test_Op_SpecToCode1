using System;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using ApiGateway;
using NUnit.Framework;

namespace ApiGateway.Tests.Controllers
{
    [TestFixture]
    public class AuthControllerTests
    {
        private HttpClient _client;

        [SetUp]
        public void Setup()
        {
            var factory = new WebApplicationFactory<Program>()
                .WithWebHostBuilder(builder =>
                {
                    builder.ConfigureServices(services =>
                    {
                        // If any services need to be mocked, it can be done here
                    });
                });

            _client = factory.CreateClient();
        }

        [Test]
        public async Task GenerateToken_ReturnsJwtToken_WhenCredentialsAreValid()
        {
            // Arrange
            var loginRequest = new
            {
                Username = "validUser",
                Password = "validPassword"
            };

            // Act
            var response = await _client.PostAsJsonAsync("api/auth/token", loginRequest);

            // Assert
            Assert.AreEqual(HttpStatusCode.OK, response.StatusCode);
            var tokenResponse = await response.Content.ReadAsStringAsync();
            Assert.IsNotEmpty(tokenResponse);
            Assert.IsTrue(tokenResponse.Contains(".", StringComparison.Ordinal)); // Ensure JWT format
        }

        [Test]
        public async Task GenerateToken_ReturnsBadRequest_WhenCredentialsAreInvalid()
        {
            // Arrange
            var loginRequest = new
            {
                Username = "",
                Password = ""
            };

            // Act
            var response = await _client.PostAsJsonAsync("api/auth/token", loginRequest);

            // Assert
            Assert.AreEqual(HttpStatusCode.BadRequest, response.StatusCode);
        }
    }
}
