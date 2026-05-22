US-008: Redirect URI Whitelist Enforcement & HTTP Callback Rejection

What
- Implement server-side enforcement to:
  1) Validate redirect_uri against a pre-configured server-side whitelist during:
     - Authorization request construction endpoint (applies to US-002).
     - SSO callback handling endpoint.
  2) Reject any callback request received over HTTP (non-HTTPS).
- On rejection, emit structured audit logs and return i18n-ready error responses (stable error code + message key + human message).
- Provide configuration to define the whitelist entries and how reverse-proxy forwarded headers are trusted.

Why
- Prevent open redirect attacks and untrusted callback abuse.
- Enforce transport security for authentication flows.
- Provide auditable events for security monitoring and compliance.

Scope and narrative
- Actors: 
  - Client application initiating SSO.
  - API Gateway (this repo) constructing authorization request and handling callbacks.
  - External IdP (not implemented here; simulated).
- Flows:
  - Authorization request construction (GET /api/auth/authorize):
    - Input: redirect_uri (query), state, response_type (optional for simulation).
    - Behavior: Validate redirect_uri against whitelist. If valid, return the constructed authorization URL (simulation) or 302 to IdP in future. If not valid, return 400 with error code and message key; log audit event.
  - Callback handling (GET /api/auth/callback):
    - Input: code, state, redirect_uri (optional depending on IdP; validated if present).
    - Behavior:
      - Verify request is HTTPS. If behind reverse proxy, accept X-Forwarded-Proto=https when TrustForwardedHeaders is enabled.
      - If insecure, reject with 400, emit audit log.
      - If redirect_uri provided, validate against whitelist; if invalid, reject with 400 and log audit.
      - Otherwise, simulate success response (actual token exchange is out-of-scope).

Functional acceptance criteria
- Whitelist configuration:
  - Maintained server-side via configuration key Security:RedirectUriWhitelist (array of URIs).
  - Whitelist comparison:
    - Normalize candidate and whitelist URIs.
    - Compare scheme (case-insensitive), host (case-insensitive), port (explicit or implicit), and path (normalize trailing slash).
    - Query string is ignored for whitelist matching.
  - If parsing of redirect_uri fails, treat as invalid and reject.
- HTTPS-only callback:
  - A callback request must be considered secure if:
    - HttpContext.Request.IsHttps == true OR
    - X-Forwarded-Proto == "https" AND Security: