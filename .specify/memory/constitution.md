Governance for US-016 — Idempotency Controls for JIT Provisioning

Quality principles
- Correctness first: No duplicate accounts can be created for the same identity provider subject (sub). All code paths must enforce single-writer semantics per sub.
- Deterministic outcomes: Given the same sub, the API must always return the same account resource without side effects.
- Observability: Emit structured logs with correlation IDs and sub hash (never raw PII) at key steps: lock-acquire, found-existing, create-start, create-complete, wait-start, wait-complete, timeout.
- Fail safely: On contention timeouts or backend errors, do not create partial resources. Provide actionable responses and avoid ambiguous states.
- Backward-compatible evolution: New endpoints and configuration must not break existing controllers or tests.
- Security by design: Authenticate requests, validate claims, and treat sub as sensitive. Do not log tokens; hash or truncate sub.
- Performance and scalability: Lock scope is fine-grained per sub. Waiting callers must not spin; they should await completion. Avoid global locks.
- Testability: Unit and concurrency tests must deterministically verify single-creation under parallel execution.

Coding standards
- C# 12, .NET 8. Nullable reference types enabled; no suppressions unless justified with comments.
- Dependency injection for services and options via IOptions<>, IServiceCollection extensions.
- Async all the way: No blocking waits (no .Result or .Wait()).
- Clear separation: Controllers only orchestrate; business rules live in services. Repositories abstract storage.
- Error responses use Models/ErrorResponse.cs with consistent Error codes and StatusCode.
- Do not throw for expected control flow; return typed results.
- Logging: Use ILogger<T>. Do not log access tokens or raw sub. Log SHA-256(sub) or first 6 chars of a hash.

Architecture guardrails
- Idempotency key is strictly the IdP sub claim from the caller’s token. No alternate client-supplied idempotency key.
- Single-flight per sub: At most one active create per sub per cluster node. Design to allow future distributed lock adaptation (e.g., Redis), but ship with robust in-memory coordinator.
- Repository abstraction: IAccountRepository supports GetBySubAsync and CreateAsync with uniqueness guarantee at repo level when possible.
- Time-bounded wait for in-flight provisioning. If the create does not complete within the configured timeout, return 202 with a polling Location to GET by sub.

Non-functional requirements
- Reliability: Under bursty duplicate requests (double-click, retry), exactly one account is created; all callers receive the same account or a 202 with poll guidance.
- Latency target: P50 <= 100ms when account exists; P95 <= creation time + 25ms for concurrent duplicates.
- Concurrency: Verified with tests running >= 20 parallel requests for same sub.
- Configuration: appsettings Provisioning.Idempotency.WaitTimeoutSeconds default 5s. Tunable without code changes.
- Compliance: Covers requirement R-03-09 idempotent JIT provisioning.

Review standards and stakeholder expectations
- Product: Demonstrable prevention of duplicate accounts under concurrent first login with the same sub.
- Security: Token validation enforced; sub extracted from validated principal. No PII leakage in logs.
- Architecture: Clear API contracts for POST /api/provisioning/jit and GET /api/provisioning/accounts/{sub}. Future-ready note for distributed lock.
- QA: Automated tests proving single creation under parallelism and correct return codes.
- DevOps: No breaking changes to existing build; new files compile; new tests pass locally and in CI.