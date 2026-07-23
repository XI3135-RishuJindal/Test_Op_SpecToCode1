# Implementation Tasks – US-001 Log in with Third-Party Single Sign-On

## Repository: XI3135-RishuJindal/Test_Op_SpecToCode1.git

### Backend API – Models and Services

- [ ] Add new SSO-related models under `Models`:
  - [ ] Add `Models/SsoLoginRequest.cs` with `Provider`, `ProviderToken`, and optional `DeviceInfo` properties.
  - [ ] Add `Models/SsoLoginResponse.cs` with `Token`, `ExpiresAt`, `UserId`, `IsNewUser`, `Provider`, and `RedirectUrl`.
  - [ ] Add `Models/AuthProviderInfo.cs` describing provider `Id`, `DisplayName`, and `IsEnabled`.

- [ ] Implement SSO service layer under `Services`:
  - [ ] Add `Services/ExternalIdentity.cs` and `Services/UserProfile.cs` internal models for external identity and stored profiles.
  - [ ] Add `Services/IExternalIdentityProvider.cs` and stub implementations `Services/GoogleIdentityProvider.cs`, `Services/FacebookIdentityProvider.cs`, `Services/AppleIdentityProvider.cs` that validate tokens in a controlled/mockable way.
  - [ ] Add `Services/IUserProfileStore.cs` and `Services/InMemoryUserProfileStore.cs` implementing thread-safe mapping from `(provider, providerUserId)` to internal `UserProfile`.
  - [ ] Add `Services/IJwtTokenGenerator.cs` and `Services/JwtTokenGenerator.cs` encapsulating JWT creation using existing JWT configuration, ensuring appropriate SSO claims.
  - [ ] Add `Services/ISsoAuthenticationService.cs` and `Services/SsoAuthenticationService.cs` to orchestrate provider validation, user mapping, and token issuance.

### Backend API – Controller and Configuration

- [ ] Extend `Controllers/AuthController.cs`:
  - [ ] Inject `ISsoAuthenticationService` and add new action `GetProviders` mapped to `GET /api/auth/providers` returning configured SSO providers.
  - [ ] Add new action `SsoLogin` mapped to `POST /api/auth/sso/login` accepting `SsoLoginRequest`, calling `ISsoAuthenticationService`, and returning `SsoLoginResponse` or `ErrorResponse` with appropriate HTTP status codes.
  - [ ] Ensure existing `GenerateToken` endpoint behavior remains unchanged.

- [ ] Update dependency injection in `Program.cs`:
  - [ ] Register `InMemoryUserProfileStore`, `JwtTokenGenerator`, `SsoAuthenticationService`, and each provider implementation with the DI container.
  - [ ] Optionally register a provider registry or use named registration pattern to resolve `IExternalIdentityProvider` by provider id.
  - [ ] Verify Serilog logging is used consistently for new SSO operations.

- [ ] Extend configuration files:
  - [ ] Update `appsettings.json` and `appsettings.Development.json` to include an `Authentication:Providers` section listing Google, Facebook, and Apple with `Enabled` flags (and stub fields for client IDs/secrets as comments or placeholders).
  - [ ] Ensure new configuration keys are read safely (with sensible defaults) in provider enumeration and future provider implementations.

### Testing

- [ ] Update `Tests/Controllers/AuthControllerTests.cs`:
  - [ ] Add unit test for `GetProviders_ReturnsExpectedProviders` verifying that Google, Facebook, and Apple are included.
  - [ ] Add unit test `SsoLogin_ValidRequest_ReturnsToken` using a mocked `ISsoAuthenticationService` to assert a 200 OK with non-empty token.
  - [ ] Add unit tests for invalid SSO login requests (e.g., missing provider, missing token) returning 400 with `ErrorResponse`.

- [ ] Add service-level tests (new files under `Tests/Services`):
  - [ ] Test `InMemoryUserProfileStore` to confirm first-login profile creation and reuse of the same `UserId` on subsequent logins with the same external identity.
  - [ ] Test `SsoAuthenticationService` orchestration with mocked providers and `IJwtTokenGenerator`, covering both new-user and existing-user flows.

### Documentation and Validation

- [ ] Update XML documentation comments on new models and controller actions so that Swagger shows SSO endpoints and payloads clearly.
- [ ] Run the API locally, exercise `GET /api/auth/providers` and `POST /api/auth/sso/login` via Swagger UI or Postman, and confirm:
  - [ ] All acceptance criteria are met (providers listed; JWT issued; first vs subsequent login behavior; token works on existing authorized endpoints).
  - [ ] Logs do not contain any provider tokens or secrets.
- [ ] Ensure `dotnet test` passes for all existing and new tests, and resolve any failing tests before merging.