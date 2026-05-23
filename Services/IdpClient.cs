using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Polly;
using Polly.CircuitBreaker;
using Polly.Retry;
using System;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

namespace ApiGateway.Services
{
    /// <summary>
    /// Implements IIdpClient providing circuit breaker and retry policies.
    /// </summary>
    public class IdpClient : IIdpClient
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<IdpClient> _logger;
        private readonly IAsyncPolicy _resiliencePolicy;

        public IdpClient(HttpClient httpClient, ILogger<IdpClient> logger, IOptions<IdpClientOptions> options)
        {
            _httpClient = httpClient;
            _logger = logger;
            _resiliencePolicy = CreateResiliencePolicy(options.Value);
        }

        private IAsyncPolicy CreateResiliencePolicy(IdpClientOptions options)
        {
            var retryPolicy = Policy
                .Handle<HttpRequestException>()
                .OrResult<HttpResponseMessage>(r => IsTransientFailure(r))
                .WaitAndRetryAsync(
                    retryCount: options.RetryCount,
                    sleepDurationProvider: retryAttempt => TimeSpan.FromMilliseconds(Math.Pow(2, retryAttempt) * 100),
                    onRetry: (outcome, timespan, retryNumber, context) =>
                    {
                        _logger.LogWarning("Retrying {RetryNumber} for {Operation} due to {Outcome}.",
                            retryNumber, context.OperationKey, outcome.Exception ?? outcome.Result);
                    });

            var circuitBreakerPolicy = Policy
                .Handle<HttpRequestException>()
                .OrResult<HttpResponseMessage>(r => IsTransientFailure(r))
                .CircuitBreakerAsync(
                    exceptionsAllowedBeforeBreaking: options.CircuitBreakerFailureCount,
                    durationOfBreak: TimeSpan.FromSeconds(options.CircuitBreakerDuration),
                    onBreak: (outcome, breakDelay, context) =>
                    {
                        _logger.LogError("Circuit broken for {Operation} due to {Outcome}.", context.OperationKey, outcome.Exception ?? outcome.Result);
                    },
                    onReset: context =>
                    {
                        _logger.LogInformation("Circuit reset for {Operation}.", context.OperationKey);
                    },
                    onHalfOpen: () =>
                    {
                        _logger.LogInformation("Circuit half-open for a trial.");
                    });

            return Policy.WrapAsync(retryPolicy, circuitBreakerPolicy);
        }

        public async Task<IntrospectionResponse> IntrospectTokenAsync(string token, CancellationToken cancellationToken)
        {
            // Design pattern for resilience matching
            return await _resiliencePolicy.ExecuteAsync(async (context, ctoken) =>
            {
                // Placeholder for network call to IdP
                // Replace with actual HTTP request and response handling
                _logger.LogInformation("Introspecting token.");
                return new IntrospectionResponse();
            }, new Context(nameof(IntrospectTokenAsync)), cancellationToken);
        }

        public async Task AcknowledgeLogoutAsync(string sessionId, CancellationToken cancellationToken)
        {
            // Placeholder for actual implementation
            _logger.LogInformation("Acknowledging logout.");
        }

        public async Task<ClaimsResponse> FetchClaimsAsync(string token, CancellationToken cancellationToken)
        {
            // Design pattern for resilience matching
            return await _resiliencePolicy.ExecuteAsync(async (context, ctoken) =>
            {
                // Placeholder for network call to IdP
                _logger.LogInformation("Fetching claims.");
                return new ClaimsResponse();
            }, new Context(nameof(FetchClaimsAsync)), cancellationToken);
        }

        private bool IsTransientFailure(HttpResponseMessage response)
        {
            return (int)response.StatusCode >= 500 || response.StatusCode == System.Net.HttpStatusCode.RequestTimeout;
        }
    }

    public class IdpClientOptions
    {
        public int RetryCount { get; set; } = 3;
        public int CircuitBreakerFailureCount { get; set; } = 5;
        public int CircuitBreakerDuration { get; set; } = 30;
    }
}