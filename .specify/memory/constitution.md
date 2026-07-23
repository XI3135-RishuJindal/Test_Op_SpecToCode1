# Specification Constitution – US-001 Log in with Third-Party Single Sign-On

## Quality Principles

1. **Security-first for authentication**
   - All SSO flows must be based on standard protocols (OAuth 2.0 / OpenID Connect).
   - Never log raw access tokens, ID tokens, authorization codes, or secrets.
   - JWTs issued by this API gateway must be signed with a strong symmetric key (HS256) or better, using keys from configuration only.
   - Validate all external tokens (issuer, audience, signature, expiry, nonce/state where applicable).

2. **Idempotent identity mapping**
   - SSO logins must deterministically map an external identity (provider + subject) to a single internal user identity.
   - First-login profile creation must be safe to retry; race conditions must not create duplicate logical users.

3. **Clear separation of external vs internal identity**
   - External providers (Google, Facebook, Apple) remain sources of authentication.
   - This service is responsible for:
     - validating external tokens,
     - mapping to internal user identity,
     - issuing internal JWTs with consistent claims.
   - Do not overload external IDs as internal user IDs; always maintain an internal user identifier.

4. **API ergonomics and UX support**
   - REST endpoints for SSO must be simple, well-named, and documented via Swagger.
   - Responses must be JSON, with consistent structure and HTTP status codes.
   - Front-end clients must be able to implement responsive SSO UX for mobile, tablet, and desktop without server changes (server is device-agnostic).

5. **Backward compatibility**
   - Do not break existing `/api/Auth/token` behavior or current JWT validation settings.
   - New SSO endpoints are additive and should coexist with current password-based test-token endpoint.

## Coding Standards

1. **C# / ASP.NET Core**
   - Use dependency injection for services (no static singletons for auth flows).
   - Place DTOs in `Models` and service classes in a dedicated namespace (e.g., `Services`).
   - Use async APIs for network / I/O interactions with providers.
   - Add XML documentation on public controllers and new models.

2. **Error Handling & Logging**
   - Use structured logging with clear event messages and correlation where possible.
   - Fail fast and explicitly: use 400 for client errors (invalid input, invalid provider token), 401 for failed authentication, 500 for unexpected server errors.
   - Return `ErrorResponse` uniformly for non-2xx results from public controllers.

3. **Configuration & Secrets**
   - All SSO client IDs, secrets, and endpoints come from configuration (`appsettings*.json` / environment variables).
   - Never hard-code secrets or tokens.
   - Support at least separate dev vs prod configuration via `IConfiguration`.

4. **Tests**
   - Add or extend unit tests for new controllers/services, especially:
     - happy path SSO login and JWT issuance,
     - invalid/missing provider tokens,
     - profile creation vs lookup.
   - Keep tests deterministic (mock external providers).

## Architecture Guardrails

1. **SSO integration pattern**
   - The API Gateway will:
     - Accept an authorization code or provider token from the client (depending on front-end pattern).
     - Exchange/validate it with Google/Facebook/Apple via dedicated service(s).
     - Normalize the identity (e.g., provider, subject, email, name).
     - Map to or create internal user record (in this codebase this may initially be in-memory or a simple store, but pattern must allow future persistence).
     - Issue a JWT compatible with existing `JwtBearer` configuration.
   - Do not embed full OAuth redirects UI flow inside this API for now; assume a front-end or mobile client handles browser redirections.

2. **Extensibility**
   - SSO provider logic must be pluggable:
     - A provider-agnostic interface (`IExternalIdentityProvider` or similar).
     - Separate implementations for Google, Facebook, Apple.
   - Make it straightforward to:
     - Disable a provider by configuration,
     - Add new providers later.

3. **Non-functional requirements**
   - **Performance**: SSO login endpoint must respond within 2 seconds in normal conditions, assuming provider responses are timely.
   - **Availability**: Failure of a single provider must not affect other providers or non-SSO endpoints.
   - **Observability**: Log high-level SSO flow steps and failures (without sensitive data) to aid debugging.

4. **Out-of-scope enforcement**
   - No new UI or device-specific front-end layouts in this repository.
   - No persistent user store implementation (database) unless explicitly added later; internal profile handling can be in-memory or stubbed but must be isolated behind an interface so it can be swapped.

## Review Standards & Stakeholder Expectations

1. **Product alignment**
   - Verify that all three providers (Google, Facebook, Apple) are represented in API semantics and documentation.
   - Confirm that “first login creates profile; subsequent logins reuse profile” behavior is testable via API.

2. **Security review**
   - Confirm correct validation of external tokens (including issuer and audience).
   - Ensure error responses do not leak sensitive provider error details or tokens.
   - Validate JWT claims: must include internal user id, provider info, and expiry.

3. **Testing expectations**
   - Unit tests passing for all controllers, including new SSO endpoints and mapping logic.
   - Clear strategy (even if mocked) for external provider interactions.

4. **Documentation**
   - Swagger/OpenAPI annotations for new endpoints.
   - Inline docs or comments explaining any stubbed or in-memory profile mapping to aid future replacement with a real user store.

---