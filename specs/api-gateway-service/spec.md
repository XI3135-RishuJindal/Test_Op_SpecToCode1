# API Gateway Service – Functional Specification

## 1. Overview

The API Gateway Service (SVC-001) is the **central entry point** for all external and internal client traffic, exposing a versioned REST API and WebSocket interface:

- REST base: `https://api.example.com/api/v1/*`
- WebSocket notifications: `wss://api.example.com/ws/v1/notifications`
- System endpoints: `/health`, `/ready`, `/metrics`, `/api/v1/info`

It proxies and governs access to feature-domain services:

- User Profile Management (F-01)
- Multi-factor Authentication (F-02)
- Automated Reporting (F-03)
- Payment Gateway (F-04)
- Real-time Notifications (F-05)

## 2. Goals & Non‑Goals

### 2.1 Goals

- Provide a **single, stable facade** for all client-facing APIs.
- Enforce **Zero Trust** on every request:
  - JWT/OIDC validation.
  - MFA-based login flow.
  - Fine-grained RBAC/ABAC via scopes and roles.
- Centralize **rate limiting**, **throttling**, and **idempotency** (payments).
- Provide **consistent error semantics** and **request tracing**.
- Support **API versioning** and evolvable contracts.
- Provide **admin capabilities** to manage:
  - Routes.
  - Rate limits.
  - RBAC policies.
  - Audit log retrieval.

### 2.2 Non‑Goals

- Implement domain-specific logic (business rules live in downstream services).
- Serve static content or front‑end assets.
- Replace identity provider or MFA backend (those remain separate services).

## 3. Functional Areas

### 3.1 System Operations

Endpoints:
- `GET /health`
- `GET /ready`
- `GET /metrics`
- `GET /api/v1/info`

Behaviors:
- `GET /health`: Aggregates health from key dependencies (User Profile, MFA, Payment, Reporting, Redis, etc.), returns `HealthResponse` with overall status and dependency breakdown.
- `GET /ready`: Indicates readiness to accept traffic (config loaded, dependencies reachable at minimal level).
- `GET /metrics`: Exposes Prometheus metrics (latency, error rates, rate limit stats, upstream health). Requires `admin:metrics` scope.
- `GET /api/v1/info`: Provides gateway name, version, environment, supported/deprecated API versions, documentation link.

Constraints:
- `/health` and `/ready` must remain unauthenticated for infra.
- `/metrics` must be **authenticated and restricted** (e.g., internal, admin role).

### 3.2 Authentication & MFA (F-02)

Endpoints:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/mfa/verify`
- `POST /api/v1/auth/token/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/mfa/enroll`
- `DELETE /api/v1/auth/mfa/enroll/{methodId}`

High-level flow:
1. **Login (First Factor)**  
   - Client posts `LoginRequest` (username, password, optional deviceFingerprint).
   - On success, returns `LoginResponse`:
     - `mfaSessionToken` (opaque, TTL 300s).
     - Selected `mfaMethod` (totp, sms, email).
     - Masked destination for user feedback.

2. **MFA Verification (Second Factor)**  
   - Client calls `POST /api/v1/auth/mfa/verify` with `MfaVerifyRequest` and `mfaSessionToken`.
   - On success, returns `TokenResponse` (access and refresh tokens).

3. **Token Refresh**
   - Client calls `POST /api/v1/auth/token/refresh` with `TokenRefreshRequest`.
   - Gateway validates refresh token (via IdP / token service) and issues rotated `TokenResponse`.

4. **Logout**
   - `POST /api/v1/auth/logout` invalidates access and refresh tokens (token revocation/blacklist via IdP/Redis).
   - Returns 204 on success.

5. **MFA Enrollment Management**
   - `POST /api/v1/auth/mfa/enroll` to enroll new MFA method (requires `mfa:enroll`).
   - `DELETE /api/v1/auth/mfa/enroll/{methodId}` to de‑enroll.

Security Constraints:
- All auth flows must enforce rate limits (login and MFA endpoints are **tightly capped**).
- MFA is **mandatory** before issuing full tokens.
- MFA strategies must be pluggable but hidden behind common Contracts.

### 3.3 User Profile Management (F-01)

Endpoints:
- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/{userId}`
- `PUT /api/v1/users/{userId}`
- `DELETE /api/v1/users/{userId}`

Responsibilities:
- Expose CRUD operations on user profiles, proxying to User Profile Service.
- Enforce scopes/roles:
  - `users:write` for create/update.
  - `users:read` (and potentially `admin`) for list and get.
  - `users:delete`/`admin` for deletion.
- Provide consistent pagination for list operations with `PaginationMeta`.
- Add caching hints:
  - `GET /users/{userId}` must send `ETag` and `Cache-Control` headers.

Constraints:
- No direct manipulation of user passwords here (delegated to auth/MFA domain).
- Input must be validated (email, phone format, privacy settings, contact details).

### 3.4 Automated Reporting (F-03)

Endpoints:
- `POST /api/v1/reports`
- `GET /api/v1/reports`
- `GET /api/v1/reports/{reportId}`
- `PUT /api/v1/reports/{reportId}`
- `PUT /api/v1/reports/{reportId}/schedule`
- `GET /api/v1/reports/{reportId}/download`

Behaviors:
- Create and configure reports using `CreateReportRequest` / `UpdateReportRequest`.
- Allow cron-based scheduling for automatic generation/delivery using `ReportScheduleRequest`.
- Support async lifecycle with statuses: `pending`, `processing`, `completed`, `failed`.
- Download returns binary PDF/CSV stream with correct headers.

