import pytest
import sys
import importlib
import inspect


# ---------------------------------------------------------------------------
# Version assertion — pytest ≥ 7.x must be active
# ---------------------------------------------------------------------------

def test_pytest_version_meets_minimum():
    """Verify that the active pytest version is at least 7.0.0."""
    version_str = pytest.__version__
    parts = version_str.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    assert major >= 7, (
        f"pytest version {version_str} is below the required minimum 7.0.0. "
        "Run: pip install 'pytest>=7.4'"
    )


def test_pytest_mock_available():
    """Verify pytest-mock is installed and importable."""
    try:
        import pytest_mock
    except ImportError:
        pytest.fail(
            "pytest-mock is not installed. Run: pip install 'pytest-mock>=3.12'"
        )
    version_str = pytest_mock.__version__
    parts = version_str.split(".")
    major = int(parts[0])
    assert major >= 3, (
        f"pytest-mock version {version_str} is below the required minimum 3.x. "
        "Run: pip install 'pytest-mock>=3.12'"
    )


def test_pytest_cov_available():
    """Verify pytest-cov is installed and importable."""
    try:
        import pytest_cov
    except ImportError:
        pytest.fail(
            "pytest-cov is not installed. Run: pip install 'pytest-cov>=4.1'"
        )


# ---------------------------------------------------------------------------
# Fixture mechanics — verify pytest fixtures work correctly
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_resource():
    """A basic fixture that yields a value and performs teardown."""
    resource = {"status": "initialized", "calls": []}
    yield resource
    # teardown — verify it runs without error
    resource["status"] = "torn_down"


@pytest.fixture
def dependent_resource(simple_resource):
    """A fixture that depends on another fixture — tests fixture composition."""
    simple_resource["calls"].append("dependent_resource_setup")
    return simple_resource


def test_fixture_setup_and_teardown(simple_resource):
    """Verify that a pytest fixture provides its value correctly."""
    assert simple_resource["status"] == "initialized"
    assert isinstance(simple_resource, dict)


def test_fixture_composition(dependent_resource):
    """Verify that fixture composition (fixture depending on fixture) works."""
    assert "dependent_resource_setup" in dependent_resource["calls"]
    assert dependent_resource["status"] == "initialized"


@pytest.fixture(scope="module")
def module_scoped_resource():
    """Verify module-scoped fixtures are supported."""
    return {"scope": "module", "created": True}


def test_module_scoped_fixture(module_scoped_resource):
    """Verify module-scoped fixture is accessible and correct."""
    assert module_scoped_resource["scope"] == "module"
    assert module_scoped_resource["created"] is True


# ---------------------------------------------------------------------------
# pytest-mock — verify mocker fixture replaces unittest.mock patterns
# ---------------------------------------------------------------------------

def _function_under_test(service):
    """Minimal production-like function that calls an injected dependency."""
    result = service.fetch("key")
    return f"processed:{result}"


def test_mocker_fixture_basic(mocker):
    """Verify the mocker fixture from pytest-mock is injected and functional."""
    mock_service = mocker.MagicMock()
    mock_service.fetch.return_value = "value1"

    result = _function_under_test(mock_service)

    assert result == "processed:value1"
    mock_service.fetch.assert_called_once_with("key")


def test_mocker_patch(mocker):
    """Verify mocker.patch works as a replacement for unittest.mock.patch."""
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="hello"))

    with open("fakefile.txt") as f:
        content = f.read()

    assert content == "hello"
    mock_open.assert_called_once_with("fakefile.txt")


def test_mocker_spy(mocker):
    """Verify mocker.spy wraps a real function and records calls."""
    import os.path

    spy = mocker.spy(os.path, "join")
    result = os.path.join("a", "b", "c")

    assert spy.call_count == 1
    spy.assert_called_once_with("a", "b", "c")


def test_mocker_stopall_is_automatic(mocker):
    """Verify that mocks created via mocker are stopped after the test (no manual cleanup needed)."""
    mock_len = mocker.patch("builtins.len", return_value=42)
    assert len([]) == 42  # patched
    # After this test, mocker automatically calls stopall — verified by the
    # next test which must see the real len()


