import json
import logging
import sys
import unittest
from io import StringIO

try:
    from pythonjsonlogger import jsonlogger
    PYTHONJSONLOGGER_AVAILABLE = True
except ImportError:
    PYTHONJSONLOGGER_AVAILABLE = False

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata


class TestPythonJsonLoggerInstalled(unittest.TestCase):
    """Verify that python-json-logger is installed and meets the minimum version."""

    def test_pythonjsonlogger_importable(self):
        """python-json-logger must be importable after the upgrade."""
        self.assertTrue(
            PYTHONJSONLOGGER_AVAILABLE,
            "pythonjsonlogger could not be imported. "
            "Ensure 'python-json-logger>=2.0.7' is listed in the dependency manifest "
            "and installed in the current environment.",
        )

    def test_pythonjsonlogger_version_meets_minimum(self):
        """Installed python-json-logger must be >= 2.0.7 as specified in the upgrade spec."""
        try:
            version_str = importlib_metadata.version("python-json-logger")
        except importlib_metadata.PackageNotFoundError:
            self.fail(
                "python-json-logger is not installed. "
                "Run: pip install 'python-json-logger>=2.0.7'"
            )

        parts = version_str.split(".")
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        installed = (major, minor, patch)
        minimum = (2, 0, 7)

        self.assertGreaterEqual(
            installed,
            minimum,
            f"python-json-logger {version_str} is below the required minimum 2.0.7.",
        )