Constraints:
- Enforce scopes `reports:read` and `reports:write`.
- 422 when configuration is semantically invalid (e.g., insufficient data).
- Gateway surfaces schedule and status but **does not** perform report generation itself.

### 3.5 Payment Gateway (F-04)

Endpoints:
- `POST /api/v1/payments`
- `GET /api/v1/payments`
- `GET /api/v1/payments/{paymentId}`
- `POST /api/v1/payments/{paymentId}/refund`

Behaviors:
- Payments:
  - Initiate a payment with `CreatePaymentRequest`.
  - Use `Idempotency-Key` header to prevent duplicate charges.
  - Proxy to Payment Service; map provider responses to `PaymentResponse`.
- Refunds:
  - Initiate full/partial refunds via `RefundRequest`; response is `RefundResponse`.
- Listing:
  - Paginated history with filtering by status, currency, date range.

Constraints:
- Strict scopes: `payments:write`, `payments:read`, `payments:refund`.
- PCI-DSS: only accept tokenized payment methods; **never** raw card data.
- Use 402 for declines, 409 for idempotency conflicts, 503 for provider issues.

### 3.6 Real-time Notifications (F-05)

Endpoints:
- `GET /api/v1/notifications`
- `PUT /api/v1/notifications/{notificationId}/read`
- `GET /api/v1/notifications/preferences`
- `PUT /api/v1/notifications/preferences`
- `GET /ws/v1/notifications` (WebSocket upgrade)

Behaviors:
- REST:
  - List notifications with filters (read/unread, type).
  - Mark notification as read.
  - Manage notification preferences (channels and types).
- WebSocket:
  - Authenticate via Authorization header or `token` query parameter.
  - On connection, send `connection.ack` with userId.
  - Push `notification.new` and `notification.updated` events.
  - Support client events `notification.read` and `ping`.

Constraints:
- Notifications are **user-scoped**; cross-user access is forbidden.
- Connection count and rate limits must be enforced.
- JWT validation is mandatory at handshake and reconnection.

### 3.7 Gateway Administration

Endpoints:
- Routes:
  - `GET /api/v1/gateway/routes`
  - `POST /api/v1/gateway/routes`
  - `PUT /api/v1/gateway/routes/{routeId}`
  - `DELETE /api/v1/gateway/routes/{routeId}`
- Rate Limits:
  - `GET /api/v1/gateway/rate-limits`
  - `POST /api/v1/gateway/rate-limits`
- RBAC:
  - `GET /api/v1/gateway/rbac/policies`
  - `POST /api/v1/gateway/rbac/policies`
- Audit Logs:
  - `GET /api/v1/gateway/audit-logs`

Behaviors:
- Provide **runtime configurability** of:
  - Route patterns, upstream URLs, auth enforcement flags.
  - Rate limit policies (scope, window, burst).
  - RBAC policies (roles, resources, actions, effect).
- Audit logs retrieval with filters by user, statusCode, path, time range.

Constraints:
- Accessible **only** with appropriate admin scopes (`admin:gateway`, `admin:rbac`, `admin:audit`).
- All changes must be:
  - Validated (no conflicting routes, invalid cron, invalid patterns).
  - Persisted and applied without full gateway downtime.
  - Fully audited via `AuditLogEvent` with actor, action, result.

## 4. Authentication, Authorization & Security

- Primary method: `Authorization: Bearer <JWT>` (RS256 signed).
- Supported flows:
  - OAuth2 Authorization Code with PKCE via external IdP (Auth0/Keycloak).
  - API keys via `X-API-Key` for M2M (subject to RBAC scopes).
- Scopes/roles:
  - Detailed in `authentication.scopes` and roles mapping.
- Token lifetimes:
  - Access: 1h; Refresh: 30d rotation.

Zero Trust Implications:
- Every request (except `health`, `ready`, `info` and select auth entrypoints) is:
  - Token-validated (signature, issuer, audience, expiry).
  - RBAC-evaluated via OPA-based PolicyDecisionPoint.
  - Rate-limited using Redis-backed counters.

## 5. Error Handling & Observability

Error model:
- `ErrorResponse` / RFC7807-style:
  - `error` (code), `message`, `statusCode`, `timestamp`, `requestId`, `path`, optional `details[]`.

Key families:
- 4xx: validation, auth, RBAC, business conflicts.
- 5xx: internal, upstream, timeouts, service unavailable.

Observability:
- `X-Request-ID` injected and returned.
- Logs: structured JSON with masked PII; correlation by requestId.
- Metrics: route-level latency, error rates, rate limit counters, upstream health.
- Traces: OpenTelemetry with span propagation to backend services.

## 6. Constraints & Assumptions

- Gateway instances are behind an L7 load balancer.
- WebSocket connections require sticky sessions or consistent hashing at LB level, or a shared WS-aware backend.
- Redis, Vault/Secrets Manager, OPA, and Observability stack are available and reachable with low latency.
- Downstream services expose stable contracts aligned with current OpenAPI spec.

## 7. Acceptance Criteria (High-Level)

1. All defined endpoints are available and conform to the given OpenAPI schema.
2. Auth and MFA flows behave as described, with correct status codes and error responses.
3. Rate limits are enforced per configured policies and surfaced via headers.
4. Payment operations are idempotent and PCI-DSS compliant with no raw card data.
5. WebSocket notifications function end-to-end with authenticated, user-scoped events.
6. Admin APIs can update routes, rate limits, and RBAC policies without downtime and with complete audit logs