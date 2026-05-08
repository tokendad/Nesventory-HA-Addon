"""Tests for NesVentory __init__ (entry setup, services)."""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.nesventory.const import (
    DOMAIN,
    SERVICE_ADD_QUICK_ITEM,
    SERVICE_IMPORT_HA_DEVICES,
    SERVICE_SYNC_HA_AREAS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_hass(*, domain_data=None):
    """Build a minimal mock HomeAssistant instance."""
    hass = MagicMock()
    hass.data = {DOMAIN: domain_data} if domain_data is not None else {}
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.services.has_service = MagicMock(return_value=False)
    hass.services.async_register = MagicMock()
    hass.services.async_remove = MagicMock()
    return hass


def _make_entry(entry_id="test-id"):
    """Build a minimal mock ConfigEntry."""
    entry = MagicMock()
    entry.entry_id = entry_id
    entry.data = {
        "url": "http://localhost:8001",
        "username": "admin",
        "password": "secret",
    }
    entry.options = {}
    entry.async_on_unload = MagicMock()
    entry.add_update_listener = MagicMock(return_value=MagicMock())
    return entry


def _make_coordinator(*, data=None):
    coord = MagicMock()
    coord.data = data
    coord.async_config_entry_first_refresh = AsyncMock()
    coord.async_request_refresh = AsyncMock()
    return coord


def _get_service_handlers(mock_hass):
    """Extract {service_name: handler} from registered service calls."""
    return {
        call.args[1]: call.args[2]
        for call in mock_hass.services.async_register.call_args_list
    }


# ---------------------------------------------------------------------------
# _get_client
# ---------------------------------------------------------------------------


class TestGetClient:
    """Tests for _get_client()."""

    def test_returns_client_from_first_coordinator(self):
        """Returns the api client from the first loaded coordinator."""
        from custom_components.nesventory import _get_client

        mock_client = MagicMock()
        mock_coord = MagicMock()
        mock_coord.client = mock_client
        hass = _make_hass(domain_data={"entry-1": mock_coord})

        result = _get_client(hass)

        assert result is mock_client

    def test_raises_when_no_entry_configured(self):
        """Raises HomeAssistantError (Exception stub) when DOMAIN has no entries."""
        from custom_components.nesventory import _get_client

        hass = _make_hass(domain_data={})

        with pytest.raises(Exception, match="not configured"):
            _get_client(hass)

    def test_raises_when_domain_missing(self):
        """Raises when DOMAIN key is absent from hass.data."""
        from custom_components.nesventory import _get_client

        hass = _make_hass()  # hass.data = {}

        with pytest.raises(Exception):
            _get_client(hass)


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


class TestAsyncSetupEntry:
    """Tests for async_setup_entry()."""

    async def test_success_stores_coordinator(self):
        """Sets up coordinator and stores it in hass.data."""
        from custom_components.nesventory import async_setup_entry

        hass = _make_hass()
        entry = _make_entry()
        mock_coord = _make_coordinator()

        with patch(
            "custom_components.nesventory.async_get_clientsession",
            return_value=MagicMock(),
        ), patch(
            "custom_components.nesventory.NesVentoryApiClient"
        ) as MockClient, patch(
            "custom_components.nesventory.NesVentoryDataUpdateCoordinator",
            return_value=mock_coord,
        ):
            MockClient.return_value.authenticate = AsyncMock(return_value=True)

            result = await async_setup_entry(hass, entry)

        assert result is True
        assert hass.data[DOMAIN][entry.entry_id] is mock_coord

    async def test_auth_failure_raises(self):
        """Raises ConfigEntryAuthFailed (Exception stub) when auth fails."""
        from custom_components.nesventory import async_setup_entry

        hass = _make_hass()
        entry = _make_entry()

        with patch(
            "custom_components.nesventory.async_get_clientsession",
            return_value=MagicMock(),
        ), patch(
            "custom_components.nesventory.NesVentoryApiClient"
        ) as MockClient:
            MockClient.return_value.authenticate = AsyncMock(return_value=False)

            with pytest.raises(Exception, match="Invalid credentials"):
                await async_setup_entry(hass, entry)

    async def test_registers_services_once(self):
        """Services are registered when not yet present."""
        from custom_components.nesventory import async_setup_entry

        hass = _make_hass()
        entry = _make_entry()
        mock_coord = _make_coordinator()

        with patch(
            "custom_components.nesventory.async_get_clientsession",
            return_value=MagicMock(),
        ), patch(
            "custom_components.nesventory.NesVentoryApiClient"
        ) as MockClient, patch(
            "custom_components.nesventory.NesVentoryDataUpdateCoordinator",
            return_value=mock_coord,
        ):
            MockClient.return_value.authenticate = AsyncMock(return_value=True)
            await async_setup_entry(hass, entry)

        assert hass.services.async_register.call_count == 3

    async def test_skips_service_registration_if_already_registered(self):
        """Services are NOT re-registered if already present."""
        from custom_components.nesventory import async_setup_entry

        hass = _make_hass()
        hass.services.has_service = MagicMock(return_value=True)
        entry = _make_entry()
        mock_coord = _make_coordinator()

        with patch(
            "custom_components.nesventory.async_get_clientsession",
            return_value=MagicMock(),
        ), patch(
            "custom_components.nesventory.NesVentoryApiClient"
        ) as MockClient, patch(
            "custom_components.nesventory.NesVentoryDataUpdateCoordinator",
            return_value=mock_coord,
        ):
            MockClient.return_value.authenticate = AsyncMock(return_value=True)
            await async_setup_entry(hass, entry)

        hass.services.async_register.assert_not_called()


# ---------------------------------------------------------------------------
# async_unload_entry
# ---------------------------------------------------------------------------


class TestAsyncUnloadEntry:
    """Tests for async_unload_entry()."""

    async def test_unload_removes_coordinator(self):
        """Removes coordinator from hass.data on unload."""
        from custom_components.nesventory import async_unload_entry

        entry = _make_entry("entry-1")
        hass = _make_hass(domain_data={"entry-1": MagicMock()})

        result = await async_unload_entry(hass, entry)

        assert result is True
        assert "entry-1" not in hass.data[DOMAIN]

    async def test_unload_removes_services_when_last_entry(self):
        """Removes all services when the last entry is unloaded."""
        from custom_components.nesventory import async_unload_entry

        entry = _make_entry("entry-1")
        hass = _make_hass(domain_data={"entry-1": MagicMock()})

        await async_unload_entry(hass, entry)

        assert hass.services.async_remove.call_count == 3

    async def test_unload_keeps_services_when_other_entries_exist(self):
        """Services are NOT removed if other entries remain."""
        from custom_components.nesventory import async_unload_entry

        entry = _make_entry("entry-1")
        hass = _make_hass(domain_data={"entry-1": MagicMock(), "entry-2": MagicMock()})

        await async_unload_entry(hass, entry)

        hass.services.async_remove.assert_not_called()


# ---------------------------------------------------------------------------
# Service: add_quick_item
# ---------------------------------------------------------------------------


class TestAddQuickItem:
    """Tests for handle_add_quick_item service handler."""

    def _setup(self):
        """Register services and extract handlers. Returns (hass, handlers)."""
        from custom_components.nesventory import _register_services

        hass = _make_hass()
        hass.data[DOMAIN] = {}
        _register_services(hass)
        return hass, _get_service_handlers(hass)

    async def test_creates_item_and_refreshes(self, mock_api_client):
        """Calls create_item and then refreshes all coordinators."""
        hass, handlers = self._setup()
        mock_coord = _make_coordinator()
        mock_api_client.create_item = AsyncMock(return_value={"id": 1, "name": "TV"})
        hass.data[DOMAIN]["e1"] = mock_coord
        # _get_client reads coordinator.client
        mock_coord.client = mock_api_client

        call = MagicMock()
        call.data = {"name": "TV", "quantity": 1, "location": None, "category": None}

        await handlers[SERVICE_ADD_QUICK_ITEM](call)

        mock_api_client.create_item.assert_awaited_once()
        mock_coord.async_request_refresh.assert_awaited_once()

    async def test_error_raises_home_assistant_error(self):
        """API failure raises HomeAssistantError (Exception stub)."""
        from aiohttp import ClientError

        hass, handlers = self._setup()
        mock_coord = _make_coordinator()
        mock_client = MagicMock()
        mock_client.create_item = AsyncMock(side_effect=ClientError("fail"))
        mock_coord.client = mock_client
        hass.data[DOMAIN]["e1"] = mock_coord

        call = MagicMock()
        call.data = {"name": "TV", "quantity": 1}

        with pytest.raises(Exception, match="Failed to add item"):
            await handlers[SERVICE_ADD_QUICK_ITEM](call)


# ---------------------------------------------------------------------------
# Service: import_ha_devices
# ---------------------------------------------------------------------------


class TestImportHaDevices:
    """Tests for handle_import_ha_devices service handler."""

    def _setup(self, devices=None, areas=None):
        """Register services, configure device/area registries, return (hass, handlers)."""
        from custom_components.nesventory import _register_services

        # Configure device registry mock
        dr_mod = sys.modules["homeassistant.helpers.device_registry"]
        mock_device_reg = MagicMock()
        mock_device_reg.devices.values.return_value = devices or []
        dr_mod.async_get.return_value = mock_device_reg

        # Configure area registry mock
        ar_mod = sys.modules["homeassistant.helpers.area_registry"]
        mock_area_reg = MagicMock()
        mock_area_reg.async_list_areas.return_value = areas or []
        ar_mod.async_get.return_value = mock_area_reg

        hass = _make_hass()
        hass.data[DOMAIN] = {}
        _register_services(hass)
        return hass, _get_service_handlers(hass)

    async def test_imports_device_with_name(self, mock_api_client):
        """Creates an item for a device that has a name."""
        device = MagicMock()
        device.name = "TV"
        device.name_by_user = None
        device.manufacturer = "Samsung"
        device.model = "QLED"
        device.area_id = None

        hass, handlers = self._setup(devices=[device])
        mock_coord = _make_coordinator()
        mock_coord.client = mock_api_client
        hass.data[DOMAIN]["e1"] = mock_coord

        call = MagicMock()
        call.data = {}

        await handlers[SERVICE_IMPORT_HA_DEVICES](call)

        mock_api_client.create_item.assert_awaited_once()
        item_name = mock_api_client.create_item.call_args.kwargs["name"]
        assert "TV" in item_name

    async def test_skips_device_without_name(self, mock_api_client):
        """Devices without a name are skipped."""
        device = MagicMock()
        device.name = None
        device.name_by_user = None

        hass, handlers = self._setup(devices=[device])
        mock_coord = _make_coordinator()
        mock_coord.client = mock_api_client
        hass.data[DOMAIN]["e1"] = mock_coord

        call = MagicMock()
        call.data = {}

        await handlers[SERVICE_IMPORT_HA_DEVICES](call)

        mock_api_client.create_item.assert_not_awaited()

    async def test_filters_by_area_id(self, mock_api_client):
        """Only imports devices whose area_id matches the filter."""
        dev_match = MagicMock()
        dev_match.name = "Light"
        dev_match.name_by_user = None
        dev_match.manufacturer = None
        dev_match.model = None
        dev_match.area_id = "kitchen"

        dev_no_match = MagicMock()
        dev_no_match.name = "Sensor"
        dev_no_match.name_by_user = None
        dev_no_match.area_id = "garage"

        hass, handlers = self._setup(devices=[dev_match, dev_no_match])
        mock_coord = _make_coordinator()
        mock_coord.client = mock_api_client
        hass.data[DOMAIN]["e1"] = mock_coord

        # Area registry for location lookup
        ar_mod = sys.modules["homeassistant.helpers.area_registry"]
        mock_area = MagicMock()
        mock_area.name = "Kitchen"
        ar_mod.async_get.return_value.async_get_area.return_value = mock_area

        call = MagicMock()
        call.data = {"area_id": "kitchen"}

        await handlers[SERVICE_IMPORT_HA_DEVICES](call)

        assert mock_api_client.create_item.call_count == 1

    async def test_all_failures_raise(self, mock_api_client):
        """If all device imports fail, raises HomeAssistantError."""
        from aiohttp import ClientError

        device = MagicMock()
        device.name = "Broken Device"
        device.name_by_user = None
        device.manufacturer = None
        device.model = None
        device.area_id = None

        hass, handlers = self._setup(devices=[device])
        mock_api_client.create_item = AsyncMock(side_effect=ClientError("fail"))
        mock_coord = _make_coordinator()
        mock_coord.client = mock_api_client
        hass.data[DOMAIN]["e1"] = mock_coord

        call = MagicMock()
        call.data = {}

        with pytest.raises(Exception, match="failed"):
            await handlers[SERVICE_IMPORT_HA_DEVICES](call)


# ---------------------------------------------------------------------------
# Service: sync_ha_areas
# ---------------------------------------------------------------------------


class TestSyncHaAreas:
    """Tests for handle_sync_ha_areas service handler."""

    def _setup(self, areas=None, existing_locations=None):
        """Register services, configure area registry, return (hass, handlers)."""
        from custom_components.nesventory import _register_services

        ar_mod = sys.modules["homeassistant.helpers.area_registry"]
        mock_area_reg = MagicMock()
        mock_area_reg.async_list_areas.return_value = areas or []
        ar_mod.async_get.return_value = mock_area_reg

        hass = _make_hass()
        mock_coord = _make_coordinator(
            data={"locations": [{"name": n} for n in (existing_locations or [])]}
        )
        hass.data[DOMAIN] = {}
        _register_services(hass)
        return hass, _get_service_handlers(hass), mock_coord

    async def test_creates_new_location_for_area(self, mock_api_client):
        """Creates a NesVentory location for each HA area."""
        area = MagicMock()
        area.name = "Bedroom"

        hass, handlers, mock_coord = self._setup(areas=[area])
        mock_coord.client = mock_api_client
        hass.data[DOMAIN]["e1"] = mock_coord

        call = MagicMock()
        await handlers[SERVICE_SYNC_HA_AREAS](call)

        mock_api_client.create_location.assert_awaited_once()
        assert mock_api_client.create_location.call_args.kwargs["name"] == "Bedroom"

    async def test_skips_existing_location(self, mock_api_client):
        """Does not create a location that already exists."""
        area = MagicMock()
        area.name = "Kitchen"

        hass, handlers, mock_coord = self._setup(
            areas=[area], existing_locations=["Kitchen"]
        )
        mock_coord.client = mock_api_client
        hass.data[DOMAIN]["e1"] = mock_coord

        call = MagicMock()
        await handlers[SERVICE_SYNC_HA_AREAS](call)

        mock_api_client.create_location.assert_not_awaited()

    async def test_all_failures_raise(self, mock_api_client):
        """If all area syncs fail, raises HomeAssistantError."""
        from aiohttp import ClientError

        area = MagicMock()
        area.name = "Garage"

        hass, handlers, mock_coord = self._setup(areas=[area])
        mock_api_client.create_location = AsyncMock(side_effect=ClientError("fail"))
        mock_coord.client = mock_api_client
        hass.data[DOMAIN]["e1"] = mock_coord

        call = MagicMock()
        with pytest.raises(Exception, match="failed"):
            await handlers[SERVICE_SYNC_HA_AREAS](call)

    async def test_refreshes_after_sync(self, mock_api_client):
        """Refreshes the coordinator after syncing areas."""
        area = MagicMock()
        area.name = "Library"

        hass, handlers, mock_coord = self._setup(areas=[area])
        mock_coord.client = mock_api_client
        hass.data[DOMAIN]["e1"] = mock_coord

        call = MagicMock()
        await handlers[SERVICE_SYNC_HA_AREAS](call)

        mock_coord.async_request_refresh.assert_awaited_once()
