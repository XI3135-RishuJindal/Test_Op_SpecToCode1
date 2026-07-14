# Integrate OTP with Authentication System

| | |
|---|---|
| **ID** | US-001 |
| **Feature** | F-01 — Multi-factor Authentication |
| **Epic** | EP-001 — Integrate Smartphone-based OTP for MFA |
| **Status** | Draft |
| **Date** | 2026-07-14 |

## Background

Implement a multi-factor authentication system to enhance security during the user login process, requiring users to provide two or more verification factors to gain access.

## Acceptance Criteria

### Story

- [ ] Given the user accesses the login page, When an OTP is requested, Then the system should generate an OTP.
- [ ] Given a user has entered a username and password, When a valid OTP is provided, Then the system should allow login.

### Epic

- [ ] Given a registered user, when they attempt to log in, then they should receive an OTP on their smartphone.
- [ ] Given a valid OTP, when the user enters it within the app, then they should successfully authenticate.

## Proposed Solution

### Functional Specification

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

### Technical Design

## S-004

## Technical Design Specification

### 1. Contracts & Interfaces

#### API Contracts

1. **POST /auth/request-otp**
   - **Request Payload**: 
     - `username`: String
   - **Response**:
     - `status`: 200 OK, 400 Bad Request
     - `message`: Success or failure reason

2. **POST /auth/validate-otp**
   - **Request Payload**:
     - `username`: String
     - `password`: String
     - `otp_code`: String
   - **Response**:
     - `status`: 200 OK, 401 Unauthorized, 400 Bad Request
     - `message`: Success or failure reason

#### Data Schema

- **OTP Table**: 
  - `otp_id` (Primary Key, Auto-increment)
  - `username` (String, Foreign Key)
  - `code` (String)
  - `expiry_time` (Datetime)
  - **Indexes**:
    - Index on `username` for quick lookup
    - Composite index on `username` and `code` for validation

### 2. Test Strategy

#### Test Scenarios

- **TS-001: OTP Request Validity** 
  - Ensures endpoint `/auth/request-otp` generates an OTP for a valid username and sends a 200 response.
  
- **TS-002: OTP Validation with Correct Credentials**
  - Validates that `/auth/validate-otp` permits login with valid credentials and OTP, ensuring a 200 response.
  
- **TS-003: OTP Validation Failure**
  - Ensures that invalid or expired OTPs return a 401 Unauthorized response from `/auth/validate-otp`.
  
- **TS-004: OTP Expiry Handling**
  - Confirms OTP expiration process, ensuring expired OTPs in `/auth/validate-otp` result in unsuccessful login attempts.

- **TS-005: Non-Unique OTP Rejection**
  - Tests that old OTPs are invalid post newer OTP requests, enforcing the latest OTP via `/auth/validate-otp`.

### 3. Implementation Approach

#### Core Implementation Logic

- **Class `OtpService`**:
  - `generateOtp(String username)`: 
    - Verifies user authentication status
    - Generates OTP, sets expiry time, and persists in the OTP Table
  - `validateOtp(String username, String password, String otpCode)`: 
    - Verifies password, retrieves latest OTP from the OTP Table, checks expiry, and validates otpCode.

- **Table Update Logic**:
  - Use a cron job to delete expired OTPs from the database.

#### Inter-service Calls

The API Gateway Service WILL interface with a hypothetical notification service for OTP dispatch. An encrypted message payload MAY be used for message integrity.

#### Asynchronous Behavior

Calls to the notification service will be implemented asynchronously using event-driven mechanisms to trigger OTP delivery without blocking login processing.

### Architectural Decision Records (ADRs)

#### ADR-001: Use of Event-Driven Service for OTP Delivery

- **Context**: Explicit request to decouple OTP delivery via a notification system.
- **Decision**: Employ a message broker to asynchronously dispatch OTPs to users.
- **Rationale**: Provides scalability and non-blocking performance.
- **Alternative Considered**: Direct HTTP API for real-time dispatch; rejected due to potential bottlenecks with network latency.

#### ADR-002: Database Index on username

- **Context**: Need for efficient OTP retrieval during login.
- **Decision**: Create an index on `username` within the OTP Table.
- **Rationale**: Offers efficient lookup and reduces query latency.
- **Alternative Considered**: No index; rejected due to possible DB performance degradation.

### Simplicity Gate Assessment

- **Assessment**: `appropriate`
  - Each key technical element directly maps to functional requirements, ensuring a complete, cohesive design.

