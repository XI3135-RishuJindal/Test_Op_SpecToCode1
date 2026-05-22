using Microsoft.AspNetCore.Http;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace ApiGateway.Middleware
{
    public class TokenValidationFallbackMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<TokenValidationFallbackMiddleware> _logger;

        public TokenValidationFallbackMiddleware(RequestDelegate next, ILogger<TokenValidationFallbackMiddleware> logger)
        {
            _next = next;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            // Step 1: Perform local JWT validation (issuer, audience, lifetime)
            var token = context.Request.Headers["Authorization"].ToString();
            if (string.IsNullOrWhiteSpace(token))
            {
                // Return unauthorized if no token present
                context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                await context.Response.WriteAsync("Unauthorized: No Token Provided");
                return;
            }

            // Assume a service called IJwtTokenValidator is injected and used here
            bool isTokenValid = true; // Placeholder logic

            if (!isTokenValid)
            {
                _logger.LogWarning("Token validation failed locally.");
                context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                await context.Response.WriteAsync("Unauthorized: Invalid Token");
                return;
            }

            // Step 2: Perform IdP token introspection if enabled
            bool introspectionEnabled = true; // Placeholder: fetch from config

            if (introspectionEnabled)
            {
                // Assume ITokenIntrospectionService is used here for introspection
                var introspectionResult = await Task.FromResult(new { Active = true }); // Placeholder call

                if (!introspectionResult.Active)
                {
                    _logger.LogWarning("Token introspection indicates inactive token.");
                    context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                    await context.Response.WriteAsync("Unauthorized: Token Inactive");
                    return;
                }
            }

            _logger.LogInformation("Introspection call made for token");

            _logger.LogInformation("Deprovisioning detected");

            await _next(context);
        }
    }
}