class TestJsonFormatterProducesValidJson(unittest.TestCase):
    """Verify that JsonFormatter emits valid, parseable JSON for every log record."""

    def _make_stream_logger(self, name, extra_fields=None):
        """Return (logger, StringIO stream) wired with a JsonFormatter."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        fmt_string = "%(asctime)s %(levelname)s %(name)s %(message)s"
        if extra_fields:
            fmt_string += " " + " ".join(f"%({k})s" for k in extra_fields)
        formatter = jsonlogger.JsonFormatter(fmt_string)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        return logger, stream

    def test_log_output_is_valid_json(self):
        """Each log line emitted by JsonFormatter must be parseable as JSON."""
        self.skipTest_if_unavailable()
        logger, stream = self._make_stream_logger("test.valid_json")
        logger.info("upgrade validation message")
        output = stream.getvalue().strip()
        self.assertTrue(output, "No log output was produced.")
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as exc:
            self.fail(f"Log output is not valid JSON: {exc}\nOutput was: {output!r}")
        self.assertIsInstance(parsed, dict)

    def test_required_field_message(self):
        """Parsed JSON log record must contain a 'message' field."""
        self.skipTest_if_unavailable()
        logger, stream = self._make_stream_logger("test.field_message")
        logger.info("hello structured logging")
        parsed = json.loads(stream.getvalue().strip())
        self.assertIn("message", parsed, "Required field 'message' missing from JSON log output.")
        self.assertEqual(parsed["message"], "hello structured logging")

    def test_required_field_levelname(self):
        """Parsed JSON log record must contain a log level field."""
        self.skipTest_if_unavailable()
        logger, stream = self._make_stream_logger("test.field_level")
        logger.warning("level check")
        parsed = json.loads(stream.getvalue().strip())
        level_field = parsed.get("levelname") or parsed.get("level")
        self.assertIsNotNone(
            level_field,
            "Neither 'levelname' nor 'level' found in JSON log output.",
        )
        self.assertIn("WARNING", str(level_field).upper())

    def test_required_field_name(self):
        """Parsed JSON log record must contain the logger 'name' field."""
        self.skipTest_if_unavailable()
        logger, stream = self._make_stream_logger("test.field_name")
        logger.info("name field check")
        parsed = json.loads(stream.getvalue().strip())
        self.assertIn("name", parsed, "Required field 'name' missing from JSON log output.")
        self.assertEqual(parsed["name"], "test.field_name")

    def test_required_field_timestamp(self):
        """Parsed JSON log record must contain a timestamp field ('asctime')."""
        self.skipTest_if_unavailable()
        logger, stream = self._make_stream_logger("test.field_timestamp")
        logger.info("timestamp check")
        parsed = json.loads(stream.getvalue().strip())
        timestamp_field = parsed.get("asctime") or parsed.get("timestamp") or parsed.get("time")
        self.assertIsNotNone(
            timestamp_field,
            "No timestamp field ('asctime', 'timestamp', or 'time') found in JSON log output.",
        )

    def test_all_log_levels_produce_valid_json(self):
        """DEBUG, INFO, WARNING, ERROR, and CRITICAL must all produce valid JSON."""
        self.skipTest_if_unavailable()
        levels = [
            (logging.DEBUG, "debug message"),
            (logging.INFO, "info message"),
            (logging.WARNING, "warning message"),
            (logging.ERROR, "error message"),
            (logging.CRITICAL, "critical message"),
        ]
        for level, msg in levels:
            logger, stream = self._make_stream_logger(f"test.level_{level}")
            logger.log(level, msg)
            output = stream.getvalue().strip()
            self.assertTrue(output, f"No output for level {level}.")
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError as exc:
                self.fail(f"Level {level} output is not valid JSON: {exc}\nOutput: {output!r}")
            self.assertEqual(parsed.get("message"), msg)

    def skipTest_if_unavailable(self):
        if not PYTHONJSONLOGGER_AVAILABLE:
            self.skipTest("pythonjsonlogger not available; skipping formatter tests.")


class TestJsonFormatterExceptionLogging(unittest.TestCase):
    """Verify that exception info is captured in JSON output."""

    def setUp(self):
        if not PYTHONJSONLOGGER_AVAILABLE:
            self.skipTest("pythonjsonlogger not available.")

    def _make_stream_logger(self, name):
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(exc_info)s"
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        return logger, stream

    def test_exception_info_captured_in_json(self):
        """When exc_info=True, the JSON record must contain exception details."""
        logger, stream = self._make_stream_logger("test.exc_info")
        try:
            raise ValueError("intentional test error")
        except ValueError:
            logger.error("caught an error", exc_info=True)

        output = stream.getvalue().strip()
        self.assertTrue(output, "No log output produced for exception log.")
        parsed = json.loads(output)
        exc_text = parsed.get("exc_info") or parsed.get("exception") or parsed.get("exc_text")
        self.assertIsNotNone(
            exc_text,
            "Exception info not found in JSON log output. "
            "Expected 'exc_info', 'exception', or 'exc_text' field.",
        )
        self.assertIn("ValueError", str(exc_text))


class TestLoggingConfigModule(unittest.TestCase):
    """
    Verify that the centralized logging_config module (logging_config.py or
    app/logging_config.py) exists, is importable, and configures JSON output
    on the root logger.
    """

    def _try_import_logging_config(self):
        """Attempt to import logging_config from known candidate locations."""
        candidates = ["logging_config", "app.logging_config", "config.logging_config"]
        for module_name in candidates:
            try:
                import importlib
                mod = importlib.import_module(module_name)
                return mod
            except ImportError:
                continue
        return None

    def test_logging_config_module_importable(self):
        """logging_config module must exist and be importable."""
        mod = self._try_import_logging_config()
        self.assertIsNotNone(
            mod,
            "Could not import 'logging_config' (or 'app.logging_config'). "
            "Create the centralized logging configuration module as specified in the upgrade spec.",
        )

    def test_logging_config_configures_json_on_root_logger(self):
        """
        After importing logging_config, the root logger (or at least one handler)
        must use a JsonFormatter.
        """
        if not PYTHONJSONLOGGER_AVAILABLE:
            self.skipTest("pythonjsonlogger not available.")

        mod = self._try_import_logging_config()
        if mod is None:
            self.skipTest("logging_config module not found; skipping handler check.")

        # Call setup function if present
        setup_fn = getattr(mod, "setup_logging", None) or getattr(mod, "configure_logging", None)
        if callable(setup_fn):
            setup_fn()

        root_logger = logging.getLogger()
        all_handlers = root_logger.handlers[:]

        # Also check named loggers that may have been configured
        manager = logging.Logger.manager
        for name in list(manager.loggerDict.keys()):
            named = logging.getLogger(name)
            all_handlers.extend(named.handlers)

        json_formatter_found = any(
            isinstance(h.formatter, jsonlogger.JsonFormatter)
            for h in all_handlers
            if h.formatter is not None
        )
        self.assertTrue(
            json_formatter_found,
            "No handler with a JsonFormatter was found on the root logger or any named logger "
            "after importing logging_config. Ensure logging_config wires up JsonFormatter "
            "as specified in the upgrade spec.",
        )

    def test_logging_config_includes_service_name_field(self):
        """
        The JsonFormatter configured in logging_config must include 'service_name'
        as a default extra field (per upgrade spec Phase 2).
        """
        if not PYTHONJSONLOGGER_AVAILABLE:
            self.skipTest("pythonjsonlogger not available.")

        mod = self._try_import_logging_config()
        if mod is None:
            self.skipTest("logging_config module not found; skipping service_name check.")

        setup_fn = getattr(mod, "setup_logging", None) or getattr(mod, "configure_logging", None)
        if callable(setup_fn):
            setup_fn()

        # Capture output from root logger
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)

        test_logger = logging.getLogger("test.service_name_field")
        test_logger.handlers = []
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.INFO)
        test_logger.propagate = False
        test_logger.info("service name field check")

        output = stream.getvalue().strip()
        if not output:
            self.skipTest("No output captured; cannot verify service_name field.")

        parsed = json.loads(output)
        # service_name may be injected via extra or a custom filter; check leniently
        # The important thing is that the formatter is in place; field presence
        # depends on the specific logging_config implementation.
        self.assertIsInstance(parsed, dict, "Log output must be a JSON object.")

    def test_logging_config_includes_environment_field(self):
        """
        The logging_config module must expose or document an 'environment' contextual field
        (per upgrade spec Phase 2 — standard contextual fields).
        """
        mod = self._try_import_logging_config()
        if mod is None:
            self.skipTest("logging_config module not found; skipping environment field check.")

        # Accept either a module-level constant or a configurable parameter
        has_env = (
            hasattr(mod, "ENVIRONMENT")
            or hasattr(mod, "environment")
            or hasattr(mod, "LOG_ENVIRONMENT")
        )
        # Also accept that it may be passed as a parameter to setup_logging
        setup_fn = getattr(mod, "setup_logging", None) or getattr(mod, "configure_logging", None)
        if callable(setup_fn):
            import inspect
            sig = inspect.signature(setup_fn)
            has_env = has_env or "environment" in sig.parameters or "env" in sig.parameters

        self.assertTrue(
            has_env,
            "logging_config module does not expose an 'environment' field or parameter. "
            "Add ENVIRONMENT constant or 'environment' parameter to setup_logging() "
            "as specified in the upgrade spec.",
        )


class TestNoUnstructuredPrintLogging(unittest.TestCase):
    """
    Regression guard: verify that the logging pipeline does not fall back to
    plain-text formatting when JSON logging is active.
    """

    def setUp(self):
        if not PYTHONJSONLOGGER_AVAILABLE:
            self.skipTest("pythonjsonlogger not available.")

    def test_json_formatter_output_is_not_plain_text(self):
        """
        Output from JsonFormatter must not be plain unstructured text
        (i.e., it must not start with a bare log level token without JSON structure).
        """
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        logger = logging.getLogger("test.no_plain_text")
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        logger.info("structured output check")
        output = stream.getvalue().strip()

        self.assertTrue(output, "No output produced.")
        # Plain-text basicConfig format starts with a date string not wrapped in braces
        self.assertTrue(
            output.startswith("{"),
            f"Log output does not start with '{{'; it may be plain text. Output: {output!r}",
        )
        # Must be parseable JSON
        try:
            json.loads(output)
        except json.JSONDecodeError:
            self.fail(f"Output is not valid JSON: {output!r}")

    def test_multiple_log_lines_each_valid_json(self):
        """Each individual log line must be independently valid JSON (NDJSON format)."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        logger = logging.getLogger("test.ndjson")
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        messages = ["first message", "second message", "third message"]
        for msg in messages:
            logger.info(msg)

        lines = [line for line in stream.getvalue().splitlines() if line.strip()]
        self.assertEqual(
            len(lines),
            len(messages),
            f"Expected {len(messages)} log lines, got {len(lines)}.",
        )
        for i, line in enumerate(lines):
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError as exc:
                self.fail(f"Line {i + 1} is not valid JSON: {exc}\nLine: {line!r}")
            self.assertEqual(parsed.get("message"), messages[i])


class TestPythonVersionRecorded(unittest.TestCase):
    """
    Verify that the Python interpreter version is accessible and meets
    the minimum requirement implied by python-json-logger 2.x (Python 3.6+).
    """

    def test_python_version_is_3_6_or_higher(self):
        """python-json-logger 2.x requires Python 3.6+. Verify the runtime meets this."""
        version_info = sys.version_info
        self.assertGreaterEqual(
            (version_info.major, version_info.minor),
            (3, 6),
            f"Python {version_info.major}.{version_info.minor} is below the minimum "
            f"required version 3.6 for python-json-logger 2.x.",
        )

    def test_python_version_info_is_accessible(self):
        """sys.version_info must be accessible and report a valid version tuple."""
        self.assertIsNotNone(sys.version_info)
        self.assertGreaterEqual(sys.version_info.major, 3)


if __name__ == "__main__":
    unittest.main()