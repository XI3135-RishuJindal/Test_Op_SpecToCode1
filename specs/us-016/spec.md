US-016 — Idempotency Controls for JIT Provisioning

What
- Add an idempotent Just-In-Time (JIT) provisioning capability to the API Gateway so that the first authenticated request for a given identity (IdP sub claim) creates an account exactly once. Subsequent concurrent or retrying requests for the same sub must return the same account instead of creating duplicates.
- The idempotency key is the IdP sub claim derived from the validated JWT.
- When a provisioning operation is already in-flight for a sub, additional requests for the same sub must either:
  - wait and return the created account if it completes within a configurable timeout, or
  - return 202 Accepted with retry guidance if the timeout elapses.
- Provide a read endpoint to fetch an account by sub to support client polling when a 202 is returned.
- Covers requirement R-03-09.

Why
- Prevents duplicate accounts and race conditions caused by double-clicks, client/network retries, and concurrent first-login events.
- Ensures deterministic, safe behavior across concurrent requests and improves user experience by returning the same account resource.

User story narrative
- As a platform, when a user authenticates for the first time, the gateway provisions a local account keyed by the IdP-subject (sub).
- If two or more first-login requests arrive nearly simultaneously for the same sub, only one account is created and all callers receive the same account id.
- If provisioning is still running, callers get either the finished account (if completed within timeout) or a 202 with a polling URL to obtain the account later.

Functional scope
- New endpoints:
  - POST /api/provisioning/jit — uses authenticated principal’s sub as idempotency key; creates or returns existing.
  - GET /api/provisioning/accounts/{sub} — returns the account if it exists.
- Idempotency behavior:
  - Check repository for existing account by sub; if found, return 200 with account.
  - If not found, attempt to acquire a per-sub lock and execute a single create.
  - Concurrent callers for the same sub must await the same in-progress operation result up to WaitTimeoutSeconds; on timeout return 202 Accepted and a Location header to GET /api/provisioning/accounts/{sub} with a Retry-After.
- Authentication/authorization:
  - Both endpoints require Bearer JWT.
  - sub claim is mandatory for POST /jit; requests without sub return 400.
- Responses:
  - 200 OK + account payload when existing or after successful creation.
  - 202 Accepted + Location + Retry-After when in-flight did not complete within timeout.
  - 400 BadRequest for missing sub or invalid payload.
  - 401 Unauthorized if token missing/invalid.
  - 409 Conflict only if repository detects a rare uniqueness violation (should not occur if locks function, but guarded).
  - 500 InternalServerError for unexpected failures with correlation id.

Acceptance criteria
- AC1: Given an existing account with sub S, POST /api/provisioning/jit returns 200 with that account, no new account is created.
- AC2: Given no account for sub S, two concurrent POST requests for S result in exactly one new account; both callers receive the same account id (200).
- AC3: For N (>=10) concurrent POST requests for the same sub S, exactly one account is created; all requests either return 200 with the same account or 202 if timeout elapses for some callers.
- AC4: When a 202 is returned, the response includes Location: /api/provisioning/accounts/{sub} and Retry-After with the remaining wait hint (integer seconds).
- AC5: GET /api/provisioning/accounts/{sub} returns 200 with the account after creation; returns 404 if not yet created or never will be (no side effects).
- AC6: Logs include correlation id and a hashed-sub marker; no raw PII.
- AC7: Unit tests demonstrate idempotency under parallelism and repository-level uniqueness protection.
- AC8: Configurable timeout default 5 seconds via Provisioning.Idempotency.WaitTimeoutSeconds; setting to 0 immediately yields 202 for in-flight scenarios.

Out of scope
- Real external identity provider integration; token issuance stays as-is for tests.
- Persistent database implementation; an in-memory repository will be delivered with clear seams to swap with a persistent store.
- Cross-process distributed locking implementation; design will include an interface to enable future Redis-based coordination but ship with an in-memory coordinator.

Cross-service dependencies
- None at this time. Future evolution may replace the in-memory repository with a User/Accounts service or database and a Redis-based single-flight/lock.

Non-functional requirements
- Thread-safe, non-blocking concurrency primitives (SemaphoreSlim/TaskCompletionSource).
- Structured logging with Serilog context enrichment.
- Deterministic tests validating single creation semantics and response codes.