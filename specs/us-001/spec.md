# US-001 – Log in with Third-Party Single Sign-On

## Summary

As a user, I want to log in using a third-party Single Sign-On provider so that I can access the app securely and conveniently across all my devices.

This story adds backend SSO capabilities to the existing API Gateway (.NET 8) while preserving the current JWT-based authorization model.

## Goals and Scope

### In Scope

1. **SSO Providers**
   - Support Google, Facebook, and Apple as SSO providers.
   - Model them as discrete options selectable by the client via an API parameter.

2. **API Capabilities**
   - Expose an endpoint (or endpoints) that:
     - Accept an SSO login request specifying provider and provider-issued token/authorization code.
     - Validate / exchange the token with the respective provider.
     - Normalize user identity information (at minimum: provider, provider user id / subject, and optionally email/name).
     - Map or create an internal user profile.
     - Issue a signed JWT consistent with existing JWT configuration (issuer, audience, signing key, expiry).
     - Redirect or instruct client to proceed to profile/home page (for SPA/native the API will return token and suggested redirect path).

3. **Profile Creation and Mapping**
   - On first successful SSO login, create an internal user “profile” associated with that external identity.
   - On subsequent logins for the same external identity:
     - Reuse the same internal user identity.
   - For this repository, a simple in-memory user store is acceptable as long as the abstraction allows future persistence.

4. **Responsiveness Across Devices**
   - API must support being called from mobile, tablet, and desktop clients.
   - No device-specific branching in backend logic; the API is device-agnostic, but must not assume any particular client capabilities beyond HTTP/JSON.

5. **Observability & Errors**
   - Log major SSO flow events:
     - Provider selected,
     - Token exchange/validation attempts,
     - Profile lookup/creation,
     - JWT issuance success/failure.
   - Return structured error responses using `ErrorResponse` for invalid inputs or failed SSO operations.

### Out of Scope

- Building or modifying front-end UI for SSO buttons or device-specific layouts.
- Implementing a persistent database-backed user store (beyond in-memory or simple placeholder mapping).
- Full OAuth authorization-code redirect handling in browser (e.g., generating consent screen URLs, handling redirects); for this story we assume:
  - The client obtains a provider token or authorization code and sends it to the API for validation/exchange.
- Support for providers beyond Google, Facebook, and Apple.
- Password-based authentication enhancements beyond the existing `/api/Auth/token` test endpoint.
- Multi-factor authentication, account recovery flows, or advanced identity features.

## User Story Narratives and Flows

### 1. Viewing Available Authentication Methods

**Narrative**

As a user, when I open the login page on any device (mobile, tablet, desktop), I want to see third-party SSO options (Google, Facebook, Apple) so that I can choose my preferred login method.

**Backend Expectations**

- Backend provides a standardized list of supported SSO providers.
- The client uses this list to render appropriate buttons.
- No device-specific logic is required on the server.

**API Behavior**

- New endpoint (proposal): `GET /api/auth/providers`
  - Response: JSON array of providers, each with:
    - `id` (e.g., `google`, `facebook`, `apple`),
    - `displayName` (e.g., `Google`),
    - `isEnabled` flag.
  - This endpoint is read-only and not authenticated.

### 2. Logging in with an SSO Provider

**Narrative**

As a user, when I select an SSO provider and complete the provider’s authentication, I want the app to accept the provider’s token, map my account, issue me an app JWT, and take me to my profile/home page.

**Backend Expectations**

- Client passes provider identifier and provider-issued credential (token or authorization code).
- Backend validates the credential with the provider.
- Backend derives an external identifier (e.g., provider subject or user id).
- Backend maps or creates user profile and issues an app JWT.

**API Behavior**

- New endpoint (proposal): `POST /api/auth/sso/login`
  - Request body (JSON):
    - `provider` (string; one of `google`, `facebook`, `apple`),
    - `accessToken` (string; provider-issued access or ID token) **or** `authorizationCode` (string).
      - For this story we treat it generically as `providerToken` for simplicity.
    - Optional `deviceInfo` (string) to help logging / analytics.
  - Response (200 OK on success):
    - `token`: string (JWT issued by our API Gateway),
    - `expiresAt`: ISO-8601 UTC timestamp,
    - `userId`: internal user identifier,
    - `isNewUser`: bool (true if this is first SSO login),
    - `provider`: provider id,
    - `redirectUrl`: string (e.g., `/profile` or `/home`), recommended by backend.
  - Error responses with `ErrorResponse`:
    - 400 Bad Request – invalid request (missing provider, unknown provider, missing token, structurally invalid token).
    - 401 Unauthorized – provider token rejected / validation failed.
    - 500 Internal Server Error – unexpected failures.

### 3. First-Time SSO Login Profile Creation

**Narrative**

As a user logging in with SSO for the first time, when provider authentication succeeds, I want the app to automatically create a profile and link my external account so that future logins are seamless.

**Backend Expectations**

- Determine whether an internal identity already exists for this external provider+subject.
- If not:
  - Create a new internal user record.
  - Associate the provider and external subject with this record.
- Idempotent behavior:
  - If a duplicate request arrives for same external identity (e.g., retry), backend should not create multiple internal users.

### 4. Subsequent SSO Logins

**Narrative**

As a returning SSO user, I expect to be logged back into my existing profile no matter which device I use.

**Backend Expectations**

- For known external identities, the system should:
  - Find the associated internal user record.
  - Issue JWT with same internal user id.
  - Respond similarly on mobile/tablet/desktop.

