To implement the notifications management feature, the following steps will be taken:

1. **Identity Provider Configuration**: Begin by configuring either Okta, Auth0, Azure AD, or Google Identity for the Authorization Code Flow with PKCE or SAML SSO. This requires appropriate registration of the application within the chosen IdP to facilitate secure communication.

2. **Endpoint Implementation**: Develop endpoints within `Controllers/AuthController.cs` to handle callback/assertion. These changes will involve integrating OAuth/SAML protocol support within existing authentication flows.

3. **Claims Mapping**: Extend the `AuthController` to parse tokens/assertions, extract user claims, and map them to existing user attributes in the system.

4. **Security Implementation**: Ensure that state and nonce checks are implemented to prevent replay attacks. Enforce SSL/TLS in project configuration (`Program.cs`, `appsettings.json`) to secure all communications.

5. **Testing and Validation**: Develop and execute tests within the `Tests/Controllers/AuthControllerTests.cs` to ensure successful integration and compliance with security standards.

This plan requires collaboration with security teams to review configuration settings for compliance.