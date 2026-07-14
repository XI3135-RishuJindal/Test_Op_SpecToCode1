## S-004

### Purpose
This specification defines the integration of OTP with the authentication system via the API Gateway Service to enable multi-factor authentication for enhanced security.

### Scope
The specification covers the generation of OTPs and their validation during user login processes within the API Gateway Service.

### Non-Goals
1. Designing backend storage for OTPs
2. Implementing specific OTP delivery mechanisms
3. Modifying user interface design
4. Authenticating users without OTP
5. Customizing OTP length or expiry time

### Key Entities
- **User**
  - Attributes: username (String), password (String)
- **OTP**
  - Attributes: code (String), expiry_time (Datetime)
- **Authentication Request**
  - Attributes: username (String), password (String), otp_code (String)

### Functional Requirements
- FR-001: The system SHALL generate an OTP upon user request on the login page.
- FR-002: The system MUST validate the username and password before proceeding to OTP generation.
- FR-003: The system SHALL send the generated OTP to the user via a defined mechanism (SMS, email) [NEEDS CLARIFICATION: What delivery methods are supported?].
- FR-004: The system MUST allow login only if a valid OTP is provided after username and password verification.
- FR-005: The system SHOULD invalidate an OTP after successful login or expiration of its time limit.

### Assumptions Propagation
- A-001: OTP delivery mechanism is assumed to be predetermined without affecting this specification.

### Success Criteria
- SC-001: Login attempts via OTP integration should be successful at least 99% of the time.
- SC-002: OTP delivery to users should complete in less than 5 seconds in 95% of calls.
- SC-003: Incorrect OTPs must prevent login in at least 99% of cases.

### Priority Levels
- P1: Core user goal (login with OTP validation)
- P2: Error handling and validation (invalid OTP, expired OTP)
- P3: None

### Edge Cases
- EC-001: Given a valid username and password, When the OTP is expired, Then login must not be allowed, and the user should receive an expiry notification.
- EC-002: Given a user requests multiple OTPs, When a non-latest OTP is used, Then login must not be allowed.
- EC-003: Given a request for OTP, When the user does not receive the OTP, Then a resend option should be included for a limited number of times.

### Independent Testability
- Preconditions: User accesses login page, enters valid credentials, requests an OTP.
- User Action: Enter the received OTP.
- Observable Outcome: User successfully logs into the system if the OTP matches.

### Separation of Concerns
This specification focuses on the integration of OTP for authentication through the API Gateway Service and does not specify internal implementation details such as HTTP operations, database schema, or communication protocols with external services. Integration with an external authentication system should be considered at a logical level.

---

## S-002

### Purpose

This specification defines the multi-factor authentication integration using OTP to enhance login security and comply with the outlined user story requirements.

### Scope

The specification addresses integration of One-Time Password (OTP) generation and validation in the Multi-factor Authentication Service to support the authentication process.

### Non-Goals

1. Implementation of OTP delivery mechanisms.
2. UI design for OTP input.
3. Password validation processes.
4. Handling OTP generation delay.
5. Comprehensive account security beyond MFA.
6. Integration with third-party authentication systems.
7. Logging and monitoring design.
8. Fraud detection algorithms.
9. Extensive user account management.
10. Non-OTP-based MFA implementations.

### Key Entities

- **User**:  
  - **Attributes**: userID (string), username (string), password (string), email (string), phone number (string)
  - **Relationships**: N/A

- **OTP**:  
  - **Attributes**: otpCode (string), userID (string), expirationTime (datetime)
  - **Relationships**: Related to User (1:1)

### Functional Requirements

- **FR-001**: The Multi-factor Authentication Service MUST generate an OTP upon user request during login.
- **FR-002**: The Multi-factor Authentication Service MUST validate an OTP once entered by the user.
- **FR-003**: The Multi-factor Authentication Service SHOULD notify users of OTP success or failure.
- **FR-004**: The Multi-factor Authentication Service MUST reject expired OTPs.
- **FR-005**: The Multi-factor Authentication Service MUST reject OTPs associated with incorrect users.

### Assumptions

- **A-001**: OTPs are generated only during login (relevant to FR-001, FR-002).
- **A-002**: OTPs are delivered via SMS or Email (relevant to FR-003).
- **A-003**: Expiry of OTP is 5 minutes (relevant to FR-004).

### Success Criteria

- **SC-001**: OTP generation time less than 2 seconds.
- **SC-002**: OTP validation greater than 95% successful within expiry time.
- **SC-003**: User login success rate at least 90% among authentic users.

### Priority Levels

- P1: FR-001, FR-002, FR-004
- P2: FR-003, FR-005
- P3: None

### Edge Cases

- **EC-001**: Given an OTP is requested multiple times, When a user enters an older OTP, Then the system should reject it as expired.
- **EC-002**: Given a user enters an incorrect OTP thrice consecutively, When the third attempt fails, Then the system should temporarily suspend OTP requests for 5 minutes.
- **EC-003**: Given an incorrect userID, When an OTP is entered, Then the system validates it against the associated user and rejects if mismatched.

### Independent Testability

For validating OTP integration:
1. Prerequisites: User exists, correct username/password entered
2. Action: Request and enter OTP
3. Outcome: Successful login with a valid OTP

### Separation of Concerns

This specification captures behavior expectation levels via abilities and user outcomes while adhering rigorously to business rules and constraints. External system references use logical identifiers without technical implementation leakage.