### 5. Responsive, Device-Agnostic SSO Experience

**Narrative**

As a user, I want SSO login to work seamlessly across different device types and screen sizes.

**Backend Expectations**

- Backend should be stateless regarding device type.
- All derived redirect behaviors must be generic (e.g., `"/home"`, `"/profile"`) and not encode device-specific URLs.
- Any device-specific UX is left to the clients.

## Functional Requirements

1. **Provider Enumeration**
   - The system SHALL expose `GET /api/auth/providers` returning:
     - A JSON array with items:
       - `id`: machine identifier (`google`, `facebook`, `apple`),
       - `displayName`: user-facing name,
       - `isEnabled`: boolean (driven by configuration).
   - The endpoint SHALL reflect configuration to enable/disable providers without code changes.

2. **SSO Login Endpoint**
   - The system SHALL expose `POST /api/auth/sso/login`.
   - Request validation:
     - `provider` is required and must be one of configured providers.
     - `providerToken` (or similar property) is required and non-empty.
   - If validation fails, the endpoint SHALL return 400 with `ErrorResponse`:
     - `Error = "InvalidRequest"`,
     - appropriate `Message`,
     - `StatusCode = 400`.

3. **External Provider Validation**
   - For each allowed provider, define a provider-specific handler that:
     - Validates the token with the provider via HTTP calls or library calls (for this story, may be abstracted/mocked).
     - Returns a normalized identity object:
       - `Provider` (e.g., `google`),
       - `ProviderUserId` / `Subject`,
       - Optionally `Email`, `Name`.
   - If the provider rejects the token, the handler SHALL signal authentication failure, resulting in:
     - 401 Unauthorized with `ErrorResponse`:
       - `Error = "ProviderAuthenticationFailed"`.

4. **User Profile Mapping**
   - The system SHALL maintain a mapping between:
     - `(Provider, ProviderUserId)` and an internal `UserId`.
   - First login:
     - If mapping not found, create a new internal user (in-memory for now) with a unique internal `UserId`.
     - Return `isNewUser = true`.
   - Subsequent logins:
     - Find mapping and return `isNewUser = false`.

5. **JWT Issuance**
   - On each successful SSO login, the system SHALL:
     - Generate a JWT similar to existing `GenerateToken`:
       - `Issuer = configuration["Jwt:Issuer"]`,
       - `Audience = configuration["Jwt:Audience"]`,
       - Sign with `configuration["Jwt:Key"]` using HS256.
     - Include claims:
       - `sub` or `NameIdentifier`: internal `UserId`,
       - `provider`: provider id,
       - `provider_user_id`: external identity id,
       - Optionally `email`.
     - Set expiry (e.g., 1 hour) configurable, default 1 hour.
   - The client can use this JWT to call existing authorized endpoints (e.g., `/api/test`).

6. **Redirection / Post-Login Target**
   - The API SHALL include a `redirectUrl` response field indicating suggested navigation after login.
   - Backend SHOULD default this to `/profile` or `/home` (configurable).
   - Actual redirection responsibility remains with the client.

7. **Logging and Monitoring**
   - At minimum, log:
     - Start and completion of SSO login attempts (without the provider token),
     - Provider used,
     - Whether login succeeded or failed,
     - Whether user was new or existing.
   - Do not log raw tokens or secrets.

## Non-Functional Requirements

- **Security**
  - Ensure HTTPS is used (already enabled via `UseHttpsRedirection`).
  - Validate token lifetimes and reject expired tokens from providers where applicable.
- **Performance**
  - SSO login API should typically complete within 2 seconds under normal network conditions; implementation must not introduce blocking waits.
- **Scalability**
  - In-memory profile mapping is acceptable initially but must be behind an interface, allowing an easy move to persistent storage later.
- **Reliability**
  - Failure of one provider must not prevent other providers from functioning.
- **Compatibility**
  - Existing AuthController `/api/Auth/token` endpoint remains unchanged.

## Acceptance Criteria Mapping

1. **AC1 - Available Authentication Methods**
   - When the client calls `GET /api/auth/providers`, the response includes `google`, `facebook`, and `apple` entries with `isEnabled = true` (configurable).
   - The API works identically regardless of client device type.

2. **AC2 - Successful SSO Login Flow**
   - Given a valid provider token and provider id:
     - `POST /api/auth/sso/login` returns:
       - 200 OK,
       - a non-empty JWT (`token`) with valid signature and expiry,
       - `userId` corresponding to mapped internal user,
       - `redirectUrl` set to either `/profile` or `/home`.
   - Using the returned JWT to call an authorized endpoint (e.g., `/api/test`) succeeds.

3. **AC3 - First-Time SSO Profile Creation**
   - If `POST /api/auth/sso/login` is called with an external identity that has no mapping, it:
     - Creates a new internal user id,
     - Returns `isNewUser = true`,
     - Subsequent call with same external identity returns `isNewUser = false` and the same `userId`.

4. **AC4 - Device-Agnostic Behavior**
   - SSO APIs do not read any device-specific header/body attributes.
   - Manual testing or automated tests confirm that the same API calls behave consistently across clients (e.g., Postman, mobile, browser-based SPA).

## Cross-Service Dependencies

- **External Providers**
  - Google OAuth/OpenID,
  - Facebook Login,
  - Apple Sign In.
- For this initial story in this repository:
  - Actual network calls may be represented by abstraction (interfaces) with stub or mock implementations for local/testing.
  - Real client IDs/secrets and endpoints will be configured via configuration, allowing later production-grade integration without code changes.

---