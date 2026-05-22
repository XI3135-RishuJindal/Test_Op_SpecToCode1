using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;

namespace ApiGateway.Middleware
{
    public class CorrelationIdMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<CorrelationIdMiddleware> _logger;

        public CorrelationIdMiddleware(RequestDelegate next, ILogger<CorrelationIdMiddleware> logger)
        {
            _next = next;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            const string HeaderKey = "X-Correlation-ID";

            if (!context.Request.Headers.TryGetValue(HeaderKey, out var correlationId))
            {
                correlationId = System.Guid.NewGuid().ToString();
                context.Request.Headers[HeaderKey] = correlationId;
            }

            context.Response.OnStarting(() => {
                context.Response.Headers[HeaderKey] = correlationId;
                return Task.CompletedTask;
            });

            using (_logger.BeginScope("CorrelationId: {CorrelationId}", correlationId))
            {
                await _next(context);
            }
        }
    }
}