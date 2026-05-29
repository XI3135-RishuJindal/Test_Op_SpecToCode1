```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
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
        private readonly IMemoryCache _cache;
        private const int OtpValidityInMinutes = 10;

        public AuthController(IConfiguration configuration, ILogger<AuthController> logger, IMemoryCache cache)
        {
            _configuration = configuration;
            _logger = logger;
            _cache = cache;
        }

        [HttpPost("token")]
        [ProducesResponseType(typeof(object), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        public IActionResult GenerateToken([FromBody] LoginRequest request)
        {
            _logger.LogInformation("Token generation requested for user: {Username}", request.Username);

            try
            {
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

                _logger.LogInformation("Token generated successfully for user: {Username}", request.Username);

                return Ok(new { Token = tokenString });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Token generation failed for user: {Username}", request.Username);
                return StatusCode(500, new ErrorResponse
                {
                    Error = "TokenGenerationError",
                    Message = "An error occurred while generating the token.",
                    StatusCode = 500
                });
            }
        }

        [HttpPost("generate-otp")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        public IActionResult GenerateOtp(string email)
        {
            _logger.LogInformation("Generating OTP for email: {Email}", email);

            if (string.IsNullOrWhiteSpace(email))
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "InvalidEmail",
                    Message = "Email cannot be null or empty",
                    StatusCode = 400
                });
            }

            var otp = GenerateRandomOtp();
            _cache.Set(email, otp, TimeSpan.FromMinutes(OtpValidityInMinutes));

            // Integration with an email service to send the OTP should be done here
            _logger.LogInformation("OTP generated and stored for email: {Email}", email);

            return Ok(new { Message = "OTP generated successfully" });
        }

        [HttpPost("verify-otp")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        public IActionResult VerifyOtp(string email, string otp)
        {
            _logger.LogInformation("Verifying OTP for email: {Email}", email);

            if (string.IsNullOrWhiteSpace(email) || string.IsNullOrWhiteSpace(otp))
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "InvalidRequest",
                    Message = "Email and OTP are required",
                    StatusCode = 400
                });
            }

            if (_cache.TryGetValue(email, out string savedOtp) && savedOtp == otp)
            {
                _cache.Remove(email);
                _logger.LogInformation("OTP verified successfully for email: {Email}", email);
                return Ok(new { Message = "OTP verified successfully" });
            }

            _logger.LogWarning("OTP verification failed for email: {Email}", email);
            return BadRequest(new ErrorResponse
            {
                Error = "InvalidOtp",
                Message = "Invalid or expired OTP",
                StatusCode = 400
            });
        }

        private string GenerateRandomOtp()
        {
            using var rng = new RNGCryptoServiceProvider();
            var bytes = new byte[4];
            rng.GetBytes(bytes);
            uint random = BitConverter.ToUInt32(bytes, 0) % 1000000;
            return random.ToString("D6");
        }
    }
}
```