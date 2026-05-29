# Spec: Upgrade Flask 1.x to 3.1 and Adopt Application Factory Pattern

---

## Summary

This spec covers the upgrade of Flask from version 1.x to version 3.1 and the concurrent adoption of the application factory pattern across the web application. The expected outcome is a modernized Flask application that eliminates deprecated APIs, resolves known security and compatibility concerns associated with Flask 1.x, and restructures application initialization to use a factory function — improving testability, configurability, and support for multiple application instances.

---

## Motivation

- **Flask 1.x is outdated and unmaintained:** Flask 1.x does not receive security patches or bug fixes. Flask 3.x represents the current supported release line with active maintenance.
- **Deprecated and removed APIs:** Flask 2.x and 3.x removed several APIs that were deprecated in 1.x (e.g., `before_first_request`, `flask.json` module changes, `flask.escape`, Werkzeug compatibility shims). Continued use of these APIs introduces technical debt and runtime risk.
- **Werkzeug and Jinja2 compatibility:** Flask 3.1 requires Werkzeug ≥ 3.0 and Jinja2 ≥ 3.1. Flask 1.x pins older versions of these dependencies, which carry their own EOL and CVE exposure.
- **Upgrade urgency:** Rated **medium** — no immediate critical CVE blocking production, but the version gap (1.x → 3.1) is large enough that further delay increases migration complexity.
- **Application factory pattern:** The current application structure (assumed global `app` instantiation) makes isolated testing, environment-specific configuration, and blueprint registration difficult. Adopting the factory pattern is a prerequisite for clean multi-environment support and is the recommended pattern in Flask 3.x documentation.
- **Compliance and maintainability:** Running on an unmaintained framework version is a risk flag in standard security audits and dependency review processes.

---

## Current State

> **Note:** Specific class names, config keys, and schema elements are not available from the provided context. Items marked **TODO** require codebase inspection before this spec is finalized.

### Application Initialization
- **TODO:** Identify the module where the global `Flask` application object is instantiated (e.g., a top-level `app = Flask(__name__)` call).
- **TODO:** Identify all modules that import the global `app` object directly for route registration, extension initialization, or request context access.

### Configuration
- **TODO:** Identify all `app.config` keys currently set at module level or via direct assignment outside a factory function.
- **TODO:** Identify environment-specific configuration classes or files (e.g., `DevelopmentConfig`, `ProductionConfig`).

### Extensions
- **TODO:** List all Flask extensions currently initialized (e.g., Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF). Note whether each is initialized with `ext.init_app(app)` or directly with `ext = Ext(app)`.

### Blueprints / Route Registration
- **TODO:** Identify all blueprints or route modules and how they are registered on the application object.

### Deprecated Flask 1.x APIs in Use
- **TODO:** Audit codebase for use of `@app.before_first_request` (removed in Flask 2.3+).
- **TODO:** Audit for use of `flask.escape` (moved to `markupsafe.escape` in Flask 2.x).
- **TODO:** Audit for use of `flask.json` module APIs that changed in Flask 2.2+.
- **TODO:** Audit for use of `flask._app_ctx_stack`, `flask._request_ctx_stack` (removed in Flask 2.3+).
- **TODO:** Audit for use of `FLASK_ENV` environment variable (deprecated in Flask 2.2, removed in Flask 2.3).

### Testing
- **TODO:** Identify how the test suite currently obtains a test client (direct `app.test_client()` on the global object vs. fixture-based).

### Entry Points
- **TODO:** Identify WSGI entry points (e.g., `wsgi.py`, server configuration files) that reference the global `app` object.

---

## Proposed Changes

### Overview Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Flask version | 1.x | 3.1 | Y |
| Werkzeug version | <2.0 (pinned by Flask 1.x) | ≥3.0 (required by Flask 3.1) | Y |
| Jinja2 version | <3.0 (pinned by Flask 1.x) | ≥3.1 (required by Flask 3.1) | Y |
| Application instantiation | Global `app = Flask(__name__)` at module level | `create_app(config=None)` factory function returning a `Flask` instance | Y |
| Extension initialization | Direct `Ext(app)` at module level (TODO: confirm) | `ext.init_app(app)` called inside factory function | Y |
| Blueprint registration | TODO: confirm current pattern | Registered inside `create_app()` | Possibly |
| `@app.before_first_request` | Used for one-time startup logic (TODO: confirm) | Replaced with explicit initialization calls inside factory or `with app.app_context()` | Y |
| `flask.escape` | Imported from `flask` | Imported from `markupsafe` | Y |
| `FLASK_ENV` variable | Used for environment selection | Replaced with `FLASK_DEBUG` or application-level config mechanism | Y |
| `flask._app_ctx_stack` / `flask._request_ctx_stack` | Accessed directly (TODO: confirm) | Removed; use `flask.g` and context locals | Y |
| Test client acquisition | Direct use of global `app.test_client()` | Obtained via factory-produced app instance in test fixtures | Y |
| WSGI entry point | References global `app` | References `create_app()` factory output | Y |
| `flask.json` usage | Flask 1.x `flask.json` API | Updated to Flask 3.x `flask.json` API (or `json` stdlib where appropriate) | Possibly |

### Key Additions
- A `create_app(config=None)` factory function becomes the canonical application entry point.
- Environment-specific configuration is passed into or resolved within the factory function.
- All extensions adopt the `init_app` pattern and are initialized inside the factory.
- All blueprints are registered inside the factory.

