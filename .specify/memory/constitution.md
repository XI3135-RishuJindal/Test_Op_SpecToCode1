Title: US-008 — Redirect URI Whitelist Enforcement & HTTPS-only Callback

Quality principles and guardrails
- Security-first:
  - Only HTTPS callbacks are accepted. If the incoming callback request is not effectively HTTPS (Request.IsHttps == false and X-Forwarded-Proto != https), immediately reject and log an audit event.
  - Redirect URIs must be validated server-side against a strict whitelist. No user-provided redirect URI may be reflected or used unless whitelisted.
  - Do not allow open redirects. Never concatenate or reflect raw query parameters into Location headers without validation.
  - Normalize and compare URIs using scheme, host, port, and path; ignore query string for whitelist checks. Enforce case-insensitive host comparison and consistent trailing slashes on path.
  - Prefer exact matches. Wildcards/globs are out-of-scope unless explicitly configured and reviewed.
- Least privilege and data minimization in logs:
  - Audit logs must include reason code, normalized redirect URI, remote IP, forwarded proto, correlation id/trace id, and HTTP status, but must not include credentials or authorization codes.
  - No secrets in logs. Truncate oversize URIs (>2KB) before logging.
- i18n-ready responses:
  - Error responses must include a stable error code and a message key suitable for localization. English message is acceptable as fallback; avoid embedding environment-specific details in Message.
- Observability:
  - Use structured logging with clear event IDs for security controls (e.g., RedirectUriNotWhitelisted, InsecureCallbackRejected).
  - Include correlation id via HttpContext.TraceIdentifier in logs and responses when available.
- Configuration and operability:
  - Whitelist values are configured server-side in appsettings (and overridable via environment variables). No client override permitted.
  - Changes to configuration should be reloadable without code changes (IOptionsMonitor acceptable), but a static IOptions snapshot is acceptable for this scope.
- Backward compatibility and safety:
  - Existing endpoints remain functional. New validation is only applied to SSO authorization construction and callback handling paths.
  - Fail secure: on parsing/normalization errors, reject the request.
- Performance and reliability:
  - O(1) lookups using HashSet of normalized URIs.
  - Deterministic behavior across environments. Explicit guidance for reverse proxy headers needed in production.

Non-functional requirements
- Availability: No single point of failure introduced by the validator service; it must be lightweight and in-process.
- Latency: Validation must add <1ms overhead per request on average.
- Testability: Unit tests for validator and controller paths (positive/negative), including forwarded header scenarios.
- Documentation: Configuration keys, examples, and operational logging guidance must be documented in the spec/plan.

Code style and standards
- .NET 8, async where applicable, guard clauses for validation.
- Use dependency injection for validator service.
- Use options pattern for configuration (RedirectUriWhitelistOptions).
- Keep controllers thin; extract normalization/validation logic to services.

Review standards and stakeholder expectations
- Security review: Validate acceptance criteria with security lead; ensure no open redirect or HTTP callback acceptance possible.
- Product/Platform review: Confirm message keys and HTTP status codes.
- DevOps review: Confirm forwarded headers configuration in production ingress (X-Forwarded-Proto) and environment variable mapping for whitelist.