## S-002

### Purpose

The purpose of this specification is to define the functionalities and requirements for generating recovery codes in the Multi-factor Authentication Service (S-002) to ensure authenticated users can regain access to their accounts when locked out.

### Scope

This specification covers the generation, presentation, and usage validation of recovery codes within the Multi-factor Authentication Service. It focuses on user interactions and business rules related to recovery code security and usage.

### Non-Goals

1. Design of user interfaces.
2. Development of underlying algorithms for code generation.
3. Integration with external identity providers.
4. Password reset functionalities.
5. Managing expired recovery codes.
6. Handling of user identification or authentication.
7. Storage and encryption of recovery codes.
8. Notification mechanisms post-generation.
9. User registration processes.
10. Logout and session management functionalities.

### Key Entities

- **RecoveryCode**: Contains attributes such as `code (string)`, `user_id (string)`, and `used (boolean)`.
- **User**: Related to RecoveryCode with a one-to-many relationship, containing `user_id (string)`, `authenticated (boolean)`.

### Functional Requirements

- FR-001: Multi-factor Authentication Service SHALL generate a set of unique recovery codes upon a user's request.
- FR-002: Multi-factor Authentication Service MUST display newly generated recovery codes immediately to the authenticated user.
- FR-003: Multi-factor Authentication Service SHALL verify that recovery codes have not been used previously before allowing their use.
- FR-004: Multi-factor Authentication Service SHALL mark a recovery code as used after it has been successfully redeemed.
- FR-005: Multi-factor Authentication Service MUST prevent the use of the same recovery code more than once.

### Assumptions Propagation

- A-001: Assumes that the user is authenticated prior to making the request. (FR-001, FR-002)
- A-002: Assumes that recovery codes are stored safely and securely in the service. (FR-003, FR-004)

### Success Criteria

- SC-001: Number of recovery codes generated per request equals 6.
- SC-002: Visibility time of recovery codes must be greater than or equal to 20 seconds.
- SC-003: Percentage of reuse attempts for already used codes must be less than 1%.

### Priority Levels

- P1: FR-001, FR-002
- P2: FR-003, FR-004, FR-005

### Edge Cases

- EC-001: Given the user requests recovery codes, When the user has already requested them recently, Then a warning SHOULD be displayed to avoid multiple redundant requests.
- EC-002: Given a recovery code is marked but not used due to a transaction failure, When retried, Then it MUST be available for another attempt.
- EC-003: Given multiple recovery codes generated, When an older request is made before a newer one is used, Then the codes MUST remain valid until used or expired.

### Independent Testability

Preconditions: The user is authenticated and requests recovery codes.  
User Action: The user attempts to use a recovery code.  
Observable Outcome: The code is either successfully redeemed or rejected if previously used.