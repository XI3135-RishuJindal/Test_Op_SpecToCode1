# Authentication Service

An **infrastructure service** responsible for authenticating user credentials,
managing multi-factor authentication (MFA), and validating user roles.

Built with **Python 3.12** and **Flask 3**, following **hexagonal architecture**
(ports & adapters).

---

## Architecture

```
app/
├── domain/          # Pure business logic — no framework dependencies
│   ├── models.py    # User, AuthResult entities
│   └── ports.py     # Abstract interfaces (ports)
├── application/     # Use-case orchestration
│   ├── auth_service.py
│   ├── mfa_service.py
│   └── role_service.py
├── infrastructure/  # Driven adapters (persistence, hashing)
│   ├── in_memory_user_repository.py
│   └── bcrypt_password_hasher.py
├── adapters/        # Driving adapters (HTTP / Flask blueprints)
│   ├── health.py
│   └── auth_routes.py
└── factory.py       # Flask application factory
main.py              # Entry-point
```

---

## Endpoints

| Method | Path          | Description                        |
|--------|---------------|------------------------------------|
| GET    | `/health`     | Liveness check                     |
| POST   | `/auth/login` | Authenticate username + password   |

### `POST /auth/login`

**Request body**

```json
{
  "username": "alice",
  "password": "secret123"
}
```

**Success response** `200`

```json
{
  "user_id": "u-001",
  "roles": ["user"],
  "requires_mfa": false
}
```

**Error response** `401`

```json
{ "error": "Invalid credentials" }
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Docker (optional)

### Local development

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd authentication-service

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Configure environment
cp .env.example .env
# Edit .env as needed

# 5. Run the development server
FLASK_ENV=development python main.py
```

### Docker

```bash
docker build -t authentication-service .
docker run --env-file .env -p 5000:5000 authentication-service
```

---

## Running Tests

```bash
pytest
# With coverage
pytest --cov=app --cov-report=term-missing
```

---

## Environment Variables

| Variable       | Default                    | Description                          |
|----------------|----------------------------|--------------------------------------|
| `FLASK_ENV`    | `production`               | `development` enables debug mode     |
| `SECRET_KEY`   | `change-me-in-production`  | Flask secret key — **must** be set   |
| `HOST`         | `0.0.0.0`                  | Bind address                         |
| `PORT`         | `5000`                     | Bind port                            |
| `BCRYPT_ROUNDS`| `12`                       | bcrypt work factor                   |

---

## TODO / Future Work

- Replace `InMemoryUserRepository` with a SQLAlchemy / PostgreSQL adapter.
- Integrate `pyotp` for real TOTP verification in `MFAService`.
- Add JWT issuance on successful login.
- Add rate-limiting middleware.
- Add OpenAPI / Swagger documentation.
