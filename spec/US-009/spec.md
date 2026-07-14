# Generate Recovery Codes

| | |
|---|---|
| **ID** | US-009 |
| **Feature** | F-01 — Multi-factor Authentication |
| **Epic** | EP-003 — Develop Backup Recovery Codes System |
| **Status** | Draft |
| **Date** | 2026-07-14 |

## Background

Part of feature *Multi-factor Authentication*.

## Acceptance Criteria

### Story

- [ ] Given the user is authenticated, When they request recovery codes, Then a set of unique recovery codes is generated.
- [ ] Given recovery codes are generated, When they are displayed, Then they are immediately visible to the user.
- [ ] Given a recovery code is used, When a subsequent request for the same code is made, Then it cannot be used again.

### Epic

- [ ] Given a user is authenticated, when they request recovery codes, then a list of codes is generated and displayed
- [ ] Given a recovery code is used, when the user attempts to use it again, then it is rejected
- [ ] Given a user has existing codes, when they regenerate them, then the old codes are invalidated and new ones are provided

## Proposed Solution

### Functional Specification

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

### Technical Design

## S-002

### Technical Design Specification for Recovery Codes in Multi-factor Authentication Service (S-002)

#### Contracts & Interfaces

**New API Endpoint**
- **Method**: `POST`
- **Path**: `/api/v1/auth/recovery-codes/generate`
- **Request Body Parameters**:
  - `user_id` (string, required): The ID of the authenticated user requesting recovery codes.
- **Response Attributes**:
  - `recovery_codes` (array of strings): Newly generated, unique recovery codes.
  - `visibility_duration` (number): Time in seconds (minimum 20) the recovery codes shall remain visible, tailored by `SC-002`.

**Database Schema Changes**
- **Table**: `recovery_codes`
  - **Columns**:
    - `code` (string, PRIMARY KEY): The unique recovery code.
    - `user_id` (string, INDEXED): The ID of the user to whom the code is issued.
    - `used` (boolean): Flag to indicate if the code has been used.
    - `created_at` (timestamp): Timestamp of when the code was generated.
  - **Indexes**:
    - `idx_user_id`: Index on the `user_id` column to enhance lookup performance.

#### Test Strategy

**Test Cases**:
1. **TC-001: Generate Recovery Codes**
   - **Inputs**: Valid `user_id`.
   - **Validates**: FR-001, SC-001.
   - **Expected Outcome**: Generates 6 unique codes visible for ≥ 20 seconds.

2. **TC-002: Display of Recovery Codes**
   - **Inputs**: Generated recovery codes request.
   - **Validates**: FR-002, SC-002.
   - **Expected Outcome**: Codes are displayed immediately and remain visible as per `visibility_duration`.

3. **TC-003: Validation of Unused Code**
   - **Inputs**: An unused recovery code.
   - **Validates**: FR-003.
   - **Expected Outcome**: Code is verifiable and marked as unused.

4. **TC-004: Mark Code as Used**
   - **Inputs**: Code used for recovery.
   - **Validates**: FR-004, FR-005.
   - **Expected Outcome**: Code is marked as used after successful redemption.

5. **TC-005: Prevent Reuse of Code**
   - **Inputs**: Code previously marked as used.
   - **Validates**: FR-005.
   - **Expected Outcome**: Reuse is denied, and a failure response is generated.

#### Implementation Approach

**Core Implementation Logic:**
- **Class**: `RecoveryCodeService`
  - **Method**: `generateRecoveryCodes(user_id: string): List<String>`
    - Generates 6 unique codes per `SC-001`.
    - Queries `recovery_codes` table to ensure uniqueness.
    - Inserts new records into `recovery_codes` table with `used` as `false`.

  - **Method**: `validateRecoveryCode(user_id: string, code: string): boolean`
    - Verifies the code matches user and is unused.
    - If valid, proceeds to mark it as used using `markCodeAsUsed`.

  - **Method**: `markCodeAsUsed(user_id: string, code: string): void`
    - Updates `used` status of `recovery_codes` record to `true`.

**Inter-Service Calls and Async Patterns:**
- There SHALL be no new inter-service calls introduced for recovery code generation; all operations are self-contained within the S-002 service.
- Asynchronous patterns are NOT required for the synchronous nature of code generation and redemption.

#### Architectural Decision Records (ADRs)

- **ADR-001: Database Schema for Recovery Codes**
  - **Context**: Required for efficient storage and querying of recovery codes.
  - **Decision**: `recovery_codes` table to store codes with indexed `user_id`.
  - **Rationale**: Ensures quick lookup and adherence to `SC-001`.
  - **Alternative**: Store codes in memory; rejected due to persistence requirements.

- **ADR-002: RESTful API Design for Code Generation**
  - **Context**: API endpoint for recovery codes.
  - **Decision**: Introduce a new POST endpoint at `/api/v1/auth/recovery-codes/generate`.
  - **Rationale**: Aligns with existing service pattern and FR-001.
  - **Alternative**: Use existing endpoints; rejected to avoid coupling OTP logic with recovery codes.

### Simplicity Gate Assessment

- **Rating**: `appropriate`
- **Justification**: All ADR elements and technical elements map directly to the functional requirements; there is neither over-engineering nor under-written specification. Each aspect accomplishes its aligned functional requirements efficiently.

## Affected Services

- `S-002`

## API Changes

| Service | Endpoint | Method | Change |
|---------|----------|--------|--------|
| `S-002` | `POST /api/v1/auth/recovery-codes` | POST | new_feature |

## Open Questions / Gaps

_No gaps identified._