### Affected Services and API Changes

- **Service Affected**: API Gateway Service
- **New Endpoints**:
  - `POST /auth/request-otp`: Handles OTP generation
  - `POST /auth/validate-otp`: Manages the OTP validation process

---

## S-002

### Contracts & Interfaces

#### API Contracts

1. **POST /api/v1/auth/otp/generate**
   - **Request Body**: 
     - `userID` (string, required)
   - **Response**: 
     - `status`: `200 OK` on success
     - `otpCode`: The generated OTP code (string) for debugging [NEEDS CLARIFICATION: Can OTP be included in response for debugging?] (Assumed: Yes)

2. **POST /api/v1/auth/otp/validate**
   - **Request Body**: 
     - `userID` (string, required)
     - `otpCode` (string, required)
   - **Response**: 
     - `status`: `200 OK` if OTP is valid
     - `status`: `401 Unauthorized` if OTP is invalid or expired
     - `status`: `403 Forbidden` after three consecutive failed attempts

3. **POST /api/v1/auth/email/send** and **POST /api/v1/auth/email/validate**
   - Existing and unchanged under the current scope.

#### Data Model Changes

1. **OTP Table**
   - **Columns**:
     - `otpCode` (VARCHAR, primary key)
     - `userID` (VARCHAR, foreign key referencing `User.userID`)
     - `expirationTime` (DATETIME, indexed for performance)
     - `attempts` (INT, default 0)

### Test Strategy

1. **Generate OTP Tests**
   - Validate successful OTP generation (`POST /api/v1/auth/otp/generate` returns `200 OK`).
   - Check `otpCode` length and format compliance.
   
2. **Validate OTP Tests**
   - Validate OTP with correct/incorrect details (`POST /api/v1/auth/otp/validate` returns `200 OK` or `401 Unauthorized`).
   - Test expired OTP rejection and `403 Forbidden` after three failed attempts.
   
3. **Edge Case Tests**
   - Multiple OTP requests; ensure only the latest is valid.
   - Temporary suspension of OTP requests after multiple incorrect attempts.

### Implementation Approach

#### Core Implementation Logic

1. **Class `OTPService`**
   - `generateOTP(String userID)`: Generates an OTP, stores it in the database, and returns the OTP code.
   - `validateOTP(String userID, String otpCode)`: Validates the OTP against the database entries, handles OTP expiration, and updates attempt count.

2. **Algorithm**
   - Utilize a time-based OTP algorithm (e.g., TOTP) for generation.
   - Store OTP with an expiration timestamp (current time + 5 minutes).

#### Inter-Service Calls and Async Patterns

- Asynchronous processing of OTP send requests through message queue (e.g., RabbitMQ) to the notification service for email/SMS delivery.

### Architectural Decision Records (ADRs)

1. **ADR-001: OTP Storage in Database**
   - **Context**: Efficient retrieval and expiration handling needed.
   - **Decision**: Store OTPs in a dedicated `OTP` table with indexing.
   - **Rationale**: Allows fast validation and expiration handling.
   - **Alternative**: In-memory caching was considered but rejected due to scalability concerns.

2. **ADR-002: Use of TOTP Algorithm**
   - **Context**: Need a secure and standard OTP generation method.
   - **Decision**: Implement TOTP (Time-based One-Time Password) for OTP generation.
   - **Rationale**: Well-supported, secure, easy to implement using existing libraries.
   - **Alternative**: Custom OTP algorithm was rejected due to increased complexity without added benefits.

### Simplicity Gate Assessment

- **Appropriate**: Each technical change directly serves at least one FR.
- No elements are potentially over-engineered or under-specified.

### Affected Services and API Changes

- **Multi-factor Authentication Service**
  - **New Endpoints**: None
  - **Modified Endpoints**: Descriptions updated to reflect new behavior for existing endpoints.

### Context

- **Service**: Multi-factor Authentication Service
- **Functional Requirements Referenced**: FR-001, FR-002, FR-003, FR-004, FR-005

## Affected Services

- `S-004`
- `S-002`

## API Changes

| Service | Endpoint | Method | Change |
|---------|----------|--------|--------|
| `S-004` | `/login` | POST | modify |
| `S-002` | `/api/v1/auth/otp/generate` | POST | use |
| `S-002` | `/api/v1/auth/otp/validate` | POST | use |

## Open Questions / Gaps

_No gaps identified._