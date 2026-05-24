## Functional Specification

**User Story: US-004**

### Title
Auth Code Exchange at IdP Token Endpoint

### Description
This feature implements the server-side authorisation code exchange flow. After receiving a valid callback with an authorization code and state (as ensured by user story US-003), the backend system must securely POST this code to the Identity Provider's (IdP) token endpoint. The request shall include the authorization code, client credentials obtained from configuration, the redirect URI used in the initial authorization request, and the PKCE `code_verifier`. A successful response will return access, ID, and optionally refresh tokens, which then undergo validation as part of US-005.

### Acceptance Criteria
- The backend exchanges the authorization code for tokens using the IdP token endpoint.
- Tokens are delivered securely and not logged or exposed in the URL.
- The flow uses HTTPS for all exchanges.
- Integration testing validates the entire exchange flow and error handling.
- Code changes do not degrade system performance or increase latency beyond predefined thresholds.

### Out of Scope
- Front-end handling of authorization flow prior to receipt of the authorization code.
- UI changes related to displaying received tokens.
- Alternative flows for non-compliant client requests.

### Dependencies
- This implementation depends on the integration setup created in user story US-003 for obtaining the authorization code.
- Validation processes detailed in US-005 depend on this implementation for input tokens.