Title: PCI DSS v4.0 Scope Statement – ApiGateway (MVP)
Version: 1.0.0
Status: Draft – pending Security and Product approval via PR
Document Owner: Engineering (ApiGateway maintainers)
Last Updated: 2026-05-15
Related Work: US-007 (Draft PCI scope statement)
Repository: XI3135-RishuJindal/Test_Op_SpecToCode1
PR Link: To be provided in merge request

1) Purpose
This document defines the PCI DSS v4.0 scope for the ApiGateway MVP in this repository. It establishes the boundary that the ApiGateway does not store, process, or transmit Cardholder Data (CHD) or Sensitive Authentication Data (SAD), and is therefore outside the Cardholder Data Environment (CDE). It provides supporting evidence, a boundary diagram, requirement applicability mapping, and risks/mitigations to guide audit readiness and future change control.

2) Definitions (PCI DSS v4.0 terminology)
- Cardholder Data (CHD): Primary Account Number (PAN) alone or with any of the following: cardholder name, expiration date, service code.
- Sensitive Authentication Data (SAD): Full track data (magnetic-stripe or equivalent on a chip), CAV2/CVC2/CVV2/CID, and PIN/PIN block. SAD must never be stored after authorization.
- Cardholder Data Environment (CDE): People, processes, and technologies that store, process, or transmit CHD or SAD, or could impact the security of the CDE.
- System Component: Any network device, server, computing device, or application within or connected to the CDE.

3) System Overview – ApiGateway (MVP)
- Purpose: Simple API gateway service for demo/testing purposes.
- Technology: .NET 8 Web API, Serilog for logging, JWT-based demo authentication.
- Endpoints
  - POST /api/auth/token – Generates a demo JWT using username/password (no payment or CHD fields).
  - GET /api/health – Liveness/status (no request body, no payment or CHD fields).
  - POST /api/test – Accepts TestRequest with Message, optional MedicationDTO, and AdditionalData (free-form). No payment or CHD fields defined; documentation explicitly prohibits CHD in AdditionalData or any field.
- Data Models (no CHD/SAD fields)
  - Models/MedicationDTO.cs – Medication attributes only.
  - Models/TestRequest.cs – Message, Medication (MedicationDTO), AdditionalData (Dictionary<string, object>).
  - Models/TestResponse.cs, Models/ErrorResponse.cs – No CHD/SAD.