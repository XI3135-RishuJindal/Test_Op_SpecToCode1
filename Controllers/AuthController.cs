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
using System.Text.RegularExpressions;

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
            TwilioClient.Init(_configuration["Twilio:AccountSid"], _configuration["Twilio:AuthToken"]);
        }

        [HttpPost("register-phone")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        public IActionResult RegisterPhoneNumber([FromBody] PhoneNumberRequest request)
        {
            _logger.LogInformation("Phone number registration requested for number: {PhoneNumber}", request.PhoneNumber);

            string pattern = @"^\+[1-9]\d{1,14}$"; // E.164 format

            if (Regex.IsMatch(request.PhoneNumber, pattern))
            {
                try
                {
                    var message = MessageResource.Create(
                        to: new PhoneNumber(request.PhoneNumber),
                        from: new PhoneNumber(_configuration["Twilio:FromPhoneNumber"]),
                        body: "Thank you for registering! Here is your verification code: 123456.");

                    _logger.LogInformation("Verification SMS sent successfully to {PhoneNumber}", request.PhoneNumber);
                    return Ok();
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to send verification SMS to {PhoneNumber}", request.PhoneNumber);
                    return BadRequest(new ErrorResponse
                    {
                        Error = "SmsFailure",
                        Message = "Failed to send SMS. Please try again later.",
                        StatusCode = 400
                    });
                }
            }
            
            _logger.LogWarning("Invalid phone number format: {PhoneNumber}", request.PhoneNumber);
            return BadRequest(new ErrorResponse
            {
                Error = "InvalidPhoneNumber",
                Message = "The phone number format is invalid.",
                StatusCode = 400
            });
        }
    }
}

public class PhoneNumberRequest
{
    public string PhoneNumber { get; set; } = string.Empty;
}
```