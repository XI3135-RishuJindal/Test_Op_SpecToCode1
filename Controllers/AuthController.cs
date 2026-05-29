```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.Diagnostics;
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
        /// Initiates SSO login process and handles performance and security validation.
        /// </summary>
        /// <returns>Action result indicating success or failure</returns>
        [HttpGet("sso")]
        public IActionResult InitiateSSOLogin()
        {
            var stopwatch = Stopwatch.StartNew();
            try
            {
                // Simulate SSO login flow triggering
                // Redirect to IdP (In actual implementation, handle actual redirect flow)
                var simulatedRedirect = SimulateSSORedirect();
                if (!simulatedRedirect)
                {
                    return BadRequest(new ErrorResponse
                    {
                        Error = "SSOError",
                        Message = "Failed to redirect to Identity Provider",
                        StatusCode = 400
                    });
                }

                // Simulating token validation (In actual implementation, validate the token received from IdP)
                var tokenValid = SimulateTokenValidation();
                if (!tokenValid)
                {
                    return Unauthorized(new ErrorResponse
                    {
                        Error = "TokenInvalid",
                        Message = "The token received is invalid",
                        StatusCode = 401
                    });
                }

                stopwatch.Stop();
                if (stopwatch.ElapsedMilliseconds > 3000)
                {
                    _logger.LogWarning("SSO login flow exceeded 3 seconds: {ElapsedMilliseconds} ms", stopwatch.ElapsedMilliseconds);
                    // Handle the timeout logic such as error response or logging
                }

                _logger.LogInformation("SSO login flow completed successfully in {ElapsedMilliseconds} ms", stopwatch.ElapsedMilliseconds);

                return Ok(new { Message = "SSO login successful" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error during SSO login");
                return StatusCode(500, new ErrorResponse
                {
                    Error = "InternalError",
                    Message = "An unexpected error occurred during SSO login",
                    StatusCode = 500
                });
            }
        }

        private bool SimulateSSORedirect()
        {
            // Simulate SSO IdP redirection (This is a placeholder for the actual implementation)
            return true;
        }

        private bool SimulateTokenValidation()
        {
            // Simulate token validation process (This is a placeholder for the actual implementation)
            return true;
        }
    }
}
```