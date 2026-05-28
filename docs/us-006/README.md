# US-006: API Gateway enhancements for Medication domain

This document captures the current understanding, assumptions, and open questions for US-006. It serves as a lightweight anchor for incremental implementation and future updates to the API Gateway.

## Problem Statement
Expose a secure, consistent, and observable API Gateway surface for Medication-related operations to front-end clients and internal consumers. The gateway should:
- Route and protect requests to the downstream Medication service(s)
- Normalize request/response contracts for clients
- Enforce authentication/authorization
- Provide robust error handling and logging
- Establish a baseline for performance, reliability, and operability

The existing technical specification for US-006 is currently empty; this document defines working assumptions and clarifies open questions to unblock iterative work.

## Intended Users
- Front-end applications (web/mobile) interacting with medication data via the gateway
- Internal service consumers (trusted systems) using gateway endpoints for medication queries
- Platform/DevOps engineers operating and observing the gateway in production
- Security and compliance stakeholders ensuring access controls and logging meet organizational policies

## Scope (Initial)
- Add Medication-focused endpoints to the gateway
- Forward calls to a downstream Medication service (single service assumed initially)
- Enforce JWT-based authentication with optional role/scope checks
- Return consistent error payloads using the existing ErrorResponse shape
- Basic request validation and pass-through of correlation/trace headers

Out of scope (initial):
- Full YARP adoption or dynamic route discovery
- Complex data aggregation across multiple services
- Fine-grained authorization policies beyond basic scopes/roles
- Offline/edge caching and distributed cache invalidation

## Expected API Surface (initial)
Base path: /api/medications

Authentication: JWT (existing gateway config). Authorization: role/scope checks as noted.

- GET /api/medications
  - Query parameters:
    - patientId (string, required)
    - status (string, optional; e.g., active, inactive)
    - page (int, optional, default=1)
    - pageSize (int, optional, default=25, max=100)
  - Response: 200 with a paginated list of MedicationDTO
  - Errors: 400 (validation), 401/403 (authz), 502/504 (downstream), 500 (unexpected)

- GET /api/medications/{medicationId}
  - Path parameters:
    - medicationId (string, required)
  - Response: 200 with a single MedicationDTO
  - Errors: 400, 401/403, 404 (not found), 502/504, 500

- POST /api/medications
  - Body: CreateMedicationRequest (aligned to downstream contract; minimally includes fields necessary to create a medication record)
  - Response: 201 with created resource (MedicationDTO) and Location header
  - Errors: 400 (validation), 401/403, 409 (conflict/idempotency violation if applicable), 422 (semantics), 502/504, 500

Notes:
- All responses on error use Models/ErrorResponse.cs format to maintain a consistent client experience.
- Correlation-Id and W3C Trace-Context headers are propagated downstream when present.

## Contract and Mapping
- MedicationDTO (existing) will be the canonical response model at the gateway boundary.
- For POST, a CreateMedicationRequest model may be introduced to avoid leaking downstream-only fields to clients.
- Field mapping is pass-through when possible; where downstream fields differ, mapping will be performed in the gateway.

## Configuration
- appsettings.json (example keys):
  - Downstream:MedicationService:BaseUrl
  - Downstream:MedicationService:TimeoutSeconds (e.g., 3-5s)
  - Downstream:MedicationService:RetryPolicy (e.g., disabled initially or conservative)
  - Security:Authorization:RequiredScopes: ["medications.read", "medications.write"] (if scope-based checks are enabled)
- Secrets/tokens for downstream (if required) are stored securely via platform secret store; not in source control.

## Non-Functional Considerations
Performance and Reliability:
- p95 latency (gateway-only) target: <= 50ms for cache-miss/simple proxy under nominal load; end-to-end depends on downstream latency.
- Timeouts: gateway-to-downstream default 3s (configurable). No retries on non-idempotent methods; conservative retries (0-2) on transient failures for GET.
- Circuit breaking to protect downstream (to be added if needed based on telemetry).

