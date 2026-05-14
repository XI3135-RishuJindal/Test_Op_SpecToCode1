import sys
import flask
import pytest

from flask import Flask

# These tests validate that Flask 3.x is *really* active, core endpoints still work,
# deprecated/removed APIs are gone, and new config keys don't error.

TARGET_MAJOR_VERSION = 3  # Accept any Flask 3.x

@pytest.fixture
def app():
    app = Flask(__name__)

    @app.route("/health")
    def health():
        return "ok"

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_flask_version_is_target():
    version = flask.__version__
    major_version = int(version.split(".")[0])
    assert major_version == TARGET_MAJOR_VERSION, f"Expected Flask major version {TARGET_MAJOR_VERSION}, got {version}"

def test_critical_path_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.data == b"ok"

def test_deprecated_apiroute_removed():
    # As of Flask 3.x, flask.ext.* imports are removed.
    # Also test that 'app.json_encoder' (deprecated in Flask 2.3, removed in 3.0) is gone or raises.
    with pytest.raises(AttributeError):
        # JSONEncoder customizations are via app.json (new API)
        Flask(__name__).json_encoder

def test_new_config_key_loads():
    # Flask 3.x introduces the TEMPLATES_AUTO_RELOAD config key (was present earlier, but formalized in docs)
    app = Flask(__name__)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    # It should exist and be retrievable without errors
    assert app.config["TEMPLATES_AUTO_RELOAD"] is True

def test_flask_ext_namespace_gone():
    # 'flask.ext' namespace proxy was removed in Flask 1.0+, but some 1.x-compatible code may still import it.
    # It must NOT be present in Flask 3.x.
    with pytest.raises(ImportError):
        __import__("flask.ext")

def test_json_provider_api_present():
    # In Flask 3.x, app.json_provider_class and app.json are the official APIs.
    app = Flask(__name__)
    assert hasattr(app, "json")
    assert hasattr(app, "json_provider_class")
    # The deprecated app.json_encoder and app.json_decoder must be gone.
    assert not hasattr(app, "json_encoder")
    assert not hasattr(app, "json_decoder")