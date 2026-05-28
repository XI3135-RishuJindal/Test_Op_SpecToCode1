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

                // Example role assignment - this would typically be retrieved from a database
                var roles = new List<string> { "Customer" }; // Default role
                if (request.Username == "admin")
                {
                    roles.Add("Administrator");
                }

                var claims = new[] {
                    new Claim(ClaimTypes.Name, request.Username),
                    new Claim(ClaimTypes.NameIdentifier, Guid.NewGuid().ToString()),
                    new Claim("username", request.Username),
                }
                .Union(roles.Select(role => new Claim("roles", role)));

                var tokenDescriptor = new SecurityTokenDescriptor
                {
                    Subject = new ClaimsIdentity(claims),
                    Expires = DateTime.UtcNow.AddHours(1),
                    Issuer = _configuration["Jwt:Issuer"],
                    Audience = _configuration["Jwt:Audience"],
                    SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
                };

                var token = tokenHandler.CreateToken(tokenDescriptor);
                var tokenString = tokenHandler.WriteToken(token);

                _logger.LogInformation("Token generated successfully");
                return Ok(new { Token = tokenString });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating token");
                return StatusCode(500, new ErrorResponse
                {
                    Error = "TokenGenerationFailed",
                    Message = "An error occurred while generating the token",
                    StatusCode = 500
                });
            }
        }
    }
}
```