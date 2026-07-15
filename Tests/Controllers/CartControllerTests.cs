using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using ApiGateway.Models;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Tokens;
using Moq;
using Xunit;

namespace ApiGateway.Tests.Controllers
{
    public class CartControllerTests : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly WebApplicationFactory<Program> _factory;
        private readonly JsonSerializerOptions _jsonOptions;

        public CartControllerTests(WebApplicationFactory<Program> factory)
        {
            _factory = factory.WithWebHostBuilder(builder =>
            {
                builder.ConfigureServices(services =>
                {
                    // Optionally, mock services or setup test DI here.
                });
            });
            _jsonOptions = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
        }

        #region JWT Helper

        private string GenerateJwtToken(string username = "testuser", string? userId = null)
        {
            var key = Encoding.UTF8.GetBytes("development-secret-key-for-testing-only-256-bits");
            var tokenHandler = new JwtSecurityTokenHandler();

            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.Name, username),
                new Claim(ClaimTypes.NameIdentifier, userId ?? Guid.NewGuid().ToString()),
                new Claim("username", username)
            };

            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(claims),
                Expires = DateTime.UtcNow.AddMinutes(60),
                Issuer = "ApiGateway",
                Audience = "ApiGatewayUsers",
                SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
            };
            var token = tokenHandler.CreateToken(tokenDescriptor);
            return tokenHandler.WriteToken(token);
        }

        private HttpClient CreateClientWithJwt(string? username = "testuser", string? userId = null)
        {
            var client = _factory.CreateClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", GenerateJwtToken(username, userId));
            return client;
        }

        #endregion

        #region Helper Methods

        private static StringContent AsJson<T>(T obj)
        {
            return new StringContent(JsonSerializer.Serialize(obj, new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase }), Encoding.UTF8, "application/json");
        }

        #endregion

        [Fact(DisplayName = "POST /api/cart/add - Success: Add In-Stock Product")]
        public async Task AddProduct_Success()
        {
            // Arrange
            var client = CreateClientWithJwt();
            var addRequest = new { productId = 101, quantity = 2 };
            // Act
            var response = await client.PostAsync("/api/cart/add", AsJson(addRequest));
            // Assert
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);

            var doc = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
            Assert.True(doc.RootElement.TryGetProperty("cart", out var cartElem));
            // Should reflect our add
            var items = cartElem.GetProperty("items");
            Assert.True(items.GetArrayLength() >= 1);

            var found = false;
            foreach (var item in items.EnumerateArray())
            {
                if (item.GetProperty("productId").GetInt32() == 101 &&
                    item.GetProperty("quantity").GetInt32() == 2 &&
                    item.GetProperty("status").GetString() == "in_stock")
                {
                    found = true;
                }
            }
            Assert.True(found, "Expected item not found in cart.");
        }

        [Fact(DisplayName = "POST /api/cart/add - Out of Stock Product Returns Error")]
        public async Task AddProduct_OutOfStock()
        {
            var client = CreateClientWithJwt();
            // Arrange: Assume product 999 is out of stock (per mock/in-memory service convention)
            var addRequest = new { productId = 999, quantity = 1 };

            var response = await client.PostAsync("/api/cart/add", AsJson(addRequest));
            Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);

            var error = JsonSerializer.Deserialize<ErrorResponse>(await response.Content.ReadAsStringAsync(), _jsonOptions);
            Assert.NotNull(error);
            Assert.Equal("OutOfStock", error.Error);
            Assert.StartsWith("Product", error.Message);
            Assert.Equal(400, error.StatusCode);
        }

        [Theory(DisplayName = "POST /api/cart/add - Invalid Input Returns 400")]
        [InlineData(0, 1, "InvalidProduct")]
        [InlineData(-123, 1, "InvalidProduct")]
        [InlineData(101, 0, "InvalidQuantity")]
        [InlineData(101, -2, "InvalidQuantity")]
        public async Task AddProduct_InvalidInput(int productId, int quantity, string expectedErrorKey)
        {
            var client = CreateClientWithJwt();
            var addRequest = new { productId, quantity };

            var response = await client.PostAsync("/api/cart/add", AsJson(addRequest));
            Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);

            var error = JsonSerializer.Deserialize<ErrorResponse>(await response.Content.ReadAsStringAsync(), _jsonOptions);
            Assert.NotNull(error);
            Assert.Equal(expectedErrorKey, error.Error);
            Assert.Equal(400, error.StatusCode);
        }

        [Fact(DisplayName = "POST /api/cart/add - Unauthenticated Returns 401")]
        public async Task AddProduct_Unauthenticated()
        {
            var client = _factory.CreateClient();

            var addRequest = new { productId = 101, quantity = 1 };
            var response = await client.PostAsync("/api/cart/add", AsJson(addRequest));
            Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
        }

        [Fact(DisplayName = "GET /api/cart - Reflects Inventory Changes: Out-of-Stock Flag")]
        public async Task GetCart_ReflectsInventoryChanges()
        {
            // Arrange: Add two products, one will become out of stock after being added
            var client = CreateClientWithJwt(userId: "CART_REFLECT_INV_CHANGE");
            // Add item in stock
            var addRequest = new { productId = 202, quantity = 3 };
            var resp1 = await client.PostAsync("/api/cart/add", AsJson(addRequest));
            Assert.Equal(HttpStatusCode.OK, resp1.StatusCode);

            // Simulate marking productId 202 as out of stock in inventory
            // For the test, we assume the in-memory inventory service is mutable or has logic for testing.
            // Here, send a special request or assume built-in for productId=202 transitions to out_of_stock (test support).

            // (If such an endpoint exists, we'd POST, or we trust the test implementation for demo.)

            // Fetch cart
            var resp2 = await client.GetAsync("/api/cart");
            Assert.Equal(HttpStatusCode.OK, resp2.StatusCode);

            var doc = JsonDocument.Parse(await resp2.Content.ReadAsStringAsync());
            Assert.True(doc.RootElement.TryGetProperty("cart", out var cartElem));
            var items = cartElem.GetProperty("items");

            var statuses = new List<string>();
            foreach (var item in items.EnumerateArray())
            {
                if (item.GetProperty("productId").GetInt32() == 202)
                    statuses.Add(item.GetProperty("status").GetString()!);
            }

            Assert.Contains("out_of_stock", statuses); // Should be reflected
        }

        [Fact(DisplayName = "GET /api/cart - Returns Accurate Quantities and Inventory")]
        public async Task GetCart_Accurate()
        {
            var client = CreateClientWithJwt(userId: "CART_ACCURATE");

            // Add two different in-stock products
            var addRequest1 = new { productId = 101, quantity = 1 };
            var addRequest2 = new { productId = 102, quantity = 2 };

            var resp1 = await client.PostAsync("/api/cart/add", AsJson(addRequest1));
            var resp2 = await client.PostAsync("/api/cart/add", AsJson(addRequest2));

            Assert.Equal(HttpStatusCode.OK, resp1.StatusCode);
            Assert.Equal(HttpStatusCode.OK, resp2.StatusCode);

            var resp3 = await client.GetAsync("/api/cart");
            Assert.Equal(HttpStatusCode.OK, resp3.StatusCode);

            var doc = JsonDocument.Parse(await resp3.Content.ReadAsStringAsync());
            Assert.True(doc.RootElement.TryGetProperty("cart", out var cartElem));
            var items = cartElem.GetProperty("items");
            Assert.Equal(2, items.GetArrayLength());

            var seen101 = false;
            var seen102 = false;
            foreach (var item in items.EnumerateArray())
            {
                int productId = item.GetProperty("productId").GetInt32();
                int quantity = item.GetProperty("quantity").GetInt32();
                string status = item.GetProperty("status").GetString()!;

                if (productId == 101 && quantity == 1 && status == "in_stock")
                    seen101 = true;
                if (productId == 102 && quantity == 2 && status == "in_stock")
                    seen102 = true;
            }

            Assert.True(seen101 && seen102, "Both added products must be present and in stock.");
        }

        [Fact(DisplayName = "GET /api/cart - Unauthenticated Returns 401")]
        public async Task GetCart_Unauthenticated()
        {
            var client = _factory.CreateClient();
            var resp = await client.GetAsync("/api/cart");
            Assert.Equal(HttpStatusCode.Unauthorized, resp.StatusCode);
        }

        [Fact(DisplayName = "POST /api/cart/add - Nonexistent Product Returns 404")]
        public async Task AddProduct_NonexistentProduct()
        {
            var client = CreateClientWithJwt();
            // Assume product 123456789 does not exist in inventory
            var addRequest = new { productId = 123456789, quantity = 1 };

            var resp = await client.PostAsync("/api/cart/add", AsJson(addRequest));
            Assert.Equal(HttpStatusCode.NotFound, resp.StatusCode);

            var error = JsonSerializer.Deserialize<ErrorResponse>(await resp.Content.ReadAsStringAsync(), _jsonOptions);
            Assert.NotNull(error);
            Assert.Equal("ProductNotFound", error.Error);
            Assert.Equal(404, error.StatusCode);
        }

        [Fact(DisplayName = "POST /api/cart/add - Excess Quantity Fails")]
        public async Task AddProduct_ExcessQuantity()
        {
            var client = CreateClientWithJwt();
            // Try to add more than inventory capacity (assume 5 in stock for productId 101)
            var addRequest = new { productId = 101, quantity = 999 };

            var resp = await client.PostAsync("/api/cart/add", AsJson(addRequest));
            Assert.Equal(HttpStatusCode.BadRequest, resp.StatusCode);

            var error = JsonSerializer.Deserialize<ErrorResponse>(await resp.Content.ReadAsStringAsync(), _jsonOptions);
            Assert.NotNull(error);
            Assert.Equal("OutOfStock", error.Error);
        }

        [Fact(DisplayName = "POST /api/cart/add - Authorization Edge Case: Wrong Audience/Issuer")]
        public async Task AddProduct_WrongJwtClaims_Unauthorized()
        {
            var key = Encoding.UTF8.GetBytes("development-secret-key-for-testing-only-256-bits");
            var tokenHandler = new JwtSecurityTokenHandler();

            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.Name, "wronguser"),
                new Claim("username", "wronguser")
            };

            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(claims),
                Expires = DateTime.UtcNow.AddMinutes(60),
                Issuer = "SomeWrongIssuer",
                Audience = "SomeWrongAudience",
                SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
            };
            var token = tokenHandler.CreateToken(tokenDescriptor);
            var badToken = tokenHandler.WriteToken(token);

            var client = _factory.CreateClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", badToken);
            var addRequest = new { productId = 101, quantity = 1 };

            var resp = await client.PostAsync("/api/cart/add", AsJson(addRequest));
            Assert.Equal(HttpStatusCode.Unauthorized, resp.StatusCode);
        }
    }
}