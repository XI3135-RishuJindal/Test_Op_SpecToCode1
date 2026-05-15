US-007: Draft PCI scope statement

Summary (WHAT)
- Produce a formal PCI scope statement for the MVP that asserts and evidences: no Cardholder Data (CHD) or Sensitive Authentication Data (SAD) is stored, processed, or transmitted by the system.
- Publish the statement in-repo at docs/compliance/pci/scope-statement.md, including scope boundaries, systems/components in scope, explicit out-of-scope declarations, and review governance.
- Provide evidence that the current API Gateway codebase contains no CHD handling and that logs/configs do not indicate payment functionality.

Why
- Establishes a clear compliance position that the MVP is out of PCI DSS scope, reducing audit burden and risk.
- Creates developer guardrails to prevent accidental CHD ingestion via models, endpoints, or logs.
- Prepares the organization for efficient future PCI scoping if/when payment features are introduced.

Narrative
- As a Compliance Lead, I need a signed scope statement documenting that the MVP handles no CHD/SAD, so that we can confidently treat the MVP as out of scope for PCI DSS and set governance for any future changes that might affect scope.

Target artifact and required content
- Path: docs/compliance/pci/scope-statement.md
- Required sections:
  1) Executive summary: MVP does not store, process, or transmit CHD/SAD.
  2) Definitions: CHD (e.g., PAN) and SAD (e.g., full track data, CAV2/CVC2/CVV2/CID, PIN/PIN block).
  3) Current architecture and data flows: API Gateway with authentication and test endpoints; no payment endpoints or PSP integrations.
  4) Scope boundaries: In-scope components for review (this repo’s API Gateway) and explicitly out-of-scope payment functions.
  5) Evidence: codebase search results for CHD indicators, endpoint inventory, logging configuration review, third-party dependency review summary.
  6) Dependencies and interfaces: No payment gateways/PSPs; JWT auth only.
  7) Controls/guardrails: Prohibit CHD fields in APIs/models; logging redaction policy; change control and re-scope triggers.
  8) Governance: Owner, approvers, effective date, next review, change log.
  9) Future considerations: If payments are added, use PSP-hosted or tokenized flows and perform full PCI re-scope.

Acceptance criteria
- A1: docs/compliance/pci/scope-statement.md exists in the repo with all required sections and governance metadata (Owner, Approvers, Effective Date, Next Review).
- A2: The statement unambiguously asserts “No CHD/SAD is stored, processed, or transmitted by the MVP” and lists API Gateway endpoints currently present, confirming none handle payments.
- A3: Evidence section includes:
  - Code search summary for terms/patterns (cardNumber, pan, cvv, cvc, expiry, track1, track2, pin, payment, checkout) with a finding of “none relevant to CHD.”
  - Logging/config review summary confirming no request body logging in production and no payment configurations.
  - Third-party library review (high level) confirming no payment SDKs or telemetry that captures payloads.
- A4: README.md contains a “Compliance