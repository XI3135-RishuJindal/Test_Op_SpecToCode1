# Proposal: Migrate Project Files to .NET 8 SDK Style

## Overview

- Objective: Migrate all project files in the codebase to the .NET 8 SDK-style project format.
- This task addresses only the project file format; no code or framework changes are included.

## Business Motivation

- Ensure ongoing compatibility with latest .NET tooling and features.
- Improve build performance and maintainability.
- Reduce technical debt by adopting current .NET standards.

## Scope

### In Scope

- Identify all project files in the repository.
- Convert each project file to the .NET 8 SDK-style format.
- Validate project builds successfully post-migration.

### Out of Scope

- Changes to source code, dependencies, or runtime versions.
- Migrating to .NET 8 framework (only project file format is covered).
- Refactoring application logic or libraries.
- Addressing unknown language or runtime concerns beyond project file structure.

## Stakeholders

- Development team (responsible for ongoing maintenance).
- Build/release engineers.
- Technical leadership overseeing modernization.

## Success Criteria

- All project files use SDK-style syntax targeting .NET 8 (format only).
- Projects build successfully using updated project files.
- No loss of existing functionality or build artifacts.

## Risks & Mitigations

- **Incompatible Tooling:**  
  *Mitigation:* Test builds with current CI/CD tooling after migration.
- **Build Breakage:**  
  *Mitigation:* Perform incremental conversions and validation after each change.
- **Legacy Features Missing in SDK Style:**  
  *Mitigation:* Identify required legacy features and find SDK-style equivalents or document gaps.

## Timeline Estimate

- Discovery & Inventory: 0.5 day
- Conversion & Validation: 1–2 days (depending on project file count/complexity)
- Testing & Final Review: 0.5 day

**Total Estimate:** 2–3 days

---

Sections not directly relevant to this task:
- N/A — not applicable to this task