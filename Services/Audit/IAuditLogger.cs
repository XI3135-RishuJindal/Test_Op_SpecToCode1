using ApiGateway.Models.Audit;

namespace ApiGateway.Services.Audit
{
    /// <summary>
    /// Defines the interface for audit logging.
    /// </summary>
    public interface IAuditLogger
    {
        Task<EmissionResult> LogEventAsync(SsoAuditEvent auditEvent, CancellationToken cancellationToken);
    }
}