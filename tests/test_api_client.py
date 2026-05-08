"""Tests for NesVentory API client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError, ClientResponseError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE_URL = "http://localhost:8001"


def _make_client(mock_session, *, token=None):
    """Create an API client with an optional pre-set token."""
    from custom_components.nesventory.api_client import NesVentoryApiClient

    client = NesVentoryApiClient(
        base_url=BASE_URL,
        username="admin",
        password="secret",
        session=mock_session,
    )
    client._token = token
    return client


def _mock_response(status=200, json_data=None, raise_on_status=None, cookies=None):
    """Build a mock aiohttp response usable as an async context manager."""
    resp = MagicMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data or {})
    # Use a real dict so .get() returns None by default (avoids truthy MagicMock)
    resp.cookies = cookies if cookies is not None else {}
    if raise_on_status:
        resp.raise_for_status = MagicMock(side_effect=raise_on_status)
    else:
        resp.raise_for_status = MagicMock()
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


# ---------------------------------------------------------------------------
# authenticate()
# ---------------------------------------------------------------------------


class TestAuthenticate:
    """Tests for NesVentoryApiClient.authenticate()."""

    async def test_authenticate_success_via_json_body(self):
        """Successful auth with token in JSON body (fallback path) returns True."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(
            return_value=_mock_response(200, {"access_token": "test-token"})
        )
        client = _make_client(mock_session)

        result = await client.authenticate()

        assert result is True
        assert client._token == "test-token"

    async def test_authenticate_success_via_cookie(self):
        """Successful auth with token in Set-Cookie header (primary path) returns True."""
        cookie_morsel = MagicMock()
        cookie_morsel.value = "cookie-token"
        mock_session = MagicMock()
        mock_session.post = MagicMock(
            return_value=_mock_response(200, cookies={"access_token": cookie_morsel})
        )
        client = _make_client(mock_session)

        result = await client.authenticate()

        assert result is True
        assert client._token == "cookie-token"

    async def test_authenticate_cookie_takes_precedence_over_body(self):
        """Cookie token is preferred over any access_token in the JSON body."""
        cookie_morsel = MagicMock()
        cookie_morsel.value = "cookie-token"
        mock_session = MagicMock()
        mock_session.post = MagicMock(
            return_value=_mock_response(
                200,
                json_data={"access_token": "body-token"},
                cookies={"access_token": cookie_morsel},
            )
        )
        client = _make_client(mock_session)

        result = await client.authenticate()

        assert result is True
        assert client._token == "cookie-token"

    async def test_authenticate_no_token_in_response(self):
        """200 response with neither cookie nor body token returns False."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(
            return_value=_mock_response(200, json_data={"token_type": "bearer"})
        )
        client = _make_client(mock_session)

        result = await client.authenticate()

        assert result is False
        assert client._token is None

    async def test_authenticate_skips_request_when_token_already_set(self):
        """If a token is already stored, authenticate() returns True immediately."""
        mock_session = MagicMock()
        client = _make_client(mock_session, token="existing-token")

        result = await client.authenticate()

        assert result is True
        mock_session.post.assert_not_called()

    async def test_authenticate_invalid_credentials(self):
        """401 response returns False and leaves token as None."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=_mock_response(401))
        client = _make_client(mock_session)

        result = await client.authenticate()

        assert result is False
        assert client._token is None

    async def test_authenticate_timeout(self):
        """TimeoutError during auth returns False."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=asyncio.TimeoutError)
        client = _make_client(mock_session)

        with patch("asyncio.timeout"):
            result = await client.authenticate()

        assert result is False

    async def test_authenticate_client_error(self):
        """ClientError during auth returns False."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=ClientError("network error"))
        client = _make_client(mock_session)

        result = await client.authenticate()

        assert result is False


# ---------------------------------------------------------------------------
# _get_json()
# ---------------------------------------------------------------------------


