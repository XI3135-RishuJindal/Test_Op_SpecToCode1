Quality principles and guardrails
- Security-first and zero-trust: treat every request as potentially compromised; re-validate tokens on each access when fallback is enabled. Never log raw tokens, secrets, or PII. Redact Authorization headers in logs.
- Defense in depth: local JWT validation + optional IdP token introspection + short token TTLs. Fallback must not weaken primary validation.
- Least privilege: only store minimal session state; use in-memory suspension cache, no long-lived secrets in code.
- Fail predictable: configurable fail-open/fail-closed on IdP outages; document defaults and operational switches.
- Time-to-revoke SLA: design to contribute to ≤15 minutes deprovisioning; prefer 5-minute max token TTL in non-dev environments.
- Observability: emit structured logs, counters for introspection calls, failures, suspensions, deprovisioning detections.
- Performance budgets: added median overhead ≤5 ms, P95 ≤50 ms per request when cache hit; P95 ≤150 ms when cache miss/introspection call. Cache introspection results for 60 seconds by default; negative results cached for 5 minutes.

Coding standards
- C# 12, .NET 8.0; nullable reference types enabled; async/await end-to-end.
- Clear separation of concerns: Controllers thin; middleware for cross-cutting concerns; services behind interfaces and registered via DI.
- Configuration via IOptions pattern; default-safe values in appsettings.Development.json; production via environment/secrets store.
- Input/output models immutable where practical; use records or set-only init; do not expose domain secrets.
- Unit tests for new components with xUnit; deterministic tests using stubbed HttpMessageHandler for HTTP calls.

Architecture guardrails
- Introduce a dedicated TokenValidationFallbackMiddleware placed after UseAuthentication and before UseAuthorization.
- Introspection behind ITokenIntrospectionService; production HTTP implementation adheres to RFC 7662 (OAuth 2.0 Token Introspection); ability to disable via config.
- In-memory suspension cache keyed by subject (sub) and token hash; eviction by TTL; no persistence.
- Error contract uses existing ApiGateway.Models.ErrorResponse with specific error codes.
- Strict dependency injection: no static singletons outside of DI; dispose HttpClient via IHttpClientFactory.

Non-functional requirements
- Reliability: middleware must degrade per config when IdP unreachable; no cascading failures (circuit breaker with backoff via Polly recommended in future).
- Security compliance: secrets in configuration must be sourced from secure providers; HSTS and HTTPS enforced as already configured.
- Compatibility: no breaking changes to public API routes; only error semantics enhanced for unauthorized/suspended scenarios.
- Logging and audit: log deprovisioning detections and suspensions with correlation id and subject (NameIdentifier), not the token.

Review standards and stakeholder expectations
- Product/security sign-off on defaults for fail-open/fail-closed and cache TTLs.
- Demonstrate through tests the immediate block on revoked/deactivated token and suspend behavior until cache TTL expiry.
- Provide runbook notes in README for enabling/disabling fallback, configuring introspection endpoint, and operational toggles.