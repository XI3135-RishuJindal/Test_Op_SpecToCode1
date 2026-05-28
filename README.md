# API Gateway

## Overview
The API Gateway project supports role-based access control (RBAC) integrated with Single Sign-On (SSO). This ensures that resources are accessed based on user roles derived from SSO tokens.

## RBAC Implementation Details
Our RBAC system extracts role information from the JWT token provided by the identity provider after successful SSO authentication. These roles are mapped to platform-specific roles such as 'Customer' and 'Administrator'.

### Role Mapping
- **Customer**: Can access basic resources essential for end-users without administrative capabilities.
- **Administrator**: Can access resource management features and administrative actions within the system.

## Setup Instructions
1. **Environment Variables**:
   - Ensure that the following JWT-related environment settings are configured:
     - `Jwt:Key`
     - `Jwt:Issuer`
     - `Jwt:Audience`

2. **Program Setup**:
   - `Program.cs` is configured to verify JWT tokens using the provided key and issuer details.
   - Tokens should have role claims within them for proper RBAC enforcement.

3. **Middleware Configuration**:
   - The authentication middleware is enhanced to intercept and decode JWT tokens to extract role claims.
   - Authorization handlers within the middleware enforce RBAC, allowing or denying access to API endpoints based on roles.

## Testing RBAC
To test the RBAC implementation:
1. Use the AuthController's endpoint to request a JWT token.
2. Ensure the token contains appropriate role claims.
3. Access the protected API endpoints to check if the access control is enforced correctly based on roles.