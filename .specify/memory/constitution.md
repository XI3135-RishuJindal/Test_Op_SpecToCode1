Quality Principles:
- Follow SOLID and DRY principles for all controller logic and model definitions.
- Maintain clear separation between business logic, controller endpoints, and data validation.
- Implement robust error handling with meaningful error responses in case of failures or invalid operations (e.g., out-of-stock).
- All API endpoints must be documented with Swagger annotations.
- Data consistency must be ensured when updating cart state, especially reflecting real-time inventory status.
- All code must be covered by unit tests (minimum 80% coverage for changed/new files) and pass linting/Coding Standards (C# .editorconfig/default conventions).
- Code and comments must be in clear, professional English.

Architecture Guardrails:
- All endpoints are to be defined in dedicated controllers in the Controllers/ folder.
- Models must be declared in Models/; new DTOs or entities are to be placed here.
- Services for business logic must eventually be in a Services/ directory, but for this version, simple logic may remain in the controller.
- Interactions with inventory or cart storage must be via clear, injectable interfaces (even if implemented in-memory/mock for now).
- Changes must not break authentication, authorization, or existing endpoints.
- Changes to shared configs (e.g., dependency injection, appsettings) must be backward-compatible.

Non-functional Requirements:
- Cart operations must complete within 500ms P95 (for in-memory/mock implementation).
- User notifications and error messages must be returned as structured JSON.
- The feature must not increase memory use by more than 10% under smoke test.
- Maintain idempotency and uniqueness for cart actions (no double add).
- All changes must be CI/CD-ready (pass tests, build and deploy cleanly).

Review & Stakeholder Expectations:
- Specs and acceptance criteria must map directly to tests.
- All stakeholders (PO, Development Lead) must review cart API contract.
- All new models and endpoints must be discoverable in Swagger UI.