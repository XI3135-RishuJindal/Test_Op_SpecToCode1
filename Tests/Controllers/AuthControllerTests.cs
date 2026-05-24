using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Net;
using System.Net.Http.Json;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;
using Moq;
using Xunit;
using ApiGateway.Controllers;
using ApiGateway.Models;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests : IClassFixture<WebApplicationFactory<ApiGateway.Program>>
    {
        private readonly WebApplicationFactory<ApiGateway.Program> _factory;

        public AuthControllerTests(WebApplicationFactory<ApiGateway.Program> factory)
        {
            _factory = factory;
        }

        [Fact]
        public async Task GenerateToken_ReturnsToken_OnValidCredentials()
        {
            // Arrange
            var client = _factory.CreateClient();
            var loginRequest = new LoginRequest { Username = "testuser", Password = "password" };

            // Act
            var response = await client.PostAsJsonAsync("/api/auth/token", loginRequest);

            // Assert
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadFromJsonAsync<Dictionary<string, string>>();
            Assert.NotNull(responseContent);
            Assert.True(responseContent.ContainsKey("token"));
        }

        [Fact]
        public async Task GenerateToken_ReturnsBadRequest_OnInvalidCredentials()
        {
            // Arrange
            var client = _factory.CreateClient();
            var loginRequest = new LoginRequest { Username = "", Password = "" };

            // Act
            var response = await client.PostAsJsonAsync("/api/auth/token", loginRequest);

            // Assert
            Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
            var errorResponse = await response.Content.ReadFromJsonAsync<ErrorResponse>();
            Assert.NotNull(errorResponse);
            Assert.Equal("InvalidCredentials", errorResponse.Error);
        }

        [Fact]
        public async Task GenerateToken_HandlesTokenSecurely()
        {
            // Arrange
            var client = _factory.CreateClient();
            var loginRequest = new LoginRequest { Username = "testuser", Password = "password" };

            // Act
            var response = await client.PostAsJsonAsync("/api/auth/token", loginRequest);

            // Assert
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadFromJsonAsync<Dictionary<string, string>>();
            var tokenHandler = new JwtSecurityTokenHandler();
            var jwtToken = tokenHandler.ReadJwtToken(responseContent["token"]);
            Assert.NotNull(jwtToken);
            Assert.Equal("ApiGatewayUsers", jwtToken.Audiences.First());
        }
    }
}