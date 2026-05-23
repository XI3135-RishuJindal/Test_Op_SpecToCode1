Title
US-021: Circuit Breaker and Retry Logic for IdP Integration

Narrative (What and Why)
As a platform operator, I need resilient integration with the Identity Provider (IdP) so that transient outages or performance issues at the IdP do not cascade into our API Gateway. When the IdP becomes unstable, the gateway should stop hammering it, degrade gracefully, and deny access by default (fail-secure). When the IdP recovers, the gateway should automatically and safely resume normal operation. Observability of these behaviors is required to support SRE operations and SLAs.

Scope (in-scope)
- Implement an IdP client abstraction and typed HttpClient for outbound calls to the IdP:
  - Token introspection
  - Back-channel logout acknowledgement
  - Claims fetching
- Apply resilience with:
  - Circuit breaker based on consecutive transient failures with configurable open duration and half-open behavior
  - Exponential backoff with jitter for retries on transient failures/timeouts
  - Per-request timeout and cancellation support
- Fail-secure behavior:
  - When the circuit is open or retries exhausted, introspection/claims calls return an AccessDenied-style result to callers inside the service
  - Logout acknowledgement is best-effort; if not possible, log and do not retry endlessly
- Observability:
  - Structured logs on retry attempts and circuit transitions (break, half-open, reset)
  - Metrics via System.Diagnostics.Metrics (counters and histogram) for requests, retries, failures, and circuit state
- Configuration:
  - appsettings keys for IdP base URL, endpoints, timeouts, retry and circuit breaker thresholds
  - Environment variable override support

Acceptance criteria
- Circuit breaker
  - Opens after reaching a configurable count of consecutive transient failures (default 5) for IdP calls
  - Remains open for a configurable duration (default 30s), then transitions to half-open allowing limited probes (default 2)
  - Logs OnBreak, OnHalfOpen, and OnReset events with fields: operation, failureCount, state, openDuration, exceptionType/statusCode, correlationId
  - When open, further calls are short-circuited immediately without outbound network I/O
- Retry
  - Uses exponential backoff with full jitter
  - Retries only on transient HTTP status codes (408, 429, 500, 502, 503, 504) and network exceptions/timeouts
  - Does not retry on 4xx except 408/429
  - Honors CancellationToken and per-request timeout
  - Emits a retry log for each attempt with attempt number and planned delay
- Fail-secure behavior
  - When breaker is open or retries are exhausted, token introspection and claims fetching result indicate access denied
  - No secrets/tokens are logged; logs contain safe identifiers only
- Observability
  - Metrics counters exist and increment as expected:
    - idp_requests_total, idp_retries_total, idp_failures_total
  - A histogram of idp_request_duration_ms is recorded
  - Circuit state metric is observable (labels/dimensions reflect Closed/HalfOpen/Open)
- Configuration
  - appsettings.json/appsettings.Development.json contain IdP and resilience settings with sane defaults
  - Values can be overridden by environment variables (standard .NET configuration)
- Testing
  - Unit tests simulate IdP transient failures and confirm breaker opens and short-circuits
  - Unit tests confirm non-retryable errors are not retried
  - Unit tests confirm jittered backoff is applied across attempts

Out of scope
- Changing the public HTTP API or authentication scheme from JWT validation to live introspection
- Distributed or cross-instance circuit breaker state
- Persistent queueing/retry of logout acknowledgements across process restarts
- External metrics exporters (