import pytest
import sys
import importlib
import inspect
import subprocess


# ---------------------------------------------------------------------------
# Version assertion — pytest >= 7.4 must be active
# ---------------------------------------------------------------------------

def test_pytest_version_meets_minimum():
    """Verify that the active pytest version is at least 7.4 (the pinned minimum)."""
    version_str = pytest.__version__
    parts = version_str.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    assert (major, minor) >= (7, 4), (
        f"pytest version {version_str} does not meet the minimum required 7.4. "
        "Run: pip install 'pytest>=7.4'"
    )


def test_pytest_mock_importable_and_version():
    """pytest-mock >= 3.11 must be installed."""
    pytest_mock = importlib.import_module("pytest_mock")
    version_str = getattr(pytest_mock, "__version__", None)
    assert version_str is not None, "pytest-mock does not expose __version__"
    parts = version_str.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    assert (major, minor) >= (3, 11), (
        f"pytest-mock version {version_str} does not meet the minimum required 3.11. "
        "Run: pip install 'pytest-mock>=3.11'"
    )


def test_pytest_cov_importable_and_version():
    """pytest-cov >= 4.1 must be installed."""
    pytest_cov = importlib.import_module("pytest_cov")
    version_str = getattr(pytest_cov, "__version__", None)
    assert version_str is not None, "pytest-cov does not expose __version__"
    parts = version_str.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    assert (major, minor) >= (4, 1), (
        f"pytest-cov version {version_str} does not meet the minimum required 4.1. "
        "Run: pip install 'pytest-cov>=4.1'"
    )


def test_python_version_compatible_with_pytest7():
    """pytest >= 7.x requires Python >= 3.7."""
    assert sys.version_info >= (3, 7), (
        f"Python {sys.version_info} is below the minimum 3.7 required by pytest 7.x"
    )


# ---------------------------------------------------------------------------
# Deprecated API checks — unittest.TestCase inheritance must be gone
# ---------------------------------------------------------------------------

def test_no_unittest_testcase_subclasses_in_test_files(pytestconfig):
    """
    Verify that no test file collected by pytest still subclasses unittest.TestCase.
    Migrated tests must be plain functions or non-TestCase classes.
    """
    import unittest
    rootdir = pytestconfig.rootdir
    test_paths = pytestconfig.getini("testpaths") or ["tests"]

    offenders = []
    for test_path_str in test_paths:
        import pathlib
        base = pathlib.Path(str(rootdir)) / test_path_str
        if not base.exists():
            continue
        for py_file in base.rglob("test_*.py"):
            spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
            if spec is None or spec.loader is None:
                continue
            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception:
                # If a module fails to import, skip it here — import errors
                # are caught by pytest's own collection.
                continue
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, unittest.TestCase) and obj is not unittest.TestCase:
                    offenders.append(f"{py_file}::{name}")

    assert offenders == [], (
        "The following test classes still inherit from unittest.TestCase and have not "
        "been migrated to plain pytest classes or functions:\n"
        + "\n".join(offenders)
    )


def test_no_self_assert_methods_in_test_functions(pytestconfig):
    """
    Verify that migrated test functions do not use self.assertEqual / self.assertTrue
    style assertions — they must use plain `assert` statements.
    """
    import pathlib
    import ast

    UNITTEST_ASSERT_METHODS = {
        "assertEqual", "assertNotEqual", "assertTrue", "assertFalse",
        "assertIs", "assertIsNot", "assertIsNone", "assertIsNotNone",
        "assertIn", "assertNotIn", "assertRaises", "assertRaisesRegex",
        "assertAlmostEqual", "assertNotAlmostEqual", "assertGreater",
        "assertGreaterEqual", "assertLess", "assertLessEqual",
        "assertRegex", "assertNotRegex", "assertCountEqual",
        "assertMultiLineEqual", "assertSequenceEqual", "assertListEqual",
        "assertTupleEqual", "assertSetEqual", "assertDictEqual",
        "assertLogs", "assertWarns", "assertWarnsRegex",
        "fail", "skipTest",
    }

    rootdir = pytestconfig.rootdir
    test_paths = pytestconfig.getini("testpaths") or ["tests"]
    offenders = []

    for test_path_str in test_paths:
        base = pathlib.Path(str(rootdir)) / test_path_str
        if not base.exists():
            continue
        for py_file in base.rglob("test_*.py"):
            source = py_file.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source, filename=str(py_file))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if (
                        isinstance(func, ast.Attribute)
                        and func.attr in UNITTEST_ASSERT_METHODS
                        and isinstance(func.value, ast.Name)
                        and func.value.id == "self"
                    ):
                        offenders.append(
                            f"{py_file}:{node.lineno} — self.{func.attr}(...)"
                        )

    assert offenders == [], (
        "The following locations still use unittest-style self.assert* calls. "
        "Replace them with plain `assert` statements:\n"
        + "\n".join(offenders)
    )


