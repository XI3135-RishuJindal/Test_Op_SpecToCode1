# Spec: Upgrade Flask 1.x → 3.1 and Adopt Application Factory Pattern

---

## Summary

This spec covers the upgrade of Flask from version 1.x to version 3.1 and the concurrent adoption of the application factory pattern across the application. The expected outcome is a fully functional Flask 3.1 application where the `app` object is created via a dedicated factory function rather than at module import time, eliminating global-state side effects, improving testability, and aligning the codebase with current Flask best practices.

---

## Motivation

| Driver | Detail | Urgency |
|---|---|---|
| Flask 1.x end-of-life | Flask 1.x receives no security patches or bug fixes; the final 1.x release is effectively abandoned upstream. | Medium |
| Security exposure | Flask 1.x depends on Werkzeug and Jinja2 versions that carry unpatched CVEs in newer advisories; upgrading to Flask 3.1 pulls in current, patched dependency versions. | Medium |
| Python compatibility | Flask 3.x drops support for Python < 3.8 and aligns with the currently supported CPython release train; Flask 1.x cannot be installed alongside modern Python tooling without conflict. | Medium |
| Tech debt | The current module-level `app = Flask(__name__)` pattern makes isolated unit testing difficult, prevents multiple configurations from coexisting, and couples extension initialization to import order. | Medium |
| Dependency hygiene | Flask 3.1 requires Werkzeug ≥ 3.1 and Jinja2 ≥ 3.1, both of which contain performance improvements and security fixes absent in the versions pinned by Flask 1.x. | Medium |

> **Note:** Specific CVE identifiers and exact current Flask 1.x patch version were not provided in the tech analysis. See Open Questions.

---

## Current State

> **Note:** No source code was provided with this task. The following describes the canonical Flask 1.x patterns that must be addressed. Specific class names, config keys, and schema elements are marked TODO where they cannot be confirmed without codebase access.

### Application Instantiation
- A module-level statement such as `app = Flask(__name__)` creates the application object at import time.
- Extensions (e.g., SQLAlchemy, Login Manager, Migrate) are initialized directly against this global `app` object at module scope.
- Configuration is applied directly to `app.config` at module level, typically reading from a single config object or environment variable.

### Blueprints & Route Registration
- Routes are registered either directly on the global `app` object or via `Blueprint` objects that are registered against it at import time.
- Any circular import issues are currently worked around by import ordering rather than factory-based deferred initialization.

### Entry Point
- The application is started by referencing the global `app` object directly (e.g., `app.run()` in a `__main__` block, or by pointing a WSGI server at the module-level `app`).
- The `FLASK_APP` environment variable currently points to the module exposing the global `app`.

### Deprecated / Removed APIs in Flask 1.x that are used (TODO)
- TODO: Confirm whether `before_first_request` decorator is used (removed in Flask 2.3+).
- TODO: Confirm whether `flask.json` module helpers (`flask.json.provider` API changed in Flask 2.2).
- TODO: Confirm whether `flask.escape` / `flask.Markup` are used (moved to `markupsafe` in Flask 2.x).
- TODO: Confirm whether `flask.signals` (Blinker) usage is present (made a hard dependency in Flask 2.3).
- TODO: Confirm whether `flask.ext.*` import shim is used (removed in Flask 1.0, but confirm absence).
- TODO: Identify all `app.config` keys in use.
- TODO: Identify all registered Flask extensions and their current versions.

---

## Proposed Changes

### Component Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Flask version | 1.x (exact patch TODO) | 3.1 | Y |
| Werkzeug version | < 2.x (pinned by Flask 1.x) | ≥ 3.1 (required by Flask 3.1) | Y |
| Jinja2 version | < 3.x (pinned by Flask 1.x) | ≥ 3.1 (required by Flask 3.1) | Y |
| Application object creation | Module-level `app = Flask(__name__)` | Factory function `create_app(config=None)` returning a configured `Flask` instance | Y |
| Extension initialization | Called directly on global `app` at import time | Called inside `create_app` via `extension.init_app(app)` pattern | Y |
| Blueprint registration | Registered against global `app` at import time | Registered inside `create_app` after extensions are initialized | N |
| Configuration loading | Applied to global `app.config` at module scope | Passed into or resolved inside `create_app`; supports per-environment config objects | N |
| Entry point / WSGI target | Points to module-level `app` symbol | Points to the return value of `create_app()` or uses `FLASK_APP=module:create_app` | Y |
| `before_first_request` usage | Decorator available in Flask 1.x | Removed in Flask 2.3; replaced with explicit initialization inside `create_app` or `with app.app_context()` | Y |
| `flask.escape` / `flask.Markup` | Importable from `flask` | Must be imported from `markupsafe` | Y |
| JSON provider | `flask.json` helpers (Flask 1.x API) | `app.json` provider interface (Flask 2.2+ API) | Y |
| Blinker (signals) | Optional dependency | Hard dependency in Flask 2.3+; must be explicitly declared | Y |
| Test client setup | Tests instantiate or import global `app` directly | Tests call `create_app` with a test config to obtain an isolated instance | Y |

### What Is Removed
- Global module-level `app` object as a public symbol.
- Any usage of `@app.before_first_request`.
- Any imports of `flask.escape` or `flask.Markup` from the `flask` namespace.
- Any Flask 1.x-only configuration or compatibility shims.

