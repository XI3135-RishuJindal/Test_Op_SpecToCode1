using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.PlatformAbstractions;
using NUnit.Framework;
using ApiGateway;

namespace ApiGateway.Tests.Controllers
{
    [TestFixture]
    public class UnauthorizedAccessTests
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
        public async Task Get_ProtectedEndpoint_ReturnsUnauthorized_WhenNoTokenProvided()
        {
            // Arrange
            var endpoint = "api/protected"; // Example endpoint, replace with actual

            // Act
            var response = await _client.GetAsync(endpoint);

            // Assert
            Assert.AreEqual(HttpStatusCode.Unauthorized, response.StatusCode);
        }
    }
}
