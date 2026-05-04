"""DataUpdateCoordinator for NesVentory."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import NesVentoryApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NesVentoryDataUpdateCoordinator(
    DataUpdateCoordinator
):  # pylint: disable=too-few-public-methods
    """Class to manage fetching NesVentory data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: NesVentoryApiClient,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: HomeAssistant instance
            client: NesVentory API client
            scan_interval: Update interval in seconds

        """
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from NesVentory.

        Fetches items, locations, and categories in parallel for efficiency.
        Location and category failures are handled gracefully — they return
        empty lists rather than failing the entire update.

        Returns:
            Dictionary containing all data from NesVentory

        Raises:
            UpdateFailed: If the core items fetch fails

        """
        try:
            # Fetch items (required), locations and categories (optional / best-effort)
            items_coro = self.client.get_items()
            locations_coro = self.client.get_locations()
            categories_coro = self.client.get_categories()

            items, locations_result, categories_result = await asyncio.gather(
                items_coro,
                locations_coro,
                categories_coro,
                return_exceptions=True,
            )

            # Items are required — propagate any exception as UpdateFailed
            if isinstance(items, BaseException):
                raise UpdateFailed(
                    f"Error fetching items from NesVentory: {items}"
                ) from items

            # Locations / categories are best-effort; log and fall back to []
            if isinstance(locations_result, BaseException):
                _LOGGER.warning(
                    "Failed to fetch locations (non-critical): %s", locations_result
                )
                locations: list[dict[str, Any]] = []
            else:
                locations = (
                    locations_result if isinstance(locations_result, list) else []
                )

            if isinstance(categories_result, BaseException):
                _LOGGER.warning(
                    "Failed to fetch categories (non-critical): %s", categories_result
                )
                categories: list[dict[str, Any]] = []
            else:
                categories = (
                    categories_result if isinstance(categories_result, list) else []
                )

            total_count = len(items) if isinstance(items, list) else 0

            total_value = 0.0
            if isinstance(items, list):
                for item in items:
                    value = item.get("value", 0) or item.get("price", 0) or 0
                    total_value += float(value)

            return {
                "items": items,
                "total_count": total_count,
                "total_value": total_value,
                "locations": locations,
                "categories": categories,
            }

        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error communicating with NesVentory: {err}") from err
