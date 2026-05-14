# SPEC: Remove Hardcoded Secrets and Use Environment Variables for Configuration

## Current State

- **Interface / Code Locations:**  
  - Application source code currently contains hardcoded secrets (API keys, DB credentials, tokens, etc.) directly in source files, e.g.,  
    ```python
    DB_PASSWORD = "hardcodedpassword"
    API_KEY = "staticapikey123"
    ```
  - These secrets may appear in:
    - Configuration classes
    - Utility files
    - Initialization scripts
    - Documentation/examples

- **Data Models:**
  - Secrets are not stored externally or in secure vaults; no use of environment variables or secret management.

- **Configuration:**
  - Credentials and sensitive settings are set in plain text within codebases or in commit history.
  - Application environment does not require any secrets to be passed in as environment variables.

- **Key Behaviors:**
  - Secrets are static and bundled with deployments.
  - Impossible/impractical to rotate credentials without code changes.
  - High risk of accidental exposure via repository access or code sharing.

---

## Target State

- **Interface / Code Locations:**
  - All secrets (database passwords, API keys, tokens, sensitive connection strings) are retrieved from environment variables using, e.g.,  
    ```python
    import os
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    API_KEY = os.environ["API_KEY"]
    ```
  - No sensitive values remain hardcoded in the codebase.

- **Data Models:**
  - N/A — not applicable to this task

- **Configuration:**
  - Secrets must be set via environment variables at deploy/runtime.
  - Application fails fast on missing env vars, with clear error messaging.
  - Documentation is updated to inform operators of required environment variable names.

- **Key Behaviors:**
  - Secrets can be rotated without a code change.
  - No secrets are committed to the repository or visible in the source code.

---

## Compatibility & Breaking Changes

1. **Breaking Change: Removal of Hardcoded Secrets**
    - **Impact:** Application will not function unless required secrets (now only available via environment variables) are provided at runtime.
    - **Migration Path:**
        - Identify all places in deployment, CI/CD, and local development where secrets were previously assumed or set via code.
        - Update deployment manifests, Dockerfiles, process managers (e.g., systemd) to set required secrets as environment variables:
          ```
          export DB_PASSWORD=actual_password
          export API_KEY=actual_apikey
          ```
        - For Docker/Kubernetes, set these as environment variables in container specs.

2. **Error on Missing Environment Variables**
    - **Impact:** Application will exit with an error if any required environment variable is missing.
    - **Migration Path:** Ensure all documented secrets are set in every environment in which the application is run.

---

## Key Flows (before vs after)

### Example: Database Connection

**Before:**
1. Application is initialized.
2. Code reads password from a hardcoded string.
3. DB connection established using hardcoded password.

**After:**
1. Application is initialized.
2. Code attempts to read `DB_PASSWORD` from the environment.
3. If present, DB connection established; if not, application fails with a clear error about missing environment variable.

### Example: API Usage

**Before:**
1. Application calls external API, using hardcoded API key from source.
2. Key cannot be changed without code (and possibly redeploy).

**After:**
1. Application retrieves `API_KEY` from environment.
2. Key may be rotated independently of code.
3. Call proceeds if key provided.

---

## Data Model Changes

N/A — not applicable to this task

---

## Configuration Changes

- **Removed:**
  - All hardcoded secret values from source code.

- **Added:**
  - The following environment variables must be set externally (list to be updated per actual code review):
    - `DB_PASSWORD`
    - `API_KEY`
    - (add others as discovered: `SECRET_KEY`, `TOKEN`, etc.)

- **Required Actions:**
  - Documentation for deployment and developer onboarding must specify required environment variables.
  - Sample `.env.example` or deployment manifests provided, with empty/default values.
  - Legacy config files with hardcoded values must be removed or replaced with placeholders or env variable references.

---