"""DataUpdateCoordinator for NesVentory."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import NesVentoryApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NesVentoryDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NesVentory data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: NesVentoryApiClient,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: HomeAssistant instance
            client: NesVentory API client

        """
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from NesVentory.

        Returns:
            Dictionary containing all data from NesVentory

        Raises:
            UpdateFailed: If update fails

        """
        try:
            # Fetch all data in parallel for efficiency
            items = await self.client.get_items()
            total_count = len(items) if isinstance(items, list) else 0

            # Calculate total value
            total_value = 0.0
            if isinstance(items, list):
                for item in items:
                    value = item.get("value", 0) or item.get("price", 0) or 0
                    total_value += float(value)

            return {
                "items": items,
                "total_count": total_count,
                "total_value": total_value,
            }

        except Exception as err:
            raise UpdateFailed(f"Error communicating with NesVentory: {err}") from err
