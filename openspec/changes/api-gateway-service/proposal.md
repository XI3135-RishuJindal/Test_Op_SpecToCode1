```markdown
# Proposal for API Gateway Service

## Purpose and Business Value
The API Gateway Service acts as the centralized entry point for all client requests, providing robust security, consistent routing, and API management features. By enforcing Zero Trust Architecture, it promotes a secure environment for accessing backend services such as User Profile Management, Multi-factor Authentication, Automated Reporting, Payment Processing, and Real-time Notifications.

## In-Scope vs Out-of-Scope
**In-Scope:**
- Routing and proxying client requests to domain services.
- JWT/OAuth 2.0 authentication and RBAC enforcement.
- SSL/TLS termination and API versioning support.
- WebSocket upgrade and proxy handling.

**Out-of-Scope:**
- Identity and Access Management beyond token validation.
- Backend service logic or state management.

## Responsibilities
- Enforce authentication and authorization for all requests.
- Apply RBAC policies and rate limiting.
- Support API versioning and WebSocket connections.

## Impact
- Directly interfaces with backend services including User Profile, MFA, Reporting, Payment, and Notification.
- Utilizes Redis and Vault for state and configuration management.

## Acceptance Criteria
- Successful routing of authenticated requests as defined in the API spec.
- Enforcement of rate limiting and RBAC for secured access.
- Operational metrics and health check endpoints available and properly reporting.
```