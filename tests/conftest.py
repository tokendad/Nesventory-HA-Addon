"""Test configuration and fixtures for NesVentory integration."""

from __future__ import annotations

import sys
import types
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Stub out the homeassistant package so unit tests run without a full HA install
# ---------------------------------------------------------------------------
def _make_module(name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


# Top-level stubs
for _mod in [
    "homeassistant",
    "homeassistant.config_entries",
    "homeassistant.const",
    "homeassistant.core",
    "homeassistant.exceptions",
    "homeassistant.helpers",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.area_registry",
    "homeassistant.helpers.device_registry",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.selector",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.components",
    "homeassistant.components.sensor",
    "homeassistant.data_entry_flow",
]:
    _make_module(_mod)

# Populate the constants/classes tests actually need
_const = sys.modules["homeassistant.const"]
_const.CONF_URL = "url"
_const.CONF_USERNAME = "username"
_const.CONF_PASSWORD = "password"
_const.CURRENCY_DOLLAR = "USD"
_const.Platform = MagicMock()

_sensor = sys.modules["homeassistant.components.sensor"]
_sensor.SensorDeviceClass = MagicMock()
_sensor.SensorEntity = object
_sensor.SensorStateClass = MagicMock()

_coord = sys.modules["homeassistant.helpers.update_coordinator"]
_coord.DataUpdateCoordinator = object
_coord.UpdateFailed = Exception
_coord.CoordinatorEntity = object

_cfg = sys.modules["homeassistant.config_entries"]
_cfg.ConfigEntry = MagicMock
_cfg.ConfigFlow = object
_cfg.OptionsFlow = object

_exc = sys.modules["homeassistant.exceptions"]
_exc.ConfigEntryAuthFailed = Exception
_exc.HomeAssistantError = Exception

_sel = sys.modules["homeassistant.helpers.selector"]
for _cls in ("NumberSelector", "NumberSelectorConfig", "NumberSelectorMode",
             "SelectSelector", "SelectSelectorConfig", "SelectSelectorMode"):
    setattr(_sel, _cls, MagicMock)

_flow = sys.modules["homeassistant.data_entry_flow"]
_flow.FlowResult = dict

_core = sys.modules["homeassistant.core"]
_core.HomeAssistant = MagicMock
_core.ServiceCall = MagicMock
_core.callback = lambda f: f

_aiohttp_client = sys.modules["homeassistant.helpers.aiohttp_client"]
_aiohttp_client.async_get_clientsession = MagicMock()

_area_reg = sys.modules["homeassistant.helpers.area_registry"]
_area_reg.async_get = MagicMock()

_device_reg = sys.modules["homeassistant.helpers.device_registry"]
_device_reg.async_get = MagicMock()

_entity_platform = sys.modules["homeassistant.helpers.entity_platform"]
_entity_platform.AddEntitiesCallback = MagicMock



@pytest.fixture
def mock_api_client():
    """Create a mock NesVentoryApiClient."""
    client = MagicMock()
    client.authenticate = AsyncMock(return_value=True)
    client.test_connection = AsyncMock(return_value=True)
    client.get_items = AsyncMock(
        return_value=[
            {
                "id": 1,
                "name": "Nintendo Switch",
                "value": 299.99,
                "status": "Active",
                "category": "Electronics",
                "location": "Living Room",
            },
            {
                "id": 2,
                "name": "AA Batteries (4-pack)",
                "price": 5.99,
                "status": "Active",
                "category": "Supplies",
                "location": "Kitchen",
            },
        ]
    )
    client.get_locations = AsyncMock(
        return_value=[
            {"id": 1, "name": "Living Room"},
            {"id": 2, "name": "Kitchen"},
        ]
    )
    client.get_categories = AsyncMock(
        return_value=[
            {"id": 1, "name": "Electronics"},
            {"id": 2, "name": "Supplies"},
        ]
    )
    client.create_item = AsyncMock(return_value={"id": 99, "name": "Test Item"})
    client.create_location = AsyncMock(return_value={"id": 99, "name": "Test Location"})
    return client


@pytest.fixture
def mock_coordinator_data():
    """Return sample coordinator data."""
    return {
        "items": [
            {
                "id": 1,
                "name": "Nintendo Switch",
                "value": 299.99,
                "status": "Active",
                "category": "Electronics",
                "location": "Living Room",
            },
            {
                "id": 2,
                "name": "AA Batteries (4-pack)",
                "price": 5.99,
                "status": "Active",
                "category": "Supplies",
                "location": "Kitchen",
            },
        ],
        "total_count": 2,
        "total_value": 305.98,
        "locations": [
            {"id": 1, "name": "Living Room"},
            {"id": 2, "name": "Kitchen"},
        ],
        "categories": [
            {"id": 1, "name": "Electronics"},
            {"id": 2, "name": "Supplies"},
        ],
    }
