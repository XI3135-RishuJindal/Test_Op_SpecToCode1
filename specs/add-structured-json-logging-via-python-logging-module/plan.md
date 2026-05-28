# PLAN: Add Structured JSON Logging via Python logging Module

---

## Overview

**Migration Strategy: Feature-Flag Gated / Incremental (Strangler-Fig)**

Structured JSON logging will be introduced incrementally alongside the existing logging configuration. A new JSON formatter and handler will be added to the Python `logging` module setup without removing existing handlers immediately. An environment variable flag (e.g., `LOG_FORMAT=json`) will gate activation of the new formatter, allowing both the legacy plain-text format and the new structured JSON format to coexist during rollout.

**Justification:**
- The upgrade urgency is rated **medium**, indicating no emergency forcing a big-bang cutover.
- The strangler-fig / feature-flag approach minimises risk: if the new formatter causes issues in production, operators can revert by changing a single environment variable without a code deployment.
- Effort is moderate; incremental delivery allows testing in lower environments before full activation.
- No breaking infrastructure changes are required — only the logging configuration layer is affected.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Design & scaffold: define `JsonFormatter` class, logging config structure, and environment variable contract | None | 1 person-day |
| 2 | Implementation: write `JsonFormatter`, update logging initialisation, add `LOG_FORMAT` flag gating | Phase 1 complete | 2 person-days |
| 3 | Integration: wire formatter into all application entry points and existing logger call sites | Phase 2 complete | 1 person-day |
| 4 | Testing: unit, integration, and regression test suite for logging output | Phase 2 complete | 1 person-day |
| 5 | Rollout & validation: enable `LOG_FORMAT=json` in staging, validate log ingestion pipeline, promote to production | Phase 3 & 4 complete | 0.5 person-days |

> **Total estimated effort: ~5.5 person-days** (derived from the moderate upgrade option).

---

## Component Changes

### 1. `JsonFormatter` (new class)

**File:** `logging_config.py` (create if absent) or the project's existing logging setup module (TODO: confirm exact file path from codebase).

**What changes structurally:**
- A new class `JsonFormatter(logging.Formatter)` is introduced.
- Overrides `format(self, record: logging.LogRecord) -> str`.
- Serialises a fixed set of standard fields plus any `extra` fields attached to the record.

**Key fields emitted per log record:**
```
timestamp, level, logger, message, module, funcName, lineno, exc_info (if present)
```

**Sketch:**
```python
import json
import logging
import traceback
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Merge any extra fields passed via `extra={}`
        for key, value in record.__dict__.items():
            if key not in _LOG_RECORD_BUILTIN_ATTRS:
                payload[key] = value
        return json.dumps(payload, default=str)
```

---

### 2. Logging Initialisation / Configuration

**File:** TODO — confirm whether the project uses `logging.config.dictConfig`, `logging.basicConfig`, a `logging.ini` / `logging.yaml` file, or a dedicated `setup_logging()` function.

**What changes structurally:**
- A `setup_logging()` function (create or update) reads `LOG_FORMAT` from the environment.
- If `LOG_FORMAT=json`, attaches `JsonFormatter` to the root logger's `StreamHandler`.
- If `LOG_FORMAT` is absent or set to any other value, falls back to the existing plain-text formatter.

**Config key introduced:** `LOG_FORMAT` (environment variable, values: `json` | `text`, default: `text`).

---

### 3. Application Entry Points

**Files:** TODO — identify `main.py`, `app.py`, `wsgi.py`, `asgi.py`, or equivalent entry points.

**What changes:**
- Each entry point must call `setup_logging()` before any other application code runs.
- No changes to individual `logger.info(...)` / `logger.error(...)` call sites are required unless callers need to add structured `extra` fields (optional enhancement, Phase 3).

---

### 4. Existing Logger Call Sites (optional enrichment)

**Files:** TODO — scan codebase for `logging.getLogger(...)` usages.

**What changes (optional):**
- Where contextual data is currently interpolated into message strings (e.g., `logger.info(f"User {user_id} logged in")`), refactor to use `extra={"user_id": user_id}` to emit structured fields.
- This is additive and non-breaking.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Python standard library `logging` | Built-in | Built-in (no change) | None | `JsonFormatter` uses only stdlib; no third-party logging library required |
| `python-json-logger` *(optional)* | N/A | TODO — confirm if team prefers a battle-tested third-party formatter | None anticipated | If adopted, install via `pip`; replaces the custom `JsonFormatter` class; version TBD from tech analysis (not provided) |

> **Note:** The tech analysis did not specify framework versions or existing dependencies. If a third-party library such as `python-json-logger` is preferred over a custom implementation, confirm the pinned version and add it to `requirements.txt` / `pyproject.toml`. Do **not** use a version sourced from training data — obtain it from the project's dependency resolution tooling.

---

## Infrastructure Changes

