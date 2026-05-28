import pytest
import json
import re
from http import HTTPStatus

# ---------------------------------------------------------------------------
# Helpers / minimal stub client
# ---------------------------------------------------------------------------
# Because the concrete framework is not yet confirmed, we use a thin adapter
# that tries to import a real test client in order of likelihood.  If none is
# available the tests are skipped with an informative message so the suite
# never silently passes against nothing.

def _build_client():
    """Return (client, post_fn) where post_fn(path, payload) -> response."""
    # --- FastAPI / Starlette ---
    try:
        from main import app as _app          # adjust import to actual module
        from fastapi.testclient import TestClient
        client = TestClient(_app, raise_server_exceptions=False)
        def _post(path, payload):
            return client.post(path, json=payload)
        return client, _post
    except ImportError:
        pass

    # --- Flask ---
    try:
        from app import app as _app           # adjust import to actual module
        _app.config["TESTING"] = True
        client = _app.test_client()
        def _post(path, payload):
            return client.post(
                path,
                data=json.dumps(payload),
                content_type="application/json",
            )
        return client, _post
    except ImportError:
        pass

    # --- Django ---
    try:
        import django
        from django.test import Client as DjangoClient
        client = DjangoClient()
        def _post(path, payload):
            return client.post(
                path,
                data=json.dumps(payload),
                content_type="application/json",
            )
        return client, _post
    except ImportError:
        pass

    return None, None


_CLIENT, _POST = _build_client()

def _skip_if_no_client():
    if _POST is None:
        pytest.skip(
            "No supported web framework found.  "
            "Ensure the application module is importable before running these tests."
        )


ORDERS_ENDPOINT = "/orders"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def post_order():
    """Thin wrapper so every test calls the same helper."""
    _skip_if_no_client()
    return _POST


@pytest.fixture
def valid_payload():
    """Minimal valid order payload.  Extend fields to match the real schema."""
    return {
        "customer_id": "cust-001",
        "items": [
            {
                "product_id": "prod-abc",
                "quantity": 2,
                "unit_price": 19.99,
            }
        ],
        "shipping_address": {
            "line1": "123 Main St",
            "city": "Springfield",
            "postal_code": "12345",
            "country": "US",
        },
    }


# ---------------------------------------------------------------------------
# 1. Upgrade-presence assertions
#    Verify that the validation layer is actually wired up (not just present
#    as dead code) by confirming the endpoint rejects known-bad payloads.
# ---------------------------------------------------------------------------

class TestValidationLayerIsActive:
    """
    These tests confirm that the validation/sanitization upgrade is live.
    A pre-upgrade endpoint would return 2xx for all of these; post-upgrade
    it must return 400.
    """

    def test_completely_empty_body_returns_400(self, post_order):
        resp = post_order(ORDERS_ENDPOINT, {})
        assert resp.status_code == HTTPStatus.BAD_REQUEST, (
            "Validation layer does not appear to be active: "
            "empty body was not rejected with 400."
        )

    def test_null_body_field_returns_400(self, post_order):
        resp = post_order(ORDERS_ENDPOINT, {"customer_id": None, "items": None})
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_missing_required_customer_id_returns_400(self, post_order, valid_payload):
        payload = dict(valid_payload)
        del payload["customer_id"]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_missing_required_items_returns_400(self, post_order, valid_payload):
        payload = dict(valid_payload)
        del payload["items"]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_missing_required_shipping_address_returns_400(self, post_order, valid_payload):
        payload = dict(valid_payload)
        del payload["shipping_address"]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST


# ---------------------------------------------------------------------------
# 2. Type validation
# ---------------------------------------------------------------------------

class TestTypeValidation:

    def test_customer_id_must_be_string(self, post_order, valid_payload):
        payload = {**valid_payload, "customer_id": 12345}
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_items_must_be_list(self, post_order, valid_payload):
        payload = {**valid_payload, "items": "not-a-list"}
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_item_quantity_must_be_integer(self, post_order, valid_payload):
        payload = dict(valid_payload)
        payload["items"] = [{**valid_payload["items"][0], "quantity": "two"}]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_item_unit_price_must_be_numeric(self, post_order, valid_payload):
        payload = dict(valid_payload)
        payload["items"] = [{**valid_payload["items"][0], "unit_price": "free"}]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_items_cannot_be_empty_list(self, post_order, valid_payload):
        payload = {**valid_payload, "items": []}
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_quantity_must_be_positive(self, post_order, valid_payload):
        payload = dict(valid_payload)
        payload["items"] = [{**valid_payload["items"][0], "quantity": 0}]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_unit_price_must_be_positive(self, post_order, valid_payload):
        payload = dict(valid_payload)
        payload["items"] = [{**valid_payload["items"][0], "unit_price": -1.00}]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST


