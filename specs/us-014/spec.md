US-014: Default Role and Permission Assignment at Provisioning

What
- Implement Just-In-Time (JIT) account provisioning that:
  - Extracts IdP role claims from a validated JWT.
  - Maps IdP roles to platform roles and permissions using the approved roles/permissions matrix (R-03-03).
  - Creates a new platform account and assigns mapped roles/permissions atomically with account creation (ties to US-001).
  - Applies a configured default role (e.g., viewer) if IdP role claims are absent or unrecognized, or denies access per configuration.
- The provisioning runs automatically during authentication (JwtBearer OnTokenValidated) and is idempotent.

Why
- Ensure consistent, policy-driven access on first login without manual provisioning.
- Enforce least-privilege defaults and predictable behavior for unknown/absent role claims.
- Satisfy requirement R-03-03 for default role and permission assignment at provisioning time.

User story narrative
- As a security-conscious platform operator, I want new users authenticated via the IdP to be provisioned automatically with the correct platform roles and permissions so that the access model is consistent, auditable, and low-touch.

Scope
- Role extraction: read “idp_roles” (multiple claims allowed) or standard “role”/“roles” from JWT.
- Mapping: configuration-driven matrix under Authorization: { RoleMappings, Roles, DefaultRole, UnknownRoleBehavior }.
- Provisioning: if account doesn’t exist for the subject (NameIdentifier), create account and assign roles+permissions in a single atomic operation; if it exists, do nothing (idempotent). Future sync behavior is out-of-scope.
- Default/deny: if claims are absent or unrecognized, either:
  - apply-default: assign DefaultRole; or
  - deny: block access (terminate auth with 403) according to UnknownRoleBehavior.
- Persistence: provide an in-memory store for test/dev and a simple JSON file store to demonstrate atomic persistence. Production DB integration is out-of-scope.

Acceptance criteria
1) Recognized IdP roles
- Given a valid JWT containing idp_roles ["idp_admin"], and RoleMappings maps idp_admin -> ["admin"], when the user first calls any authorized API, then:
  - an account is created for the subject with roles ["admin"] and permissions per Roles["admin"],
  - the operation is logged with subject, mapped roles, and success=true,
  - the request proceeds authorized (subject to endpoint policies).

2) Absent IdP role claims, apply-default
- Given a valid JWT with no idp_roles, and UnknownRoleBehavior=apply-default with DefaultRole="viewer",
  - an account is created with role ["viewer"] and its permissions,
  - request proceeds authorized (subject to endpoint policies).

3) Unknown IdP role, deny
- Given a valid JWT with idp_roles ["external_contractor"], and UnknownRoleBehavior=deny,
  - provisioning does not create an account,
  - authentication fails with 403 (or 401 where applicable),
  - a warning log notes unknown role and outcome=denied.

4) Idempotency
- Given a subject that already has an account, repeating requests with the same token does not duplicate roles or permissions; no-op provisioning occurs and the request proceeds.

5) Atomicity (dev store semantics)
- The file-based store writes a new account by writing to a temp file and atomic rename; partial writes do not leave corrupted account files.

6) Observability
- Structured log fields: event=provisioning, subjectId, username, idpRoles, mappedRoles, outcome. Errors include stack trace.

Out-of-scope
- Admin UI, production RBAC datastore, cross-service propagation, role change synchronization on subsequent logins, fine-grained authorization policies on existing endpoints.

Cross-service dependencies and assumptions
- US-001 (Account creation) is logically related; for this API Gateway, we implement an internal Account model and store abstraction for dev/test. Future services can replace the store behind IAccountStore.
- Identity provider supplies JWT with user identifier (NameIdentifier) and optional role claims.

Configuration schema (example)
- Authorization:
  - DefaultRole: "viewer"
  - UnknownRoleBehavior: "apply-default" | "deny"
  - RoleMappings: maps IdP roles to platform roles. Example:
    - "idp_admin": ["admin"]
    - "idp_editor": ["editor"]
    - "idp_viewer": ["viewer"]
  - Roles: maps platform roles to permissions. Example:
    - "admin": ["*"]
    - "editor": ["data:read", "data:write"]
    - "viewer": ["data:read"]