**Log ingestion pipeline:** TODO — if logs are shipped to a log aggregator (e.g., Elasticsearch, Loki, Datadog, Splunk), confirm that the ingest parser is updated to expect JSON rather than plain text. This is a prerequisite before enabling `LOG_FORMAT=json` in production.

**Docker / container base image:** N/A — no base image change required; the formatter is pure Python.

**Kubernetes manifests:** TODO — if `LOG_FORMAT` is injected via a `ConfigMap` or `Deployment` env block, add the key there. Example:
```yaml
env:
  - name: LOG_FORMAT
    value: "json"
```

**CI/CD pipeline:** TODO — confirm pipeline file location (e.g., `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`). Add a lint/test step that asserts log output is valid JSON when `LOG_FORMAT=json` is set.

**`requirements.txt` / `pyproject.toml`:** Add `python-json-logger` (version TODO) if the third-party library path is chosen.

---

## Rollback Strategy

Each phase is independently reversible.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** | Delete scaffolded files / branch; no production impact. |
| **Phase 2** | Revert `logging_config.py` changes via `git revert` or branch deletion; `LOG_FORMAT` env var not yet set in any environment, so no runtime impact. |
| **Phase 3** | Revert entry-point changes via `git revert`; restore previous `setup_logging()` call or remove it entirely to restore prior behaviour. |
| **Phase 4** | Remove or skip new test cases; no production impact. |
| **Phase 5 — Staging** | Set `LOG_FORMAT=text` (or unset the variable) in the staging environment; restart the service; JSON output stops immediately without a code deployment. |
| **Phase 5 — Production** | Set `LOG_FORMAT=text` (or unset the variable) in the production environment config / Kubernetes `ConfigMap`; rolling restart; plain-text logging resumes. If log aggregator parser was updated, revert the parser config in parallel. |

> **Key invariant:** Because the `LOG_FORMAT` flag gates the formatter at runtime, rollback in any live environment requires only an environment variable change and a process restart — no code change or redeployment is needed.

---

## Testing Strategy

### Unit Tests

**Tool:** `pytest`
**Target coverage:** ≥ 90% of `logging_config.py` / `JsonFormatter` class.

| Test | Description |
|------|-------------|
| `test_json_formatter_output_is_valid_json` | Assert `JsonFormatter.format(record)` returns a string parseable by `json.loads`. |
| `test_json_formatter_required_fields` | Assert `timestamp`, `level`, `logger`, `message` keys are always present. |
| `test_json_formatter_exception_field` | Assert `exception` key is present when `exc_info` is set on the record. |
| `test_json_formatter_extra_fields` | Assert custom `extra` dict keys are promoted to top-level JSON fields. |
| `test_setup_logging_json_mode` | Set `LOG_FORMAT=json` in env, call `setup_logging()`, assert root logger handler uses `JsonFormatter`. |
| `test_setup_logging_text_mode` | Unset `LOG_FORMAT`, call `setup_logging()`, assert root logger handler does **not** use `JsonFormatter`. |

### Integration Tests

**Tool:** `pytest` with `capsys` or `caplog` fixtures.

- Emit a log line through the full application logging stack with `LOG_FORMAT=json`.
- Capture stdout/stderr; parse as JSON; assert field values match the emitted log call.
- Test with `LOG_FORMAT=text` to confirm no regression in plain-text output.

### Regression Tests

- Run the existing test suite in full with `LOG_FORMAT=json` set to confirm no existing test breaks due to log output format changes.
- Confirm that `logger.info(...)` call sites that previously used f-string interpolation still produce correct `message` values.

### Performance Tests

**Tool:** `timeit` or `pytest-benchmark`.

- Benchmark `JsonFormatter.format()` against the default `logging.Formatter.format()` for a representative log record.
- Acceptable overhead: < 2× the baseline formatter latency (JSON serialisation is expected to add some cost).
- TODO: define throughput SLA if the application is log-intensive.

### CI Gate

TODO — confirm CI platform. Recommended gate:

```
pytest --cov=logging_config --cov-fail-under=90
```

Add this as a required status check before merging any PR that touches `logging_config.py` or entry-point files.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| `JsonFormatter` design approved | Phase 1 | End of Day 1 | TODO |
| `JsonFormatter` + `setup_logging()` implemented | Phase 2 | End of Day 3 | TODO |
| All entry points wired; `extra` fields added to key call sites | Phase 3 | End of Day 4 | TODO |
| Full test suite passing; CI gate configured | Phase 4 | End of Day 5 | TODO |
| `LOG_FORMAT=json` enabled in staging; log pipeline validated | Phase 5 | End of Day 5 (afternoon) | TODO |
| `LOG_FORMAT=json` promoted to production | Phase 5 | End of Day 6 | TODO |

> Effort derived from the moderate upgrade option (~5.5 person-days total). Calendar duration assumes a single engineer; parallelisation across two engineers could compress Phases 2–4 to ~3 calendar days.