using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<AuthController> _logger;
        private readonly HttpClient _httpClient;

        public AuthController(IConfiguration configuration, ILogger<AuthController> logger, HttpClient httpClient)
        {
            _configuration = configuration;
            _logger = logger;
            _httpClient = httpClient;
        }

        /// <summary>
        /// Method to exchange authorization code for tokens at the IdP token endpoint
        /// </summary>
        /// <param name="authorizationCode">Authorization code received from the IdP</param>
        /// <returns>A result indicating success or failure of the token exchange</returns>
        [HttpPost("exchange-token")]
        public async Task<IActionResult> ExchangeToken([FromBody] string authorizationCode)
        {
            if (string.IsNullOrWhiteSpace(authorizationCode))
            {
                return BadRequest("Invalid authorization code.");
            }

            try
            {
                var clientId = _configuration["IdentityProvider:ClientId"];
                var clientSecret = _configuration["IdentityProvider:ClientSecret"];
                var tokenEndpoint = _configuration["IdentityProvider:TokenEndpoint"];
                var redirectUri = _configuration["IdentityProvider:RedirectUri"];

                var requestData = new Dictionary<string, string>
                {
                    { "grant_type", "authorization_code" },
                    { "code", authorizationCode },
                    { "redirect_uri", redirectUri },
                    { "client_id", clientId },
                    { "client_secret", clientSecret }
                };

                var requestContent = new FormUrlEncodedContent(requestData);
                var response = await _httpClient.PostAsync(tokenEndpoint, requestContent);

                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    // TODO: Parse responseContent to extract tokens

                    return Ok("Tokens exchanged successfully.");
                }
                else
                {
                    return StatusCode((int)response.StatusCode, "Token exchange failed.");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during token exchange");
                return StatusCode(500, "Internal server error during token exchange.");
            }
        }
    }
}