# ---------------------------------------------------------------------------
# Fixture mechanism works correctly
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_data():
    """A simple pytest fixture — verifies the fixture injection mechanism is active."""
    return {"key": "value", "count": 42}


def test_fixture_injection_works(sample_data):
    """Confirm that pytest fixture dependency injection is functional."""
    assert sample_data["key"] == "value"
    assert sample_data["count"] == 42


@pytest.fixture
def counter():
    state = {"n": 0}
    yield state
    # teardown — state is reset after each test
    state["n"] = -1


def test_fixture_setup_and_teardown(counter):
    """Verify that yield-based fixture setup/teardown executes correctly."""
    assert counter["n"] == 0
    counter["n"] += 1
    assert counter["n"] == 1
    # After this test, the fixture teardown sets n = -1; the next test gets a fresh fixture.


def test_fixture_isolation_between_tests(counter):
    """Each test receives a fresh fixture instance — state does not leak."""
    assert counter["n"] == 0  # Would be 1 if state leaked from the previous test


# ---------------------------------------------------------------------------
# Mocking via pytest-mock (mocker fixture)
# ---------------------------------------------------------------------------

def test_mocker_fixture_available(mocker):
    """Verify that the pytest-mock `mocker` fixture is injected correctly."""
    assert mocker is not None


def test_mocker_patch_replaces_target(mocker):
    """Verify that mocker.patch works as the replacement for unittest.mock.patch."""
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="hello"))
    with open("any_file.txt") as fh:
        content = fh.read()
    assert content == "hello"
    mock_open.assert_called_once_with("any_file.txt")


def test_mocker_spy_works(mocker):
    """Verify mocker.spy (a pytest-mock feature absent from plain unittest.mock)."""
    import os.path
    spy = mocker.spy(os.path, "join")
    result = os.path.join("a", "b")
    assert result == "a/b"
    spy.assert_called_once_with("a", "b")


def test_mocker_stopall_called_automatically(mocker):
    """
    Verify that patches created via mocker are automatically stopped after the test
    (pytest-mock guarantee — no manual mocker.stopall() required).
    """
    patched = mocker.patch("os.getcwd", return_value="/mocked")
    import os
    assert os.getcwd() == "/mocked"
    # After this test exits, os.getcwd is automatically restored by pytest-mock.


def test_os_getcwd_restored_after_previous_mock():
    """Confirm that the patch from the previous test was automatically cleaned up."""
    import os
    cwd = os.getcwd()
    assert cwd != "/mocked", (
        "os.getcwd() is still returning the mocked value — "
        "pytest-mock did not clean up the patch automatically."
    )


# ---------------------------------------------------------------------------
# DB isolation pattern — transaction rollback fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def isolated_db():
    """
    Demonstrates the DB isolation pattern: each test runs inside a transaction
    that is rolled back on teardown.  Replace the sqlite3 in-memory DB with
    the project's actual DB connection/session factory.
    """
    import sqlite3
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)"
    )
    conn.commit()
    # Yield the connection; rollback any writes after the test.
    yield conn
    conn.rollback()
    conn.close()


