using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ApiGateway.Models;

namespace ApiGateway.Controllers
{
    /// <summary>
    /// Provides authentication-related endpoints including test token issuance and SSO helper APIs.
    /// </summary>
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
        /// Generate JWT token for testing purposes.
        /// </summary>
        /// <param name="request">Login request.</param>
        /// <returns>JWT token.</returns>
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

                return Ok(new
                {
                    token = tokenString,
                    expiresAt = tokenDescriptor.Expires
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating token for user: {Username}", request.Username);
                return StatusCode(StatusCodes.Status500InternalServerError, new ErrorResponse
                {
                    Error = "TokenGenerationError",
                    Message = "An error occurred while generating the token",
                    StatusCode = 500
                });
            }
        }

        /// <summary>
        /// Get the list of available third-party SSO providers.
        /// </summary>
        /// <remarks>
        /// This endpoint is unauthenticated and can be used by clients to populate SSO login options.
        /// Providers are currently configured in-memory and are all enabled by default (Google, Facebook, Apple).
        /// </remarks>
        /// <returns>
        /// A list of providers that can be used with the <c>POST /api/auth/sso/login</c> endpoint.
        /// </returns>
        [HttpGet("providers")]
        [ProducesResponseType(typeof(IEnumerable<AuthProviderInfo>), StatusCodes.Status200OK)]
        public IActionResult GetProviders()
        {
            // For this implementation the providers are stubbed in-memory and all enabled.
            var providers = new List<AuthProviderInfo>
            {
                new()
                {
                    Id = "google",
                    DisplayName = "Google",
                    IsEnabled = true
                },
                new()
                {
                    Id = "facebook",
                    DisplayName = "Facebook",
                    IsEnabled = true
                },
                new()
                {
                    Id = "apple",
                    DisplayName = "Apple",
                    IsEnabled = true
                }
            };

            _logger.LogInformation("Returning {Count} SSO providers", providers.Count);

            return Ok(providers);
        }

        /// <summary>
        /// Stubbed SSO login endpoint description.
        /// </summary>
        /// <remarks>
        /// Note: The concrete SSO login behavior (token validation, user mapping, JWT issuance)
        /// is implemented in the SSO services layer. This XML documentation describes the
        /// contract used by Swagger and API consumers:
        ///
        /// Request (JSON):
        ///
        /// <code language="json">
        /// {
        ///   "provider": "google",
        ///   "providerToken": "provider-issued-token-or-code",
        ///   "deviceInfo": "optional device description"
        /// }
        /// </code>
        ///
        /// Successful response (200 OK):
        ///
        /// <code language="json">
        /// {
        ///   "token": "jwt-token-from-api-gateway",
        ///   "expiresAt": "2024-01-01T12:34:56Z",
        ///   "userId": "internal-user-id",
        ///   "isNewUser": true,
        ///   "provider": "google",
        ///   "redirectUrl": "/profile"
        /// }
        /// </code>
        ///
        /// Error responses use <see cref="ErrorResponse"/> with:
        /// - 400 Bad Request for invalid input,
        /// - 401 Unauthorized when the provider token is rejected,
        /// - 500 Internal Server Error for unexpected failures.
        /// </remarks>
        /// <param name="request">The SSO login request payload containing provider and provider token.</param>
        /// <returns>An <see cref="SsoLoginResponse"/> on success, or <see cref="ErrorResponse"/> on failure.</returns>
        [HttpPost("sso/login")]
        [ProducesResponseType(typeof(SsoLoginResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status500InternalServerError)]
        public IActionResult SsoLogin([FromBody] SsoLoginRequest request)
        {
            // The real implementation is provided by the SSO authentication services and
            // is out of scope for this documentation-focused task. This stub exists only
            // so that XML comments can describe the endpoint in Swagger.
            return StatusCode(StatusCodes.Status501NotImplemented, new ErrorResponse
            {
                Error = "NotImplemented",
                Message = "SSO login is implemented in a different branch or service layer.",
                StatusCode = StatusCodes.Status501NotImplemented
            });
        }

        /// <summary>
        /// Simple login request used by the test token endpoint.
        /// </summary>
        public class LoginRequest
        {
            /// <summary>
            /// Username for test token generation.
            /// </summary>
            public string Username { get; set; } = string.Empty;

            /// <summary>
            /// Password for test token generation.
            /// </summary>
            public string Password { get; set; } = string.Empty;
        }
    }
}