### Key Removals
- Global module-level `app` object (or it is reduced to a thin entry-point shim that calls the factory).
- All usage of APIs removed between Flask 1.x and Flask 3.1 (see deprecated API list above).

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Flask 1.x → 3.1 major version jump | All Flask APIs, extension compatibility, and Werkzeug/Jinja2 pins change | Upgrade Flask to 3.1; audit and update all extensions to versions compatible with Flask 3.x; resolve all removed API usages |
| `@app.before_first_request` removed | Any one-time startup logic using this decorator stops executing | Move logic into the factory function body, a CLI command, or an explicit `with app.app_context()` block at startup |
| `flask.escape` removed | Import errors at runtime | Replace all `from flask import escape` with `from markupsafe import escape` |
| `FLASK_ENV` removed | Environment detection silently fails or errors | Replace with `FLASK_DEBUG` for debug toggling; use application config classes or `APP_ENV` convention for environment selection |
| `flask._app_ctx_stack` / `flask._request_ctx_stack` removed | AttributeError at runtime | Refactor to use `flask.g`, `current_app`, or context-local proxies as appropriate |
| Global `app` object replaced by factory | Any module importing `app` directly will break | Update all imports to obtain `app` via the factory or use `current_app` proxy within request/application context |
| Extension initialization pattern change | Extensions initialized with `Ext(app)` at module level will not work correctly with factory pattern | Convert all extensions to `ext = Ext()` at module level + `ext.init_app(app)` inside factory |
| Werkzeug ≥ 3.0 required | Werkzeug API changes (e.g., `ImmutableMultiDict`, routing, request/response APIs) may break code using Werkzeug internals directly | TODO — audit direct Werkzeug API usage and update to Werkzeug 3.x API |
| Jinja2 ≥ 3.1 required | Jinja2 template behavior changes (e.g., `Undefined` handling, autoescape defaults) | TODO — audit templates and Jinja2 environment configuration for compatibility |
| Test suite fixture changes | Tests relying on global `app` will fail | Refactor test fixtures to call `create_app()` with a test configuration object; obtain `test_client()` from the factory-produced instance |
| WSGI entry point change | Deployment configuration referencing the global `app` object will fail | Update WSGI entry point to call `create_app()` and expose the returned instance |
| `flask.json` API changes | JSON encoding/decoding behavior or import paths may differ | TODO — audit all `flask.json` usages and update to Flask 3.x API; migrate to stdlib `json` where Flask-specific behavior is not needed |

---

## Acceptance Criteria

1. **Given** the dependency manifest is updated, **when** the application dependencies are installed, **then** Flask 3.1.x, Werkzeug ≥ 3.0, and Jinja2 ≥ 3.1 are the resolved versions with no dependency conflicts.

2. **Given** the refactored codebase, **when** a static analysis or grep is performed for `@app.before_first_request`, `flask.escape`, `flask._app_ctx_stack`, `flask._request_ctx_stack`, and `FLASK_ENV`, **then** zero occurrences are found.

3. **Given** the refactored codebase, **when** the application module is inspected, **then** a `create_app` function exists that accepts a configuration parameter and returns a fully initialized `Flask` application instance.

4. **Given** the factory function is called with a production configuration, **when** the returned application instance is inspected, **then** all registered blueprints, extensions, and configuration values are present and correctly initialized.

5. **Given** the factory function is called with a test configuration, **when** `app.testing` is checked on the returned instance, **then** it is `True` and a test client can be obtained from the instance without referencing any global `app` object.

6. **Given** the full test suite, **when** all tests are executed against the factory-produced test application instance, **then** all previously passing tests continue to pass with no regressions.

7. **Given** the WSGI entry point, **when** the application is started via the WSGI server, **then** the server successfully serves requests by invoking the `create_app()` factory — not a module-level global `app` object.

8. **Given** all Flask extensions in use, **when** the application starts, **then** each extension is initialized via the `init_app(app)` pattern inside the factory, and no extension is initialized with a direct `Ext(app)` call at module import time.

9. **Given** the application is running under Flask 3.1, **when** any previously supported HTTP endpoint is called, **then** the response status code and body match the expected values defined in the existing integration test suite.

10. **Given** the CI pipeline, **when** a build is triggered, **then** the pipeline completes successfully with no import errors, no deprecation warnings escalated to errors, and all tests passing.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact Flask 1.x patch version currently in use? This affects the precise delta of removed APIs to address. | TODO | TODO |
| 2 | Which Flask extensions are in use, and have their maintainers released Flask 3.x-compatible versions? | TODO | TODO |
| 3 | Is there any direct usage of Werkzeug internals (routing, request/response classes, data structures) that will be broken by the Werkzeug 3.x upgrade? | TODO | TODO |
| 4 | Are there any Jinja2 template behaviors (e.g., autoescape, undefined handling, custom filters) that are affected by the Jinja2 3.1 upgrade? | TODO | TODO |
| 5 | What is the intended configuration mechanism inside `create_app`? (e.g., environment variable, config object, config file path) | TODO | TODO |
| 6 | Are there any background workers, CLI commands (`flask.cli`), or Celery tasks that hold a reference to the global `app` object and need to be updated? | TODO | TODO |
| 7 | Does the deployment environment (WSGI server, container, PaaS) have any constraints on how the application entry point is specified that would affect the factory pattern adoption? | TODO | TODO |
| 8 | Are there any third-party integrations (e.g., APM agents, middleware) that wrap the global `app` object and need to be updated to wrap the factory output instead? | TODO | TODO |
| 9 | What Python runtime version is in use, and is it compatible with Flask 3.1 (requires Python ≥ 3.9)? | TODO | TODO |
| 10 | Is there an existing test coverage baseline, and what is the minimum acceptable coverage threshold to validate no regressions? | TODO | TODO |