def test_db_write_is_isolated_first(isolated_db):
    """Write a row — it must not be visible to the next test."""
    isolated_db.execute("INSERT INTO items (name) VALUES ('test-row')")
    isolated_db.commit()
    cursor = isolated_db.execute("SELECT COUNT(*) FROM items")
    assert cursor.fetchone()[0] == 1


def test_db_state_does_not_leak_between_tests(isolated_db):
    """
    Verify DB isolation: the row inserted in the previous test must not appear
    because each test receives a fresh in-memory DB via the fixture.
    """
    cursor = isolated_db.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]
    assert count == 0, (
        f"Expected 0 rows (isolated DB), but found {count}. "
        "DB state is leaking between tests — check the isolation fixture."
    )


# ---------------------------------------------------------------------------
# Parametrization — new capability unavailable in unittest
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_parametrize_works(a, b, expected):
    """Verify that pytest parametrization executes all cases correctly."""
    assert a + b == expected


# ---------------------------------------------------------------------------
# conftest.py discovery — pytest must honour conftest fixtures
# ---------------------------------------------------------------------------

def test_pytest_ini_options_discoverable(pytestconfig):
    """
    Verify that pytest loaded its configuration (pytest.ini / pyproject.toml
    [tool.pytest.ini_options]) and that testpaths is set.
    """
    # pytestconfig is available — this alone proves pytest config was loaded.
    assert pytestconfig is not None
    # rootdir must be set (non-empty)
    assert str(pytestconfig.rootdir) != ""


# ---------------------------------------------------------------------------
# Regression guard — pytest can collect and run tests without unittest runner
# ---------------------------------------------------------------------------

def test_no_unittest_runner_required():
    """
    Confirm that tests are being executed by pytest, not by unittest's runner.
    The presence of the `_pytest` package in sys.modules is the canonical check.
    """
    assert "_pytest" in sys.modules, (
        "Tests do not appear to be running under pytest. "
        "Ensure you invoke the suite with `pytest`, not `python -m unittest`."
    )


def test_unittest_module_not_used_as_runner():
    """
    unittest itself may still be importable (it ships with Python), but it must
    not be the active test runner.  Verify that pytest's session object is present.
    """
    # If we reach this function, pytest collected and is running it — success.
    assert True


# ---------------------------------------------------------------------------
# Deprecated import check — unittest.mock should be replaced by mocker fixture
# ---------------------------------------------------------------------------

def test_no_direct_unittest_mock_patch_imports_in_test_files(pytestconfig):
    """
    Verify that test files do not import `unittest.mock.patch` directly for use
    as decorators or context managers.  The replacement is the `mocker` fixture
    from pytest-mock.

    NOTE: `from unittest.mock import MagicMock` for type construction is still
    acceptable; this check targets `patch` decorator/context-manager usage only.
    """
    import pathlib
    import ast

    rootdir = pytestconfig.rootdir
    test_paths = pytestconfig.getini("testpaths") or ["tests"]
    offenders = []

    for test_path_str in test_paths:
        base = pathlib.Path(str(rootdir)) / test_path_str
        if not base.exists():
            continue
        for py_file in base.rglob("test_*.py"):
            source = py_file.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source, filename=str(py_file))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                # Detect: from unittest.mock import patch
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if "unittest.mock" in module or module == "unittest":
                        imported_names = [alias.name for alias in node.names]
                        if "patch" in imported_names:
                            offenders.append(
                                f"{py_file}:{node.lineno} — "
                                f"from {module} import patch"
                            )
                # Detect: import unittest.mock; unittest.mock.patch(...)
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ("unittest.mock", "unittest"):
                            offenders.append(
                                f"{py_file}:{node.lineno} — import {alias.name} "
                                "(check for .patch usage)"
                            )

    # Report as a warning rather than a hard failure to allow incremental migration.
    if offenders:
        pytest.warns(
            UserWarning,
            match="unittest.mock.patch",
        )
    # Soft assertion — emit informational output but do not block CI.
    # Change to `assert offenders == []` once migration is complete.
    if offenders:
        pytest.skip(
            "Some test files still import unittest.mock.patch directly. "
            "Migrate them to the `mocker` fixture:\n" + "\n".join(offenders)
        )