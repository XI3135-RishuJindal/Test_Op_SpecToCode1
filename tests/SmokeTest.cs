using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Xunit;

namespace YourNamespace.Tests
{
    public class ApiIntegrationTests
    {
        private readonly HttpClient _client;

        public ApiIntegrationTests()
        {
            var factory = new WebApplicationFactory<Startup>(); // Adjust to your app's Startup class
            _client = factory.CreateClient();
        }

        [Fact]
        public async Task Get_User_By_Id_Returns_User()
        {
            // Arrange
            var userId = 1; // Adjust based on your data setup

            // Act
            var response = await _client.GetAsync($"/api/users/{userId}");
            response.EnsureSuccessStatusCode();

            // Assert
            var user = await response.Content.ReadFromJsonAsync<User>(); // Adjust User model accordingly
            Assert.NotNull(user);
            Assert.Equal(userId, user.Id);
        }

        [Fact]
        public async Task Authenticate_User_Returns_Jwt()
        {
            // Arrange
            var loginInfo = new { Username = "testuser", Password = "password" }; // Adjust for your case

            // Act
            var response = await _client.PostAsJsonAsync("/api/auth/login", loginInfo);
            response.EnsureSuccessStatusCode();

            // Assert
            var jwt = await response.Content.ReadAsStringAsync();
            Assert.False(string.IsNullOrWhiteSpace(jwt));
        }

        [Fact]
        public async Task Get_Products_Returns_Product_List()
        {
            // Act
            var response = await _client.GetAsync("/api/products");
            response.EnsureSuccessStatusCode();

            // Assert
            var products = await response.Content.ReadFromJsonAsync<List<Product>>(); // Adjust Product model accordingly
            Assert.NotNull(products);
            Assert.NotEmpty(products);
        }

        // Additional tests as needed
    }
}