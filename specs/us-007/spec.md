Story: US-007 — Draft PCI scope statement

What
- Produce a formal PCI scope statement for the MVP declaring that the system does not store, process, or transmit Cardholder Data (CHD) or Sensitive Authentication Data (SAD).
- Document the architectural boundary and data flows demonstrating the absence of CHD handling by the MVP.
- Define guardrails and an approval workflow to require PCI reassessment before any future payment feature is introduced.

Why
- To prevent unnecessary PCI scope and reduce compliance burden.
- To provide auditors, security reviewers, and stakeholders with a clear, authoritative statement and evidence of non-involvement with CHD/SAD.
- To institutionalize controls so any change that could impact PCI scope is detected and reviewed.

Narrative
- As a Security/Compliance Lead, I need a signed scope statement clarifying that the MVP is out of PCI scope so that we avoid unintended compliance obligations and have a documented baseline for audits.
- As an Engineering Lead, I need explicit boundaries and guardrails to ensure no code paths capture or log CHD.
- As a Product Owner, I need a clear declaration that the MVP does not include payment acceptance to align expectations.

Acceptance criteria
- A PCI scope statement exists at openspec/compliance/pci-scope-statement.md with:
  - Document metadata: title, version, owner, last/next review dates, approvers, story reference (US-007).
  - Definitions for CHD and SAD aligned to PCI DSS v4.0.
  - Explicit negative assertions: MVP does not store, process, or transmit CHD/SAD; no PAN, CVV/CVC/CID, PIN data, or track data in any system components; no payment forms/SDKs/iframes; no logs/traces contain CHD.
  - Architectural boundary: clear description that all MVP endpoints are unrelated to payment capture and do not proxy payment data.
  - Data flow diagram file (Mermaid or similar) showing end-user browsers do not send CHD to the MVP and, if applicable, payment flows bypass the MVP entirely to a PSP.
  - Evidence references (if applicable): PSP attestation/AOC or statement of responsibility; otherwise, statement that MVP has no payment capability.
  - Reassessment gate language: any payment-related feature requires PCI impact assessment before merge.
- README.md updated to reference the new compliance document.
- Repository-wide search performed and noted in the statement confirming no payment SDKs or PAN-like patterns exist.
- Approval captured via PR from Security/Compliance Lead and Product Owner.

Out of scope
- Implementing payment functionality, tokenization, or vaulting.
- Broader compliance frameworks (e.g., SOC 2, HIPAA) beyond PCI scoping language.
- Code changes to logging beyond confirming current configuration does not capture CHD (MVP has no payment capture).

Cross-service dependencies
- None for MVP features. If a PSP is later adopted, only PSP-hosted pages or redirects are allowed; no CHD passes through the API Gateway.
- Organizational dependencies: Security/Compliance Lead, Engineering Lead, Product Owner for approvals.

Constraints and assumptions
- Current API Gateway exposes health, auth (JWT issuance), and test endpoints; no payment endpoints exist.
- Logging via Serilog captures operational data only; request bodies with CHD do not exist because the MVP includes no payment inputs.
- No third-party payment SDKs or libraries are included in the repository.