# Implementation Plan – US-001 Log in with Third-Party Single Sign-On

## Architectural Approach

1. **New Auth Layer Components**
   - Introduce a provider-agnostic SSO service layer:
     - `Services/ISsoAuthenticationService` – orchestrates SSO login flow (validation, mapping, JWT issuance).
     - `Services/IExternalIdentityProvider` – abstracts each external provider.
     - Implementations:
       - `Services/GoogleIdentityProvider`,
       - `Services/FacebookIdentityProvider`,
       - `Services/AppleIdentityProvider`.
   - Introduce a `Services/IUserProfileStore` abstraction with an in-memory implementation `InMemoryUserProfileStore` for mapping provider identities to internal user IDs.

2. **Controller Additions**
   - Extend `Controllers/AuthController.cs`:
     - Add `GET /api/auth/providers`.
     - Add `POST /api/auth/sso/login`.
   - Keep existing `/api/Auth/token` endpoint unchanged for compatibility.

3. **JWT Token Issuance**
   - Reuse existing JWT creation logic by:
     - Extracting token generation into a helper/service:
       - `Services/IJwtTokenGenerator` with implementation `JwtTokenGenerator`.
   - New SSO endpoint will call `IJwtTokenGenerator.CreateToken` with the internal user id and SSO-specific claims (provider, provider_user_id, email).

4. **Configuration and Feature Flags**
   - Extend `appsettings.json` and `appsettings.Development.json` with an `Authentication:Providers` section, e.g.:
     ```json
     "Authentication": {
       "Providers": {
         "Google": { "Enabled": true },
         "Facebook": { "Enabled": true },
         "Apple": { "Enabled": true }
       }
     }
     ```
   - Provider config will also be used later to hold client IDs and secrets; for now stub values are acceptable.

5. **Dependency Injection Setup**
   - In `Program.cs`:
     - Register new services:
       - `builder.Services.AddSingleton<IUserProfileStore, InMemoryUserProfileStore>();`
       - `builder.Services.AddScoped<IJwtTokenGenerator, JwtTokenGenerator>();`
       - `builder.Services.AddScoped<ISsoAuthenticationService, SsoAuthenticationService>();`
       - Register provider implementations and a small registry to resolve provider by id.

6. **Testing Strategy**
   - Create new unit tests in `Tests/Controllers/AuthControllerTests.cs`:
     - Test `GET /api/auth/providers` via controller method directly.
     - Test `POST /api/auth/sso/login` for:
       - Valid request returning 200 and a token.
       - Missing provider, missing token (400).
       - Provider auth failure mapped to 401.
   - Create unit tests for `SsoAuthenticationService` and `InMemoryUserProfileStore` if feasible within existing testing pattern:
     - In-memory store mapping correctness and idempotency.

## Detailed Design

### Data Models

1. **New Request/Response DTOs (under `Models`)**

- `SsoLoginRequest`:
  - `string Provider { get; set; }`
  - `string ProviderToken { get; set; }`
  - `string? DeviceInfo { get; set; }`

- `SsoLoginResponse`:
  - `string Token { get; set; }`
  - `DateTime ExpiresAt { get; set; }`
  - `string UserId { get; set; }`
  - `bool IsNewUser { get; set; }`
  - `string Provider { get; set; }`
  - `string RedirectUrl { get; set; }`

- `AuthProviderInfo`:
  - `string Id { get; set; }`
  - `string DisplayName { get; set; }`
  - `bool IsEnabled { get; set; }`

- `ExternalIdentity` (internal model in `Services` or `Models`):
  - `string Provider { get; set; }`
  - `string ProviderUserId { get; set; }`
  - `string? Email { get; set; }`
  - `string? Name { get; set; }`

2. **User Profile Store Models**

- `UserProfile`:
  - `string UserId { get; set; }`
  - `string? Email { get; set; }`
  - `Dictionary<string, string> ExternalIds` mapping provider -> providerUserId.

