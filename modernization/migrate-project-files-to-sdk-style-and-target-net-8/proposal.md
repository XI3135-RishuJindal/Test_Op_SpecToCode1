# Proposal: Migration of Project Files to SDK-Style and Target .NET 8

## Overview

- Modernize existing project files by migrating to the SDK-style format.
- Set all projects to target .NET 8.

## Business Motivation

- Enable long-term maintainability and support by aligning with modern .NET standards.
- Simplify project structure and dependencies for easier onboarding and tooling support.
- Unlock access to new .NET 8 features, performance improvements, and security patches.
- Reduce technical debt by eliminating legacy project formats.

## Scope

### In Scope

- Convert all existing project files to the SDK-style project format.
- Modify project files to target .NET 8.
- Validate successful builds after migration.

### Out of Scope

- Refactoring application code for .NET 8 compatibility (unless strictly required for build).
- Upgrading non-project-file dependencies (e.g., external libraries or tools).
- Adding new features or changing functionality beyond the project file structure.
- Update of build/release pipelines unless required to support SDK-style and .NET 8 projects.

## Stakeholders

- Application development team
- Technical leads/architects
- DevOps/build engineering team
- Product owners/project managers

## Success Criteria

- All projects use SDK-style project files.
- All projects target .NET 8 and can build successfully in local and CI environments.
- No loss of existing project references, build configurations, or metadata.
- No regression in application function from the migration.

## Risks & Mitigations

- **Risk:** Incompatibilities between current code and .NET 8.
  - *Mitigation:* Run automated tests after upgrade; address minimal required code issues as strictly necessary.
- **Risk:** Loss of configuration during project file migration.
  - *Mitigation:* Backup all project files; perform side-by-side diff; verify key settings post-migration.
- **Risk:** Build or CI pipeline failures due to tool/version mismatches.
  - *Mitigation:* Update build agents and pipelines as needed; communicate changes to DevOps early.

## Timeline Estimate

- Discovery and project backup: 1 day
- Migrate and convert project files: 2 days
- Update target framework and resolve build issues: 2 days
- Validation (builds, tests, and peer review): 1 day

**Total estimate:** 5-6 business days

---

All other aspects not described above are N/A — not applicable to this task.