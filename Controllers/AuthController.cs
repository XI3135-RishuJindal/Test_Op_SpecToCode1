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
            // Log the incoming SAML authentication request with contextual details
            _logger.LogInformation(
                "SAML authentication token generation requested. Username: {Username}, RemoteIP: {RemoteIP}, RequestPath: {RequestPath}",
                request?.Username ?? "(null)",
                HttpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                HttpContext.Request.Path);

            try
            {
                // Validate that required credentials are present
                if (string.IsNullOrWhiteSpace(request?.Username) || string.IsNullOrWhiteSpace(request?.Password))
                {
                    // Enhanced diagnostic log: capture which field(s) are missing
                    _logger.LogWarning(
                        "SAML authentication request rejected due to missing credentials. " +
                        "UsernameProvided: {UsernameProvided}, PasswordProvided: {PasswordProvided}, " +
                        "RemoteIP: {RemoteIP}, RequestPath: {RequestPath}",
                        !string.IsNullOrWhiteSpace(request?.Username),
                        !string.IsNullOrWhiteSpace(request?.Password),
                        HttpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                        HttpContext.Request.Path);

                    return BadRequest(new ErrorResponse
                    {
                        Error = "InvalidCredentials",
                        Message = "Username and password are required",
                        StatusCode = 400
                    });
                }

                // For demo purposes, accept any non-empty credentials.
                // In production, this would validate against a user store.
                var tokenHandler = new JwtSecurityTokenHandler();
                var key = Encoding.UTF8.GetBytes(
                    _configuration["Jwt:Key"] ?? "default-secret-key-for-development");

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

                // Log successful token issuance with expiry details for audit trail
                _logger.LogInformation(
                    "SAML authentication token generated successfully. " +
                    "Username: {Username}, TokenExpiry: {TokenExpiry}, " +
                    "Issuer: {Issuer}, Audience: {Audience}",
                    request.Username,
                    tokenDescriptor.Expires,
                    tokenDescriptor.Issuer,
                    tokenDescriptor.Audience);

                return Ok(new { token = tokenString });
            }
            catch (Exception ex)
            {
                // Enhanced error log: capture full exception context for SAML diagnostics
                _logger.LogError(
                    ex,
                    "An unexpected error occurred while processing SAML authentication request. " +
                    "Username: {Username}, RemoteIP: {RemoteIP}, ErrorMessage: {ErrorMessage}",
                    request?.Username ?? "(null)",
                    HttpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                    ex.Message);

                return StatusCode(StatusCodes.Status500InternalServerError, new ErrorResponse
                {
                    Error = "InternalServerError",
                    Message = "An unexpected error occurred while processing the authentication request",
                    StatusCode = 500
                });
            }
        }
    }

    /// <summary>
    /// Login request model used for SAML-based authentication token generation
    /// </summary>
    public class LoginRequest
    {
        public string Username { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }
}
