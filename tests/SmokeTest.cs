using Microsoft.AspNetCore.Mvc;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Net.Http;
using System.Threading.Tasks;

namespace MyApi.Tests
{
    [TestClass]
    public class ApiSmokeTests
    {
        private static readonly HttpClient httpClient = new HttpClient();

        [TestMethod]
        public async Task GetValues_ReturnsOk()
        {
            // Arrange
            var requestUri = "http://localhost:5000/api/values"; // Update with actual base URL after deployment

            // Act
            var response = await httpClient.GetAsync(requestUri);

            // Assert
            Assert.AreEqual(System.Net.HttpStatusCode.OK, response.StatusCode);
        }

        [TestMethod]
        public async Task GetValueById_ReturnsOk()
        {
            // Arrange
            var requestUri = "http://localhost:5000/api/values/1"; // Update with actual base URL after deployment

            // Act
            var response = await httpClient.GetAsync(requestUri);

            // Assert
            Assert.AreEqual(System.Net.HttpStatusCode.OK, response.StatusCode);
        }

        [TestMethod]
        public async Task PostValue_CreatesValue()
        {
            // Arrange
            var requestUri = "http://localhost:5000/api/values"; // Update with actual base URL after deployment
            var content = new StringContent("{\"name\":\"Test Value\"}", System.Text.Encoding.UTF8, "application/json");

            // Act
            var response = await httpClient.PostAsync(requestUri, content);

            // Assert
            Assert.AreEqual(System.Net.HttpStatusCode.Created, response.StatusCode);
        }
    }
}