# PCI Scope Statement — API Gateway MVP (Out of PCI Scope)
Reference: US-007 — Draft PCI scope statement

Metadata
- Title: PCI Scope Statement — API Gateway MVP
- Version: 1.0.0
- Owner: Security/Compliance Lead
- Repository: XI3135-RishuJindal/Test_Op_SpecToCode1
- Last Review Date: 2026-05-15
- Next Review Date: 2026-11-15
- Approvers: Security/Compliance Lead (GitHub PR approval), Product Owner (GitHub PR approval)
- Engineering Reviewer: Engineering Lead
- Effective Date: 2026-05-15

Decision summary
- The MVP API Gateway is out of PCI DSS scope. The system does not store, process, or transmit Cardholder Data (CHD) or Sensitive Authentication Data (SAD).
- No payment functionality is included in the MVP. No payment forms, SDKs, or iframes exist in the repository. No system components handle Primary Account Number (PAN) or any SAD.

Definitions (aligned to PCI DSS v4.0)
- Cardholder Data (CHD): At minimum, PAN. May also include cardholder name, expiration date, and service code. Protection requirements apply whenever PAN is stored, processed, or transmitted, alone or in combination with other elements.
- Sensitive Authentication Data (SAD): Full track data (track 1/track 2), card verification codes/values (e.g., CVV2/CVC2/CID), and PIN/PIN block. SAD must never be stored post-authorization.
- Primary Account Number (PAN): Unique payment card number that identifies the issuer and the individual account.

Negative assertions for MVP
- No CHD/SAD handling
  - The MVP does not store, process, or transmit PAN or any CHD/SAD.
  - No full track data, CVV/CVC/CID, PIN, or PIN block is accepted, processed, logged, or stored.
- No payment user interfaces or SDKs
  - No payment collection forms, iframes, hosted fields, or payment SDKs are present.
  - No JavaScript or mobile payment libraries (e.g., Stripe, Adyen, Braintree, PayPal, Square) are included.
- No payment proxying
  - The API Gateway does not proxy, relay, or transform payment or PAN-bearing requests to any upstream.
- No logs or telemetry with CHD/SAD
  - Serilog is configured for operational logging only (console and file). There are no inputs for CHD/SAD, and controllers do not capture fields that could be CHD/SAD. Therefore, logs, traces, and metrics cannot contain CHD/SAD.

System and architectural boundary
- In scope for this statement (MVP boundary):
  - API Gateway (.NET 8) with endpoints:
    - GET /api/health — liveness/readiness.
    - POST /api/auth/token — demo JWT issuance; accepts username/password only.
    - POST /api/test — demo/test endpoint for non-payment payloads (message, optional medication DTO, additional data).
  - Logging: Serilog writes to console and rolling files (logs/apigateway-*.txt).
- Explicitly out of scope (not present in MVP):
  - Any payment acceptance components (web pages, mobile views, SDKs, webhooks handling payment details).
  - Any data stores, message buses, or caches that would store or route CHD/SAD.
- Boundary statement:
  - All MVP endpoints are unrelated to payment capture and do not proxy or relay payment data. The system has no payment capability and no technical path through which CHD/SAD could traverse the API Gateway.

Data flows
- End-user browsers or clients interact with the API Gateway only for non-payment activities (health checks, authentication token request with username/password for demo, and test operations).
- No CHD/SAD is ever submitted to or through the API Gateway.
- Future payment flows, if adopted, must use PSP-hosted payment pages or redirects that bypass the API Gateway entirely. No PAN, CVV, or track data is to be sent to the API Gateway.

Diagram
- The following Mermaid diagram depicts the data flows and the architectural boundary for the MVP. A future, optional payment path to a PSP is illustrated as a dashed line to emphasize that it bypasses the API Gateway and does not exist in the MVP.

```mermaid
flowchart TD
  subgraph MVP_Boundary[API Gateway MVP Boundary]
    APIGW[API Gateway (.NET 8)]
    LOGS[(Serilog Logs: Console/File)]
    APIGW --> LOGS
  end

  USER[End-user Browser/Client] -->|Non-payment requests (health, auth token, test)| APIGW

  %% No CHD/SAD through API Gateway
  note1{{"No CHD/SAD accepted or processed"}}
  APIGW --- note1

  %% Future-only PSP path (bypasses API Gateway)
  USER -.->|Payment details (PAN, CVV) - future only| PSP[Payment Service Provider (Hosted Payment Page/Redirect)]
  PSP -.->|Non-CHD token/receipt to merchant systems - future only| MERCH[Merchant Systems (outside MVP)]

  classDef future stroke-dasharray: 5 5;
  class USER,PSP,MERCH future;
```

- Diagram source: openspec/compliance/pci-dataflow.mmd

Repository-wide verification (performed 2026-05-15 UTC)
- Tools/commands executed from repository root:
  - PAN-like patterns (13–19 contiguous digits, excluding build artifacts)
    - Command: rg -nEI --hidden --glob '!.git/' --glob '!bin/' --glob '!obj/' '\b[0-9]{13,19}\b' .
    - Result: 0 suspicious matches.
  - Payment/CHD/SAD keywords
    - Command: rg -nEI --hidden --glob '!.git/' --glob '!bin/' --glob '!obj/' '(card|pan|cvv|cvc|csc|cid|track1|track2|magstripe|pin(?!g)|payment|stripe|braintree|adyen|paypal|square|checkout|merchant|acquirer)' .
    - Result: 0 matches.
  - Package/library verification
    - Reviewed project files (ApiGateway.csproj, Tests/ApiGateway.Tests.csproj): no payment SDKs or libraries present.
- Outcome:
  - No payment SDKs/libraries detected.
  - No PAN-like sequences detected.
  - No references to CHD/SAD or payment processing detected.

Evidence and responsibilities
- MVP evidence: No payment capability included in MVP; therefore, there is no PSP, AOC