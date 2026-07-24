## Project Identity

**Name**  
Lightweight Production Change-Management Checklist

**Purpose**  
Define and implement a concise, repeatable checklist to govern production changes across the organization.

**High-Level Goal**  
Establish a minimal, practical, and enforceable change-management checklist that reduces production incidents and improves auditability without introducing heavyweight process overhead.

---

## Guiding Principles

1. **Prefer lightweight, checklist-driven controls over complex workflow tools because upgrade urgency is medium and process overhead must remain low.**  
2. **Prefer consistency across teams over team-specific customization because the tech stack is unknown and the checklist must be technology-agnostic.**  
3. **Prefer human-verifiable steps (checklists, sign-offs) over tool-specific automation because current language/runtime/build tools are unknown.**  
4. **Prefer minimal mandatory items over exhaustive lists because the goal is a “lightweight” checklist that teams will actually adopt.**  
5. **Prefer documenting required outcomes (e.g., “rollback verified”) over prescribing specific tools because implementation details vary across systems.**

---

## Constraints

### Timeline and Effort Ceiling

- **Person-days ceiling:** TODO — not specified in the “conservative” option.  
- Until clarified, the checklist must be small enough to be implemented and rolled out incrementally with minimal team disruption.

### Technology Mandates

- **Language / Runtime / Build tool:** N/A — unknown and not required for a process/checklist task.  
- **Cloud provider:** N/A — not specified and not required to define a generic checklist.  
- **Compliance requirements:** TODO — none specified; if regulatory or internal audit requirements exist, they must be integrated later without expanding scope beyond a “lightweight” checklist.

### Budget or Scope Freezes

- **Scope:** Limited strictly to defining and implementing a production change-management checklist (no tooling build-out, no platform migration, no broader ITSM redesign).  
- **Budget:** TODO — not specified; assume only low-cost process and documentation changes unless otherwise approved.

---

## Quality Standards

1. **Checklist Definition**
   - A single canonical checklist document stored in version control.  
   - Maximum 1 page length for the core checklist (excluding examples/FAQ).

2. **Pilot and Validation**
   - Checklist piloted with at least **1 production team** and applied to **≥3 real production changes** before general rollout.  
   - At least **1 post-change review** (lightweight retro) conducted during pilot to confirm usability.

3. **Review and Approval**
   - **At least 2 reviewers** (e.g., one from operations/SRE, one from development or product) must formally review and approve the checklist before it is marked as “adopted”.  
   - Changes to the checklist must follow a simple review process (e.g., PR with at least 1 independent reviewer).

4. **Documentation**
   - A “How to use this checklist” guide containing:  
     - When the checklist MUST be used (scope of changes).  
     - Roles responsible for each checklist item.  
     - Examples of a completed checklist for at least **2 different change types** (e.g., routine deployment vs urgent hotfix).

5. **Adoption Gate**
   - The checklist must be easily consumable: available in a format suitable for inclusion in existing change tickets or deployment templates (e.g., a markdown snippet or form).  
   - For teams adopting the checklist, **100% of planned production changes** must show an attached or referenced completed checklist.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use a single, technology-agnostic “lightweight” checklist instead of tool- or stack-specific procedures. | Language/runtime/build tools are unknown; a generic checklist avoids rework and keeps the process simple and widely applicable. | accepted |
| ADR-002 | Limit the scope strictly to defining and implementing the checklist, not building automation or new workflow systems. | The modernization goal is only to define and implement a lightweight checklist; expanding to tooling or ITSM redesign would exceed the stated task. | accepted |
| ADR-003 | Constrain the checklist to minimal mandatory items that fit on one page. | To keep the process lightweight and encourage adoption while upgrade urgency is only medium. | accepted |

