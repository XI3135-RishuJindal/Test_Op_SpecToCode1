### Functional Specification

#### User Story Narrative
The focus of this story is to enhance the security and reliability of the SSO post-authentication process. This involves implementing strategic checks on IdP claims such as `sub`, `email`, `name`, and `roles`. These claims are crucial for determining the validity of a user's identity and access rights. Access is to be denied and an appropriate error message returned when any required claim is missing or invalid. The system also needs to log these failures for auditing purposes without altering account data.

#### Acceptance Criteria
1. Validate that all required IdP claims are present upon authentication.
2. Deny access if any claim is missing or invalid.
3. Return a standardized error message.
4. Log each instance of validation failure in a structured format.
5. Ensure no account creation or modification on failure.

#### Out-of-Scope Items
- Modification of the authentication mechanism itself.
- Integration with new logging services.
- Changes to non-authentication-related controllers.

#### Cross-Service Dependencies
- Requires interaction with existing authentication and logging services.