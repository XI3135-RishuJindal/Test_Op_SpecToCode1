```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ApiGateway.Models;

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
        /// Generate JWT token for testing purposes
        /// </summary>
        /// <param name="request">Login request</param>
        /// <returns>JWT token</returns>
        [HttpPost("token")]
        [ProducesResponseType(typeof(object), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        public IActionResult GenerateToken([FromBody] LoginRequest request)
        {
            _logger.LogInformation("Token generation requested for user: {Username}", request.Username);

            try
            {
                // Simple validation for demo purposes
                if (string.IsNullOrWhiteSpace(request.Username) || string.IsNullOrWhiteSpace(request.Password))
                {
                    return BadRequest(new ErrorResponse
                    {
                        Error = "InvalidCredentials",
                        Message = "Username and password are required",
                        StatusCode = 400
                    });
                }

                // For demo purposes, accept any non-empty credentials
                // In production, this would validate against a user store
                var tokenHandler = new JwtSecurityTokenHandler();
                var key = Encoding.UTF8.GetBytes(_configuration["Jwt:Key"] ?? "default-secret-key-for-development");
                
                var tokenDescriptor = new SecurityTokenDescriptor
                {
                    Subject = new ClaimsIdentity(new[]
                    {
                        new Claim(ClaimTypes.Name, request.Username),
                        new Claim(ClaimTypes.NameIdentifier, Guid.NewGuid().ToString()),
                        new Claim("username", request.Username)
                    }),
                    Expires = DateTime.UtcNow.AddHours(1),
                    Issuer = _configuration["Jwt:Issuer"],
                    Audience = _configuration["Jwt:Audience"],
                    SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
                };

                var token = tokenHandler.CreateToken(tokenDescriptor);
                var tokenString = tokenHandler.WriteToken(token);

                _logger.LogInformation("Token generated successfully for user: {Username}", request.Username);
                return Ok(new { token = tokenString });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error during token generation for user: {Username}", request.Username);
                return StatusCode(500, new ErrorResponse
                {
                    Error = "TokenGenerationError",
                    Message = "An unexpected error occurred",
                    StatusCode = 500
                });
            }
        }

        /// <summary>
        /// Validate the claims of a JWT token
        /// </summary>
        /// <param name="claimsPrincipal">ClaimsPrincipal to validate</param>
        /// <returns>True if valid, otherwise false</returns>
        private bool ValidateClaims(ClaimsPrincipal claimsPrincipal)
        {
            var requiredClaims = new[] { "sub", "email", "name", "roles" };
            var missingClaims = requiredClaims.Where(claim => !claimsPrincipal.HasClaim(c => c.Type == claim)).ToList();

            if (missingClaims.Any())
            {
                _logger.LogWarning("Missing or invalid claims: {Claims}", string.Join(", ", missingClaims));
                return false;
            }
            return true;
        }
    }
}
```