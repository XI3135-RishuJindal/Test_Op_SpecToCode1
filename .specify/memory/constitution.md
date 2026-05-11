Quality Principles:
- Security: Ensure that no unauthorized SDKs are included that may compromise security.
- Reliability: The CI pipeline must pass consistently.

Tech Guardrails:
- Utilize established CI tools for dependency scanning.
- Limit external libraries to those approved for use in the project.

Coding Standards:
- Follow standard naming conventions for scripts and configuration files.
- Ensure documentation is updated with any changes made during implementation.

Non-Functional Requirements:
- Dependency scanning should not add more than 5% to the total CI pipeline execution time.
- The system should alert the team immediately if a forbidden dependency is detected.