Security:
- JWT validation already configured in the gateway; enforce audience/issuer/signing key.
- Optional scope/role checks:
  - GET requires medications.read
  - POST requires medications.write
- Input validation and length limits on query/path/body to mitigate injection and abuse.
- PII/PHI handling: avoid logging sensitive fields; structured logs should redact payloads or log metadata only.
- TLS termination at the ingress/load balancer; gateway enforces HTTPS redirection (already enabled).

Observability:
- Serilog structured logging in place; ensure correlation and trace headers are included.
- Emit key events: request start/stop, downstream call start/stop, error categorization, and latency.
- Consider OpenTelemetry for tracing in a subsequent increment; for now, forward traceparent/tracestate if present.

Rate Limiting and Throttling:
- Initial protection via platform ingress WAF/API gateway where available.
- Application-level rate limiting can be introduced if ingress controls are insufficient.

Error Handling:
- Normalize downstream errors into ErrorResponse with appropriate HTTP status codes.
- Differentiate 4xx vs 5xx between client errors and downstream/system errors.

Compatibility and Versioning:
- Introduce /api/medications under v1 surface if versioning is adopted later (e.g., /api/v1/medications).
- Avoid breaking changes; use additive evolution.

Deployment:
- Containerized .NET 8 service. No changes to Dockerfile required for initial scope.

## Testing Strategy
- Unit tests: parameter validation, authz policy checks, mapping functions, error normalization.
- Integration tests: with a mocked/stubbed downstream Medication service using WireMock or similar.
- Contract tests: ensure MedicationDTO remains stable; align with downstream schema expectations.
- Performance smoke tests: baseline latency under nominal load.
- Security tests: verify authn/authz, header propagation, and input validation.

## Risks
- Downstream instability or inconsistent contracts leading to fragile mapping
- Overly strict timeouts causing user-facing errors; too lenient timeouts impacting tail latency
- Scope/role model mismatch between gateway and identity provider
- Sensitive data leakage via logs if redaction not correctly enforced
- Scope creep into aggregation or cross-domain concerns beyond Medication

## Initial Assumptions
- A single downstream Medication service exists and is reachable via HTTP(S); no service mesh required initially.
- Gateway continues using controller-based routing; YARP/reverse proxy may be evaluated later.
- JWT tokens include scopes/roles compatible with medications.read and medications.write or equivalent.
- No strong idempotency requirement for POST; if required, an Idempotency-Key header approach can be added later.
- Pagination for GET list is supported by the downstream service (or emulated by the gateway if necessary).

## Open Questions
- Downstream endpoints and exact contract:
  - What are the precise URLs, payload schemas, and status codes of the Medication service?
  - Are there fields in MedicationDTO that must be transformed or filtered for clients?
- Authorization:
  - Should we enforce scope-based checks, role-based checks, or both? What are the exact claim names?
  - Are there multi-tenant constraints (e.g., patient scoping) that require additional claim validation?
- Idempotency and concurrency:
  - Is POST required to be idempotent? If yes, what keying strategy and conflict behavior are expected?
  - Are there optimistic concurrency tokens (ETags) for updates we should anticipate in future stories?
- Pagination and filtering:
  - What filters are required beyond patientId and status (date ranges, prescriber, etc.)?
  - What maximum pageSize is acceptable?
- Observability:
  - Is OpenTelemetry a near-term requirement? Which backends (Jaeger, OTLP, App Insights)?
- Rate limiting:
  - Should per-user or per-IP limits be enforced at the gateway, and what thresholds are acceptable?
- Compliance:
  - Are there explicit compliance requirements (HIPAA/PHI) that mandate additional logging controls or data minimization?
- Versioning:
  - Do we need to introduce explicit API versioning (e.g., /api/v1) now or defer until first public release?

## Next Steps
- Confirm downstream Medication service contract and finalize gateway mapping
- Decide on authorization model (scopes/roles) and required claims
- Introduce configuration keys for downstream base URL and timeout
- Implement GET endpoints first with robust error normalization and tests
- Iterate on POST create flow with validation and security review
- Revisit observability and rate limiting based on production readiness needs