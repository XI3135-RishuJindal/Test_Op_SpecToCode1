```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ApiGateway.Models;
using Microsoft.AspNetCore.Authorization;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<AuthController> _logger;

        public AuthController(IConfiguration configuration, ILogger<AuthController> logger)
        {
            _configuration = configuration;
            _logger = logger;
        }

        [HttpGet("oauth")]
        public IActionResult OAuthLogin()
        {
            var clientId = _configuration["OAuth:ClientId"];
            var redirectUri = _configuration["OAuth:RedirectUri"];
            var authority = _configuration["OAuth:Authority"];
            var responseType = _configuration["OAuth:ResponseType"];
            var state = "random-state-value"; // Generate securely
            var nonce = "random-nonce-value"; // Generate securely

            var authorizationEndpoint = $"{authority}/authorize?client_id={clientId}&response_type={responseType}&redirect_uri={Uri.EscapeDataString(redirectUri)}&state={state}&nonce={nonce}";

            return Redirect(authorizationEndpoint);
        }

        [HttpGet("callback")]
        public IActionResult Callback(string code, string state, string nonce)
        {
            // Validate state and nonce for security

            // Exchange code for tokens from Identity Provider

            // Logic to handle token response

            return Ok();
        }
    }
}
```