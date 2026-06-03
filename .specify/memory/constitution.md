Quality Principles:
- Responsive Design: All UIs must adapt fluidly to screens from 320px wide up to large desktops. No horizontal scrolling should be needed.
- Accessibility (a11y): UIs must meet WCAG 2.1 AA standards, including semantic HTML, labeled inputs, keyboard navigation, and screen reader compatibility.
- Validation & Usability: Required fields must be clearly indicated and visually emphasized upon validation failure.
- Documentation: All UI components must have accompanying description and field annotation.
- Internationalization ready: Text should be externalized for easy translation (not hardcoded).
- Coding Standards: Use consistent naming, clear file structure, and organize logic for maintainability.
Architecture Guardrails:
- UI implementation (e.g., Blazor, Razor Pages, or React) must be separated from business/data logic.
- All form data models should directly reference or be mapped to the MedicationDTO model where applicable.
- No direct database or backend business logic in the UI layer.
Non-Functional Requirements:
- Form loads in under 1s on a 4G connection.
- Automated tests must exist for field validation, responsiveness, and keyboard accessibility.
Review Standards:
- Stakeholders expect field requirements, responsive behavior, and accessibility to be demoed on real mobile/desktop emulators.
- All acceptance criteria must be verifiable through tests or observable UI behavior.
- Source code should be peer-reviewed for maintainability and standards compliance.