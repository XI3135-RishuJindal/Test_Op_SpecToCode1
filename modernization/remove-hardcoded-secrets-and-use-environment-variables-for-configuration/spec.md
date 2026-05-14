# SPEC: Remove Hardcoded Secrets and Use Environment Variables for Configuration

## Current State

- **Application Secrets** (API keys, database passwords, tokens, etc.) are **hardcoded** directly within source files (e.g., inside `.java`, `.js`, `.py`, `.go` files).
- Typical usage pattern:
    ```python
    API_KEY = "12345-SECRET-PROD-KEY"
    DB_PASSWORD = "hardcoded_db_password"
    ```
- **No externalization**: Sensitive values are directly committed to the codebase.
- **No use** of runtime configuration or environment-based secret injection.
- Application start-up, API clients, and database connections fetch credentials from hardcoded vars/constants.
- **No documented method** for secret rotation or secure secret updates without code changes and redeploys.
- **Deployment environments** (dev, staging, prod) require source changes for different secret values.

---

## Target State

- **All application secrets** are referenced via **environment variables** (e.g., `os.getenv("API_KEY")`, `process.env.API_KEY`).
- Hardcoded constants for secrets are removed from source code.
- **Environment-specific secrets** provided via deployment configuration (env files, CI/CD secret stores, cloud secret managers, etc.).
- Application code reads secrets at runtime from the environment.
    ```python
    import os
    API_KEY = os.environ["API_KEY"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    ```
- **Secret management is externalized**, allowing **rotation and updates** without code changes.
- Non-secret configurations (features, ports, etc. not covered in this scope) remain unchanged.

---

## Compatibility & Breaking Changes

| Breaking Change                                                      | Migration Path                                                                                      |
|---------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Application will fail to start if required secrets are missing from the environment | **Migration Required:**<br> - Identify all now-required env variables.<br> - Update deployment manifests, CI/CD pipelines, or local dev scripts to supply these env variables before starting the application.<br> - Document expected env vars for each environment.<br><br>**Fallback:** Optionally implement runtime checks for missing variables with descriptive error messages and exit.|
| Secrets no longer present in source code                             | N/A (security improvement; not a breaking change to application function)                           |


---

## Key Flows (before vs after)

### Example: Database Connection Initialization

**Before**
1. Application imports a config/settings/constants module.
2. Connection string is built using hardcoded DB_PASSWORD variable.
3. Application connects to the database using this string.

**After**
1. Application reads `DB_PASSWORD` from the environment (`os.environ` or equivalent).
2. Connection string is built using the value from the environment.
3. Application connects to the database using the runtime-supplied password.

---

### Example: Calling an external API

**Before**
1. API key is a hardcoded constant.
2. Each API client call uses this constant for authentication.

**After**
1. API key is read at startup from the environment.
2. API client uses the env value.
3. Rotation or update to API key only requires updating the environment configuration.

---

## Data Model Changes

N/A — not applicable to this task

---

## Configuration Changes

- **New Required Environment Variables:** List of all secrets affected, e.g.:
    - `API_KEY`
    - `DB_PASSWORD`
    - `SECRET_TOKEN`
    - (repeat for each secret removed from code)
- **No changes to config files** beyond removing secret literals.
- **No new feature flags** or config keys.
- **Deployment updates required:** Secrets must now be supplied by:
    - `.env` files (for local/dev)
    - ENV assignments in docker, kubernetes manifests, etc.
    - CI/CD secret management systems

---

## Summary

This effort completely removes hardcoded secrets from the codebase and requires configuration via environment variables in all runtime environments, improving security and operational flexibility. No other changes are made outside of this scope.