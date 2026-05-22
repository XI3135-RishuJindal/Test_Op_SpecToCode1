US-017: Token Validation Fallback for Deprovisioning Detection

What
Introduce a token validation fallback mechanism that, on every access to a protected resource, performs:
1) local JWT verification (existing), and
2) a configurable IdP token introspection check or short-TTL session validation.
If the token is expired, revoked, or the associated IdP account is deactivated, the gateway must immediately:
- deny the request,
- invalidate the session (block the presented token), and
- suspend the account for a configurable period (in-memory block by subject), acting as a safety net when back-channel logout (US-004) is delayed or fails.

Why
- Satisfies requirement R-03-04 (fallback path) and contributes to the ≤15-minute deprovisioning SLA by detecting revocations promptly and by enforcing short token TTLs as a backstop.
- Reduces reliance on back-channel logout’s timeliness; prevents continued access with stale or revoked credentials.

Scope
- Apply fallback validation on all endpoints protected by [Authorize].
- Add middleware, services, configuration, and tests to support per-request introspection and suspension behavior.
- No changes to public API surface (routes); only error responses on unauthorized/suspended accesses are standardized.

User story narrative
As a security engineer,
I want the API Gateway to verify the presented access token on each request and, if IdP indicates it is inactive or the account is deactivated, to immediately block access and suspend the account,
so that users are deprovisioned within SLA even if back-channel logout is delayed.

Actors and systems
- API Gateway (this repo)
- Identity Provider (IdP) supporting OAuth 2.0 Introspection (RFC 7662) or equivalent status API
- Optional back-channel logout system (referenced but not implemented here)

Functional requirements
FR-1 Local validation: Continue validating issuer, audience, lifetime, and signature as currently configured.
FR-2 Fallback introspection: When enabled, for each authenticated request, call the IdP introspection endpoint with the presented token to fetch active status and subject.
FR-3 Revocation/deactivation reaction: If introspection indicates active=false, or account_status in {deactivated, disabled, locked}, immediately:
- deny the current request,
- cache the negative result keyed by token hash for 5 minutes (configurable),
- mark the subject as suspended in an in-memory suspension cache for 15 minutes (configurable),
- emit a security log event DeprovisioningDetected.
FR-4 Short TTL backstop: Document and enforce via config that acceptable max access token TTL is 15 minutes; recommend ≤5 minutes in production to meet SLA even when introspection is unavailable.
FR-5 Caching: Cache positive introspection for 60 seconds (configurable) to constrain latency; negative cache 5 minutes to avoid thrashing.
FR-6 IdP outage behavior: Configurable:
- FailOpen=true (default in Development): if introspection is unavailable, proceed using local JWT validation and token lifetime.
- FailOpen=false (recommended for high-security environments): deny the request after either N consecutive introspection failures (default 3) or when token age exceeds a configurable grace window (default 5 minutes).
FR-7 Error responses: On deny, return 401 Unauthorized (or 403 Forbidden when suspended by subject) with ErrorResponse:
- TokenInactive when introspection active=false.
- AccountSuspended when subject is in suspension cache.
- IntrospectionUnavailable when FailOpen=false and the deny condition is triggered.
FR-8 Observability: Log structured events and expose metrics counters:
- introspection.calls, introspection.failures, deprovisioning.detected, suspensions.active.
FR-9 Configuration: Add TokenValidation:Fallback section with keys:
- Enabled (bool)
- Introspection: { Enabled, Endpoint, ClientId, ClientSecret, CacheTtlSeconds, NegativeCacheTtl