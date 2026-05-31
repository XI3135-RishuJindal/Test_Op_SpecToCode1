```markdown
# API Gateway Service Specification

## Purpose
This document outlines the requirements for the API Gateway Service to ensure secure, comprehensive API routing, authentication, and management functionalities.

### Requirements
- The system SHALL authenticate every inbound request using JWT/OAuth 2.0.
- The system SHALL authenticate, authorize, and proxy requests to domain services.
- The system SHALL expose health and readiness probe endpoints.

#### Scenario: Request Routing
**Given** a client request with a valid JWT token,  
**When** the request is received at the gateway,  
**Then** the gateway SHALL route the request to the appropriate backend service.

#### Scenario: JWT Authorization
**Given** an inbound client request,  
**When** authentication is verified,  
**Then** the gateway SHALL enforce RBAC policies to determine access.

## Technologies and Runtime
- Node.js (TypeScript)
- NGINX and Redis

## Connectivity and Dependencies
- Connects to Redis for rate limiting.
- Depends on Vault for retrieving JWT keys.

## APIs and Endpoints
- Implements REST endpoints as detailed in `<ApiSpec>`.
- WebSocket endpoints for real-time notifications.

## Key Flows and Data Models
- Detailed API interaction scenarios for authentication flows.
- Route definition and policy management via administrative APIs.

## TODO
- Specific data models used in routing and JWT validation need further clarification from context.
```