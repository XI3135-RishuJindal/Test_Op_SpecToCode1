# TASKS: Add Structured JSON Logging via Python `logging` Module

---

## Prerequisites

- [ ] [XS] Confirm Python interpreter version in use and record it in the project README or a `.python-version` file
- [ ] [XS] Verify `python-json-logger` (or chosen JSON formatter library) is installable in the target environment by running `pip install python-json-logger` locally
- [ ] [XS] Confirm write access to the project's dependency manifest (`requirements.txt`, `pyproject.toml`, or `setup.cfg`) and logging configuration files

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch `feature/structured-json-logging` from the main branch
- [ ] [S] Audit all existing `logging` call sites across the codebase and document current log format, handlers, and any existing `logging.config` dictionaries or `.ini` files in a scratch note or PR description
- [ ] [XS] Capture a baseline sample of current log output (format, fields, levels) by running the application or relevant tests and saving representative output to `docs/logging-baseline.txt`
- [ ] [XS] Add `python-json-logger>=2.0.7` (or pinned version matching environment constraints) to the project dependency manifest (`requirements.txt` / `pyproject.toml`)

---

## Phase 2 — Core Upgrade

- [ ] [S] Create a centralized logging configuration module `logging_config.py` (or equivalent, e.g., `app/logging_config.py`) that instantiates a `pythonjsonlogger.jsonlogger.JsonFormatter` with a defined set of fields (`timestamp`, `level`, `name`, `message`, `exc_info`)
- [ ] [M] Replace or extend the existing `logging.basicConfig` / `logging.config.dictConfig` / `logging.config.fileConfig` call(s) with the new JSON formatter configuration defined in `logging_config.py`, ensuring the root logger and all named loggers emit JSON
- [ ] [S] Update all modules that instantiate their own `StreamHandler` or `FileHandler` with custom formatters to use the shared `JsonFormatter` from `logging_config.py` instead
- [ ] [XS] Add standard contextual fields (`service_name`, `environment`) as default extras in the `JsonFormatter` configuration in `logging_config.py`
- [ ] [XS] Ensure `logging_config.py` is imported and called at application entry point(s) (e.g., `main.py`, `app/__init__.py`, `wsgi.py`) before any other module emits log records

---

## Phase 3 — Testing & Validation

- [ ] [M] Write unit tests in `tests/test_logging_config.py` that assert log output is valid JSON, contains required fields (`timestamp`, `level`, `name`, `message`), and that exception info is serialized correctly
- [ ] [S] Run the full existing test suite and confirm no tests fail due to log format changes (e.g., tests asserting on plain-text log output must be updated to parse JSON)
- [ ] [XS] Manually verify JSON log output by running the application locally and piping output through `python -m json.tool` to confirm each line is valid JSON
- [ ] [XS] Confirm that log records at all levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) produce valid, consistently structured JSON output

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Add `python-json-logger` to any CI dependency installation step (e.g., `pip install -r requirements.txt` in `.github/workflows/*.yml` or equivalent pipeline config) and confirm the CI pipeline passes
- [ ] [XS] If log output is consumed by a log aggregator (e.g., Datadog, CloudWatch, ELK), verify the JSON field names (`timestamp`, `level`, `message`) match the aggregator's expected schema — update field name mappings in `logging_config.py` if needed

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CHANGELOG.md` with an entry describing the addition of structured JSON logging, the library used, and the fields emitted
- [ ] [S] Update or create a `docs/logging.md` runbook documenting the JSON log schema (field names, types, example output), how to add extra fields to individual log calls, and how to adjust log level via environment variable
- [ ] [XS] Merge feature branch via PR, request review from at least one team member familiar with the observability stack, and confirm no regressions in staging log output before merging to main

---

> **Out of scope:** Log aggregator pipeline configuration, alerting rules, log rotation, and any non-Python service logging — none of these are present in the provided tech analysis.