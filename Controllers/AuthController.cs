using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ApiGateway.Models;
using ApiGateway.Utilities;

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
            // Never log secrets/passwords or any potentially sensitive user-provided fields
            _logger.LogInformation("Token generation requested for user: {Username}", SensitiveDataMasker.Safe(request.Username));

            try
            {
                if (request == null)
                {
                    return BadRequest(new ErrorResponse
                    {
                        Error = "InvalidRequest",
                        Message = "Request body cannot be null",
                        StatusCode = 400
                    });
                }

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

                _logger.LogInformation("Token generated successfully for user: {Username}", SensitiveDataMasker.Safe(request.Username));

                return Ok(new
                {
                    access_token = tokenString,
                    token_type = "Bearer",
                    expires_in = (int)TimeSpan.FromHours(1).TotalSeconds
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating token");
                return BadRequest(new ErrorResponse
                {
                    Error = "TokenGenerationFailed",
                    Message = "An error occurred while generating the token",
                    StatusCode = 400,
                    Details = null
                });
            }
        }
    }
}