class TestGetJson:
    """Tests for NesVentoryApiClient._get_json()."""

    async def test_get_json_auto_authenticates_when_no_token(self):
        """If no token is set, _get_json calls authenticate first."""
        data = [{"id": 1}]
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, data))
        client = _make_client(mock_session)  # token=None
        client.authenticate = AsyncMock(side_effect=lambda: setattr(client, "_token", "tok") or True)  # noqa: E501

        result = await client._get_json(f"{BASE_URL}/api/v1/items/")

        client.authenticate.assert_awaited_once()
        assert result == data

    async def test_get_json_retries_on_401(self):
        """On 401, re-authenticates and retries the request once."""
        data = [{"id": 2}]
        resp_401 = _mock_response(401)
        resp_200 = _mock_response(200, data)

        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=[resp_401, resp_200])

        client = _make_client(mock_session, token="old-token")

        async def _reauth():
            client._token = "new-token"
            return True

        client.authenticate = _reauth

        result = await client._get_json(f"{BASE_URL}/api/v1/items/")

        assert result == data
        assert mock_session.get.call_count == 2

    async def test_get_json_reauth_failure_raises(self):
        """If re-auth fails after 401, the original 401 error is surfaced."""
        request_info = MagicMock()
        resp_401 = _mock_response(
            401,
            raise_on_status=ClientResponseError(request_info, (), status=401),
        )
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=resp_401)

        client = _make_client(mock_session, token="bad-token")
        client.authenticate = AsyncMock(return_value=False)

        with pytest.raises(ClientResponseError):
            await client._get_json(f"{BASE_URL}/api/v1/items/")

    async def test_get_json_no_recursion_on_second_401(self):
        """With _retry=False, a 401 response is not retried again."""
        request_info = MagicMock()
        resp_401 = _mock_response(
            401,
            raise_on_status=ClientResponseError(request_info, (), status=401),
        )
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=resp_401)

        client = _make_client(mock_session, token="token")
        client.authenticate = AsyncMock(return_value=True)

        with pytest.raises(ClientResponseError):
            await client._get_json(f"{BASE_URL}/api/v1/items/", _retry=False)

        client.authenticate.assert_not_awaited()


# ---------------------------------------------------------------------------
# test_connection()
# ---------------------------------------------------------------------------


class TestTestConnection:
    """Tests for NesVentoryApiClient.test_connection()."""

    async def test_connection_success_with_token(self):
        """200 response returns True when token is already set."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200))
        client = _make_client(mock_session, token="tok")

        result = await client.test_connection()

        assert result is True

    async def test_connection_authenticates_when_no_token(self):
        """If no token, authenticate() is called before the GET."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200))
        client = _make_client(mock_session)  # no token

        async def _auth():
            client._token = "tok"
            return True

        client.authenticate = _auth

        result = await client.test_connection()

        assert result is True

    async def test_connection_auth_failure_returns_false(self):
        """If authentication fails, test_connection returns False."""
        client = _make_client(MagicMock())  # no token
        client.authenticate = AsyncMock(return_value=False)

        result = await client.test_connection()

        assert result is False

    async def test_connection_non_200_returns_false(self):
        """Non-200 GET response returns False."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(503))
        client = _make_client(mock_session, token="tok")

        result = await client.test_connection()

        assert result is False

    async def test_connection_timeout_returns_false(self):
        """TimeoutError returns False."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=asyncio.TimeoutError)
        client = _make_client(mock_session, token="tok")

        with patch("asyncio.timeout"):
            result = await client.test_connection()

        assert result is False

    async def test_connection_client_error_returns_false(self):
        """ClientError returns False."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=ClientError("err"))
        client = _make_client(mock_session, token="tok")

        result = await client.test_connection()

        assert result is False


# ---------------------------------------------------------------------------
# get_items()
# ---------------------------------------------------------------------------


class TestGetItems:
    """Tests for NesVentoryApiClient.get_items()."""

    async def test_get_items_returns_list(self):
        """Successful response returns the list of items."""
        items = [{"id": 1, "name": "Test"}]
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, items))
        client = _make_client(mock_session, token="tok")

        result = await client.get_items()

        assert result == items

    async def test_get_items_non_list_returns_empty(self):
        """Non-list JSON response is coerced to an empty list."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, {"count": 0}))
        client = _make_client(mock_session, token="tok")

        result = await client.get_items()

        assert result == []

    async def test_get_items_timeout_raises(self):
        """TimeoutError propagates out of get_items."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=asyncio.TimeoutError)
        client = _make_client(mock_session, token="tok")

        with patch("asyncio.timeout"):
            with pytest.raises(asyncio.TimeoutError):
                await client.get_items()

    async def test_get_items_client_error_raises(self):
        """ClientError propagates out of get_items."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=ClientError("err"))
        client = _make_client(mock_session, token="tok")

        with pytest.raises(ClientError):
            await client.get_items()


