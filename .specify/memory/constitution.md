# Constitution: .NET 8.0 SDK-Style Migration

## Project Identity

**Name:** .NET Project SDK-Style Modernization  
**Purpose:** Migrate project files and configuration to .NET 8.0, adopting the SDK-style project format.  
**High-Level Goal:** Transition legacy project structures to .NET 8.0 SDK-style to ensure future compatibility and streamline build configurations.

---

## Guiding Principles

1. **Prefer SDK-style project formats over legacy formats because .NET 8.0 mandates SDK-style for full tooling support.**
2. **Prefer .NET 8.0 compatibility over legacy framework compatibility because continued support and security rely on current LTS versions.**
3. **Minimize code and configuration changes not directly required by the SDK-style migration because the upgrade scope is strictly project file and configuration modernization.**
4. **Ensure repeatable and verifiable upgrades over ad-hoc/manual changes because predictable outcomes and team consensus are required for maintainability and auditability.**

---

## Constraints

- **Timeline and Effort Ceiling:**  
  Person-days: as estimated in the "moderate" upgrade option (exact figure unknown, enforce limit per that option).
- **Technology Mandates:**  
  - All project files must be migrated to .NET 8.0 SDK-style format.
  - Final runtime version: .NET 8.0.
- **Cloud Provider:**  
  N/A — not applicable to this task.
- **Compliance Requirements:**  
  N/A — not applicable to this task.
- **Budget or Scope Freezes:**  
  - Upgrade scope is limited strictly to project file and configuration migration to .NET 8.0 SDK-style, as per the modernization goal and upgrade option.
  - No inclusion of unrelated refactoring or feature work.

---

## Quality Standards

- **Testing Coverage Floor:**  
  N/A — not applicable to this task (test suite change not in scope of migration).
- **Code Review Requirements:**  
  - 100% of project file and configuration changes must undergo peer review by at least one team member other than the author.
- **Documentation Must-Haves:**  
  - Migration steps and any incompatibilities encountered must be documented in the migration notes.
  - All updated configuration and project files must be accompanied by a commit message describing the rationale and scope of change.
- **Deployment Gates:**  
  - Successful build verification on .NET 8.0 must be demonstrated in CI before merge.

---

## Decision Log

| ID  | Decision                                                             | Rationale                                                                          | Status   |
|-----|----------------------------------------------------------------------|-------------------------------------------------------------------------------------|----------|
| 1   | Adopt .NET 8.0 SDK-style project files for all applicable components | .NET 8.0 mandates SDK-style; ensures future support and compatibility               | Accepted |
| 2   | Scope limited strictly to project file/config migration              | Modernization goal and upgrade option define exact, narrow scope                    | Accepted |

---