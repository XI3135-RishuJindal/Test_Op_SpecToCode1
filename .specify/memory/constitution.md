Principles and guardrails for US-020 (Provisioning Error Handling — Graceful Denial and No Partial State)

Quality principles
- Atomicity first: A provisioning attempt is all-or-nothing. No user-visible or persisted side-effects may remain when an error occurs.
- Deterministic failure contract: Internal errors surface a single standardized error shape with stable error codes and HTTP status.
- Observability: Every failure produces a structured audit log entry with correlation/request IDs and diagnostic context; logs must be sufficient to reconstruct the failure timeline.
- Least surprise: Success paths return clear, minimal payloads; failure paths never leak sensitive internals.
- Back-pressure and timeouts: Downstream calls in the provisioning path must be short-circuited by bounded timeouts and cancellation tokens; timeouts are treated as failures triggering rollback.
- Idempotence readiness: While full idempotency keys are out-of-scope, the design should be compatible with future idempotent semantics.

Coding standards
- Use the existing ErrorResponse model for error payloads. Include: Error (code), Message, StatusCode, Timestamp, Details (optional redacted), and a RequestId header X-Request-ID in responses.
- Use structured logging via Serilog with contextual properties (RequestId, UserId, Operation, Outcome, ErrorCode).
- Wrap provisioning orchestrations in TransactionScope (System.Transactions) or a defined IUnitOfWork abstraction. Commit only at the very end of the happy path.
- Validate inputs early; return 400s for validation errors with precise error codes (e.g., InvalidRequest, InvalidPayload).
- No secrets or stack traces in API responses. Sensitive information only in logs guarded by configuration.
- Async all the way for IO-bound operations; honor CancellationToken in orchestrator and controller.

Architecture guardrails
- Introduce a ProvisioningController and a ProvisioningOrchestrator service behind an interface to keep the controller slim and swap implementations.
- Centralize error-to-response mapping via an ExceptionHandlingMiddleware and domain exceptions (ProvisioningException, DownstreamTimeoutException).
- Implement an IAuditLogger that writes structured audit entries to Serilog. It must be callable from both success and failure branches.
- Keep the API Gateway independent of a concrete database for now; use TransactionScope to future-proof atomicity. Provide a compensation fallback (try/finally cleanups) for non-transactional steps.

Non-functional requirements
- Reliability: On any internal error, return 500 within 3s (configurable timeout), with audited failure.
- Performance: Median provisioning success should not exceed 500ms under normal load for the demo path (no real DB).
- Security: Endpoint requires Authorization. Never log secrets or full tokens. PII redaction for email/user metadata in audit logs if configured.
- Testability: Unit tests must cover success, validation error, and injected internal error with assertions for standardized error shape and audit logging calls.
- Operability: All responses include X-Request-ID; logs correlate using the same key.

Review standards and stakeholder expectations
- Product signs off that: a) failures never leave partial state; b) users see a consistent failure message; c) audit events appear with required fields.
- QA validates acceptance criteria using automated tests and negative scenarios (timeout simulation).
- Architecture review confirms transaction boundaries and compensations are correctly implemented and do not leak side effects.