## Summary

This specification covers the refactoring of application configuration to use environment variables for secrets, replacing any storage of secrets within config files or code constants. The expected outcome is that all sensitive values (e.g., API keys, passwords, tokens) will be exclusively sourced from environment variables, reducing the risk of exposure through version control or accidental leaks.

## Motivation

The drivers for this change are as follows:
- **Security:** Storing secrets in code or config files can result in accidental exposure if files are added to version control or shared inappropriately.
- **Compliance:** Best practices and compliance frameworks (e.g., SOC2, ISO 27001) require secrets not be committed to VCS.
- **Upgrade Urgency:** Medium, as per tech analysis. No specific vulnerabilities or EOL drivers have been cited, but there is recognized and ongoing tech debt in secret management practices.

## Current State

- **Interfaces:** N/A — specific application interfaces, classes, or frameworks are not described in the context.
- **APIs/Data Models:** Secrets are currently defined and accessed via configuration files or code-level constants. These may include items such as database credentials, API tokens, or access keys.
- **Key Behaviours:** At runtime, the application reads these secrets from disk-based config files or hardcoded values.
- **Config Keys/Schemas:** Specific names, data types, or schema elements for secrets are not provided in current context.  
- **Affected Components:** TODO — List exact configuration elements once identified.

## Proposed Changes

| Component          | Before                                   | After                                    | Breaking? (Y/N) |
|--------------------|------------------------------------------|-------------------------------------------|-----------------|
| Application config | Secrets stored in code or config files    | Secrets are sourced solely from environment variables | Y               |
| Secret access code | Loads values via file/constant accessors  | Reads values from environment variable lookup | Y            |
| Config files       | Contain sensitive data                    | Contain no secrets; only public/harmless config | Y           |

## Compatibility & Breaking Changes

| Breaking Change                                           | Migration Path                                                                                    |
|----------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| Application no longer loads secrets from config files     | Operators must configure all required secrets using environment variables before deployment.      |
| Direct access to secrets via constants/config removed     | Callers must use environment variable lookups in all relevant contexts.                          |
| TODO (Specific keys/classes to update)                   | TODO (Document for each once identified.)                                                        |

## Acceptance Criteria

1. **Given** that the application is started without the required environment variable for a secret, **when** the secret is accessed, **then** a clear error is produced and the secret is not loaded from any config file or code constant.
2. **Given** the required environment variable is set, **when** the application starts, **then** all secret-dependent functionality initializes successfully and uses the value from the environment variable.
3. **Given** a config file with secret values exists, **when** the application is started, **then** none of those secret config values are loaded or used by the application.
4. **Given** a codebase scan, **when** searching for previously-hardcoded or config-file secrets, **then** no secrets are present in either source code or configuration files.
5. **Given** CI configuration with environment variables for secrets, **when** tests requiring secrets run, **then** they succeed by obtaining secrets via the environment.

## Open Questions

| # | Question                                                                     | Owner (or TODO) | Due Date (or TODO) |
|---|------------------------------------------------------------------------------|-----------------|--------------------|
| 1 | Which config keys/secrets need to be migrated to environment variables?       | TODO            | TODO               |
| 2 | Are there backward-compatibility requirements with existing deployment tools? | TODO            | TODO               |
| 3 | What error messaging/logging format is required for missing environment vars? | TODO            | TODO               |
| 4 | Is there automation for migrating secrets from config to environment securely?| TODO            | TODO               |