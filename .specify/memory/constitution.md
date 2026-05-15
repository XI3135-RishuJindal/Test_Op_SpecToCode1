Title: Compliance documentation quality principles for US-007 — Draft PCI scope statement

Purpose
- Establish review standards, stakeholder expectations, and guardrails for creating and maintaining the PCI scope statement that declares no Cardholder Data (CHD) is stored, processed, or transmitted by the MVP.

Standards and guardrails
- Authoritative references: Align language and definitions with PCI DSS v4.0 (use the official terms CHD, SAD, PAN, CVV/CVC/CID, track data, PIN/PIN block).
- Scope clarity: The statement must explicitly declare the MVP’s systems are out of PCI scope because they do not store, process, or transmit CHD/SAD and must describe compensating boundaries (use of a third-party PSP-hosted payment page or no payment capability at all).
- Negative assertions: Explicitly state what is not present (no PAN, no SAD, no tokens that can be reversed to PAN, no payment forms, no payment SDKs, no iframe capturing PAN).
- Data flow depiction: Include a simple data-flow diagram showing that users never submit CHD to the MVP. If a PSP exists, show the browser-to-PSP path bypassing MVP backends.
- Logging and telemetry: Affirm no logs, traces, metrics, or error payloads can contain CHD. Commit to redaction patterns and verify no fields resemble PAN or SAD.
- Evidence: Reference or link to PSP AOC/Attestation or contractual statement of responsibility (if applicable). If no PSP is used by MVP, explicitly state “no payment capability included in MVP.”
- Change control: Any future introduction of payment capability requires a new PCI impact assessment before merge; add a “reassessment gate” guideline in the repository.
- Versioning and approvals: Include document metadata (version, owner, last review date, next review date, approvers). Changes require Security and Product Owner approvals via PR.
- Repository placement: Store the statement under openspec/compliance/ with diagram sources (e.g., .mmd Mermaid or .drawio). Keep binary exports alongside source or in artifacts.
- Traceability: Reference this story ID (US-007) in the document header for audit traceability.

Review expectations
- Security/Compliance Lead: Verifies accuracy of PCI terminology, negative assertions, boundaries, and evidence references.
- Engineering Lead: Confirms the implementation matches the statement (no payment code paths, no SDKs, no CHD-like fields).
- Product Owner: Confirms business scope matches MVP (no payment acceptance).
- Legal/Privacy (optional): Verifies clarity of shared responsibility with PSP or absence of payment handling.
- Documentation quality: Clear, concise, single page if possible; include DFD; link to evidence; accessible via README.

Non-functional requirements for documentation
- Discoverability: README lists the compliance document and diagram.
- Maintainability: Next review date within 6–12 months or prior to any payment-related feature work.
- Auditability: Approvals recorded in PR; diagram/source included and versioned.

Risk controls
- Repository search and CI check to ensure no PAN-like patterns or payment SDKs are introduced without review.
- Logging policy confirmation: ensure app logging settings do not capture request bodies containing payment fields (not applicable now, but guardrail noted).