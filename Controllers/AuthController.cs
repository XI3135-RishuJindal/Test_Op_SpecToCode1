using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using ApiGateway.Models;
using ApiGateway.Models.Audit;
using ApiGateway.Services.Audit;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IAuditLogger _auditLogger;
        private readonly ILogger<AuthController> _logger;

        public AuthController(IAuditLogger auditLogger, ILogger<AuthController> logger)
        {
            _auditLogger = auditLogger;
            _logger = logger;
        }

        /// <summary>
        /// Initiates the SSO login flow.
        /// </summary>
        [HttpGet("sso/login")]
        public IActionResult BeginSso()
        {
            string correlationId = HttpContext.Request.Headers["X-Correlation-ID"].ToString();

            var auditEvent = new SsoAuditEvent
            {
                EventType = "flow_initiated",
                Outcome = "started",
                CorrelationId = correlationId,
                Timestamp = DateTime.UtcNow,
                Service = "api-gateway",
                Environment = "Development"
            };

            _auditLogger.LogEventAsync(auditEvent, HttpContext.RequestAborted);
            _logger.LogInformation("SSO flow initiated with correlation ID: {CorrelationId}", correlationId);

            return Ok(new { Message = "SSO flow initiated", CorrelationId = correlationId });
        }
    }
}