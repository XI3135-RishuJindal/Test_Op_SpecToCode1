Purpose
Establish durable quality principles, coding standards, architecture guardrails, and non-functional requirements to guide the creation of a deferred Payments epic. This governs decisions now (documentation-only, no runtime behavior) and later (when payments are implemented).

Quality principles
- MVP safety first: no runtime or API surface introduced for payments in the current MVP; documentation and configuration may be added only if inert.
- Security by design: treat all payment data as highly sensitive; assume PCI-DSS scope if card data ever transits or is stored; prefer tokenization and third-party vaulting.
- Reliability and idempotency: all payment write operations must be idempotent; support retry-safe operations and exactly-once effects using outbox pattern.
- Observability: emit structured logs with correlation IDs; define traces and metrics for any future payment flows (auth/capture/refund/reconcile).
- Separation of concerns: API Gateway remains thin (routing/auth); orchestration and provider logic live outside of the gateway.
- Backward compatibility: future payment APIs must be versioned and additive when possible.
- Documentation-as-contract: specifications precede code; ADRs capture key architecture decisions; clear deferrals and prerequisites are mandatory.

Coding standards (applicable to this repo when code changes are introduced)
- Language: C# 12, .NET 8, nullable reference types enabled, async/await with CancellationToken where applicable.
- Authentication/Authorization: JWT via Microsoft.AspNetCore.Authentication.JwtBearer; granular authorization policies; no hard-coded secrets.
- Configuration: IOptions pattern; configuration via appsettings.* with environment overrides; feature flags for new capabilities (e.g., Payments.Enabled).
- Logging: Serilog; structured logging with requestId/correlationId; no sensitive data in logs; log levels: Information default, Warning for recoverable issues, Error for failures.
- Testing: xUnit; targeted unit tests per controller/service; add contract tests for payment provider adapters; use Moq/Fakes; keep tests deterministic and non-flaky.
- Error handling: consistent ErrorResponse payloads; map external provider errors to internal error taxonomy; never leak provider raw messages to clients.
- API standards: RESTful, JSON; OpenAPI documented; use idempotency keys for write operations.

Architecture guardrails
- Clean architecture: domain/application layers decoupled from infrastructure; adapters for payment providers (Stripe/Adyen/etc.).
- Messaging: event-driven for post-authorization workflows (capture, notify, reconcile); use outbox/inbox patterns for reliability.
- Data: no storage of PAN/CVV; only store tokens and provider references; encryption at rest for any sensitive references.
- Secrets: use secret stores; never commit secrets; rotate keys regularly.
- Compliance: PCI-DSS and PSD2/SCA considered; do not scope API Gateway into PCI zone if avoidable.
- Deployment: blue/green or canary for payment services; feature flags for safe rollout.
- Observability: tracing across gateway → orchestrator → provider; define SLIs/SLOs before launch.

Non-functional requirements (for future payments delivery; informative now)
- Security: PCI-DSS readiness; OWASP ASVS compliance; regular dependency scanning.
- Availability: target ≥ 99.9% for payment orchestration service.
- Latency: P95 auth ≤ 500 ms excluding provider latency; overall P95 end-to-end ≤ 1.5 s.
- Throughput: design for burst traffic; rate limiting and circuit breakers to providers.
- Resilience: retries with backoff; provider failover strategy; compensating transactions for partial failures.
- Auditability: immutable audit trail for all state transitions; reconciliation against provider reports.
- Privacy: GDPR adherence; data minimization and retention limits.

Out-of-scope enforcement (for this MVP story)
- No controllers, routes, or public APIs for payments in API Gateway.
- Only inert configuration and documentation may be added.
- Any references to payments must be disabled by feature flag (Payments.Enabled = false).

Documentation and decision records
- Maintain specs under specs/create-deferred-payments-epic/.
- Record key decisions (e.g., orchestration vs. direct provider calls) in the plan file and reference in future ADRs.
- Keep README up to date with epic status and deferral.