### What Is Added
- `create_app(config=None)` factory function as the canonical application entry point.
- Per-environment configuration support enabled by the factory signature.
- Explicit `init_app(app)` calls for all extensions, scoped inside the factory.
- Test fixtures that call `create_app` with an isolated test configuration.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Global `app` symbol removed | Any module that imports `app` directly from the application module will break | Callers must obtain the app via `create_app()` or use Flask's `current_app` proxy within a request/application context |
| `before_first_request` removed (Flask 2.3) | Any setup logic registered with this decorator will not run | Move logic into `create_app` body or invoke it explicitly inside `with app.app_context()` during startup |
| `flask.escape` / `flask.Markup` removed from `flask` namespace | Import errors at runtime | Update all import sites to import from `markupsafe` directly |
| Werkzeug 3.x API changes | Internal use of Werkzeug utilities (routing, request, response objects) may break | Audit all direct Werkzeug imports; consult Werkzeug 3.x changelog for removed APIs — TODO: enumerate specific usages |
| Jinja2 3.x API changes | Custom Jinja2 extensions or environment manipulation may break | TODO: audit custom Jinja2 usage against Jinja2 3.x changelog |
| `flask.json` provider API changed (Flask 2.2) | Custom JSON encoding/decoding registered via old API will not apply | Migrate to `app.json_provider_class` or `app.json` provider interface |
| Blinker now a hard dependency | Environments without Blinker installed will fail to start | Add `blinker` to the declared dependencies |
| WSGI entry point change | Deployment configuration pointing to module-level `app` will break | Update `FLASK_APP`, WSGI server config, and any process manager config to reference `create_app` factory or its return value |
| Extension versions pinned to Flask 1.x | Flask extensions pinned to old versions may be incompatible with Flask 3.1 | TODO: audit each extension (Flask-SQLAlchemy, Flask-Login, Flask-Migrate, etc.) and upgrade to versions compatible with Flask 3.1 |
| Test setup using global `app` | Existing tests that import the global `app` will fail or share state between test cases | Refactor test fixtures to call `create_app` with `TESTING=True` config per test or test session |

---

## Acceptance Criteria

1. **Given** the application dependencies are installed, **when** the dependency manifest is inspected, **then** Flask 3.1.x, Werkzeug ≥ 3.1, Jinja2 ≥ 3.1, and Blinker are all declared and resolved without version conflicts.

2. **Given** the application source, **when** a static analysis scan is run for the symbol `app = Flask(`, **then** no such module-level instantiation exists outside of the `create_app` factory function.

3. **Given** the `create_app` factory, **when** it is called with no arguments, **then** it returns a fully configured, runnable `Flask` application instance without raising any exception.

4. **Given** the `create_app` factory, **when** it is called with a test configuration object, **then** it returns a separate `Flask` instance whose configuration reflects the test overrides and which shares no mutable state with any other instance created in the same process.

5. **Given** the application is started via the WSGI entry point, **when** a valid HTTP request is sent to each registered route, **then** the response status code and body match the pre-upgrade baseline for that route.

6. **Given** the full test suite, **when** it is executed against the Flask 3.1 application, **then** all tests pass and no test relies on a globally imported `app` object.

7. **Given** the codebase, **when** a static analysis scan is run for imports of `flask.escape` or `flask.Markup`, **then** no such imports are found.

8. **Given** the codebase, **when** a static analysis scan is run for usage of `@app.before_first_request` or `@blueprint.before_app_first_request`, **then** no such usages are found.

9. **Given** the application running under Flask 3.1, **when** all registered Flask extensions are initialized via `init_app(app)` inside `create_app`, **then** no extension raises a compatibility error or deprecation warning that is treated as an error in CI.

10. **Given** the deployment configuration, **when** the WSGI server or process manager starts the application, **then** it successfully resolves the entry point to the `create_app` factory and serves requests without error.

11. **Given** a CI pipeline, **when** a pull request is opened against the main branch, **then** the pipeline runs the full test suite against Flask 3.1 and fails the build if any test fails or any prohibited import pattern is detected.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact current Flask 1.x version pinned in the dependency manifest? | TODO | TODO |
| 2 | Which Flask extensions are in use (e.g., Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF) and what versions are currently pinned? | TODO | TODO |
| 3 | Are there any direct Werkzeug imports in application code that may be affected by Werkzeug 3.x breaking changes? | TODO | TODO |
| 4 | Is `before_first_request` currently used anywhere in the codebase? | TODO | TODO |
| 5 | Are `flask.escape` or `flask.Markup` imported anywhere in the codebase? | TODO | TODO |
| 6 | Are there custom Jinja2 extensions or environment modifications that need to be validated against Jinja2 3.x? | TODO | TODO |
| 7 | What is the current WSGI server and deployment configuration (e.g., Gunicorn, uWSGI, serverless)? Entry point update approach depends on this. | TODO | TODO |
| 8 | Are there specific CVE identifiers driving the urgency of this upgrade that should be tracked in the security backlog? | TODO | TODO |
| 9 | Is there a custom JSON encoder/decoder registered via the Flask 1.x `flask.json` API that must be migrated to the Flask 2.2+ provider interface? | TODO | TODO |
| 10 | What Python version is the runtime using? Flask 3.1 requires Python ≥ 3.9 — confirm the runtime meets this requirement. | TODO | TODO |
| 11 | Are there any third-party packages (not Flask extensions) that have a transitive dependency on Flask 1.x and would conflict with Flask 3.1? | TODO | TODO |