# ---------------------------------------------------------------------------
# 3. Sanitization — injection and special-character payloads
# ---------------------------------------------------------------------------

class TestSanitization:

    def _assert_not_reflected_verbatim(self, resp, injection_string):
        """
        After sanitization the raw injection string must not appear verbatim
        in the response body (it may be escaped or stripped).
        """
        body = resp.text if hasattr(resp, "text") else resp.data.decode()
        assert injection_string not in body, (
            f"Injection string was reflected verbatim in the response: {injection_string!r}"
        )

    def test_sql_injection_in_customer_id_rejected_or_sanitized(
        self, post_order, valid_payload
    ):
        injection = "'; DROP TABLE orders; --"
        payload = {**valid_payload, "customer_id": injection}
        resp = post_order(ORDERS_ENDPOINT, payload)
        # Must either reject (400) or sanitize (2xx but string not reflected raw)
        if resp.status_code == HTTPStatus.OK or resp.status_code == HTTPStatus.CREATED:
            self._assert_not_reflected_verbatim(resp, injection)
        else:
            assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_script_injection_in_string_field_rejected_or_sanitized(
        self, post_order, valid_payload
    ):
        injection = "<script>alert('xss')</script>"
        payload = dict(valid_payload)
        payload["shipping_address"] = {
            **valid_payload["shipping_address"],
            "line1": injection,
        }
        resp = post_order(ORDERS_ENDPOINT, payload)
        if resp.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            self._assert_not_reflected_verbatim(resp, injection)
        else:
            assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_null_bytes_in_string_field_rejected_or_sanitized(
        self, post_order, valid_payload
    ):
        payload = {**valid_payload, "customer_id": "cust\x00evil"}
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code in (
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.OK,
            HTTPStatus.CREATED,
        ), "Unexpected status code for null-byte payload"
        if resp.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            body = resp.text if hasattr(resp, "text") else resp.data.decode()
            assert "\x00" not in body

    def test_control_characters_stripped_from_string_fields(
        self, post_order, valid_payload
    ):
        payload = {**valid_payload, "customer_id": "cust\r\n\t\x1b-001"}
        resp = post_order(ORDERS_ENDPOINT, payload)
        # Accept 400 (strict) or 2xx with control chars removed
        if resp.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            body = resp.text if hasattr(resp, "text") else resp.data.decode()
            assert not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", body)

    def test_oversized_string_field_rejected(self, post_order, valid_payload):
        payload = {**valid_payload, "customer_id": "A" * 10_001}
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code in (
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        )

    def test_whitespace_only_customer_id_rejected(self, post_order, valid_payload):
        payload = {**valid_payload, "customer_id": "   "}
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST


# ---------------------------------------------------------------------------
# 4. Structured error response contract
# ---------------------------------------------------------------------------

class TestErrorResponseContract:
    """
    Post-upgrade, 400 responses must carry a structured body so callers can
    programmatically identify which field(s) failed validation.
    """

    def _parse_body(self, resp):
        try:
            return resp.json()
        except Exception:
            raw = resp.data if hasattr(resp, "data") else resp.content
            return json.loads(raw)

    def test_400_response_is_json(self, post_order, valid_payload):
        payload = dict(valid_payload)
        del payload["customer_id"]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        body = self._parse_body(resp)
        assert isinstance(body, dict), "400 response body must be a JSON object"

    def test_400_response_contains_error_indicator(self, post_order, valid_payload):
        payload = dict(valid_payload)
        del payload["items"]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        body = self._parse_body(resp)
        # Accept common error envelope keys
        has_error_key = any(
            k in body for k in ("error", "errors", "detail", "message", "violations")
        )
        assert has_error_key, (
            f"400 response body does not contain a recognised error key. Body: {body}"
        )

    def test_400_response_references_failing_field(self, post_order, valid_payload):
        payload = dict(valid_payload)
        del payload["customer_id"]
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        body_str = resp.text if hasattr(resp, "text") else resp.data.decode()
        assert "customer_id" in body_str, (
            "400 response should reference the failing field name 'customer_id'"
        )

    def test_200_or_201_returned_for_valid_payload(self, post_order, valid_payload):
        resp = post_order(ORDERS_ENDPOINT, valid_payload)
        assert resp.status_code in (
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
        ), (
            f"Valid payload was unexpectedly rejected with status {resp.status_code}. "
            "Ensure the validation layer does not block well-formed requests."
        )


# ---------------------------------------------------------------------------
# 5. Deprecated / pre-upgrade behaviour no longer present
# ---------------------------------------------------------------------------

