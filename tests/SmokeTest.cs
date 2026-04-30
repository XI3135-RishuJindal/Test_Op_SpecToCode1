using System.Net.Http;
using System.Net;
using System.Threading.Tasks;
using Xunit;
using Newtonsoft.Json;

namespace MyApi.Tests
{
    public class SmokeTests
    {
        private readonly HttpClient _client;

        public SmokeTests()
        {
            var webAppFactory = new WebApplicationFactory<Startup>();
            _client = webAppFactory.CreateClient();
        }

        [Fact]
        public async Task Get_Health_Check_Returns_Ok()
        {
            // Arrange
            var requestUri = "/api/health";

            // Act
            var response = await _client.GetAsync(requestUri);

            // Assert
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        }

        [Fact]
        public async Task Get_Users_Returns_Expected_Data()
        {
            // Arrange
            var requestUri = "/api/users";

            // Act
            var response = await _client.GetAsync(requestUri);
            response.EnsureSuccessStatusCode(); // Will throw if not a success code.

            var responseData = await response.Content.ReadAsStringAsync();
            var users = JsonConvert.DeserializeObject<List<User>>(responseData);

            // Assert
            Assert.NotNull(users);
            Assert.True(users.Count > 0);
        }

        [Fact]
        public async Task Post_User_Creation_Returns_Created()
        {
            // Arrange
            var newUser = new User { Name = "Test User", Email = "testuser@example.com" };
            var content = new StringContent(JsonConvert.SerializeObject(newUser), Encoding.UTF8, "application/json");
            var requestUri = "/api/users";

            // Act
            var response = await _client.PostAsync(requestUri, content);

            // Assert
            Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        }
    }
}