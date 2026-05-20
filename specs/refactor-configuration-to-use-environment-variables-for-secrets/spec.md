## Summary

This spec covers the refactor of application configuration to use environment variables for all secrets, replacing any secrets currently stored in configuration files, code, or other non-environment-variable sources. The expected outcome is that all secrets (passwords, API keys, tokens, etc.) are exclusively loaded from environment variables at runtime. This improves security posture and aligns with best practices for secret management.

## Motivation

Storing secrets in configuration files or code poses security and compliance risks, including accidental disclosure via source control or logs. Refactoring to use environment variables for all secrets mitigates these risks, enables better integration with secrets management systems, and meets modern security expectations. This change is motivated by the need to address medium-priority tech debt and to reduce ongoing operational risk. No EOL dates or CVEs are cited in the tech analysis, but this work is part of a broader modernization effort.

## Current State

- **Interfaces**: Configuration is loaded from files or embedded directly in code. Specific classes, methods, or config keys handling secrets are not specified in the tech analysis (**TODO: Populate with details when available**).
- **Behaviour**: At application startup or runtime, secrets are read from non-environment-variable sources. The mechanism for loading and applying secrets is unclear (**TODO**).
- **Data models**: N/A — not applicable to this task unless configuration modeling is defined.
- **Key affected elements**: Any config file fields, code variables, or build-time constants that contain secrets (**TODO: List when identified**).

## Proposed Changes

| Component         | Before                                   | After                                          | Breaking? (Y/N) |
|-------------------|------------------------------------------|------------------------------------------------|-----------------|
| Secret Handling   | Secrets are loaded from files or code     | Secrets are always loaded from env variables    | Y               |
| Configuration API | Accepts secrets via file/config fields    | Removes file/config secret fields; uses env     | Y               |
| Documentation     | Instructs placement of secrets in config  | Documents only env variable usage for secrets   | Y               |
| CI/Test Fixtures  | May use file-based secrets                | Must set required secrets as environment vars   | Y               |

## Compatibility & Breaking Changes

| Breaking Change                                     | Migration Path                        |
|-----------------------------------------------------|---------------------------------------|
| Secrets no longer read from files or code           | Update deployments to supply secrets as env vars; remove secret values from files/config. |
| Configuration API fields for secrets are removed    | Update callers to set secrets via env vars only. |
| Test and CI jobs must change secret provisioning    | Update CI scripts and test fixtures to set env vars as required. |
| TODO: Exact package/refactoring points              | TODO                                 |

## Acceptance Criteria

1. **Given** a deployment without environment variables set for required secrets, **when** the application starts, **then** it must fail securely with a clear error indicating which env vars are missing.
2. **Given** all required secret environment variables are set, **when** the application starts, **then** it must initialize fully and operate using those secrets (with no fallback to file or code-based secrets).
3. **Given** a secret is removed from a configuration file and not provided via env var, **when** the application starts, **then** it must not read the secret from the old location and must fail as in criterion 1.
4. **Given** CI jobs and test scripts set secrets only via environment variables, **when** tests run, **then** all secret-driven features must pass test assertions and logs must not contain secret values.

## Open Questions

| #  | Question                                                                  | Owner               | Due Date   |
|----|---------------------------------------------------------------------------|---------------------|------------|
| 1  | Which classes, config keys, or modules handle secret loading currently?    | TODO                | TODO       |
| 2  | Are there any build or deployment environments that cannot provide env vars? | TODO                | TODO       |
| 3  | Is there a secrets rotation procedure that must be updated for this change? | TODO                | TODO       |
| 4  | Which secrets are in scope (list of all secret names/keys/fields)?        | TODO                | TODO       |
| 5  | Will this apply to legacy branches, or only main branch going forward?    | TODO                | TODO       |