class TestDeprecatedBehaviourAbsent:
    """
    Before this upgrade the endpoint accepted arbitrary payloads without
    rejection.  These tests confirm that permissive pre-upgrade behaviour is
    gone.
    """

    def test_arbitrary_extra_fields_do_not_cause_500(self, post_order, valid_payload):
        payload = {**valid_payload, "injected_field": "unexpected_value"}
        resp = post_order(ORDERS_ENDPOINT, payload)
        assert resp.status_code != HTTPStatus.INTERNAL_SERVER_ERROR, (
            "Unexpected fields must not cause a 500 — they should be ignored or rejected."
        )

    def test_completely_wrong_content_type_returns_4xx(self, post_order):
        _skip_if_no_client()
        # Send plain text instead of JSON
        if _CLIENT is None:
            pytest.skip("No client available")
        try:
            # FastAPI / requests-style
            resp = _CLIENT.post(
                ORDERS_ENDPOINT,
                data="not json at all",
                headers={"Content-Type": "text/plain"},
            )
        except TypeError:
            # Flask test client
            resp = _CLIENT.post(
                ORDERS_ENDPOINT,
                data="not json at all",
                content_type="text/plain",
            )
        assert 400 <= resp.status_code < 500, (
            f"Non-JSON content type should return a 4xx, got {resp.status_code}"
        )

    def test_pre_upgrade_passthrough_of_empty_body_no_longer_returns_2xx(
        self, post_order
    ):
        resp = post_order(ORDERS_ENDPOINT, {})
        assert resp.status_code not in (
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
        ), (
            "Pre-upgrade behaviour (accepting empty body) is still present. "
            "Validation layer may not be wired up."
        )


# ---------------------------------------------------------------------------
# 6. New configuration / schema keys load without errors
# ---------------------------------------------------------------------------

class TestNewConfigurationLoads:
    """
    Verify that the new validation schema / configuration introduced by this
    upgrade is importable and structurally sound.
    """

    def test_validation_schema_or_model_is_importable(self):
        """
        Try to import the validation schema/model added in this upgrade.
        Adjust the import path to match the actual module created.
        """
        imported = False
        candidates = [
            ("orders.schemas", "OrderCreateSchema"),
            ("orders.models", "OrderRequest"),
            ("orders.validators", "OrderValidator"),
            ("schemas.orders", "OrderCreateSchema"),
            ("app.schemas", "OrderCreateSchema"),
            ("api.orders.schema", "OrderSchema"),
        ]
        for module_path, class_name in candidates:
            try:
                import importlib
                mod = importlib.import_module(module_path)
                assert hasattr(mod, class_name), (
                    f"Module {module_path!r} found but does not expose {class_name!r}"
                )
                imported = True
                break
            except ImportError:
                continue

        if not imported:
            pytest.skip(
                "Could not locate the new validation schema module. "
                "Update the 'candidates' list in this test to match the actual module path."
            )

    def test_sanitization_utility_is_importable(self):
        """
        Verify the sanitization utility/middleware added in this upgrade loads.
        """
        imported = False
        candidates = [
            ("orders.sanitizers", "sanitize_order_input"),
            ("orders.utils", "sanitize_order_input"),
            ("utils.sanitize", "sanitize_order_input"),
            ("middleware.sanitization", "OrderSanitizer"),
            ("app.sanitizers", "sanitize_order_input"),
        ]
        for module_path, attr_name in candidates:
            try:
                import importlib
                mod = importlib.import_module(module_path)
                assert hasattr(mod, attr_name), (
                    f"Module {module_path!r} found but does not expose {attr_name!r}"
                )
                imported = True
                break
            except ImportError:
                continue

        if not imported:
            pytest.skip(
                "Could not locate the sanitization utility module. "
                "Update the 'candidates' list in this test to match the actual module path."
            )

    def test_validation_config_keys_present_in_settings(self):
        """
        If the upgrade introduced new settings/config keys (e.g. max payload
        size, max string length), verify they are present and have sane values.
        """
        settings_imported = False
        settings = None
        for module_path in ("config", "settings", "app.config", "core.config"):
            try:
                import importlib
                settings = importlib.import_module(module_path)
                settings_imported = True
                break
            except ImportError:
                continue

        if not settings_imported:
            pytest.skip("Settings module not found; skipping config key assertions.")

        # Check for at least one of the expected new config keys
        expected_keys = [
            "MAX_ORDER_PAYLOAD_SIZE",
            "ORDER_MAX_STRING_LENGTH",
            "ORDER_VALIDATION_ENABLED",
            "INPUT_SANITIZATION_ENABLED",
        ]
        found = [k for k in expected_keys if hasattr(settings, k)]
        assert found, (
            f"None of the expected new validation config keys {expected_keys} "
            f"were found in the settings module. "
            "Add the missing keys or update this test to match the actual key names."
        )