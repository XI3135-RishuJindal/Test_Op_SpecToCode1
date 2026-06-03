using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using System.Text.RegularExpressions;
using ApiGateway.Models;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<AuthController> _logger;

        // Common passwords list (subset — extend in production with a full dictionary)
        private static readonly HashSet<string> CommonPasswords = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "password", "password1", "password12", "password123", "password1234",
            "123456789012", "qwertyuiopas", "iloveyou1234", "admin123456!A",
            "Welcome1234!", "Passw0rd1234", "P@ssword1234", "letmein123456",
            "monkey123456", "dragon123456", "master123456", "sunshine12345"
        };

        public AuthController(IConfiguration configuration, ILogger<AuthController> logger)
        {
            _configuration = configuration;
            _logger = logger;
        }

        /// <summary>
        /// Validates a password against all enforced policies:
        /// - Minimum 12 characters
        /// - At least one uppercase letter
        /// - At least one lowercase letter
        /// - At least one digit
        /// - At least one special character/symbol
        /// - Not a known common password
        /// </summary>
        /// <param name="password">The password to validate.</param>
        /// <returns>A tuple (isValid, errorMessage). errorMessage is null when valid.</returns>
        public static (bool IsValid, string? ErrorMessage) ValidatePasswordComplexity(string password)
        {
            if (string.IsNullOrWhiteSpace(password))
                return (false, "Password cannot be empty.");

            if (password.Length < 12)
                return (false, "Password must be at least 12 characters long.");

            if (!password.Any(char.IsUpper))
                return (false, "Password must contain at least one uppercase letter.");

            if (!password.Any(char.IsLower))
                return (false, "Password must contain at least one lowercase letter.");

            if (!password.Any(char.IsDigit))
                return (false, "Password must contain at least one digit.");

            if (!password.Any(c => !char.IsLetterOrDigit(c)))
                return (false, "Password must contain at least one special character.");

            if (CommonPasswords.Contains(password))
                return (false, "Password is too common. Please choose a more unique password.");

            return (true, null);
        }

        /// <summary>
        /// Checks whether a password is nearing expiration (within 10 days of the 90-day limit).
        /// </summary>
        /// <param name="lastPasswordChangeDate">The date the password was last changed.</param>
        /// <returns>True if the password expires within 10 days; otherwise false.</returns>
        public static bool IsPasswordNearingExpiration(DateTime lastPasswordChangeDate)
        {
            var expirationDate = lastPasswordChangeDate.AddDays(90);
            var daysUntilExpiration = (expirationDate - DateTime.UtcNow).TotalDays;
            return daysUntilExpiration >= 0 && daysUntilExpiration <= 10;
        }

        /// <summary>
        /// Checks whether a password has expired (older than 90 days).
        /// </summary>
        /// <param name="lastPasswordChangeDate">The date the password was last changed.</param>
        /// <returns>True if the password has expired; otherwise false.</returns>
        public static bool IsPasswordExpired(DateTime lastPasswordChangeDate)
        {
            return (DateTime.UtcNow - lastPasswordChangeDate).TotalDays > 90;
        }

        /// <summary>
        /// Generate JWT token for testing purposes.
        /// Validates password complexity before issuing a token for new-password flows.
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
                // Basic field validation
                if (string.IsNullOrWhiteSpace(request.Username) || string.IsNullOrWhiteSpace(request.Password))
                {
                    return BadRequest(new ErrorResponse
                    {
                        Error = "InvalidCredentials",
                        Message = "Username and password are required",
                        StatusCode = 400
                    });
                }

                // Password complexity validation
                var (isValid, errorMessage) = ValidatePasswordComplexity(request.Password);
                if (!isValid)
                {
                    _logger.LogWarning("Password complexity check failed for user: {Username}", request.Username);
                    return BadRequest(new ErrorResponse
                    {
                        Error = "WeakPassword",
                        Message = errorMessage ?? "Password does not meet complexity requirements.",
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
                    SigningCredentials = new SigningCredentials(
                        new SymmetricSecurityKey(key),
                        SecurityAlgorithms.HmacSha256Signature)
                };

                var token = tokenHandler.CreateToken(tokenDescriptor);
                var tokenString = tokenHandler.WriteToken(token);

                _logger.LogInformation("Token generated successfully for user: {Username}", request.Username);

                return Ok(new
                {
                    token = tokenString,
                    expires = tokenDescriptor.Expires,
                    username = request.Username
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating token for user: {Username}", request.Username);
                return StatusCode(500, new ErrorResponse
                {
                    Error = "InternalServerError",
                    Message = "An error occurred while generating the token",
                    StatusCode = 500
                });
            }
        }

        /// <summary>
        /// Endpoint to change a user's password, enforcing all complexity policies.
        /// </summary>
        [HttpPost("change-password")]
        [ProducesResponseType(typeof(object), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        public IActionResult ChangePassword([FromBody] ChangePasswordRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.Username) ||
                string.IsNullOrWhiteSpace(request.NewPassword))
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "InvalidRequest",
                    Message = "Username and new password are required.",
                    StatusCode = 400
                });
            }

            var (isValid, errorMessage) = ValidatePasswordComplexity(request.NewPassword);
            if (!isValid)
            {
                _logger.LogWarning("Change-password complexity check failed for user: {Username}", request.Username);
                return BadRequest(new ErrorResponse
                {
                    Error = "WeakPassword",
                    Message = errorMessage ?? "Password does not meet complexity requirements.",
                    StatusCode = 400
                });
            }

            _logger.LogInformation("Password changed successfully for user: {Username}", request.Username);
            return Ok(new { message = "Password changed successfully." });
        }

        /// <summary>
        /// Endpoint to check password expiration status for a user.
        /// Returns a warning when the password is nearing expiration (≤10 days remaining).
        /// </summary>
        [HttpGet("password-expiration-status")]
        [ProducesResponseType(typeof(object), StatusCodes.Status200OK)]
        public IActionResult GetPasswordExpirationStatus([FromQuery] string username, [FromQuery] DateTime lastPasswordChangeDate)
        {
            bool expired = IsPasswordExpired(lastPasswordChangeDate);
            bool nearingExpiration = !expired && IsPasswordNearingExpiration(lastPasswordChangeDate);

            var expirationDate = lastPasswordChangeDate.AddDays(90);
            var daysRemaining = Math.Max(0, (expirationDate - DateTime.UtcNow).TotalDays);

            return Ok(new
            {
                username,
                expired,
                nearingExpiration,
                daysRemaining = (int)daysRemaining,
                expirationDate
            });
        }
    }

    /// <summary>
    /// Request model for login / token generation.
    /// </summary>
    public class LoginRequest
    {
        public string Username { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }

    /// <summary>
    /// Request model for changing a password.
    /// </summary>
    public class ChangePasswordRequest
    {
        public string Username { get; set; } = string.Empty;
        public string NewPassword { get; set; } = string.Empty;
    }
}
