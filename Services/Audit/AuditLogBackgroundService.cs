using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.Threading;
using System.Threading.Channels;
using System.Threading.Tasks;
using ApiGateway.Models.Audit;

namespace ApiGateway.Services.Audit
{
    public class AuditLogBackgroundService : BackgroundService
    {
        private readonly Channel<SsoAuditEvent> _channel;
        private readonly IAuditLogger _auditLogger;
        private readonly ILogger<AuditLogBackgroundService> _logger;

        public AuditLogBackgroundService(Channel<SsoAuditEvent> channel, IAuditLogger auditLogger, ILogger<AuditLogBackgroundService> logger)
        {
            _channel = channel;
            _auditLogger = auditLogger;
            _logger = logger;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            await foreach (var auditEvent in _channel.Reader.ReadAllAsync(stoppingToken))
            {
                try
                {
                    var result = await _auditLogger.LogEventAsync(auditEvent, stoppingToken);

                    if (!result.IsSuccessful)
                    {
                        _logger.LogWarning("Failed to emit audit event: {ErrorMessage}", result.ErrorMessage);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Exception while processing audit log event");
                }
            }
        }
    }
}