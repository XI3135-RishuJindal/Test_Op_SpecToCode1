# Design Document: Remove Hardcoded Secrets and Use Environment Variables for Configuration

## Architecture Overview

#### Before Modernization
- Application secrets (e.g., API keys, passwords, tokens) are embedded directly in source code files or static configuration files present in source control.
- Secrets are exposed to anyone with access to the codebase and are not environment-specific, increasing the risk of leaks and improper credential usage.

#### After Modernization
- All secrets are retrieved at runtime from environment variables, not code or static config files.
- Environment-specific secrets are managed outside the codebase, reducing exposure.
- Application configuration supports reading sensitive values using standard environment variable interfaces provided by the operating system or deployment scripts.

---

## Migration Strategy

- **Approach:** Strangler Fig Pattern
    - Incrementally refactor code to replace hardcoded secrets with environment variable lookups, on a per-component basis.
    - Legacy secrets remain temporarily for fallback but will be systematically removed after validation.
    - No in-place “big bang” change—enables testing and rollback on a per-secret or per-component basis.

---

## Component Changes

### Application Source Code
- Replace references to hardcoded secrets with calls to read from environment variables:
    - E.g., change `password = "hardcoded123"` to `password = os.environ.get("DB_PASSWORD")` (syntax varies by language).
- Remove any non-secret configuration from this change; only secrets are refactored.

### Configuration Files
- Remove any plaintext secrets from config files that are checked into source control.
- Update application help docs and README to declare the new required environment variables.

### Secret Management
- Document the list of required environment variables per environment (local, staging, production).
- Optionally, introduce dotenv (`.env`) support for local development only, with that file excluded from source control (if supported in the language/tooling).

---

## Dependency Upgrade Plan

| dependency         | current version | target version | migration notes              |
|--------------------|----------------|---------------|-----------------------------|
| N/A — not applicable to this task |                |               |                             |

---

## CI/CD Pipeline Changes

- Update pipeline scripts to inject secrets as environment variables at build and deploy stages, instead of storing or templating secrets into config files.
- Remove pipeline steps that write secrets to files.
- For local builds, provide documentation on using a `.env` or export commands.
- For production, integrate with the CI/CD's environment variable or secret manager functionality (e.g., GitHub Actions Secrets, GitLab CI variables, Jenkins Credentials).

---

## Infrastructure Changes

- Ensure deployment orchestrators (Docker, Kubernetes, etc.) are configured to provide secrets via environment variables (e.g., `env` in Docker Compose, `envFrom`/`secretRef` in Kubernetes).
- Remove any file-mounting or pre-seeding of secrets into config files.
- (If not currently used) Recommend a secret store for fuller future improvements, but not in scope for this task.

---

## Rollback Plan

- Retain a branch/tag before changes for fast rollback.
- Keep hardcoded secrets commented (not deleted) until environment-variable-based secret handling is verified in production; uncomment if quick revert is needed.
- In the event of post-deploy failure attributable to secret loading, revert code and config to pre-migration versions, and redeploy with the previously used process for handling secrets.

---

## Testing Strategy

### Unit Tests
- Mock or inject environment variables as needed to test code paths that consume secrets from environment variables.
- Ensure missing variable behavior is handled gracefully (fail with clear error).

### Integration Tests
- In test deployments, ensure environment variables propagate to the app and are parsed/read correctly.

### Regression Tests
- Use existing application tests to ensure no service functionality is broken by configuration change.

### Performance Tests
- N/A — not applicable to this task

---