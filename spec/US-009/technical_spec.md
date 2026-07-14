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