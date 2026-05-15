Delivery approach
- Author the PCI scope statement using a standardized template under openspec/compliance/pci-scope-statement.md. Include a concise description of the boundary and a negative assertion that the MVP does not store, process, or transmit CHD/SAD.
- Create a simple data-flow diagram (Mermaid .mmd) under openspec/compliance/pci-dataflow.mmd to visualize that CHD never reaches the MVP. If a PSP is envisioned for future phases, show a browser-to-PSP flow that bypasses the API Gateway.
- Perform evidence collection and verification: grep the repository for PAN-like patterns (e.g., 13–19 digit sequences) and keywords (card, pan, cvv, cvc, track1, track2), confirm absence of payment SDKs, and note the outcome in the statement.
- Update README.md to reference the compliance document so it is discoverable.
- Route a PR for approvals by Security/Compliance Lead and Product Owner. Capture approvals in the PR thread for auditability and set the next review date.

Stakeholders
- Security/Compliance Lead: primary reviewer and approver.
- Engineering Lead: technical verifier that no payment code paths/logging exist.
- Product Owner: scope confirmation and approver.
- Legal/Privacy (optional): consult if PSP responsibilities are to be referenced.

Tools and systems
- GitHub for authoring, code review, and approvals.
- Mermaid (or draw.io) for diagramming.
- Optional: Confluence mirror link if the organization maintains external compliance documentation; the repo remains the system of record.

Operational guardrails
- Add a “PCI reassessment required before payment features” note to the statement. Consider opening a tracking issue for a repository rule or checklist in PR templates to enforce reassessment when adding payment-related code.

Evidence to attach or reference
- If using a PSP later, link to their AOC or responsibility matrix. For MVP with no payment capability, state “No PSP in MVP; no payment capture.”

Deliverables
- pci-scope-statement.md with all acceptance criteria satisfied.
- pci-data