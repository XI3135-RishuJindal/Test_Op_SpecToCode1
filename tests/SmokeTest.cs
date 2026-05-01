using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace MyApi.Tests
{
    public class ApiIntegrationTests : IClassFixture<WebApplicationFactory<Startup>>
    {
        private readonly HttpClient _client;

        public ApiIntegrationTests(WebApplicationFactory<Startup> factory)
        {
            _client = factory.CreateClient();
        }

        [Fact]
        public async Task Get_EndpointsReturnSuccessAndCorrectContentType()
        {
            // Arrange
            var request = "/api/yourendpoint"; // Replace with your actual endpoint

            // Act
            var response = await _client.GetAsync(request);

            // Assert
            response.EnsureSuccessStatusCode(); // Status Code 200-299
            Assert.Equal("application/json; charset=utf-8", response.Content.Headers.ContentType.ToString());
        }

        [Fact]
        public async Task Post_EndpointReturnsCreatedResponse()
        {
            // Arrange
            var request = "/api/yourendpoint"; // Replace with your actual endpoint
            var content = new StringContent("{ \"name\": \"Test\" }", Encoding.UTF8, "application/json");

            // Act
            var response = await _client.PostAsync(request, content);

            // Assert
            Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        }

        [Fact]
        public async Task Put_EndpointReturnsOkResponse()
        {
            // Arrange
            var request = "/api/yourendpoint/1"; // Replace with your actual endpoint and id
            var content = new StringContent("{ \"name\": \"Updated Name\" }", Encoding.UTF8, "application/json");

            // Act
            var response = await _client.PutAsync(request, content);

            // Assert
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        }

        [Fact]
        public async Task Delete_EndpointReturnsNoContent()
        {
            // Arrange
            var request = "/api/yourendpoint/1"; // Replace with your actual endpoint and id

            // Act
            var response = await _client.DeleteAsync(request);

            // Assert
            Assert.Equal(HttpStatusCode.NoContent, response.StatusCode);
        }
    }
}