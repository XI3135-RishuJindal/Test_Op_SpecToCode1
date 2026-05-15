US-007: Draft PCI scope statement

What
- Produce an auditable PCI DSS v4.0 scope statement for the MVP in this repository (ApiGateway).
- The statement must clearly assert that the MVP does not store, process, or transmit Cardholder Data (CHD) or Sensitive Authentication Data (SAD).
- Provide explicit scoping boundaries, in-scope and out-of-scope components, justifications, and “N/A” mapping for PCI DSS requirements directly tied to CHD storage/processing/transmission.
- Include a simple boundary diagram and evidence references to code review.

Why
- To document PCI scope early and avoid unintended expansion of the PCI footprint.
- To support audit readiness and ensure stakeholder alignment on constraints around payment-related features.
- To set guardrails for future features so that any payment capability is implemented through a segmented third-party provider and triggers a new scope review.

Context summary from repository review
- Endpoints: /api/health (status only), /api/auth/token (username/password for demo JWT), /api/test (message and optional MedicationDTO). None reference CHD or payment fields.
- Data models: MedicationDTO and TestRequest/Response contain no CHD fields. TestRequest.AdditionalData could accept arbitrary input; documentation must prohibit sending CHD.
- Logging: Serilog to console and file. No code logs payment details; statement must emphasize prohibition on logging CHD and note that no CHD should be sent.
- No payment SDKs or third-party payment integrations present.

Acceptance criteria
- A repository document exists at docs/compliance/pci/scope-statement.md containing:
  - Purpose, scope, definitions (CHD, SAD, CDE), system overview of ApiGateway.
  - Boundary statement: ApiGateway is outside the CDE; no CHD/SAD stored, processed, or transmitted by MVP.
  - Explicit in-scope list (ApiGateway service, its logs) with “reason: outside CDE, general security practices still apply.”
  - Explicit out-of-scope list (CDE, payment processors, payment UIs/SDKs, tokenization, storage of PAN, SAD).
  - N/A mapping: PCI DSS v4.0 sections for CHD storage/processing/transmission (e.g., Req. 3.x for storage, portions of Req. 4.x for transmission of CHD) marked N/A with justification.
  - Data flow diagram (saved as docs/diagrams/pci-scope-boundary.png) showing no CHD flows.
  - Risks and mitigations: warn against sending CHD to any endpoint, call out AdditionalData as free-form and prohibited for CHD.
  - Approval block with named approvers and dates (Security, Product; Legal optional).
  - Versioning metadata and links to this spec and PR.
- README updated with a short “Compliance” section linking to the scope statement.
- Evidence of code review supporting assertions is included in the scope statement (paths, notes).
- Stakeholder sign-offs recorded in the PR or in the document metadata.

Out of scope
- Implementing payment features, tokenization, or PAN/SAD handling.
- Adding runtime CHD pattern detection or WAF rules (may be follow-up items).
- Changes to application authentication or authorization unrelated to PCI scope.

Dependencies and cross-service considerations
- None for MVP. If/when a payment provider is introduced (e.g., Stripe, Adyen), the provider and any payment UI/SDKs would be in-scope for a new review; the ApiGateway must remain segmented from the CDE or only handle non-sensitive tokens.

Non-functional requirements
- Discoverable in repository; written in clear language; ready for audit; approved by stakeholders; version-controlled.

Deliverables
- docs/compliance/pci/scope-statement.md
- docs/diagrams/pci-scope-boundary.png (plus editable source docs/diagrams/pci-scope-boundary.drawio)
- README Compliance section update
- PR with Security and Product approvals