# Authentication Service

An **infrastructure** microservice responsible for:

- Authenticating user credentials (username + password)
- Managing Multi-Factor Authentication (MFA / TOTP)
- Validating user roles

Built with **Python 3.12** and **Flask 3**, following **hexagonal architecture** (ports & adapters).

---

## Architecture

```
app/
├── domain/                  # Pure business logic — no framework dependencies
│   ├── models.py            # Core entities: User, AuthResult
│   ├── ports.py             # Abstract interfaces (ports)
│   └── services.py          # Use-case implementations
├── adapters/
│   ├── inbound/
│   │   └── http_routes.py   # Flask blueprints (HTTP adapter)
│   └── outbound/
│       ├── in_memory_user_repo.py  # In-memory user store (dev/test)
│       └── bcrypt_hasher.py        # Bcrypt password hasher
└── factory.py               # Application factory (dependency wiring)
main.py                      # Entry-point
```

The domain layer depends on **nothing** outside the standard library.  
Adapters depend on the domain; the domain never depends on adapters.

---

## Quick Start

### 1. Clone & configure

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY to a long random string
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # for tests
```

### 3. Run locally

```bash
python main.py
# or with gunicorn:
gunicorn --bind 0.0.0.0:5000 main:app
```

### 4. Docker

```bash
docker build -t auth-service .
docker run --env-file .env -p 5000:5000 auth-service
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Liveness probe |
| `POST` | `/auth/login` | Authenticate username + password |
| `POST` | `/auth/mfa/enable` | Enable MFA for a user |
| `POST` | `/auth/mfa/verify` | Verify a TOTP token |
| `POST` | `/auth/roles/check` | Check whether a user holds a role |

### `GET /health`

```json
{ "status": "ok", "service": "authentication-service" }
```

### `POST /auth/login`

**Request**
```json
{ "username": "alice", "password": "s3cr3t" }
```

**Response 200**
```json
{ "user_id": "u-123", "roles": ["user"], "requires_mfa": false }
```

### `POST /auth/mfa/enable`

**Request**
```json
{ "user_id": "u-123" }
```

**Response 200**
```json
{ "user_id": "u-123", "mfa_secret": "BASE32SECRET" }
```

### `POST /auth/mfa/verify`

**Request**
```json
{ "user_id": "u-123", "token": "123456" }
```

**Response 200**
```json
{ "valid": true }
```

### `POST /auth/roles/check`

**Request**
```json
{ "user_id": "u-123", "role": "admin" }
```

**Response 200**
```json
{ "user_id": "u-123", "role": "admin", "has_role": false }
```

---

## Running Tests

```bash
pytest -v
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Flask environment |
| `FLASK_DEBUG` | `false` | Enable debug mode |
| `PORT` | `5000` | HTTP listen port |
| `SECRET_KEY` | *(required)* | Session signing key |
| `BCRYPT_ROUNDS` | `12` | Bcrypt cost factor |

See `.env.example` for a full template.

---

## License

MIT
