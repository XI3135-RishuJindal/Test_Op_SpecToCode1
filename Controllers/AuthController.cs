```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ApiGateway.Models;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.IdentityModel.Protocols.OpenIdConnect;
using Microsoft.Extensions.Options;

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

        /// <summary>
        /// Initiates the SSO login process with a selected Identity Provider (IdP).
        /// </summary>
        [HttpGet("sso-login")]
        public IActionResult InitiateSsoLogin([FromQuery] string provider)
        {
            var redirectUrl = Url.Action(nameof(SsoCallback), "Auth", null, Request.Scheme);
            var properties = new AuthenticationProperties { RedirectUri = redirectUrl };
            return Challenge(properties, provider);
        }

        /// <summary>
        /// Callback endpoint for the Identity Provider to return authentication results.
        /// </summary>
        [HttpGet("sso-callback")]
        public async Task<IActionResult> SsoCallback()
        {
            var result = await HttpContext.AuthenticateAsync(OpenIdConnectDefaults.AuthenticationScheme);
            if (!result.Succeeded)
            {
                _logger.LogWarning("SSO login failed.");
                return BadRequest(new ErrorResponse
                {
                    Error = "SSOFailed",
                    Message = "Single Sign-On login process failed. Please try again.",
                    StatusCode = 400
                });
            }

            var token = result.Properties.GetTokenValue("id_token");
            var userClaims = ParseIdToken(token);

            // Assuming user profile extraction and account linking logic here

            return Redirect("/products");
        }

        private ClaimsPrincipal ParseIdToken(string idToken)
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes(_configuration["Jwt:Key"]);

            var tokenValidationParameters = new TokenValidationParameters
            {
                // Token parameters
                ValidateIssuer = true,
                ValidateAudience = true,
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ValidIssuer = _configuration["Jwt:Issuer"],
                ValidAudience = _configuration["Jwt:Audience"],
                ValidateLifetime = true,
            };

            var principal = tokenHandler.ValidateToken(idToken, tokenValidationParameters, out _);
            return principal;
        }
    }
}
```