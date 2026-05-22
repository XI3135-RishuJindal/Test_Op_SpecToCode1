WHAT
Implement structured audit log emission to the R-06 audit logging endpoint for all SSO login events in the ApiGateway service. The gateway must emit a JSON event for each significant step and outcome within the SSO lifecycle:
- flow_initiated: SSO flow start at /api/auth/sso/login
- login_success: identity validated and local session/JWT issued
- token_validation_failed: JWT bearer validation failure during protected API access
- state_mismatch: OAuth/OIDC state/nonce mismatch during callback
- redirect_uri_rejected: redirect URI validation failed
- http_callback_rejected: malformed/invalid callback request
- idp_unreachable: network or protocol failure to the IdP
- session_established: session creation after SSO success

Each event must:
- Conform to the R-06 JSON schema v1 (defined below) and be sent via HTTPS POST to the configured endpoint.
- Exclude secrets, tokens, passwords, authorization codes, and raw PII. The subject identifier must be pseudonymized (SHA-256 with configurable salt).
- Include correlation_id and request metadata (safe subset) for auditability.

WHY
- Regulatory and security requirements mandate immutable audit trails for authentication events.
- Centralized R-06 ingestion allows SOC monitoring, incident response, and forensics.
- Consistent structured events improve troubleshooting (via correlation_id) without exposing sensitive data.

R-06 event format (v1)
Common envelope fields:
- audit_schema_version: "r06.v1"
- event_type: one of [flow_initiated, login_success, token_validation_failed, state_mismatch, redirect_uri_rejected, http_callback_rejected, idp_unreachable, session_established]
- outcome: "success" | "failure" | "started"
- timestamp: ISO-8601 UTC
- service: service name (e.g., "api-gateway")
- environment: env name (e.g., "dev", "staging", "prod")
- correlation_id: GUID/trace id per request
- client_id: OAuth/OIDC client identifier if applicable
- idp: IdP identifier/issuer (do not log URL query params)
- subject_pseudonymous_id: SHA-256(salt + stable-subject-identifier)
- remote_ip: IPv4/IPv6 masked (e.g., /24 for IPv4)
- user_agent_hash: SHA-256 hash of full UA string (do not emit raw UA)
- http_status: integer when applicable
- error_code: short machine-readable code (when failure)
- error_reason: short sanitized description (no tokens, no PII)
- redirect_uri_decision: "accepted" | "rejected" (when applicable)
- session_id: opaque random identifier when session is established
- metadata: optional object with low-risk attributes only (e.g., tenant, prompt)

Acceptance criteria
1) Emission coverage
- When /api/auth/sso/login is called, the gateway emits flow_initiated with outcome=started.
- On successful callback and token issuance, emits login_success and session_established (two distinct events with the same correlation_id).
- On JWT validation failures in protected endpoints (JwtBearer OnAuthenticationFailed), emits token_validation_failed.
- On OIDC callback with missing/invalid state, emits state_mismatch (failure).
- On redirect URI validation failure, emits redirect_uri_rejected (failure).
- On callback endpoint rejecting malformed request (400/403), emits http_callback_rejected (failure).
- On IdP network/protocol errors, emits idp_unreachable (failure).

2) Data protection
- No access_token, refresh_token, password, auth_code, or raw PII is present in any emitted payload or logs.
- subject_pseudonymous_id is present and derived from stable subject data using SHA-256 with configurable salt.
- remote_ip is masked and user_agent is hashed.

3) Delivery guarantees
- Events are queued and sent by a background worker; API request path is not blocked if R-06 is slow or down.
- Retries with exponential backoff on 5xx/timeouts; 4xx are not retried.
- Failures are logged locally with Serilog at Warning/Error with correlation_id only.

4) Operability
- Configurable via appsettings: Audit:Enabled, Audit:R06:EndpointUrl, Audit:R06:ApiKey, Audit:Service, Audit:Environment, Audit:PseudonymizationSalt, Audit:QueueCapacity, Audit:TimeoutSeconds, Audit:RetryPolicy.
- Health log/metric counters exist for emitted, retried, failed.

5) Tests
- Unit tests validate construction and redaction of SsoAuditEvent models.
- Unit tests simulate JwtBearer authentication failure and assert emission call.
- A test verifies subject pseudonymization and user_agent hashing.
- Configurable feature flag disables emission (no network calls) while leaving local logs.

Out of scope
- Full OIDC client implementation and UI flows beyond minimal endpoints needed to trigger events.
- Persistent storage of audit logs locally.
- SIEM dashboards and alerting rules.
- Multi-tenant advanced routing beyond emitting tenant metadata.

Cross-service dependencies
- R-06 audit ingestion service (HTTPS endpoint). Requires network egress and API key.
- Identity Provider availability for certain failure scenarios (mockable for tests).
- Secret management for API keys and salts (local dev via appsettings.Development.json, non-dev via environment/KeyVault).

Event examples (representative)
- flow_initiated started:
  { "audit_schema_version":"r06.v1","event_type":"flow_initiated","outcome":"started","timestamp":"2026-01-01T00:00:00Z","service":"api-gateway","environment":"dev","correlation_id":"...","client_id":"api-gw","idp":"authz.example","remote_ip":"203.0.113.0/24","user_agent_hash":"..."}
- token_validation_failed:
  { "audit_schema_version":"r06.v1","event_type":"token_validation_failed","outcome":"failure","timestamp":"...","service":"api-gateway","environment":"dev","correlation_id":"...","http_status":401,"error_code":"jwt_invalid_signature","error_reason":"JWT signature invalid"}