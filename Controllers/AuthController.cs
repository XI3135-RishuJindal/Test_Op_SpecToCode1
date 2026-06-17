```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ApiGateway.Models;
using Twilio;
using Twilio.Rest.Api.V2010.Account;
using Twilio.Types;

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
            TwilioClient.Init(
                _configuration["Twilio:AccountSid"],
                _configuration["Twilio:AuthToken"]);
        }

        /// <summary>
        /// Register and send verification SMS
        /// </summary>
        /// <param name="phoneNumber">User's phone number</param>
        /// <returns>Status of registration</returns>
        [HttpPost("register")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        public IActionResult RegisterPhoneNumber([FromBody] string phoneNumber)
        {
            _logger.LogInformation("Registration requested for phone number: {PhoneNumber}", phoneNumber);

            if (string.IsNullOrWhiteSpace(phoneNumber) || !IsValidPhoneNumber(phoneNumber))
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "InvalidPhoneNumber",
                    Message = "The phone number is not valid.",
                    StatusCode = 400
                });
            }

            try
            {
                var message = MessageResource.Create(
                    body: "Your verification token is 123456.",
                    from: new PhoneNumber(_configuration["Twilio:FromNumber"]),
                    to: new PhoneNumber(phoneNumber)
                );

                _logger.LogInformation("SMS sent successfully to: {PhoneNumber}", phoneNumber);
                return Ok(new { Message = "Verification SMS sent successfully." });

            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error sending SMS to {PhoneNumber}", phoneNumber);
                return StatusCode(500, new ErrorResponse
                {
                    Error = "SmsSendFailure",
                    Message = "There was an error sending the SMS.",
                    StatusCode = 500
                });
            }
        }

        private bool IsValidPhoneNumber(string phoneNumber)
        {
            // Simple placeholder for accurate phone validation
            var phoneRegex = @"^\+?[1-9]\d{1,14}$";
            return System.Text.RegularExpressions.Regex.IsMatch(phoneNumber, phoneRegex);
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
                return Ok(new { Token = tokenString });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating token for user: {Username}", request.Username);
                return StatusCode(500, new ErrorResponse
                {
                    Error = "TokenGenerationError",
                    Message = "There was an error generating the token.",
                    StatusCode = 500
                });
            }
        }
    }
}
```