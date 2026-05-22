namespace ApiGateway.Models.Audit
{
    /// <summary>
    /// Represents an SSO audit event.
    /// </summary>
    public class SsoAuditEvent
    {
        public string AuditSchemaVersion { get; set; } = "r06.v1";
        public string EventType { get; set; } = string.Empty;
        public string Outcome { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public string Service { get; set; } = string.Empty;
        public string Environment { get; set; } = string.Empty;
        public string CorrelationId { get; set; } = string.Empty;
        public string? ClientId { get; set; }
        public string Idp { get; set; } = string.Empty;
        public string SubjectPseudonymousId { get; set; } = string.Empty;
        public string RemoteIp { get; set; } = string.Empty;
        public string UserAgentHash { get; set; } = string.Empty;
        public int? HttpStatus { get; set; }
        public string? ErrorCode { get; set; }
        public string? ErrorReason { get; set; }
        public string? RedirectUriDecision { get; set; }
        public string? SessionId { get; set; }
        public object? Metadata { get; set; }
    }
}