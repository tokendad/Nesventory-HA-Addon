"""Sensor platform for NesVentory."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_DOLLAR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NesVentoryDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NesVentory sensors from a config entry."""
    coordinator: NesVentoryDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create sensor entities
    entities = [
        NesVentoryTotalItemsSensor(coordinator, entry),
        NesVentoryTotalValueSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class NesVentoryTotalItemsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total number of items in NesVentory."""

    _attr_has_entity_name = True
    _attr_name = "Total Items"
    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: NesVentoryDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data update coordinator
            entry: Config entry

        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total_items"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "NesVentory",
            "manufacturer": "NesVentory",
            "model": "Inventory System",
            "configuration_url": entry.data.get("url"),
        }

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("total_count")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "last_update": self.coordinator.last_update_success_time,
        }


class NesVentoryTotalValueSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total value of items in NesVentory."""

    _attr_has_entity_name = True
    _attr_name = "Total Value"
    _attr_icon = "mdi:cash"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CURRENCY_DOLLAR

    def __init__(
        self,
        coordinator: NesVentoryDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data update coordinator
            entry: Config entry

        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total_value"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "NesVentory",
            "manufacturer": "NesVentory",
            "model": "Inventory System",
            "configuration_url": entry.data.get("url"),
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("total_value")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "last_update": self.coordinator.last_update_success_time,
            "item_count": self.coordinator.data.get("total_count", 0),
        }
