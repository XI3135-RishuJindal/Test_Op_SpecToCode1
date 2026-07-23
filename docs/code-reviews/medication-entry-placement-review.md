# Code Review: Medication Entry UI – Placement & Structure

**Date:** <!-- fill in review date -->  
**Reviewer(s):** <!-- team lead / peer reviewer names -->  
**Author:** <!-- developer name -->  
**Story:** US-001 – Build Responsive Medication Entry UI  
**Review scope:** File/folder placement and structural conventions only  
                 (functionality, accessibility, and test coverage are reviewed separately)

---

## 1. Files Under Review

| File | Location | Status |
|------|----------|--------|
| `MedicationEntry.razor` | `Pages/Medications/` | ✅ Correct |
| `MedicationEntry.razor.cs` | `Pages/Medications/` | ✅ Correct |
| `MedicationEntry.razor.css` | `Pages/Medications/` | ✅ Correct |
| `MedicationEntryModel` (class) | `ApiGateway.Pages.Medications` namespace | ✅ Correct |

---

## 2. Placement Checklist

| Criterion | Result | Notes |
|-----------|--------|-------|
| Component lives under `Pages/Medications/` | ✅ Pass | Matches plan.md guidance |
| File naming follows `<Feature>.<ext>` pattern | ✅ Pass | `MedicationEntry.razor`, `.cs`, `.css` |
| Namespace matches folder path (`ApiGateway.Pages.Medications`) | ✅ Pass | Consistent with solution root `ApiGateway` |
| Code-behind (`.razor.cs`) separates logic from markup | ✅ Pass | `HandleValidSubmit` kept minimal in `.razor`; model + annotations in `.razor.cs` |
| Component-scoped CSS in `.razor.css` | ✅ Pass | No global style pollution |
| Route `@page "/medications/entry"` is consistent with folder | ✅ Pass | Kebab-case URL mirrors `Pages/Medications` |
| No direct DB / backend business logic in UI layer | ✅ Pass | Submit handler has TODO comment; no service calls yet |
| `MedicationEntryModel` maps to `MedicationDTO` fields | ✅ Pass | `Name`, `Dosage`, `Frequency`, `Route` covered |

---

## 3. Convention Compliance

### 3.1 Razor / Blazor Conventions
- **Markup** (`MedicationEntry.razor`): Contains only `@page`, HTML, `<EditForm>`, and a minimal `@code` block.  
- **Logic** (`MedicationEntry.razor.cs`): Contains the `MedicationEntryModel` class with data annotations.  
- **Styles** (`MedicationEntry.razor.css`): Component-scoped; no global overrides.

### 3.2 Naming
- PascalCase component name (`MedicationEntry`) — consistent with existing controllers (`AuthController`, `HealthController`).
- Namespace `ApiGateway.Pages.Medications` follows the `<ProjectRoot>.<FolderPath>` convention used in the project.

### 3.3 Constitution Guardrails
- UI layer contains no database or backend business logic. ✅  
- Model fields reference `MedicationDTO` property names (`Name`, `Dosage`). ✅  
- Text is defined in markup (not hardcoded in C#) — i18n-ready. ✅  

---

## 4. Feedback Log

| # | Feedback | Raised by | Resolution | Status |
|---|----------|-----------|------------|--------|
| 1 | *(No structural issues found in initial review)* | — | — | ✅ Closed |

> **Instructions for reviewers:** Add rows to the table above for any file/folder placement or structural feedback. Mark status as `Open`, `In Progress`, or `Closed`. Do **not** record functional or accessibility feedback here — those belong in the functional review.

---

## 5. Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | | | |
| Peer Reviewer | | | |
| Tech Lead | | | |

---

## 6. Next Steps

- [ ] Functional review (form validation, responsive layout, accessibility) — separate review ticket
- [ ] Demo on mobile and desktop emulators per constitution review standards
- [ ] Update README if new setup steps are needed for Blazor pages routing
