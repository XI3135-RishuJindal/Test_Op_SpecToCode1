## PCI Scope Statement Draft – Functional Specification

### What & Why

This deliverable is a written PCI DSS scope statement for the MVP release of the ApiGateway system. The purpose is to declare—in a manner fit for audit and compliance review—that the MVP does not store, process, or transmit Cardholder Data (CHD) or Sensitive Authentication Data (SAD), thus placing the system out-of-scope for most PCI DSS requirements. Such clear documentation ensures alignment with risk assessment procedures, satisfies auditor expectations, and reduces compliance burden for the team now and in the future.

#### User Story Reference
US-007: As a technical/compliance lead, I must be able to demonstrate through an authoritative scope statement that our system does not handle CHD.

### Acceptance Criteria

- The statement must explicitly state that the ApiGateway system (MVP) does not store, process, or transmit Cardholder Data or Sensitive Authentication Data.
- The document must clarify the current architecture and data flows, demonstrating the absence of CHD or SAD at any logical or physical layer.
- The scope boundaries must be unambiguous—there must be no language that could introduce uncertainty about system posture.
- Any planned future features that could alter scope must be declared out-of-scope for this version.
- The statement must be suitable for sharing with compliance auditors, risk managers, and security stakeholders.
- The location and versioning of the statement must be in accordance with repository documentation practices.

### Out-of-Scope

- Policies or technical controls for systems storing/processing CHD.
- Details about non-MVP or planned future features which MIGHT introduce PCI scope (if/when these are implemented, a new review will be triggered).
- Legal review and submission to external auditors (covered by separate process).

### Dependencies/Cross-Service Considerations

- Alignment with any architecture documents, data flow diagrams, or system boundary definitions currently maintained by the team.
- Should be referenced in CI/CD pipelines or compliance documentation as a formal artifact.