### Service Interfaces

1. `IExternalIdentityProvider`
   - Methods:
     - `Task<ExternalIdentity?> ValidateTokenAsync(string providerToken, CancellationToken cancellationToken = default);`
   - Each implementation must:
     - Return `null` or throw a dedicated exception on invalid token.

2. `IUserProfileStore`
   - Methods:
     - `Task<UserProfile?> FindByExternalIdentityAsync(string provider, string providerUserId);`
     - `Task<UserProfile> CreateOrUpdateForExternalIdentityAsync(ExternalIdentity externalIdentity);`
   - In-memory implementation uses a thread-safe collection (e.g., `ConcurrentDictionary<(string, string), UserProfile>`).

3. `IJwtTokenGenerator`
   - Methods:
     - `string GenerateToken(UserProfile user, ExternalIdentity externalIdentity, out DateTime expiresAt);`

4. `ISsoAuthenticationService`
   - Methods:
     - `Task<SsoLoginResponse> LoginWithProviderAsync(SsoLoginRequest request, CancellationToken cancellationToken = default);`
   - Orchestration steps:
     - Validate request.
     - Resolve provider implementation by `Provider`.
     - Validate token with provider; get `ExternalIdentity`.
     - Map/create `UserProfile` via store.
     - Generate JWT via `IJwtTokenGenerator`.
     - Fill `SsoLoginResponse` including `IsNewUser` status and `RedirectUrl` (from configuration default).

### Controller Changes

In `AuthController`:

1. Inject new services via constructor:
   - `ISsoAuthenticationService` and `IConfiguration` (already present) and maybe an `ILogger<AuthController>` (already present).

2. **GET /api/auth/providers**
   - New action:
     - Reads configured providers from `IConfiguration`.
     - Returns a list of `AuthProviderInfo`.
     - Always returns 200 with at least `{ google, facebook, apple }`, marking disabled ones via `IsEnabled`.

3. **POST /api/auth/sso/login**
   - New action:
     - Accepts `SsoLoginRequest` from body.
     - Logs provider selection (without token).
     - Calls `_ssoAuthService.LoginWithProviderAsync(...)`.
     - Returns 200 with `SsoLoginResponse`.
   - Error handling:
     - If service throws validation exception, return 400 `ErrorResponse`.
     - If service throws provider auth exception, return 401 `ErrorResponse`.
     - If any unhandled exception, log and return 500 `ErrorResponse`.

### Program.cs Updates

- Add DI registrations for new services and provider implementations.
- Ensure no change to existing authentication / JWT validation configuration.
- Optionally configure Serilog enrichment for SSO categories if needed (leveraging existing logging).

## Testing and Validation

1. **Unit Tests**
   - `AuthControllerTests`:
     - `GetProviders_ReturnsConfiguredProviders`.
     - `SsoLogin_ValidRequest_ReturnsToken`:
       - Mock `ISsoAuthenticationService` to return a prepared `SsoLoginResponse`.
     - `SsoLogin_InvalidRequest_ReturnsBadRequest`:
       - Mock service to throw a `ValidationException` or custom, verify 400 and `ErrorResponse`.
   - Service-level tests (if added under `Tests/Services/...`):
     - `SsoAuthenticationService_LoginWithProvider_CreatesNewUserForFirstLogin`.
     - `SsoAuthenticationService_LoginWithProvider_UsesExistingUserForSubsequentLogin`.

2. **Manual Testing / Swagger**
   - Update swagger documentation via XML docs and let `AddSwaggerGen` pick them up.
   - Run app and:
     - Call `GET /api/auth/providers`.
     - Call `POST /api/auth/sso/login` with mocked provider tokens and stub provider implementations that always accept tokens for given patterns.
     - Use returned JWT in `Authorization: Bearer` header to call `/api/test`.

3. **Security Review**
   - Confirm no logs include token values.
   - Ensure provider token parameters are treated as secrets.

---