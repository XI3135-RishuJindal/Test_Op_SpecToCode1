# Invalidate Used Recovery Codes

| | |
|---|---|
| **ID** | US-010 |
| **Feature** | F-01 — Multi-factor Authentication |
| **Epic** | EP-003 — Develop Backup Recovery Codes System |
| **Status** | Draft |
| **Date** | 2026-07-14 |

## Background

Part of feature *Multi-factor Authentication*.

## Acceptance Criteria

### Story

- [ ] Given a recovery code is used for account recovery, When it is successful, Then the recovery code is invalidated immediately.
- [ ] Given an invalid recovery code is used, When attempted, Then the user receives a notification about the invalid code.
- [ ] Given the system is invalidating recovery codes, When a code is used, Then it complies with security standards for invalidation.

### Epic

- [ ] Given a user is authenticated, when they request recovery codes, then a list of codes is generated and displayed
- [ ] Given a recovery code is used, when the user attempts to use it again, then it is rejected
- [ ] Given a user has existing codes, when they regenerate them, then the old codes are invalidated and new ones are provided

## Proposed Solution

### Functional Specification

## S-002

### Purpose
This specification defines how recovery codes used within the Multi-factor Authentication Service SHALL be invalidated, ensuring they are not reused, to safeguard against unauthorized access.

### Scope
The scope covers the invalidation of recovery codes used during the account recovery process within the Multi-factor Authentication Service, including error handling and security compliance.

### Non-Goals
1. Does not specify how recovery codes are generated.
2. Does not describe user interface elements.
3. Does not cover non-recovery code authentication methods.
4. Does not handle rate limiting for recoveries.
5. Does not detail persistence mechanisms for recovery codes.
6. Does not describe how notifications are sent to users.

### Key Entities
- **RecoveryCode**
  - Attributes: code (string), isUsed (boolean)
  - Relationships: Associated with a user (User has many RecoveryCodes)

### Functional Requirements
- FR-001: The system SHALL invalidate a recovery code immediately after it is used successfully.
- FR-002: The system MUST ensure a used recovery code CANNOT be reused.
- FR-003: The system SHALL notify the user when an invalid or already used recovery code is attempted.
- FR-004: The system MUST comply with established security standards during code invalidation.
- FR-005: The system SHOULD log any attempts to use invalid recovery codes for audit purposes.

### Assumptions Propagation
- A-001: Recovery codes are initially valid until used, then invalidated. (Affects: FR-001, FR-002)
- A-002: Invalid codes include those already used or non-existent. (Affects: FR-003)

### Success Criteria
- SC-001: 100% of used recovery codes are invalidated immediately after use.
- SC-002: User receives notification within 5 seconds of an invalid code attempt.
- SC-003: 100% compliance with security standards for invalidation process.

### Priority Levels
- P1: FR-001
- P1: FR-002
- P2: FR-003
- P1: FR-004
- P2: FR-005

### Edge Cases
- EC-001: Given a recovery code is tampered with, When used, Then the system must still ensure invalidation and proper notification.
- EC-002: Given a temporary service outage, When a code is used, Then the system must retry invalidation upon service recovery.
- EC-003: Given simultaneous requests with the same code, When processed, Then the system ensures code invalidation occurs only once.

### Independent Testability
- Preconditions: Valid recovery code, Successful code entry interface, User logged in.
- User Action: Execute account recovery using the code.
- Observable Outcome: The code becomes invalid, preventing reuse, and a confirmation message indicates invalidation.

### Separation of Concerns
The specification focuses on user capabilities of ensuring recovery code invalidation and notification upon failure. The focus is on user outcomes rather than technical details or specific implementation steps.

### Technical Design

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

## Affected Services

- `S-002`

## API Changes

| Service | Endpoint | Method | Change |
|---------|----------|--------|--------|
| `S-002` | `[POST] /api/v1/auth/recovery/validate` | POST | modification |

## Open Questions / Gaps

_No gaps identified._