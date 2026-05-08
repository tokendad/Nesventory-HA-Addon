"""Tests for NesVentory DataUpdateCoordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


def _make_coordinator(client):
    """Instantiate coordinator with a mock hass and the given client."""
    from custom_components.nesventory.coordinator import NesVentoryDataUpdateCoordinator

    return NesVentoryDataUpdateCoordinator(MagicMock(), client)


class TestNesVentoryDataUpdateCoordinator:
    """Tests for NesVentoryDataUpdateCoordinator._async_update_data()."""

    async def test_update_data_success(self, mock_api_client):
        """Full success path returns all expected keys."""
        coord = _make_coordinator(mock_api_client)
        result = await coord._async_update_data()

        assert result["total_count"] == 2
        assert result["total_value"] == pytest.approx(305.98)
        assert len(result["items"]) == 2
        assert len(result["locations"]) == 2
        assert len(result["categories"]) == 2

    async def test_update_data_locations_failure_non_fatal(self, mock_api_client):
        """Locations failure does not fail the update — returns []."""
        mock_api_client.get_locations = AsyncMock(side_effect=Exception("network error"))
        coord = _make_coordinator(mock_api_client)

        result = await coord._async_update_data()

        assert result["locations"] == []
        assert result["total_count"] == 2

    async def test_update_data_categories_failure_non_fatal(self, mock_api_client):
        """Categories failure does not fail the update — returns []."""
        mock_api_client.get_categories = AsyncMock(side_effect=Exception("timeout"))
        coord = _make_coordinator(mock_api_client)

        result = await coord._async_update_data()

        assert result["categories"] == []
        assert result["total_count"] == 2

    async def test_update_data_both_optional_fail(self, mock_api_client):
        """Both locations and categories failing gracefully falls back to []."""
        mock_api_client.get_locations = AsyncMock(side_effect=Exception("err"))
        mock_api_client.get_categories = AsyncMock(side_effect=Exception("err"))
        coord = _make_coordinator(mock_api_client)

        result = await coord._async_update_data()

        assert result["locations"] == []
        assert result["categories"] == []
        assert result["total_count"] == 2

    async def test_update_data_items_failure_raises(self, mock_api_client):
        """Items failure raises an exception (wrapped as UpdateFailed)."""
        mock_api_client.get_items = AsyncMock(side_effect=Exception("items down"))
        coord = _make_coordinator(mock_api_client)

        with pytest.raises(Exception):
            await coord._async_update_data()

    async def test_update_data_value_price_fallback(self, mock_api_client):
        """total_value uses 'estimated_value', falls back to 'purchase_price'."""
        mock_api_client.get_items = AsyncMock(
            return_value=[
                {"estimated_value": None, "purchase_price": "10.0"},
                {"purchase_price": "5.0"},
                {"estimated_value": None, "purchase_price": "3.0"},
                {"estimated_value": "20.0"},
            ]
        )
        coord = _make_coordinator(mock_api_client)

        result = await coord._async_update_data()

        assert result["total_value"] == pytest.approx(38.0)
        assert result["total_count"] == 4

    async def test_update_data_total_count(self, mock_api_client):
        """total_count matches the number of items returned."""
        mock_api_client.get_items = AsyncMock(
            return_value=[{"id": i} for i in range(10)]
        )
        coord = _make_coordinator(mock_api_client)

        result = await coord._async_update_data()

        assert result["total_count"] == 10

    async def test_update_data_empty_items(self, mock_api_client):
        """Empty items list -> count 0 and value 0.0."""
        mock_api_client.get_items = AsyncMock(return_value=[])
        coord = _make_coordinator(mock_api_client)

        result = await coord._async_update_data()

        assert result["total_count"] == 0
        assert result["total_value"] == 0.0
        assert result["items"] == []
