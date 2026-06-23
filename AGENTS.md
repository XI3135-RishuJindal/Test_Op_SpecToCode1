# AGENTS.md

## Stack

- **Service:** Identity Registration & Verification Service
- **Type:** business
- **Technologies:**
- Spring Boot or NestJS
- REST/JSON + OpenAPI
- Bean Validation/class-validator
- Argon2id/bcrypt
- PostgreSQL repository pattern
- Redis (optional for ephemeral references)
- OpenTelemetry
- **Responsibilities:**
- Accept registration commands with idempotency handling
- Validate DTOs (email format/normalization, password policy, CAPTCHA/risk result)
- Hash passwords securely (Argon2id/bcrypt) and create users in PENDING_VERIFICATION
- Generate signed, short-lived, single-use verification tokens
- Process verify-email commands and transition account to ACTIVE
- Write integration events to outbox transactionally with user data
- Return security-safe generic responses to prevent enumeration

## General Rules

- Always read files in /specs before implementing
- Never implement without acceptance criteria
- Code should be simple and readable
- Avoid overengineering
- The project follows a hexagonal architecture

## Required Workflow

1. Read the specs in the /specs directory
2. Generate tasks.md if it does not exist
3. Implement based on the tasks
4. Create automated tests
5. Validate acceptance criteria

## Testing

- Cover all acceptance criteria
- Tests should be clear and straightforward
- Generated code must reach **90% unit test coverage**

## Constraints

- Do not invent requirements that are not described
- Do not change behavior without updating the spec
