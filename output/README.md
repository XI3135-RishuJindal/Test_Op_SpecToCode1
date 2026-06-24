# Account Management Service

A **COBOL / IBM Mainframe** business service responsible for account file operations and customer data import/update. The service follows **Hexagonal Architecture (Ports and Adapters)** to keep domain logic isolated from infrastructure concerns.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Technology Stack](#technology-stack)
4. [Getting Started](#getting-started)
5. [Building](#building)
6. [Running](#running)
7. [Health Check](#health-check)
8. [Testing](#testing)
9. [Environment Variables](#environment-variables)
10. [Docker](#docker)
11. [Contributing](#contributing)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Driving Adapters (Primary)                 │
│          ACCTAPI.cbl  ·  ACCTHLTH.cbl                       │
└────────────────────────┬────────────────────────────────────┘
                         │  calls via CALL / LINKAGE
┌────────────────────────▼────────────────────────────────────┐
│                    Ports (Interfaces)                       │
│                     ACCTPORT.cbl                            │
└────────────────────────┬────────────────────────────────────┘
                         │  implemented by
┌────────────────────────▼────────────────────────────────────┐
│                   Domain Core                               │
│                    ACCTDMN.cbl                              │
│   (business rules: validation, state transitions)          │
└────────────────────────┬────────────────────────────────────┘
                         │  delegates I/O to
┌────────────────────────▼────────────────────────────────────┐
│               Driven Adapters (Secondary)                   │
│        ACCTFILE.cbl (VSAM)  ·  ACCTIMPT.cbl (Import)       │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Program | Responsibility |
|---|---|---|
| Primary Adapter | `ACCTAPI.cbl` | Exposes CRUD operations to callers / CICS |
| Primary Adapter | `ACCTHLTH.cbl` | Health check endpoint |
| Port | `ACCTPORT.cbl` | Defines operation codes and result codes |
| Domain | `ACCTDMN.cbl` | Business rules, validation, state machine |
| Secondary Adapter | `ACCTFILE.cbl` | VSAM indexed file I/O |
| Secondary Adapter | `ACCTIMPT.cbl` | Sequential flat-file customer import |
| Copybook | `ACCTCOPY.cpy` | Shared data structures |

---

## Project Structure

```
account-management-service/
├── src/
│   ├── domain/
│   │   └── ACCTDMN.cbl          # Domain core — business rules
│   ├── ports/
│   │   └── ACCTPORT.cbl         # Port definitions (operation & result codes)
│   ├── adapters/
│   │   ├── primary/
│   │   │   ├── ACCTAPI.cbl      # Driving adapter — CRUD API
│   │   │   └── ACCTHLTH.cbl     # Driving adapter — health check
│   │   └── secondary/
│   │       ├── ACCTFILE.cbl     # Driven adapter — VSAM file
│   │       └── ACCTIMPT.cbl     # Driven adapter — customer import
│   └── copybooks/
│       └── ACCTCOPY.cpy         # Shared copybook
├── tests/
│   ├── test_health.py           # Health check test suite
│   ├── test_account_api.py      # Account CRUD test suite
│   ├── test_import.py           # Import adapter test suite
│   ├── conftest.py              # Pytest fixtures
│   └── health_check.py          # Docker HEALTHCHECK script
├── Dockerfile
├── .dockerignore
├── .env.example
├── Makefile
├── requirements-test.txt
└── README.md
```

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | COBOL (IBM Enterprise COBOL / GnuCOBOL) |
| File I/O | VSAM KSDS (Keyed Sequential Data Set) |
| Import | Sequential flat file |
| Test harness | Python 3 + pytest |
| Container | Docker (GnuCOBOL on Ubuntu 22.04) |
| CI | Makefile-driven |

---

## Getting Started

### Prerequisites

- **GnuCOBOL** ≥ 3.1 (local) **or** Docker
- Python 3.9+ (for test harness)

### Clone and configure

```bash
git clone <repo-url>
cd account-management-service
cp .env.example .env
# Edit .env as needed
```

---

## Building

```bash
# Compile all COBOL programs
make compile

# Or compile a single program
cobc -x -free -o bin/ACCTHLTH src/adapters/primary/ACCTHLTH.cbl
```

---

## Running

```bash
# Run via Makefile
make run

# Or invoke a compiled program directly
./bin/ACCTAPI
```

---

## Health Check

The `ACCTHLTH` program returns a health response structure with:

| Field | Value |
|---|---|
| `LS-STATUS` | `UP  ` |
| `LS-SERVICE-NAME` | `ACCOUNT-MANAGEMENT-SERVICE` |
| `LS-VERSION` | `1.0.0` |
| `LS-RESULT-CODE` | `00` |

```bash
# Run health check manually
python3 tests/health_check.py
```

---

## Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
make test

# Run with coverage
make test-coverage
```

Test files:

| File | Coverage |
|---|---|
| `tests/test_health.py` | Health check endpoint |
| `tests/test_account_api.py` | CRUD operations via ACCTAPI |
| `tests/test_import.py` | Customer data import |

---

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Default | Description |
|---|---|---|
| `SERVICE_NAME` | `account-management-service` | Service identifier |
| `SERVICE_VERSION` | `1.0.0` | Semantic version |
| `ACCT_VSAM_PATH` | `/data/accounts.dat` | Path to VSAM data file |
| `IMPORT_FILE_PATH` | `/data/import/customers.dat` | Path to import flat file |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `HEALTH_CHECK_ENABLED` | `true` | Enable/disable health check |

---

## Docker

```bash
# Build image
docker build -t account-management-service:1.0.0 .

# Run container
docker run --rm \
  -v $(pwd)/data:/data \
  --env-file .env \
  account-management-service:1.0.0

# Run tests inside container
docker run --rm account-management-service:1.0.0 make test
```

---

## Contributing

1. Follow IBM Enterprise COBOL coding standards.
2. All new programs must include a `LINKAGE SECTION` with typed parameters.
3. Domain logic belongs in `ACCTDMN.cbl` only — adapters must not contain business rules.
4. Add or update tests in `tests/` for every new operation.
5. Run `make test` before submitting a pull request.
