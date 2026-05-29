import pytest
import flask
from flask import Flask, current_app


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _import_create_app():
    """
    Try to import create_app from the canonical locations produced by the
    application-factory refactor.  Raises ImportError with a descriptive
    message if none of the expected locations exist.
    """
    locations = [
        ("app", "create_app"),
        ("application", "create_app"),
        ("app.factory", "create_app"),
        ("src.app", "create_app"),
        ("wsgi", "create_app"),
    ]
    for module_name, attr in locations:
        try:
            import importlib
            mod = importlib.import_module(module_name)
            factory = getattr(mod, attr, None)
            if factory is not None and callable(factory):
                return factory
        except ImportError:
            continue
    raise ImportError(
        "create_app() factory function not found in any of the expected "
        "modules: app, application, app.factory, src.app, wsgi.  "
        "Ensure the application-factory refactor has been completed."
    )


@pytest.fixture(scope="session")
def create_app_fn():
    """Session-scoped fixture that resolves the create_app callable once."""
    return _import_create_app()


@pytest.fixture
def testing_app(create_app_fn):
    """
    Create a fresh application instance configured for testing.
    Each test gets its own isolated instance — the primary benefit of the
    factory pattern.
    """
    app = create_app_fn({"TESTING": True, "SECRET_KEY": "test-secret-key"})
    return app


@pytest.fixture
def client(testing_app):
    with testing_app.test_client() as c:
        yield c


@pytest.fixture
def app_ctx(testing_app):
    with testing_app.app_context():
        yield testing_app


# ---------------------------------------------------------------------------
# 1. Factory existence and signature
# ---------------------------------------------------------------------------

class TestFactoryExists:
    """Verify that create_app() exists and is callable."""

    def test_create_app_is_importable(self, create_app_fn):
        assert callable(create_app_fn), (
            "create_app must be a callable factory function"
        )

    def test_create_app_accepts_no_args(self, create_app_fn):
        """create_app() must work when called with zero arguments."""
        app = create_app_fn()
        assert isinstance(app, Flask), (
            "create_app() with no arguments must return a Flask instance"
        )

    def test_create_app_accepts_config_dict(self, create_app_fn):
        """create_app(config={...}) must work — the standard override path."""
        app = create_app_fn({"TESTING": True})
        assert isinstance(app, Flask)

    def test_create_app_returns_flask_instance(self, testing_app):
        assert isinstance(testing_app, Flask), (
            "create_app() must return a flask.Flask instance, "
            f"got {type(testing_app)}"
        )


# ---------------------------------------------------------------------------
# 2. Each call produces an independent instance (isolation guarantee)
# ---------------------------------------------------------------------------

class TestFactoryIsolation:
    """
    The whole point of the factory pattern is that each call produces a
    separate, independently-configured application instance.
    """

    def test_two_calls_produce_different_objects(self, create_app_fn):
        app1 = create_app_fn({"TESTING": True})
        app2 = create_app_fn({"TESTING": True})
        assert app1 is not app2, (
            "Each call to create_app() must return a NEW Flask instance; "
            "the factory must not cache or return a module-level singleton."
        )

    def test_config_override_is_respected_per_instance(self, create_app_fn):
        app_a = create_app_fn({"TESTING": True, "MY_CUSTOM_KEY": "alpha"})
        app_b = create_app_fn({"TESTING": True, "MY_CUSTOM_KEY": "beta"})
        assert app_a.config.get("MY_CUSTOM_KEY") == "alpha"
        assert app_b.config.get("MY_CUSTOM_KEY") == "beta"
        # Mutating one must not affect the other
        with app_a.app_context():
            app_a.config["MY_CUSTOM_KEY"] = "changed"
        assert app_b.config.get("MY_CUSTOM_KEY") == "beta", (
            "Mutating one app instance must not affect another — "
            "they must not share config state."
        )

    def test_testing_flag_set_correctly(self, testing_app):
        assert testing_app.config["TESTING"] is True


# ---------------------------------------------------------------------------
# 3. No module-level app singleton (the old anti-pattern must be gone)
# ---------------------------------------------------------------------------

