Story: US-020 — Provisioning Error Handling — Graceful Denial and No Partial State

What
- Add a Just-In-Time (JIT) provisioning API endpoint to the API Gateway that orchestrates account creation steps. When any internal error occurs (e.g., database failure, downstream timeout), the operation must:
  1) Roll back any partial state (atomicity).
  2) Return a standardized error response to the caller.
  3) Emit an audit log entry recording the failure with correlation metadata.
- Introduce centralized error handling and transactional integrity controls around the provisioning flow, fulfilling requirement R-03-10.

Why
- Users and integrators must never observe partially created accounts. Consistent failure semantics reduce support load and ambiguity.
- Auditable trails of failures are required for compliance and postmortems.
- Establishes a reference pattern (orchestrator + transaction + audit + standardized errors) to reuse across similar flows.

Scope
- New endpoint: POST /api/provisioning/jit (Authorized) that accepts a ProvisioningRequest and returns either 201 with ProvisioningResponse or a standardized ErrorResponse on failure.
- Transactional behavior: The provisioning orchestration executes within a transaction boundary (TransactionScope). If the environment lacks a transactional resource, the orchestrator must perform compensating actions for any non-transactional steps prior to error propagation.
- Centralized error handling via middleware to ensure consistency across controllers.
- Structured auditing on both success and failure including: requestId, userId (if available), operation, outcome (Success/Failure), errorCode (if failure), and duration.
- Timeouts: Any downstream call in the orchestrator is bounded by a configurable timeout; timeout equals failure; ensure rollback.

Acceptance criteria
- AC-01 Standardized error: On internal error during JIT provisioning, API returns HTTP 500 with body:
  { Error: "ProvisioningFailed", Message: "Provisioning failed due to an internal error.", StatusCode: 500, Timestamp: <UTC>, Details: null or redacted }, and includes header X-Request-ID.
- AC-02 No partial state: When a step fails, previously executed steps are rolled back; commit occurs only after the final step succeeds. Demonstrated by unit tests asserting no Commit() when injected failure occurs.
- AC-03 Audit on failure: A structured audit log entry is produced with fields: RequestId, Operation="JITProvisioning", Outcome="Failure", ErrorCode="ProvisioningFailed" (or specific), Reason (message), DurationMs, and optional UserId. Logged via IAuditLogger.
- AC-04 Success response: On success, return 201 Created with ProvisioningResponse { AccountId, Status="Provisioned", RequestId, CreatedAtUtc } and include X-Request-ID header. Audit Outcome="Success".
- AC-05 Validation errors: Invalid payloads (e.g., missing required fields) return 400 with ErrorResponse Error="InvalidRequest" and no transaction started.
- AC-06 Timeout handling: A simulated downstream timeout leads to rollback and AC-01 error; audit includes ErrorCode="DownstreamTimeout".
- AC-07 Observability: All controller responses include X-Request-ID; logs contain this ID to allow correlation.
- AC-08 Security: Endpoint requires a valid JWT. No sensitive internals (stack traces, secrets) are included in responses.

Out-of-scope
- Real database integration, external identity management, messaging buses, and idempotency keys.
- Multi-entity saga across microservices (future extension).
- Dedicated audit storage separate from application logs (optional future).

API contract
- POST /api/provisioning/jit
  - Auth: Bearer JWT required.
  - Request (ProvisioningRequest):
    - string ExternalUserId (required)
    - string Email (required, validated format)
    - string PlanCode (required)
    - Dictionary<string, object> Metadata (optional)
    - bool? SimulateInternalError (optional; for test)
    - bool? SimulateTimeout (optional; for test)
  - Responses:
    - 201 Created: ProvisioningResponse { AccountId: string, Status: "Provisioned", CreatedAtUtc: DateTime, RequestId: string }
    - 400 BadRequest: ErrorResponse with Error="InvalidRequest" or "InvalidPayload"
    - 401 Unauthorized: ErrorResponse
    - 500 InternalServerError: ErrorResponse with Error="ProvisioningFailed" or "DownstreamTimeout"

Error taxonomy
- ProvisioningFailed (generic internal error)
- DownstreamTimeout (timeout during a downstream call)
- InvalidRequest / InvalidPayload (validation issues)

Cross-service dependencies
- None implemented in this repository. The orchestrator will stub downstream interactions to demonstrate transactional boundaries and timeout behavior. The design permits future injection of repositories/clients with transactional participation.

Compliance mapping
- R-03-10: Ensures atomicity of account creation, standardized error to user, and audit log on failure.

Risks and mitigations
- No actual DB may limit TransactionScope effectiveness: mitigate with compensation logic and unit tests simulating commit/rollback behavior.
- Overexposing details: ensure response Details is null by default; rich details only in logs.
- Hanging calls: enforce timeouts and cancellation for all simulated downstream operations.