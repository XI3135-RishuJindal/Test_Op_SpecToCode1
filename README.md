# API Gateway

## Overview
This repository contains the API Gateway service for the SSO authentication system, generated and maintained by ACE DevOps Agent. The gateway handles JWT-based authentication, request routing, and comprehensive audit logging for up to 10,000 concurrent users.

## Files
- `openspec/changes/api-01/specs.md`
- `openspec/changes/api-gateway/proposal.md`
- `openspec/changes/api-gateway/specs/spec.md`
- `openspec/changes/api-gateway/tasks.md`
- `.dockerignore`
- `ApiGateway.csproj`
- `ApiGateway.sln`
- `appsettings.Development.json`
- `appsettings.json`
- `Dockerfile`
- `Program.cs`
- `README.md`
- `Controllers/AuthController.cs`
- `Controllers/HealthController.cs`
- `Controllers/TestController.cs`
- `Models/ErrorResponse.cs`
- `Models/MedicationDTO.cs`
- `Models/TestRequest.cs`
- `Models/TestResponse.cs`
- `Properties/launchSettings.json`
- `Tests/ApiGateway.Tests.csproj`
- `Tests/Controllers/AuthControllerTests.cs`
- `Tests/Controllers/HealthControllerTests.cs`
- `Tests/Controllers/TestControllerTests.cs`

## Setup
1. Ensure your CI/CD platform is properly configured
2. Configure required secrets in your repository settings
3. Push code to trigger the pipeline

## Pipeline Features
- Automated build and test
- Security scanning
- Deployment automation
- Quality gates

---

## Audit Logging

### Overview
The API Gateway uses [Serilog](https://serilog.net/) for structured, asynchronous audit logging. Logs capture all security-relevant events (authentication attempts, token operations, session activity) to support real-time security audits and system health monitoring. Logging is non-blocking and completes within the 3-second SLA requirement.

Logs are written to two sinks simultaneously:
- **Console** – structured output for container/orchestration environments
- **Rolling file** – daily rotated files under `logs/`

---

### Log Format

Each log entry is a structured record with the following fields:

| Field           | Type     | Description                                                         |
|-----------------|----------|---------------------------------------------------------------------|
| `Timestamp`     | DateTime | UTC timestamp of the event (ISO 8601, e.g. `2024-06-01T12:34:56Z`) |
| `Level`         | string   | Severity level: `Information`, `Warning`, `Error`, `Fatal`         |
| `Message`       | string   | Human-readable description of the event                            |
| `UserId`        | string   | Identifier of the user involved in the operation (when applicable) |
| `Username`      | string   | Username of the actor (when applicable)                            |
| `OperationType` | string   | The type of operation (see [Logged Events](#logged-events))        |
| `Outcome`       | string   | `Success` or `Failure`                                             |
| `RequestId`     | string   | Unique GUID correlating a single request across log lines          |
| `SourceContext` | string   | Fully-qualified class name that emitted the log entry              |
| `Exception`     | string   | Exception details (only present on `Error`/`Fatal` entries)        |

#### Example Log Entry (console / structured text)

```
[2024-06-01 12:34:56 INF] Token generated successfully for user: johndoe
  UserId:        "a1b2c3d4-..."
  Username:      "johndoe"
  OperationType: "TokenGeneration"
  Outcome:       "Success"
  RequestId:     "f7e6d5c4-..."
  SourceContext: "ApiGateway.Controllers.AuthController"
```

#### Example Log Entry (file – plain text with rolling date suffix)

File: `logs/apigateway-20240601.txt`

```
2024-06-01 12:34:56.789 +00:00 [INF] Token generated successfully for user: johndoe
```

---

### Logged Events

The following events are captured by the audit log:

| OperationType       | Trigger                                          | Default Level |
|---------------------|--------------------------------------------------|---------------|
| `TokenGeneration`   | `POST /api/auth/token` – successful token issue  | Information   |
| `TokenDenied`       | `POST /api/auth/token` – invalid credentials     | Warning       |
| `RequestReceived`   | Any authenticated controller action starts       | Information   |
| `RequestValidation` | Request body validation failure                  | Warning       |
| `StartupSuccess`    | Application started successfully                 | Information   |
| `StartupFailure`    | Unhandled exception during startup               | Fatal         |

> **Privacy note:** Logs never record passwords, raw JWT secrets, or other sensitive personal data. Only non-sensitive identifiers (usernames, GUIDs) are included, in compliance with GDPR and internal security policy.

---

### Log Configuration

Logging behaviour is controlled via `appsettings.json` (and overridden per-environment in `appsettings.Development.json`).

**`appsettings.json` (production defaults)**
```json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "System": "Warning"
      }
    }
  }
}
```

**`appsettings.Development.json` (development overrides)**
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.AspNetCore": "Information"
    }
  }
}
```

To change the minimum log level at runtime, update the `Serilog.MinimumLevel.Default` key and restart the service (or redeploy the container).

---

### Accessing Log Data

#### Local / Development

Log files are written to the `logs/` directory relative to the application working directory:

```
logs/
  apigateway-20240601.txt
  apigateway-20240602.txt
  ...
```

To tail logs in real time:

```bash
# Linux / macOS
tail -f logs/apigateway-$(date +%Y%m%d).txt

# Windows PowerShell
Get-Content "logs\apigateway-$(Get-Date -Format 'yyyyMMdd').txt" -Wait
```

#### Docker / Container Environments

Console output (stdout/stderr) is the primary log sink in containerised deployments. Retrieve logs with:

```bash
# View live container logs
docker logs -f <container_name_or_id>

# Save the last 500 lines to a file
docker logs --tail 500 <container_name_or_id> > gateway_audit.log
```

If the container mounts a host volume for the `logs/` directory, the rolling files are also accessible on the host at the configured mount path.

#### CI/CD / Orchestration Platforms

In Kubernetes or similar platforms, use your log aggregation stack (e.g. Loki, Elasticsearch, Splunk) to query by:
- **Label/tag**: `app=api-gateway`
- **Field**: `SourceContext` contains `ApiGateway`
- **Field**: `Level` = `Warning` or `Error` for anomaly detection

---

### Log Retention Policy

| Environment | Retention Period | Storage        |
|-------------|-----------------|----------------|
| Development | 7 days          | Local `logs/`  |
| Staging     | 30 days         | Mounted volume |
| Production  | 90 days         | Centralised log aggregator |

Rolling files are rotated daily. Files older than the retention window should be archived or deleted by the infrastructure team's scheduled job.

---

### Searching and Filtering Logs

**Find all failed token requests:**
```bash
grep "TokenDenied\|InvalidCredentials" logs/apigateway-*.txt
```

**Find all log entries for a specific user:**
```bash
grep "johndoe" logs/apigateway-*.txt
```

**Find all errors and fatals:**
```bash
grep "\[ERR\]\|\[FTL\]" logs/apigateway-*.txt
```

**Correlate a full request lifecycle by RequestId:**
```bash
grep "f7e6d5c4-1234-5678-abcd-ef0123456789" logs/apigateway-*.txt
```

---

### Security and Compliance

- Logs are **immutable** once written; file permissions should prevent modification by application accounts.
- All logging is performed **asynchronously** to avoid introducing latency into authenticated request paths.
- Audit logs support **non-repudiation** by recording the `UserId`, `Username`, `OperationType`, and `Outcome` for every security-relevant event.
- Sensitive fields (passwords, JWT signing keys, PII beyond username) are **never** written to logs.
- Access to production log storage should be restricted to authorised operations and security personnel only.

---

## Generated by
ACE DevOps Agent - Automated DevOps Intelligence Platform
