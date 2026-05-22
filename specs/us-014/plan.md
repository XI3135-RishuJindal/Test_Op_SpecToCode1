Delivery plan — HOW

Architecture decisions
- Implement JIT provisioning inside the JwtBearer authentication pipeline using options.Events.OnTokenValidated to ensure actions run only after token validation, before controller execution.
- Introduce a configuration-driven RoleMappingService that extracts IdP roles from claims and maps them to platform roles using typed options (AuthorizationOptions).
- Add AccountProvisioningService that ensures an account exists for the subject and assigns roles/permissions atomically; design for idempotency.
- Provide a pluggable store: IAccountStore with InMemoryAccountStore and FileAccountStore (JSON per subject) using write-then-rename for atomicity on POSIX/NTFS.

API and contracts
- No public API changes for existing endpoints. For test convenience, extend AuthController token generation to accept optional roles in the request and emit them as “idp_roles” claims, enabling end-to-end testing without a real IdP.

Data model (new)
- Models/Account.cs: Id (GUID), SubjectId (string), Username (string), Roles (string[]), Permissions (string[]), CreatedAt, UpdatedAt.
- Models/Role.cs: Name (string), Permissions (string[]).
- Models/Permission.cs: Name (string). (Lightweight for future extension.)

Configuration binding
- Options/AuthorizationOptions.cs with:
  - string DefaultRole
  - string UnknownRoleBehavior ("apply-default" | "deny")
  - Dictionary<string, string[]> RoleMappings (IdP role -> platform roles)
  - Dictionary<string, string[]> Roles (platform role -> permissions)
- Bind from "Authorization" section in appsettings.json/appsettings.Development.json.