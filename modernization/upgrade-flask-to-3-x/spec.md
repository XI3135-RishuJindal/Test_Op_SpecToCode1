# Flask Modernization Spec: Upgrade to 3.x

## Current State

- **Flask Version:** 2.x  
- **Interfaces/APIs:**  
  - Application instances via `Flask(__name__)`
  - Blueprints, `@app.route`, view functions
  - Extensions: Possible usage of Flask extensions (not exhaustively known)
  - Usage of imports such as `from flask import ...`
- **Data Models:**  
  - N/A — Flask is a web framework, does not define core data models in the app
- **Key Behaviours:**  
  - Synchronous request handling
  - Implicit reloading behaviours
  - Legacy API imports: usage of e.g., `flask.json`, `flask.ext`, or direct access to config objects

## Target State

- **Flask Version:** 3.x
- **Interfaces/APIs:**  
  - Application instantiation is unchanged
  - `flask.ext.*` is **not supported**; all extensions must use fully-qualified import paths.
  - Some built-in methods (e.g., error handlers, JSON handling) have stricter type requirements.
  - All deprecated aliases and apis removed (ex: `flask.json` moved to `flask.json.provider`)
- **Data Models:**  
  - N/A — not applicable to this task
- **Key Behaviours:**  
  - Stricter type checking and validation
  - Removal of long-since-deprecated APIs
  - Some previously synchronous hooks MAY now offer (or require) async support

## Compatibility & Breaking Changes

| Breaking Change | Migration Path |
|-----------------|---------------|
| Removal of `flask.ext` imports | Replace `from flask.ext.foo import bar` with `from flask_foo import bar` (use the new extension import syntax) |
| Removal of `flask.json.*` | Update imports from `from flask.json import ...` to `from flask.json.provider import ...` or recommended alternative |
| Removal of deprecated APIs | Replace use of APIs flagged as deprecated in Flask 2.x (see release notes for details) |
| Some APIs now keyword-only | Refactor call sites to pass arguments explicitly by name per Flask 3.x release notes |
| Extensions must be compatible with Flask 3.x | Upgrade all Flask extensions to their Flask-3.x compatible versions |
| Synchronous-only hooks may change | For request hooks (`before_request`, etc.), validate whether async implementation is required/beneficial. |

## Key Flows (before vs after)

### App/Extension Import  
**Before:**  
```python
from flask.ext.foo import bar
```
**After:**  
```python
from flask_foo import bar
```

### JSON Import  
**Before:**  
```python
from flask.json import jsonify
```
**After:**  
```python
from flask.json.provider import jsonify
# Or: from flask import jsonify (if still supported by extension)
```

### Extension Compatibility  
**Before:**  
- Extension installed at any version, possibly pre-Flask-3.x

**After:**  
- All extensions upgraded to Flask-3.x compatible release

## Data Model Changes

N/A — not applicable to this task

## Configuration Changes

- **Requirements**:  
  - `Flask>=3.0.0` in requirements.txt (or equivalent build file)
  - All Flask extensions versions audited and updated for Flask 3.x compatibility

- **No new environment variables or config keys** introduced by core Flask.

---