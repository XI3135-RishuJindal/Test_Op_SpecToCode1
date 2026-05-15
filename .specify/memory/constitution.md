Title: Compliance-first engineering constitution for US-007 — Draft PCI scope statement

Purpose
- Establish guardrails ensuring the MVP is definitively out of PCI DSS scope by prohibiting any storage, processing, or transmission of Cardholder Data (CHD) or Sensitive Authentication Data (SAD).
- Define documentation standards, review gates, and stakeholder expectations for compliance artifacts added to the repository.

Quality principles
- Compliance by design: Architectural and process decisions must default to zero-CHD handling. Any future payment capability must be designed as PSP-redirect or tokenized flows and trigger a re-scope assessment.
- Least data/least functionality: Do not collect, accept, proxy, or log financial data. APIs must avoid parameters that suggest CHD (e.g., cardNumber, pan, cvc, cvv, expiry).
- Explicit scoping: Document scope boundaries, in-scope components, and out-of-scope items. Maintain a change log and next-review date.
- Auditability: Compliance documents in-repo with versioning, owner, approvers, effective date. Evidence references (code searches, config, endpoints inventory).
- Secure by default: TLS 1.2+ enforced, authentication on modification endpoints, structured logging with sensitive-data redaction policies.
- Observability without leakage: Logs must not include request bodies or fields that could contain CHD. If message bodies must be logged for debugging in dev, mask/disable in prod.

Coding and documentation standards
- No CHD/SAD data structures: Do not add model properties named or semantically equivalent to cardNumber, pan, primaryAccountNumber, expiry, expMonth, expYear, cvv, cvc, track1, track2, pin, pinBlock.
- Request/response contracts: Public APIs must not include CHD-like fields. Any addition of “payment” or “billing” fields requires Security/Compliance review prior to merge.
- Logging: Never log secrets or user-supplied identifiers that could be CHD. Prefer metadata (requestId, status) over payload content.
- Configuration: No keys/secrets in repo; use secret stores. Ensure no config references to payment endpoints in MVP.
- Documentation artifacts: Place PCI docs under docs/compliance/pci/*.md with front-matter (Title, Version, Owner, Approvers, Effective Date, Next Review), and sections: Executive Summary, Scope Boundaries, Systems Inventory, Data Flows, Evidence, Governance.

Architecture guardrails
- No payment processing path: API Gateway must not initiate, proxy, or terminate payment sessions; no forwarding of CHD.
- Future payments pattern (if ever needed): Use hosted payment page or client-side tokenization by PSP; backend only handles opaque tokens, never PAN. Any change → mandatory PCI re-scope.
- Network/data flow: No connections to payment processors in MVP; ensure DFD depicts zero CHD ingress/egress.
- Dependency hygiene: Third-party libraries must not introduce telemetry that can capture payloads containing CHD.

Non-functional requirements (NFRs)
- Security: TLS 1.2+; authenticated/authorized endpoints; no sensitive data at rest/in transit; default-deny for CHD flows.
- Reliability: Logging and error handling must not echo request bodies.
- Compliance documentation: Published scope statement with approvals, stored in repo; revalidated each release or scope change.
- Monitoring: Alerts if new routes with “payment/checkout/card” detected (lint/check as a CI safeguard when introduced in future).

Review standards and stakeholder expectations
- Stakeholders: Product Owner, Engineering Lead, Security/Compliance Lead (approver), DevOps Lead.
- Acceptance requires: completed PCI scope statement in repo, evidence of codebase search for CHD indicators, approvals recorded, README link added, next review date set.
- Change management: Any PR adding payment-adjacent terminology requires Compliance review. Create a follow-up issue to define the re-scope trigger checklist.