Quality Principles:
- Forms must be accessible per WCAG 2.1 AA: labeled fields, keyboard navigation support, programmatically associated labels, and meaningful error states.
- UI must render responsively and remain fully usable on devices with screen widths from 320px (mobile) to ≥1200px (desktop).
- Code must be clearly organized, with presentation separation (e.g., .cshtml, Razor, or frontend directory for UI logic).
- Use semantic HTML for structure, especially form, label, input, and button elements.
- Input validation is deferred to API implementation—this UI focuses on layout and accessibility, not field validation logic.
- No sensitive data is logged, and test credentials are not hardcoded in UI.
- All new UI code must be covered by unit or integration tests at the component or rendering level where feasible.
- Follow .NET, C#, and team naming conventions on filenames, namespaces, and UI classes.
- All markup and logic changes are peer-reviewed and demonstrate accessibility and responsive compliance prior to merge.