"""Tests for NesVentory API client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError


class TestAuthenticate:
    """Tests for NesVentoryApiClient.authenticate()."""

    @pytest.mark.asyncio
    async def test_authenticate_success(self):
        """Test successful authentication returns True and stores token."""
        from custom_components.nesventory.api_client import NesVentoryApiClient

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"access_token": "test-token"})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_response)

        client = NesVentoryApiClient(
            base_url="http://localhost:8001",
            username="admin",
            password="secret",
            session=mock_session,
        )

        result = await client.authenticate()

        assert result is True
        assert client._token == "test-token"

    @pytest.mark.asyncio
    async def test_authenticate_invalid_credentials(self):
        """Test failed authentication returns False."""
        from custom_components.nesventory.api_client import NesVentoryApiClient

        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_response)

        client = NesVentoryApiClient(
            base_url="http://localhost:8001",
            username="admin",
            password="wrong",
            session=mock_session,
        )

        result = await client.authenticate()

        assert result is False
        assert client._token is None

    @pytest.mark.asyncio
    async def test_authenticate_timeout(self):
        """Test timeout during authentication returns False."""
        from custom_components.nesventory.api_client import NesVentoryApiClient

        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=asyncio.TimeoutError)

        client = NesVentoryApiClient(
            base_url="http://localhost:8001",
            username="admin",
            password="secret",
            session=mock_session,
        )

        with patch("asyncio.timeout"):
            result = await client.authenticate()

        assert result is False


class TestGetItems:
    """Tests for NesVentoryApiClient.get_items()."""

    @pytest.mark.asyncio
    async def test_get_items_returns_list(self):
        """Test that get_items returns a list."""
        from custom_components.nesventory.api_client import NesVentoryApiClient

        items = [{"id": 1, "name": "Test"}]

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=items)
        mock_response.raise_for_status = MagicMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)

        client = NesVentoryApiClient(
            base_url="http://localhost:8001",
            username="admin",
            password="secret",
            session=mock_session,
        )
        client._token = "test-token"

        result = await client.get_items()

        assert result == items