def test_real_len_after_mocker_test():
    """Verify that the previous test's mock was cleaned up automatically."""
    assert len([1, 2, 3]) == 3


# ---------------------------------------------------------------------------
# Deprecated unittest.TestCase patterns — verify they are NOT required
# ---------------------------------------------------------------------------

def test_no_testcase_inheritance_required():
    """Verify plain functions (not TestCase subclasses) are discovered and run."""
    # This test itself is the proof — it is a plain function with no class.
    assert True


def test_pytest_native_assertions_work():
    """Verify pytest's assertion rewriting works (no self.assert* needed)."""
    value = [1, 2, 3]
    assert 2 in value
    assert len(value) == 3
    assert value != [3, 2, 1]


def test_pytest_raises_replaces_assertraises():
    """Verify pytest.raises() works as a replacement for self.assertRaises."""
    with pytest.raises(ValueError, match="invalid literal"):
        int("not_a_number")


def test_pytest_raises_captures_exception_info():
    """Verify exc_info is accessible via pytest.raises context manager."""
    with pytest.raises(KeyError) as exc_info:
        d = {}
        _ = d["missing_key"]

    assert "missing_key" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Parameterization — verify pytest.mark.parametrize works
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (0, 0),
    (-1, -2),
])
def test_parametrize_replaces_subtest(input_val, expected):
    """Verify pytest.mark.parametrize works as a replacement for unittest subTest."""
    assert input_val * 2 == expected


# ---------------------------------------------------------------------------
# conftest.py fixture discovery — verify fixtures from conftest are usable
# ---------------------------------------------------------------------------

def test_conftest_fixture_pattern(tmp_path):
    """
    Verify that pytest built-in fixtures (like tmp_path) are injected correctly.
    tmp_path is a pytest built-in that replaces manual tempfile management.
    """
    test_file = tmp_path / "upgrade_check.txt"
    test_file.write_text("pytest migration succeeded")
    assert test_file.read_text() == "pytest migration succeeded"


def test_capsys_builtin_fixture(capsys):
    """Verify capsys built-in fixture captures stdout/stderr correctly."""
    print("upgrade validation output")
    captured = capsys.readouterr()
    assert "upgrade validation output" in captured.out


# ---------------------------------------------------------------------------
# unittest.mock import — verify it is NOT needed (pytest-mock covers it)
# ---------------------------------------------------------------------------

def test_unittest_mock_not_imported_in_test_module():
    """
    Verify this test module itself does not import unittest.mock,
    confirming the migration away from the old pattern.
    """
    import sys
    # The current test module should not have pulled in unittest.mock
    assert "unittest.mock" not in sys.modules or _unittest_mock_was_not_imported_by_us()


def _unittest_mock_was_not_imported_by_us():
    """
    unittest.mock may be imported transitively by pytest internals;
    what matters is that this test file does not import it directly.
    """
    current_module = sys.modules[__name__]
    source_file = inspect.getfile(current_module)
    with open(source_file, "r") as f:
        source = f.read()
    return "import unittest.mock" not in source and "from unittest.mock" not in source


# ---------------------------------------------------------------------------
# Summary marker — single test that asserts all key upgrade conditions
# ---------------------------------------------------------------------------

def test_upgrade_summary():
    """
    Consolidated upgrade validation:
    - pytest >= 7.x is active
    - pytest-mock >= 3.x is active
    - pytest-cov is present
    - Python version is compatible (>= 3.8)
    """
    # pytest version
    major = int(pytest.__version__.split(".")[0])
    assert major >= 7, f"pytest {pytest.__version__} < 7.x"

    # pytest-mock version
    import pytest_mock
    mock_major = int(pytest_mock.__version__.split(".")[0])
    assert mock_major >= 3, f"pytest-mock {pytest_mock.__version__} < 3.x"

    # pytest-cov present
    import pytest_cov  # noqa: F401

    # Python >= 3.8
    assert sys.version_info >= (3, 8), (
        f"Python {sys.version_info} is below the minimum 3.8 required by pytest 7.x"
    )