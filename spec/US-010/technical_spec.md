## S-002

## Technical Design Specification

### 1. Contracts & Interfaces

#### API Contracts
- **POST /api/v1/auth/recovery-code/use**
  - **Request Payload**:
    - `code` (string, required): The recovery code to be invalidated.
  - **Response**:
    - `200 OK`: Code successfully invalidated.
    - `400 Bad Request`: Code already used or invalid.
    - `500 Internal Server Error`: Unrecoverable error during operation.

#### Data Schema
- **Table: RecoveryCode**
  - **Columns**:
    - `code` (string, PRIMARY KEY): The recovery code.
    - `isUsed` (boolean, DEFAULT FALSE): Flag indicating if the code has been used.
    - `userId` (integer, FOREIGN KEY): ID of the user to whom the code belongs.
  - **Indexes**:
    - Index on `userId` for faster retrieval.
  
### 2. Test Strategy

#### Test Cases

1. **Test Code Invalidation (FR-001 & FR-002)**
   - **Precondition**: Valid recovery code that is not used.
   - **Action**: POST to `/api/v1/auth/recovery-code/use` with code.
   - **Expected Outcome**: Receive `200 OK`. Code's `isUsed` becomes TRUE.

2. **Test Avoid Reuse (FR-002)**
   - **Precondition**: A recovery code marked `isUsed = TRUE`.
   - **Action**: POST to `/api/v1/auth/recovery-code/use` with the used code.
   - **Expected Outcome**: Receive `400 Bad Request`.

3. **Test Error Notification (FR-003)**
   - **Precondition**: Invalid recovery code.
   - **Action**: POST to `/api/v1/auth/recovery-code/use` with invalid code.
   - **Expected Outcome**: Receive `400 Bad Request` with error message.

4. **Test Security Compliance (FR-004)**
   - **Precondition**: Simulate attack with repeated invalid attempts.
   - **Action**: POST to `/api/v1/auth/recovery-code/use`.
   - **Expected Outcome**: No patterns of unauthorized access detected.

5. **Test Logging Attempts (FR-005)**
   - **Precondition**: Invalid recovery code submission.
   - **Action**: Check system logs after POST attempt.
   - **Expected Outcome**: Logging entry for invalid code attempt exists.

### 3. Implementation Approach

#### Core Implementation

1. **Class: RecoveryCodeService**
   - **Method: useRecoveryCode(code: String)**
     - Validates the code.
     - Sets `isUsed` to TRUE on successful validation.
     - Throws error on invalid/used code.

2. **Method Logic**
   - Query RecoveryCode table by `code`.
   - If `isUsed` is FALSE, update `isUsed` to TRUE.
   - If `isUsed` is TRUE or code is not found, return appropriate error.

#### Inter-Service Communication
- Audit logs from invalid attempts SHALL be asynchronously sent to the logging service using a standard message queue (RabbitMQ).

#### ADR-001: Use Existing Messaging Infrastructure
- **Context**: Existing system uses RabbitMQ for asynchronous events.
- **Decision**: Use RabbitMQ to log invalid attempts.
- **Rationale**: Reuse of existing infrastructure minimizes integration effort.
- **Alternative**: Implement a new logging service. Rejected due to unnecessary complexity.

### Simplicity Gate Assessment
- **Rating**: Appropriate
  - The technical elements directly map to FR-001 through FR-005 without unnecessary overhead.

### Affected Services and API Changes
- **Multi-factor Authentication Service**: Addition of `/api/v1/auth/recovery-code/use` endpoint to handle recovery code invalidation. 

- **Logging Service**: Will receive audit logs asynchronously.

This technical design ensures all specified functional requirements align with efficient, secure, and maintainable implementation practices, achieving the compliance directives laid out in the functional specification.