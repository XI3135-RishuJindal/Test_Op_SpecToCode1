# SPEC: Upgrade Flask to 3.x

## Current State

- **Flask Version:** 2.x (example: Flask 2.2.x)
- **Dependencies:** Various Flask-compatible extensions (e.g., flask-restful, flask-login), may rely on implicit async handling and features deprecated in Flask 2.x.
- **Application Interfaces:**
    - Usage of `flask.app.Flask` and classic synchronous route handlers
    - May use deprecated APIs like `flask.ext.*`
    - Error handlers using old syntax
    - Some extensions not yet vetted for Flask 3.x compatibility
- **Configuration:**
    - Standard config files (`config.py`, `app.config[...]`)
    - Potential use of legacy environment variables and config keys
- **Key Behaviors:**
    - Synchronous route handling prevalent
    - Potential reliance on reloader behavior and default werkzeug server
    - Implicit behavior for async code unsupported

## Target State

- **Flask Version:** 3.x (example: Flask 3.0.x)
- **Dependencies:** All major dependencies confirmed compatible with Flask 3.x
    - **flask-restful** 0.3.10+ or latest
    - **flask-login** 0.6.3+ or latest
    - **werkzeug** 3.x
    - Extensions replaced if unmaintained/incompatible
- **Application Interfaces:**
    - All route handlers explicitly synchronous or properly async (if desired)
    - No usage of removed/deprecated APIs (e.g., `flask.ext.*`)
    - Updated error handler signatures as required by Flask 3.x
- **Configuration:**
    - Updated config files for deprecated/removed config keys
    - Use of new environment variables or configs if required
- **Key Behaviors:**
    - Async route handling works as per Flask 3.x behavior
    - Uses the new `flask run`/reloader approach
    - No reliance on implicit/legacy behavior

## Compatibility & Breaking Changes

| Area                         | Breaking Change                                                                     | Migration Path                                                          |
|------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| API Import Paths              | Removal of `flask.ext.*` namespace                                                 | Update imports to use standard extension package (e.g. `import flask_login`) |
| Error Handler Signature       | Error handlers now require positional-only arguments for exceptions                 | Update handler function signatures to match new requirements             |
| Synchronous vs Async Routes   | Implicit async no longer supported; explicit async/await required                   | Refactor handlers: mark with `async def` if truly async, else keep sync  |
| Werkzeug Compatibility       | werkzeug 3.x removes some deprecated utilities                                      | Refactor usage of removed werkzeug APIs or downgrade/replace dependencies|
| Deprecated Config Keys        | Removal of deprecated config keys (e.g., `PREFERRED_URL_SCHEME`)                   | Remove/replace usage in config files and code                            |
| Extension Support             | Some Flask extensions incompatible with 3.x                                         | Upgrade to compatible versions; find alternatives if needed              |

## Key Flows (before vs after)

**1. Route Handler Registration**

_Before (Flask 2.x):_
```python
@app.route('/foo')
def foo():
    return 'bar'
```

_After (Flask 3.x):_
```python
@app.route('/foo')
def foo():
    return 'bar'
# OR, if async:
@app.route('/foo')
async def foo():
    return 'bar'
```
_Explicitly distinguish between sync and async handlers as needed._

---

**2. Extension Usage**

_Before:_
```python
from flask.ext.login import LoginManager
```

_After:_
```python
from flask_login import LoginManager
```

---

**3. Error Handling Registration**

_Before:_
```python
@app.errorhandler(Exception)
def handle_error(e):
    return str(e), 500
```

_After (Flask 3.x requires positional-only for error handler):_
```python
@app.errorhandler(Exception)
def handle_error(e, /):
    return str(e), 500
```

## Data Model Changes

N/A — not applicable to this task

## Configuration Changes

- **Deprecated Config Keys:** Remove deprecated keys like `PREFERRED_URL_SCHEME` if present.
- **Werkzeug/Flask CLI:** If using environment variables such as `FLASK_ENV`, note that `FLASK_ENV=development` is now deprecated; use `FLASK_DEBUG=1` instead.

| Config Key            | Before (2.x)                  | After (3.x)            | Action                      |
|-----------------------|-------------------------------|------------------------|-----------------------------|
| FLASK_ENV             | development                   | N/A; use FLASK_DEBUG   | Remove/replace              |
| PREFERRED_URL_SCHEME  | http/https                    | Removed                | Remove from config          |
| Other Flask-specific  | Legacy keys potentially used  | Confirm all supported  | Validate & update as needed |

---

**End of SPEC.**