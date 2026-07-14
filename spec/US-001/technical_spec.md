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