# ---------------------------------------------------------------------------
# get_locations() and get_categories()
# ---------------------------------------------------------------------------


class TestGetLocations:
    """Tests for NesVentoryApiClient.get_locations()."""

    async def test_get_locations_returns_list(self):
        """Successful response returns the list of locations."""
        locations = [{"id": 1, "name": "Kitchen"}]
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, locations))
        client = _make_client(mock_session, token="tok")

        result = await client.get_locations()

        assert result == locations

    async def test_get_locations_non_list_returns_empty(self):
        """Non-list response is coerced to []."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, None))
        client = _make_client(mock_session, token="tok")

        result = await client.get_locations()

        assert result == []

    async def test_get_locations_timeout_raises(self):
        """TimeoutError propagates."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=asyncio.TimeoutError)
        client = _make_client(mock_session, token="tok")

        with patch("asyncio.timeout"):
            with pytest.raises(asyncio.TimeoutError):
                await client.get_locations()

    async def test_get_locations_client_error_raises(self):
        """ClientError propagates."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=ClientError("err"))
        client = _make_client(mock_session, token="tok")

        with pytest.raises(ClientError):
            await client.get_locations()


class TestGetCategories:
    """Tests for NesVentoryApiClient.get_categories()."""

    async def test_get_categories_returns_list(self):
        """Successful response returns the list of categories."""
        categories = [{"id": 1, "name": "Electronics"}]
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, categories))
        client = _make_client(mock_session, token="tok")

        result = await client.get_categories()

        assert result == categories

    async def test_get_categories_timeout_raises(self):
        """TimeoutError propagates."""
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=asyncio.TimeoutError)
        client = _make_client(mock_session, token="tok")

        with patch("asyncio.timeout"):
            with pytest.raises(asyncio.TimeoutError):
                await client.get_categories()


# ---------------------------------------------------------------------------
# get_total_items_count() and get_total_value()
# ---------------------------------------------------------------------------


class TestAggregates:
    """Tests for aggregate helper methods."""

    async def test_get_total_items_count(self):
        """Returns the number of items."""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, items))
        client = _make_client(mock_session, token="tok")

        count = await client.get_total_items_count()

        assert count == 3

    async def test_get_total_items_count_error_returns_zero(self):
        """Error returns 0 without raising."""
        client = _make_client(MagicMock(), token="tok")
        client.get_items = AsyncMock(side_effect=ClientError("err"))

        count = await client.get_total_items_count()

        assert count == 0

    async def test_get_total_value_uses_value_field(self):
        """Sums the 'estimated_value' field from items (API returns strings)."""
        items = [{"estimated_value": "100.00"}, {"estimated_value": "50.25"}]
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, items))
        client = _make_client(mock_session, token="tok")

        total = await client.get_total_value()

        assert total == 150.25

    async def test_get_total_value_falls_back_to_price(self):
        """Falls back to 'purchase_price' when 'estimated_value' is absent or None."""
        items = [
            {"estimated_value": None, "purchase_price": "25.00"},
            {"purchase_price": "15.00"},
            {"estimated_value": None, "purchase_price": "10.00"},
        ]
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=_mock_response(200, items))
        client = _make_client(mock_session, token="tok")

        total = await client.get_total_value()

        assert total == 50.0

    async def test_get_total_value_error_returns_zero(self):
        """Error returns 0.0 without raising."""
        client = _make_client(MagicMock(), token="tok")
        client.get_items = AsyncMock(side_effect=ClientError("err"))

        total = await client.get_total_value()

        assert total == 0.0


# ---------------------------------------------------------------------------
# create_item()
# ---------------------------------------------------------------------------


class TestCreateItem:
    """Tests for NesVentoryApiClient.create_item()."""

    async def test_create_item_success(self):
        """Creates an item and returns the response dict."""
        created = {"id": 42, "name": "Keyboard"}
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=_mock_response(201, created))
        client = _make_client(mock_session, token="tok")

        result = await client.create_item("Keyboard")

        assert result == created

    async def test_create_item_with_optional_fields(self):
        """Passes location and category in the request payload."""
        created = {"id": 43, "name": "Mouse"}
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=_mock_response(201, created))
        client = _make_client(mock_session, token="tok")

        result = await client.create_item(
            "Mouse", quantity=2, location="Desk", category="Peripherals"
        )

        assert result == created
        call_kwargs = mock_session.post.call_args.kwargs
        assert call_kwargs["json"]["location"] == "Desk"
        assert call_kwargs["json"]["category"] == "Peripherals"
        assert call_kwargs["json"]["quantity"] == 2

    async def test_create_item_401_retry(self):
        """On 401, re-authenticates and retries the POST."""
        created = {"id": 44, "name": "Monitor"}
        resp_401 = _mock_response(401)
        resp_201 = _mock_response(201, created)

        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=[resp_401, resp_201])

        client = _make_client(mock_session, token="old-token")

        async def _reauth():
            client._token = "new-token"
            return True

        client.authenticate = _reauth

        result = await client.create_item("Monitor")

        assert result == created
        assert mock_session.post.call_count == 2

    async def test_create_item_timeout_raises(self):
        """TimeoutError propagates from create_item."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=asyncio.TimeoutError)
        client = _make_client(mock_session, token="tok")

        with patch("asyncio.timeout"):
            with pytest.raises(asyncio.TimeoutError):
                await client.create_item("Lost Item")

    async def test_create_item_client_error_raises(self):
        """ClientError propagates from create_item."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=ClientError("err"))
        client = _make_client(mock_session, token="tok")

        with pytest.raises(ClientError):
            await client.create_item("Lost Item")

    async def test_create_item_authenticates_when_no_token(self):
        """Calls authenticate first when token is not set."""
        created = {"id": 45, "name": "Desk"}
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=_mock_response(201, created))
        client = _make_client(mock_session)  # no token

        async def _auth():
            client._token = "tok"
            return True

        client.authenticate = _auth

        result = await client.create_item("Desk")

        assert result == created


# ---------------------------------------------------------------------------
# create_location()
# ---------------------------------------------------------------------------


class TestCreateLocation:
    """Tests for NesVentoryApiClient.create_location()."""

    async def test_create_location_success(self):
        """Creates a location and returns the response dict."""
        created = {"id": 10, "name": "Garage"}
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=_mock_response(201, created))
        client = _make_client(mock_session, token="tok")

        result = await client.create_location("Garage")

        assert result == created

    async def test_create_location_timeout_raises(self):
        """TimeoutError propagates."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=asyncio.TimeoutError)
        client = _make_client(mock_session, token="tok")

        with patch("asyncio.timeout"):
            with pytest.raises(asyncio.TimeoutError):
                await client.create_location("Garage")

    async def test_create_location_client_error_raises(self):
        """ClientError propagates."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=ClientError("err"))
        client = _make_client(mock_session, token="tok")

        with pytest.raises(ClientError):
            await client.create_location("Garage")

    async def test_create_location_401_retry(self):
        """On 401, re-authenticates and retries the POST."""
        created = {"id": 11, "name": "Attic"}
        resp_401 = _mock_response(401)
        resp_201 = _mock_response(201, created)

        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=[resp_401, resp_201])
        client = _make_client(mock_session, token="old-token")

        async def _reauth():
            client._token = "new-token"
            return True

        client.authenticate = _reauth

        result = await client.create_location("Attic")

        assert result == created


# ---------------------------------------------------------------------------
# _get_headers()
# ---------------------------------------------------------------------------


class TestGetHeaders:
    """Tests for NesVentoryApiClient._get_headers()."""

    def test_headers_with_token(self):
        """Authorization header is included when token is set."""
        client = _make_client(MagicMock(), token="my-token")
        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer my-token"
        assert headers["Content-Type"] == "application/json"

    def test_headers_without_token(self):
        """Authorization header is absent when no token is set."""
        client = _make_client(MagicMock())
        headers = client._get_headers()

        assert "Authorization" not in headers
        assert headers["Content-Type"] == "application/json"
