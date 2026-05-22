Quality principles and guardrails for SSO Audit Log Emission

Security and privacy
- Do not log secrets, access tokens, refresh tokens, passwords, authorization codes, or full PII.
- Pseudonymize end-user identifiers before emitting audit logs using SHA-256 with an app-configured salt. Never emit the clear-text username, email, subject, or phone.
- Limit network egress to the R-06 audit endpoint via HTTPS only. Validate TLS and pin host by configuration.
- Apply least-privilege to any credential used for the R-06 endpoint (API key/bearer). Store secrets in configuration providers (not source) and reference by key.

Audit event integrity
- Every significant SSO event produces a log within the same request correlation context.
- Include required attributes: event_type, outcome, correlation_id, service, env, timestamp, http_status (if applicable), client_id, idp, redirect_uri_decision, error_code/error_reason (sanitized), subject_pseudonymous_id.
- Ensure at-least-once delivery with a bounded in-memory queue and retry with exponential backoff. Drop oldest on sustained backpressure to avoid memory bloat, but always record a local Serilog warning.

Observability and traceability
- Generate or propagate a Correlation-Id for each inbound request; include it in every audit event and in application logs.
- Add minimal metrics (counters) for emitted, retried, failed events.

Coding standards
- C# 12 / .NET 8, nullable enabled, async/await, cancellation tokens on I/O.
- Follow SOLID: IAuditLogger interface; R06AuditLogger implementation; HTTP client typed and injected.
- Use structured logging (Serilog) with scalar fields; no string interpolation that can leak sensitive data.
- All public models have XML doc comments. Unit tests validate no forbidden fields make it to the payload.

Non-functional requirements
- Performance: audit emission must not add more than 5ms p50 to request latency (performed off the critical path via background queue).
- Reliability: 99.9% success to R-06 under normal network conditions; retries for transient 5xx/timeout.
- Timeouts: 2s per POST, 3 retries, capped backoff at 10s, circuit-breaker on sustained failures.
- Configurability: feature flag Audit:Enabled, endpoint URL, API key, tenant, service name, environment, redaction settings.
- Schema governance: version field audit_schema_version = "r06.v1" to support evolution.

Review & acceptance standards
- Unit tests cover success and failure paths, pseudonymization, and redaction.
- Log payload sample validated against R-06 JSON schema (in test).
- Security review validates no tokens/passwords/PII appear even under error conditions.
- Config validated for dev/prod parity; secrets not committed to repo.