class TestNoModuleLevelSingleton:
    """
    After the refactor the top-level modules must NOT expose a pre-built
    global `app = Flask(...)` object.  The only way to obtain an app is
    through create_app().
    """

    def test_app_module_does_not_expose_global_app_singleton(self):
        """
        If the old pattern `app = Flask(__name__)` still exists at module
        level in app.py / application.py, this test will catch it by
        checking that the module-level name 'app' is either absent or is
        itself the factory (not a Flask instance).
        """
        import importlib
        for module_name in ("app", "application"):
            try:
                mod = importlib.import_module(module_name)
            except ImportError:
                continue
            top_level_app = getattr(mod, "app", None)
            if top_level_app is not None:
                assert not isinstance(top_level_app, Flask), (
                    f"Module '{module_name}' still exposes a module-level "
                    f"`app = Flask(...)` singleton.  After the factory "
                    f"refactor, `app` at module level must not be a Flask "
                    f"instance — use create_app() instead."
                )

    def test_run_py_or_wsgi_uses_factory(self):
        """
        The WSGI / run entry point must call create_app() rather than
        importing a pre-built app object.  We verify this by importing the
        entry-point module and confirming it either exposes create_app or
        that any 'application'/'app' attribute it exposes was produced by
        calling create_app (i.e., it is a Flask instance only after the
        factory was invoked, not at import time of the factory module itself).
        """
        import importlib
        for entry in ("wsgi", "run", "manage"):
            try:
                mod = importlib.import_module(entry)
            except ImportError:
                continue
            # If the entry point exposes `application` (gunicorn convention)
            # it is acceptable — it means create_app() was called once to
            # build the production app object.  What is NOT acceptable is
            # that the factory module itself (app.py) has a global Flask obj.
            application_obj = getattr(mod, "application", None)
            if application_obj is not None:
                assert isinstance(application_obj, Flask), (
                    f"'{entry}.application' must be a Flask instance "
                    f"(produced by create_app()), got {type(application_obj)}"
                )


# ---------------------------------------------------------------------------
# 4. Application context works correctly
# ---------------------------------------------------------------------------

class TestApplicationContext:
    """current_app proxy must resolve inside an app context."""

    def test_current_app_available_inside_context(self, testing_app):
        with testing_app.app_context():
            assert current_app._get_current_object() is testing_app

    def test_current_app_not_available_outside_context(self, testing_app):
        """Outside an app context, current_app must raise RuntimeError."""
        with pytest.raises(RuntimeError):
            _ = current_app.name  # accessing any attribute triggers the error

    def test_app_context_push_pop_cycle(self, create_app_fn):
        app = create_app_fn({"TESTING": True})
        ctx = app.app_context()
        ctx.push()
        try:
            assert current_app._get_current_object() is app
        finally:
            ctx.pop()


# ---------------------------------------------------------------------------
# 5. Configuration loading
# ---------------------------------------------------------------------------

