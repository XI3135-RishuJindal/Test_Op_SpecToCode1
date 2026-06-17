```csharp
// ... other using directives ...
using ApiGateway.Services;

namespace ApiGateway.Controllers
{
    // ... existing code ...

    public AuthController(
        IConfiguration configuration, 
        ILogger<AuthController> logger,
        IAuthenticatorAppService authenticatorAppService)
    {
        _configuration = configuration;
        _logger = logger;
        _authenticatorAppService = authenticatorAppService;
    }

    // ... existing code ...
    
    /// <summary>
    /// MFA Step: Generate setup code for authenticator app
    /// </summary>
    [HttpGet("mfa/setup")]
    [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
    public IActionResult GenerateMfaSetupCode()
    {
        var accountName = User.Identity?.Name ?? "default-user";
        var issuer = "ApiGatewayApp";
        var setupCode = _authenticatorAppService.GenerateSetupCode(accountName, issuer);
        return Ok(setupCode);
    }

    /// <summary>
    /// MFA Step: Validate the provided TOTP code
    /// </summary>
    [HttpPost("mfa/validate")]
    [ProducesResponseType(typeof(bool), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
    public IActionResult ValidateMfaToken([FromBody] string token)
    {
        var secret = _configuration["MFA:SecretKey"];
        var isValid = _authenticatorAppService.ValidateToken(secret, token);

        if (!isValid)
        {
            return BadRequest(new ErrorResponse
            {
                Error = "InvalidToken",
                Message = "The provided MFA token is invalid",
                StatusCode = 400
            });
        }

        return Ok(true);
    }
}
```