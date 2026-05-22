using System.Net.Http;
using System.Text.Json;
using ApiGateway.Models.Audit;
using Microsoft.Extensions.Logging;

namespace ApiGateway.Services.Audit
{
    public class R06AuditLogger : IAuditLogger
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<R06AuditLogger> _logger;

        public R06AuditLogger(HttpClient httpClient, ILogger<R06AuditLogger> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
        }

        public async Task<EmissionResult> LogEventAsync(SsoAuditEvent auditEvent, CancellationToken cancellationToken)
        {
            try
            {
                var jsonContent = JsonSerializer.Serialize(auditEvent);
                var content = new StringContent(jsonContent, System.Text.Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync("audit/event", content, cancellationToken);

                if (response.IsSuccessStatusCode)
                {
                    return new EmissionResult { IsSuccessful = true, HttpStatusCode = (int)response.StatusCode };
                }
                else
                {
                    var error = await response.Content.ReadAsStringAsync();
                    _logger.LogError("Failed to log audit event: {Error}", error);
                    return new EmissionResult { IsSuccessful = false, HttpStatusCode = (int)response.StatusCode, ErrorMessage = error };
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Exception while logging audit event");
                return new EmissionResult { IsSuccessful = false, ErrorMessage = ex.Message };
            }
        }
    }
}