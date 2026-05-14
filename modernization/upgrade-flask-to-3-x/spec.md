# Flask 3.x Upgrade SPEC

## Current State

### Interfaces & APIs
- **Framework version:** Flask 2.x (assumed based on upgrade target)
- **App import:** Typically uses `from flask import Flask`.
- **Request/Response flow:** Handled via flask.Request, flask.Response objects.
- **Error handling:** Uses Werkzeug exceptions and `@app.errorhandler`.
- **CLI commands:** Uses `flask` command-line.
- **Route decorators:** `@app.route`, `@app.before_request`, `@app.after_request`.
- **Extensions:** Various Flask extensions (version compatibility varies).
- **Jinja2 templates:** Default templating system.
- **Blueprint registration:** Via `app.register_blueprint`.
- **Testing:** Uses `flask.testing.FlaskClient`.

### Data Models
- **N/A — not applicable to this task**
  - The upgrade does not directly affect ORM or database models.

### Key Behaviours
- Application startup and teardown using `@app.before_first_request`, `@app.teardown_appcontext`.
- Synchronous view function support (async support present but limited).
- Uses Werkzeug 2.x as dependency.

## Target State

### Interfaces & APIs
- **Framework version:** Flask 3.x
- **App import/API:** Largely unchanged, but several deprecations and stricter contract.
- **Request/Response flow:** `flask.Request`/`flask.Response`, with changes to error handling and some API cleanups.
- **Error handling:** Some exception classes moved/removed, error handling behavior cleaned up.
- **CLI commands:** Largely unchanged.
- **Route decorators:** Synchronous *and* asynchronous view functions are first-class.
- **Extensions:** Must be compatible with Flask 3.x (see Compatibility section).
- **Jinja2 changes:** Avoid legacy APIs in blueprints/templates.
- **Blueprint registration:** More stringent error-throwing on misusage.
- **Testing:** `flask.testing.FlaskClient` improved for async; legacy methods deprecated.

### Data Models
- **N/A — not applicable to this task**

### Key Behaviours
- App startup/teardown hooks continue to work; slight changes for async/await.
- **Werkzeug 3.x** required by Flask 3.x.

## Compatibility & Breaking Changes

### 1. Werkzeug Dependency
- **Breaking change:** Flask 3.x requires Werkzeug 3.x. Some objects/functions/classes may have moved or been removed.
- **Migration:** Upgrade Werkzeug to 3.x and update imports/usages per Werkzeug changelog.

### 2. Removed/Changed APIs
- **Deprecation removals:** Several APIs deprecated in Flask 2.x are now removed. Notably:
  - `flask.safe_join` has been removed (use `werkzeug.utils.safe_join`).
  - `flask.json_available` removed.
  - `app.session_cookie_name` property removed; use `app.config["SESSION_COOKIE_NAME"]`.
- **Migration:** Refactor all uses per the [Flask 3.0 Migration Guide](https://flask.palletsprojects.com/en/3.0.x/changes/#version-3-0-0).

### 3. Error Handling and Exceptions
- **Breaking change:** Some exceptions moved/removed; application code may need updated import statements.
- **Migration:** Update import paths and usages per Flask 3.x and Werkzeug 3.x docs.

### 4. Async View Functions
- **Change:** Async views now fully supported and may require async test clients.
- **Migration:** For code/tests using async, ensure `await`/`async` patterns are correct as per [Flask async docs](https://flask.palletsprojects.com/en/3.0.x/async-await/).

### 5. Extension Compatibility
- **Breaking change:** Extensions not compatible with Flask 3.x will break.
- **Migration:** Upgrade all Flask extensions to latest versions supporting Flask 3.x.

### 6. Testing API Changes
- **Change:** Some test client APIs deprecated/removed.
- **Migration:** Update tests to use current `app.test_client()` patterns.

### 7. Import Changes
- **Breaking change:** Several imports moved/removed (see above).
- **Migration:** Search codebase for deprecated/removed APIs and update.

## Key Flows (before vs after)

### 1. View Registration and Routing

**Before (Flask 2.x):**
1. Define view functions (sync or async).
2. Register with `@app.route`.
3. Extension loading/blueprint registration.

**After (Flask 3.x):**
1. Define view functions (sync or async, async now fully supported).
2. Register as before with `@app.route`.
3. Extension/blueprint registration as before (but extensions must be Flask 3.x compatible).

### 2. Exception Handling

**Before (Flask 2.x):**
- Use `from flask import abort`, handle errors with `@app.errorhandler`.

**After (Flask 3.x):**
- Same, but ensure all exception classes exist in their new locations (may need to import from Werkzeug).

### 3. Testing

**Before (Flask 2.x):**
- Use `app.testing = True; client = app.test_client()`.
- Use legacy send patterns.

**After (Flask 3.x):**
- Use updated FlaskClient.
- When using async, tests should be async as per Flask 3.x testing docs.

## Data Model Changes

N/A — not applicable to this task

## Configuration Changes

### 1. SESSION_COOKIE_NAME
- **Before:** `app.session_cookie_name`
- **After:** Use `app.config["SESSION_COOKIE_NAME"]`

### 2. Extension-Related Configs
- **Migration:** Update any extension configs as needed per their Flask 3.x compatibility docs.

### 3. Environment Variables, Feature Flags
- N/A — not applicable to this task unless extension upgrades specify changes.

---

*References:*
- https://flask.palletsprojects.com/en/3.0.x/changes/
- https://werkzeug.palletsprojects.com/en/3.0.x/changes/
- https://flask.palletsprojects.com/en/3.0.x/async-await/
- https://flask.palletsprojects.com/en/3.0.x/migrating/