# Spec: Externalize All Configuration to Environment Variables

## Summary

This spec covers the migration of all hardcoded and file-embedded configuration values to environment variables across the application. The expected outcome is a runtime-configurable application that follows the [12-Factor App](https://12factor.net/config) methodology, where no environment-specific values (credentials, endpoints, feature flags, tuning parameters, etc.) are baked into the build artifact. Operators will be able to deploy the same artifact across development, staging, and production environments by supplying the appropriate environment variables at runtime.

---

## Motivation

**Technical drivers:**
- Hardcoded configuration values create tight coupling between the build artifact and a specific deployment environment, making promotion across environments error-prone and manual.
- Secrets and credentials embedded in source code or committed configuration files represent a security risk and may violate compliance requirements (e.g., SOC 2, PCI-DSS, GDPR data handling controls).
- Configuration drift between environments is difficult to audit when values are scattered across source files rather than centralized in a well-known, observable location.
- Upgrade urgency is rated **medium** — there is no immediate production outage risk, but the current approach is a recognized source of tech debt that blocks safe CI/CD automation and environment parity.

**Business drivers:**
- Enables self-service environment provisioning without requiring code changes or new builds.
- Reduces the blast radius of credential rotation (update the environment variable; no rebuild required).
- Supports containerized and cloud-native deployment patterns where environment injection is the standard configuration mechanism.

> **Note:** Specific CVEs, EOL dates, and framework versions were not provided in the tech analysis. If any configuration library in use has known CVEs or is end-of-life, those should be recorded here once identified. See Open Questions.

---

## Current State

The tech analysis did not supply source code context, specific class names, config keys, or schema elements. The following describes the general current-state pattern that this spec targets; it must be validated against the actual codebase during planning.

| Aspect | Current Behaviour |
|---|---|
| Configuration storage | Values are hardcoded inline or stored in committed configuration files (e.g., config files checked into version control) |
| Secret handling | Credentials (DB passwords, API keys, tokens) may be present in source or config files |
| Environment differentiation | Separate config files or build-time flags are used per environment |
| Runtime overridability | Configuration cannot be changed without modifying source or rebuilding the artifact |
| Discoverability | No single authoritative list of all configuration keys exists |

> **TODO:** Enumerate every specific configuration key, class, config file name, and schema element present in the codebase. This inventory is a prerequisite for planning.

---

## Proposed Changes

### Overview

All configuration values that vary by environment, contain secrets, or represent operational tuning parameters must be sourced exclusively from environment variables at runtime. A documented manifest of all supported environment variables (names, types, defaults, and whether they are required) must be produced as a deliverable.

### Component Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Application configuration loading | Values read from hardcoded literals or committed config files | Values read from environment variables at process startup | Y — deployment scripts and CI pipelines must supply variables |
| Secret / credential storage | Credentials embedded in source or config files | Credentials injected via environment variables; removed from source entirely | Y — existing deployment runbooks must be updated |
| Environment-specific config files | Separate files per environment (e.g., dev/staging/prod variants) | Single artifact; environment determined entirely by injected variables | Y — file-based override mechanism is removed |
| Configuration defaults | Defaults scattered across code | Defaults defined in one place (the configuration manifest/documentation); absent required variables cause a startup failure with a clear error | N — default values are preserved where safe |
| CI/CD pipeline configuration | May rely on committed config files or build-time substitution | Must supply all required environment variables via pipeline secret store | Y — pipeline definitions must be updated |
| Local development setup | Developers may rely on committed config files | Developers use a local environment variable file (not committed) populated from a documented template | N — developer workflow changes but is not breaking to the application |
| Configuration documentation | None or ad hoc | A canonical environment variable reference document listing every variable, its type, whether it is required, and its default value | N — additive |

> **TODO:** Populate the Component column with actual class names, config file names, and module identifiers once the codebase inventory is complete.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Config files removed from repository | Any deployment or tooling that reads config files directly will fail | Update all deployment scripts, Dockerfiles, Helm charts, and CI pipelines to inject environment variables instead |
| Hardcoded defaults removed or made explicit | Callers relying on implicit defaults may observe changed behaviour if a variable is not set | Document all defaults in the environment variable manifest; ensure startup validation emits a clear error for missing required variables |
| Build-time environment differentiation removed | Build pipelines that produce environment-specific artifacts must be restructured | Produce a single artifact; supply environment variables at deploy time via the pipeline's secret/variable store |
| Credentials no longer in source control | Any process that reads credentials from the repository will break | Migrate credentials to a secrets manager or pipeline secret store; distribute access to the new location to all affected teams |
| Local developer config files not committed | Developers who relied on committed config files for local setup will need to recreate their local environment | Provide a documented, non-committed template file listing all variables with safe local defaults; include setup instructions in the project README |
| TODO: Additional breaking changes | TODO | TODO — to be completed after codebase inventory |

---

## Acceptance Criteria

1. **Given** a complete list of configuration keys has been inventoried, **when** the codebase is audited, **then** zero hardcoded environment-specific values (hostnames, ports, credentials, API keys, feature flags) remain in committed source or config files.

2. **Given** the application is started without any environment variables set, **when** a required variable is absent, **then** the application fails to start and emits an error message that names the missing variable(s) explicitly — it does not start in a silently misconfigured state.

3. **Given** a valid complete set of environment variables is supplied, **when** the application starts, **then** it reaches a healthy/ready state within the same time bounds as the previous configuration approach.

4. **Given** the same build artifact, **when** it is deployed to two different environments with different environment variable sets, **then** each instance connects to its respective environment's dependencies (databases, APIs, etc.) without any code or artifact change.

5. **Given** a credential value is rotated (environment variable updated), **when** the application is restarted, **then** it uses the new credential without requiring a rebuild or code change.

6. **Given** a CI/CD pipeline run, **when** the pipeline executes, **then** all required environment variables are sourced from the pipeline's secret store and no config file containing secrets is read from the repository.

7. **Given** a new developer joins the project, **when** they follow the documented setup instructions using the environment variable template, **then** they can run the application locally without modifying any committed file.

8. **Given** the environment variable reference document, **when** it is reviewed, **then** every environment variable accepted by the application is listed with its name, data type, whether it is required or optional, its default value (if optional), and a plain-language description.

9. **Given** a static analysis or secret-scanning CI check is configured, **when** a pull request is opened that introduces a hardcoded secret or environment-specific value, **then** the CI check fails and blocks the merge.

10. **Given** the application is running, **when** a non-secret configuration value is queried via any existing health or diagnostics endpoint, **then** the value reported matches the environment variable that was injected — confirming live configuration is sourced from the environment.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the complete inventory of configuration keys, config files, and classes that currently hold configuration? This is a prerequisite for all other work. | TODO | TODO |
| 2 | Are any configuration libraries (e.g., a config-loading framework) currently in use, and if so, are they EOL or carrying known CVEs? | TODO | TODO |
| 3 | What secrets manager or pipeline secret store will be used to hold credentials in the target state (e.g., Vault, AWS Secrets Manager, GitHub Actions Secrets, etc.)? | TODO | TODO |
| 4 | Are there any configuration values that are legitimately static across all environments and therefore acceptable to keep hardcoded? If so, what is the policy for distinguishing them? | TODO | TODO |
| 5 | What is the agreed naming convention for environment variables (e.g., `APP_`, `SERVICE_NAME_` prefix, screaming snake case)? | TODO | TODO |
| 6 | Should the application support a local `.env`-style file for developer convenience, and if so, what library or mechanism is approved for loading it (ensuring it is never committed)? | TODO | TODO |
| 7 | Are there any regulatory or compliance requirements that constrain how certain configuration values (e.g., encryption keys) may be injected or stored? | TODO | TODO |
| 8 | What is the rollback plan if a deployment fails due to a missing or misconfigured environment variable after the migration? | TODO | TODO |
| 9 | Which teams or individuals own the existing deployment runbooks and CI/CD pipelines that must be updated as part of this migration? | TODO | TODO |
| 10 | Is there a requirement to support dynamic configuration reload at runtime (without restart), or is restart-on-change acceptable? | TODO | TODO |