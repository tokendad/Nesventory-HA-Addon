"""Tests for NesVentory sensor platform."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


def _make_entry(entry_id="abc123", url="http://localhost:8001", options=None):
    """Build a minimal mock ConfigEntry."""
    entry = MagicMock()
    entry.entry_id = entry_id
    entry.data = {"url": url}
    entry.options = options or {}
    return entry


def _make_coordinator(data=None):
    """Build a minimal mock coordinator."""
    coord = MagicMock()
    coord.data = data
    coord.last_update_time = None
    return coord


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


class TestAsyncSetupEntry:
    """Tests for sensor.async_setup_entry."""

    async def test_setup_base_sensors(self):
        """Sets up two base sensors (total items + total value)."""
        from custom_components.nesventory.sensor import async_setup_entry
        from custom_components.nesventory.const import DOMAIN

        coord = _make_coordinator()
        entry = _make_entry()

        mock_hass = MagicMock()
        mock_hass.data = {DOMAIN: {entry.entry_id: coord}}
        add_entities = MagicMock()

        await async_setup_entry(mock_hass, entry, add_entities)

        add_entities.assert_called_once()
        entities = add_entities.call_args.args[0]
        assert len(entities) == 2

    async def test_setup_with_tracked_categories(self):
        """Adds a NesVentoryCategorySensor for each tracked category."""
        from custom_components.nesventory.sensor import async_setup_entry
        from custom_components.nesventory.const import CONF_TRACKED_CATEGORIES, DOMAIN

        coord = _make_coordinator()
        entry = _make_entry(options={CONF_TRACKED_CATEGORIES: ["Electronics", "Supplies"]})

        mock_hass = MagicMock()
        mock_hass.data = {DOMAIN: {entry.entry_id: coord}}
        add_entities = MagicMock()

        await async_setup_entry(mock_hass, entry, add_entities)

        entities = add_entities.call_args.args[0]
        assert len(entities) == 4  # 2 base + 2 category

    async def test_setup_with_tracked_locations(self):
        """Adds a NesVentoryLocationSensor for each tracked location."""
        from custom_components.nesventory.sensor import async_setup_entry
        from custom_components.nesventory.const import CONF_TRACKED_LOCATIONS, DOMAIN

        coord = _make_coordinator()
        entry = _make_entry(options={CONF_TRACKED_LOCATIONS: ["Kitchen"]})

        mock_hass = MagicMock()
        mock_hass.data = {DOMAIN: {entry.entry_id: coord}}
        add_entities = MagicMock()

        await async_setup_entry(mock_hass, entry, add_entities)

        entities = add_entities.call_args.args[0]
        assert len(entities) == 3  # 2 base + 1 location


# ---------------------------------------------------------------------------
# NesVentoryTotalItemsSensor
# ---------------------------------------------------------------------------


class TestTotalItemsSensor:
    """Tests for NesVentoryTotalItemsSensor."""

    def _make_sensor(self, data=None):
        from custom_components.nesventory.sensor import NesVentoryTotalItemsSensor

        coord = _make_coordinator(data)
        entry = _make_entry()
        return NesVentoryTotalItemsSensor(coord, entry)

    def test_unique_id(self):
        """Unique ID follows {entry_id}_total_items pattern."""
        sensor = self._make_sensor()
        assert sensor._attr_unique_id == "abc123_total_items"

    def test_native_value_with_data(self):
        """Returns total_count when data is available."""
        sensor = self._make_sensor({"total_count": 7, "items": []})
        assert sensor.native_value == 7

    def test_native_value_no_data(self):
        """Returns None when coordinator data is None."""
        sensor = self._make_sensor(None)
        assert sensor.native_value is None

    def test_extra_state_attributes_with_data(self):
        """Returns grouped status and category counts."""
        items = [
            {"status": "Active", "category": "Electronics"},
            {"status": "Active", "category": "Electronics"},
            {"status": "Inactive", "category": "Supplies"},
        ]
        sensor = self._make_sensor({"total_count": 3, "items": items})
        attrs = sensor.extra_state_attributes

        assert attrs["items_by_status"] == {"Active": 2, "Inactive": 1}
        assert attrs["items_by_category"]["Electronics"] == 2
        assert attrs["items_by_category"]["Supplies"] == 1

    def test_extra_state_attributes_no_data(self):
        """Returns empty dict when data is None."""
        sensor = self._make_sensor(None)
        assert sensor.extra_state_attributes == {}

    def test_extra_state_attributes_category_name_fallback(self):
        """Falls back to 'category_name' field when 'category' is absent."""
        items = [{"category_name": "Peripherals", "status": "Active"}]
        sensor = self._make_sensor({"total_count": 1, "items": items})
        attrs = sensor.extra_state_attributes
        assert attrs["items_by_category"]["Peripherals"] == 1

    def test_extra_state_attributes_tags_fallback(self):
        """Falls back to first tag name when category fields are absent."""
        items = [{"tags": [{"id": "1", "name": "Gaming"}], "status": "Active"}]
        sensor = self._make_sensor({"total_count": 1, "items": items})
        attrs = sensor.extra_state_attributes
        assert attrs["items_by_category"]["Gaming"] == 1

    def test_extra_state_attributes_unknown_status(self):
        """Uses 'Unknown' when status is None or missing."""
        items = [{"status": None}, {}]
        sensor = self._make_sensor({"total_count": 2, "items": items})
        attrs = sensor.extra_state_attributes
        assert attrs["items_by_status"]["Unknown"] == 2


# ---------------------------------------------------------------------------
# NesVentoryTotalValueSensor
# ---------------------------------------------------------------------------


class TestTotalValueSensor:
    """Tests for NesVentoryTotalValueSensor."""

    def _make_sensor(self, data=None):
        from custom_components.nesventory.sensor import NesVentoryTotalValueSensor

        coord = _make_coordinator(data)
        entry = _make_entry()
        return NesVentoryTotalValueSensor(coord, entry)

    def test_unique_id(self):
        """Unique ID follows {entry_id}_total_value pattern."""
        sensor = self._make_sensor()
        assert sensor._attr_unique_id == "abc123_total_value"

    def test_native_value_with_data(self):
        """Returns total_value from coordinator data."""
        sensor = self._make_sensor({"total_value": 399.99, "items": []})
        assert sensor.native_value == pytest.approx(399.99)

    def test_native_value_no_data(self):
        """Returns None when data is None."""
        sensor = self._make_sensor(None)
        assert sensor.native_value is None

    def test_extra_state_attributes_with_data(self):
        """Returns value_by_category and item_count using correct API value fields."""
        items = [
            {"estimated_value": "100.0", "tags": [{"id": "1", "name": "Electronics"}]},
            {"purchase_price": "20.0", "tags": [{"id": "2", "name": "Supplies"}]},
        ]
        sensor = self._make_sensor(
            {"total_value": 120.0, "total_count": 2, "items": items}
        )
        attrs = sensor.extra_state_attributes

        assert attrs["item_count"] == 2
        assert attrs["value_by_category"]["Electronics"] == pytest.approx(100.0)
        assert attrs["value_by_category"]["Supplies"] == pytest.approx(20.0)

    def test_extra_state_attributes_no_data(self):
        """Returns empty dict when data is None."""
        sensor = self._make_sensor(None)
        assert sensor.extra_state_attributes == {}


# ---------------------------------------------------------------------------
# NesVentoryCategorySensor
# ---------------------------------------------------------------------------


class TestCategorySensor:
    """Tests for NesVentoryCategorySensor."""

    def _make_sensor(self, category_name, data=None):
        from custom_components.nesventory.sensor import NesVentoryCategorySensor

        coord = _make_coordinator(data)
        entry = _make_entry()
        return NesVentoryCategorySensor(coord, entry, category_name)

    def test_unique_id_slug(self):
        """Unique ID slugifies the category name."""
        sensor = self._make_sensor("Smart Home")
        assert sensor._attr_unique_id == "abc123_category_smart_home"

    def test_native_value_counts_matching_items(self):
        """Counts items whose tags include the category name."""
        items = [
            {"tags": [{"name": "Electronics"}]},
            {"tags": [{"name": "Electronics"}, {"name": "Gadgets"}]},
            {"tags": [{"name": "Supplies"}]},
            {"tags": []},
        ]
        sensor = self._make_sensor("Electronics", {"items": items})
        assert sensor.native_value == 2

    def test_native_value_no_matching_tags(self):
        """Returns 0 when no items have the matching tag."""
        items = [
            {"tags": [{"name": "Furniture"}]},
            {"tags": []},
        ]
        sensor = self._make_sensor("Electronics", {"items": items})
        assert sensor.native_value == 0

    def test_native_value_no_data(self):
        """Returns 0 when coordinator data is None."""
        sensor = self._make_sensor("Electronics", None)
        assert sensor.native_value == 0

    def test_extra_state_attributes(self):
        """Returns category name in attributes."""
        sensor = self._make_sensor("Electronics")
        assert sensor.extra_state_attributes == {"category": "Electronics"}


# ---------------------------------------------------------------------------
# NesVentoryLocationSensor
# ---------------------------------------------------------------------------


class TestLocationSensor:
    """Tests for NesVentoryLocationSensor."""

    def _make_sensor(self, location_name, data=None):
        from custom_components.nesventory.sensor import NesVentoryLocationSensor

        coord = _make_coordinator(data)
        entry = _make_entry()
        return NesVentoryLocationSensor(coord, entry, location_name)

    def test_unique_id_slug(self):
        """Unique ID slugifies the location name."""
        sensor = self._make_sensor("Living Room")
        assert sensor._attr_unique_id == "abc123_location_living_room"

    def test_native_value_counts_matching_items(self):
        """Counts items whose location_id resolves to the location name."""
        locations = [
            {"id": "loc-1", "name": "Kitchen"},
            {"id": "loc-2", "name": "Garage"},
        ]
        items = [
            {"location_id": "loc-1"},
            {"location_id": "loc-1"},
            {"location_id": "loc-2"},
            {"location_id": None},
        ]
        sensor = self._make_sensor("Kitchen", {"items": items, "locations": locations})
        assert sensor.native_value == 2

    def test_native_value_unknown_location_id(self):
        """Returns 0 when location_id does not map to the target location."""
        items = [{"location_id": "unknown-uuid"}]
        sensor = self._make_sensor("Kitchen", {"items": items, "locations": []})
        assert sensor.native_value == 0

    def test_native_value_no_data(self):
        """Returns 0 when coordinator data is None."""
        sensor = self._make_sensor("Kitchen", None)
        assert sensor.native_value == 0

    def test_extra_state_attributes(self):
        """Returns location name in attributes."""
        sensor = self._make_sensor("Kitchen")
        assert sensor.extra_state_attributes == {"location": "Kitchen"}