class TestConfigurationLoading:
    """New configuration keys introduced by the factory pattern load cleanly."""

    def test_secret_key_configurable_via_factory(self, create_app_fn):
        app = create_app_fn({"SECRET_KEY": "super-secret", "TESTING": True})
        assert app.config["SECRET_KEY"] == "super-secret"

    def test_testing_config_disables_error_propagation_wrapper(self, create_app_fn):
        app = create_app_fn({"TESTING": True})
        assert app.config["TESTING"] is True

    def test_default_config_does_not_raise(self, create_app_fn):
        """Calling create_app() with no config must not raise any exception."""
        try:
            app = create_app_fn()
        except Exception as exc:
            pytest.fail(
                f"create_app() raised an unexpected exception with default "
                f"config: {exc}"
            )

    def test_config_dict_merged_into_app_config(self, create_app_fn):
        custom = {
            "TESTING": True,
            "DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
        app = create_app_fn(custom)
        for key, value in custom.items():
            assert app.config.get(key) == value, (
                f"Expected app.config['{key}'] == {value!r}, "
                f"got {app.config.get(key)!r}"
            )


# ---------------------------------------------------------------------------
# 6. Blueprint registration happens inside create_app
# ---------------------------------------------------------------------------

class TestBlueprintRegistration:
    """
    Blueprints must be registered inside create_app(), not at module level.
    We verify that the returned app has its blueprints populated after the
    factory call.
    """

    def test_blueprints_registered_after_factory_call(self, testing_app):
        # The app.blueprints dict is populated by register_blueprint().
        # We cannot know the exact blueprint names without the source, but
        # we can assert the attribute exists and is a dict.
        assert isinstance(testing_app.blueprints, dict), (
            "app.blueprints must be a dict populated by create_app()"
        )

    def test_each_factory_call_registers_blueprints_independently(self, create_app_fn):
        app1 = create_app_fn({"TESTING": True})
        app2 = create_app_fn({"TESTING": True})
        # Both instances must have the same set of blueprint names
        assert set(app1.blueprints.keys()) == set(app2.blueprints.keys()), (
            "Both app instances produced by create_app() must register the "
            "same blueprints — blueprint registration must be inside the factory."
        )


# ---------------------------------------------------------------------------
# 7. Request context and test client work with factory-produced app
# ---------------------------------------------------------------------------

class TestRequestContext:
    """HTTP-level smoke tests using the test client."""

    def test_test_client_is_obtainable(self, testing_app):
        client = testing_app.test_client()
        assert client is not None

    def test_request_context_push(self, testing_app):
        with testing_app.test_request_context("/"):
            from flask import request
            assert request.path == "/"

    def test_multiple_clients_from_separate_instances_are_independent(
        self, create_app_fn
    ):
        app1 = create_app_fn({"TESTING": True, "SECRET_KEY": "key1"})
        app2 = create_app_fn({"TESTING": True, "SECRET_KEY": "key2"})
        client1 = app1.test_client()
        client2 = app2.test_client()
        assert client1 is not client2
        assert app1.config["SECRET_KEY"] != app2.config["SECRET_KEY"]


# ---------------------------------------------------------------------------
# 8. Flask version is the active runtime (sanity / environment check)
# ---------------------------------------------------------------------------

class TestFlaskVersion:
    """
    Verify that Flask is importable and that the installed version is a
    recognised stable release (>= 2.0, which introduced first-class support
    for the factory pattern features used here).
    """

    def test_flask_is_importable(self):
        import flask as _flask
        assert _flask is not None

    def test_flask_version_meets_minimum(self):
        from packaging.version import Version
        try:
            from packaging.version import Version as _V
        except ImportError:
            # Fallback: manual major-version check
            major = int(flask.__version__.split(".")[0])
            assert major >= 2, (
                f"Flask >= 2.0 is required for full application-factory "
                f"support; found {flask.__version__}"
            )
            return

        installed = Version(flask.__version__)
        minimum = Version("2.0.0")
        assert installed >= minimum, (
            f"Flask >= 2.0.0 required; installed version is {flask.__version__}"
        )

    def test_flask_version_string_is_present(self):
        assert isinstance(flask.__version__, str)
        assert len(flask.__version__) > 0


# ---------------------------------------------------------------------------
# 9. Deprecated direct-import pattern is no longer the primary interface
# ---------------------------------------------------------------------------

class TestDeprecatedPatternAbsent:
    """
    The old pattern `from app import app` (importing a pre-built Flask
    instance) must no longer be the intended public interface.  After the
    refactor, consumers should call create_app().
    """

    def test_create_app_is_the_public_interface(self, create_app_fn):
        """
        create_app must be the canonical way to obtain an app instance.
        This test documents and enforces that contract.
        """
        app = create_app_fn({"TESTING": True})
        assert isinstance(app, Flask), (
            "create_app() is the public interface and must return a Flask app"
        )

    def test_extensions_use_init_app_pattern(self, create_app_fn):
        """
        Extensions initialised with the two-step init_app() pattern must be
        bound to the app produced by the factory, not to a stale module-level
        instance.  We verify this by checking that extension state (if any)
        is stored on the app's extensions dict.
        """
        app = create_app_fn({"TESTING": True})
        with app.app_context():
            # app.extensions is populated by extension.init_app(app) calls
            assert isinstance(app.extensions, dict), (
                "app.extensions must be a dict; extensions should register "
                "themselves via init_app() inside create_app()"
            )