Quality principles and guardrails for US-014 — Default Role and Permission Assignment at Provisioning

1) Security and correctness
- Enforce least-privilege by default: unknown/absent IdP role claims result in the configured default role, or deny entirely if configured to do so.
- JIT provisioning must execute only after token validation and must not trust unvalidated input. All actions occur inside JwtBearer OnTokenValidated.
- Idempotent and atomic provisioning: creating an account and assigning roles must succeed entirely or not at all; repeated executions must not duplicate role assignments.

2) Configuration-driven behavior
- Role and permission mappings are defined in configuration under Authorization.* with typed options binding. No hard-coded production mappings in code.
- UnknownRoleBehavior must be one of: apply-default, deny. DefaultRole must exist in the Roles matrix.

3) Reliability and observability
- Log with structured Serilog events at Information for successful provisioning, Warning for unknown roles, and Error for unexpected failures; include correlation (RequestId/TraceIdentifier), subject (NameIdentifier), and mapped roles.
- Emit metrics counters (if/when available): accounts_provisioned_total, provisioning_failures_total. For now, log counters as structured fields.

4) Compatibility and maintainability
- Backward-compatible: existing endpoints and tests continue to work. If Authorization section is absent, fall back to default role “viewer”; never throw during startup because of missing mappings in development.
- Follow .NET 8 coding standards, static analyzers, nullable reference types enabled, SOLID via DI, small testable services (role mapping, provisioning, store).
- No business logic in controllers beyond orchestrating; provisioning runs in auth pipeline, not inside user endpoints.

5) Performance and scalability
- Mapping is O(n) in number of input IdP roles; keep in-memory caches for options values. Store operations are non-blocking where possible; for file persistence use write-then-rename to achieve atomicity.

6) Testing and acceptance
- Unit tests cover: role claim extraction, mapping to platform roles, default/deny behavior, idempotent provisioning, and atomic operation semantics for the in-memory/file store.
- Acceptance criteria (in spec) are the gating checklist; PRs must include configuration examples and migration notes.

7) Documentation and change control
- Document Authorization configuration schema and examples in the spec/plan.
- Any change to role names or permissions requires product/security approval tied to R-03-03 and recorded in changelog.

8) Out of scope guardrails
- No admin UI, no production DB integration in this story. Provide Store abstractions to enable future DB addition without breaking APIs.