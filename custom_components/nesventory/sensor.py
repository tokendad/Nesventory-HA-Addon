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
from homeassistant.const import CONF_URL, CURRENCY_DOLLAR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_TRACKED_CATEGORIES,
    CONF_TRACKED_LOCATIONS,
    DOMAIN,
)
from .coordinator import NesVentoryDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def _device_info(entry: ConfigEntry) -> dict[str, Any]:
    """Build the shared device info dict for all NesVentory sensors."""
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": "NesVentory",
        "manufacturer": "NesVentory",
        "model": "Inventory System",
        "configuration_url": entry.data.get(CONF_URL),
    }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NesVentory sensors from a config entry."""
    coordinator: NesVentoryDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        NesVentoryTotalItemsSensor(coordinator, entry),
        NesVentoryTotalValueSensor(coordinator, entry),
    ]

    # Add category sensors for each tracked category
    for category_name in entry.options.get(CONF_TRACKED_CATEGORIES, []):
        entities.append(NesVentoryCategorySensor(coordinator, entry, category_name))

    # Add location sensors for each tracked location
    for location_name in entry.options.get(CONF_TRACKED_LOCATIONS, []):
        entities.append(NesVentoryLocationSensor(coordinator, entry, location_name))

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
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total_items"
        self._attr_device_info = _device_info(entry)

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

        items: list[dict[str, Any]] = self.coordinator.data.get("items", [])

        # Items by status
        status_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}
        for item in items:
            status = item.get("status", "Unknown") or "Unknown"
            status_counts[status] = status_counts.get(status, 0) + 1

            cat_name = item.get("category") or item.get("category_name")
            if not cat_name:
                tags = item.get("tags") or []
                cat_name = (
                    tags[0].get("name")
                    if tags and isinstance(tags[0], dict)
                    else "Uncategorized"
                )
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

        top_categories = dict(
            sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        return {
            "items_by_status": status_counts,
            "items_by_category": top_categories,
            "last_update": self.coordinator.last_update_time,
        }


class NesVentoryTotalValueSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total value of items in NesVentory."""

    _attr_has_entity_name = True
    _attr_name = "Total Value"
    _attr_icon = "mdi:cash"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = CURRENCY_DOLLAR

    def __init__(
        self,
        coordinator: NesVentoryDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total_value"
        self._attr_device_info = _device_info(entry)

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

        items: list[dict[str, Any]] = self.coordinator.data.get("items", [])
        category_values: dict[str, float] = {}
        for item in items:
            cat_name = item.get("category") or item.get("category_name")
            if not cat_name:
                tags = item.get("tags") or []
                cat_name = (
                    tags[0].get("name")
                    if tags and isinstance(tags[0], dict)
                    else "Uncategorized"
                )
            item_value = item.get("estimated_value")
            if item_value is None:
                item_value = item.get("purchase_price")
            value = float(item_value or 0)
            category_values[cat_name] = category_values.get(cat_name, 0.0) + value

        top_by_value = dict(
            sorted(category_values.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        return {
            "value_by_category": top_by_value,
            "item_count": self.coordinator.data.get("total_count", 0),
            "last_update": self.coordinator.last_update_time,
        }


class NesVentoryCategorySensor(CoordinatorEntity, SensorEntity):
    """Sensor for item count in a specific category."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:tag"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: NesVentoryDataUpdateCoordinator,
        entry: ConfigEntry,
        category_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._category_name = category_name
        slug = category_name.lower().replace(" ", "_")
        self._attr_name = f"Category {category_name}"
        self._attr_unique_id = f"{entry.entry_id}_category_{slug}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> int:
        """Return item count for this category."""
        if not self.coordinator.data:
            return 0
        items: list[dict[str, Any]] = self.coordinator.data.get("items", [])
        return sum(
            1
            for item in items
            if any(
                tag.get("name") == self._category_name
                for tag in (item.get("tags") or [])
            )
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {"category": self._category_name}


class NesVentoryLocationSensor(CoordinatorEntity, SensorEntity):
    """Sensor for item count in a specific location."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:map-marker"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: NesVentoryDataUpdateCoordinator,
        entry: ConfigEntry,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._location_name = location_name
        slug = location_name.lower().replace(" ", "_")
        self._attr_name = f"Location {location_name}"
        self._attr_unique_id = f"{entry.entry_id}_location_{slug}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> int:
        """Return item count for this location."""
        if not self.coordinator.data:
            return 0
        locations: list[dict[str, Any]] = self.coordinator.data.get("locations", [])
        loc_id_map: dict[str, str] = {
            loc["id"]: loc["name"]
            for loc in locations
            if loc.get("id") and loc.get("name")
        }
        items: list[dict[str, Any]] = self.coordinator.data.get("items", [])
        return sum(
            1
            for item in items
            if loc_id_map.get(item.get("location_id", "")) == self._location_name
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {"location": self._location_name}
