Quality principles and guardrails
- Reliability first: All outbound IdP calls must be resilient, bounded by timeouts, and must not amplify downstream failures.
- Fail secure: On IdP unavailability or circuit open, default to deny access for authorization-dependent flows.
- Least surprise: No retries for non-transient failures; no hidden side effects; keep behavior deterministic and observable.
- Idempotency: Only retry idempotent operations; adhere to US-005 guarantees. Token introspection and claims fetch are idempotent; back-channel logout acknowledgement must be designed and treated as idempotent.
- Performance: Exponential backoff with jitter on retries; minimal overhead when IdP is healthy.
- Observability: Structured logging on every resilience event (retry, break, half-open, reset), plus metrics via System.Diagnostics.Metrics counters/histograms.
- Config-driven: All thresholds, windows, and durations must be configurable via appsettings and environment overrides.
- Security and privacy: Never log tokens, secrets, or PII. Log only hashed or truncated tokens if necessary. Deny by default on uncertainty.
- Thread-safe: Policy instances are singletons per HttpClientFactory. No shared mutable state outside DI-managed services.
- Timeouts: Apply per-request timeouts below upstream gateway limits. Use cancellation tokens end-to-end.
- Backward compatibility: Do not change public HTTP surface of the API Gateway for this story; introduce an IdP client and wire DI only.
- Testing: Include unit tests for retry and circuit breaker behavior, including threshold open, half-open probe, and non-retryable status mapping. Tests must be deterministic.

Coding standards
- C# 12 / .NET 8. Async-first APIs (Task/async).
- Dependency Injection for all services and options (IOptions<T>).
- HttpClientFactory for outbound calls; no raw new HttpClient().
- Use Polly policies for resilience; no custom spin/sleep logic.
- Use Serilog for structured logging with event ids and correlation identifiers.
- Options pattern: Strongly-typed options with validation and reasonable defaults.
- Small interfaces: IIdpClient with explicit methods for each IdP operation.

Non-functional requirements
- Resilience: Circuit breaker default opens after N=5 consecutive transient failures; open state duration default 30s; half-open probe count 2. Configurable.
- Retry: Max attempts default 3 with exponential backoff and full jitter; initial backoff 200ms; max backoff 5s. Configurable.
- Observability: Emit counters idp_requests_total, idp_retries_total, idp_failures_total, idp_circuit_state (enum label via dimension), and a duration histogram for IdP calls.
- Latency budgets: Default per-request timeout 2s; configurable 500ms–10s range.
- Resource usage: Policies must not allocate per-call unnecessarily; use shared delegates.

Review standards and stakeholder expectations
- Product/security sign-off that “deny on IdP outage” meets fail-secure policy.
- SRE sign-off on policy defaults, metrics, and log fields for dashboards/alerts.
- QA sign-off after running failure-injection tests proving breaker/ retry behaviors.
- Documentation updated with configuration keys, defaults, and tuning guidance.