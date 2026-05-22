using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;

namespace ApiGateway.Services
{
    public class TokenIntrospectionService : ITokenIntrospectionService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private readonly ILogger<TokenIntrospectionService> _logger;

        public TokenIntrospectionService(HttpClient httpClient, IConfiguration configuration, ILogger<TokenIntrospectionService> logger)
        {
            _httpClient = httpClient;
            _configuration = configuration;
            _logger = logger;
        }

        public async Task<IntrospectionResponse> IntrospectTokenAsync(string token)
        {
            // URL and credentials should be fetched from configuration
            var introspectionEndpoint = _configuration["TokenValidation:Fallback:Introspection:Endpoint"];
            var clientId = _configuration["TokenValidation:Fallback:Introspection:ClientId"];
            var clientSecret = _configuration["TokenValidation:Fallback:Introspection:ClientSecret"];

            var requestMessage = new HttpRequestMessage(HttpMethod.Post, introspectionEndpoint)
            {
                Content = new FormUrlEncodedContent(new[]
                {
                    new KeyValuePair<string, string>("token", token),
                    new KeyValuePair<string, string>("client_id", clientId),
                    new KeyValuePair<string, string>("client_secret", clientSecret)
                })
            };

            var response = await _httpClient.SendAsync(requestMessage);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("Introspection call failed with status code {StatusCode}", response.StatusCode);
                return new IntrospectionResponse { Active = false };
            }

            // Parse response content here
            var content = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Introspection response: {Content}", content);

            // For simplicity, let's assume content is directly parsed
            return new IntrospectionResponse { Active = true }; // Placeholder
        }
    }
}