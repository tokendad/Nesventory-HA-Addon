"""The NesVentory integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import NesVentoryApiClient
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SERVICE_ADD_QUICK_ITEM,
    SERVICE_IMPORT_HA_DEVICES,
    SERVICE_SYNC_HA_AREAS,
)
from .coordinator import NesVentoryDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Service schemas
ADD_QUICK_ITEM_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Optional("quantity", default=1): vol.All(int, vol.Range(min=1, max=999)),
        vol.Optional("location"): str,
        vol.Optional("category"): str,
    }
)

IMPORT_HA_DEVICES_SCHEMA = vol.Schema(
    {
        vol.Optional("area_id"): str,
        vol.Optional("overwrite", default=False): bool,
    }
)

SYNC_HA_AREAS_SCHEMA = vol.Schema({})


def _get_client(hass: HomeAssistant) -> NesVentoryApiClient:
    """Get the API client from the first loaded config entry."""
    for coordinator in hass.data.get(DOMAIN, {}).values():
        return coordinator.client
    raise HomeAssistantError("NesVentory integration is not configured")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NesVentory from a config entry."""
    _LOGGER.debug("Setting up NesVentory integration")

    session = async_get_clientsession(hass)
    client = NesVentoryApiClient(
        base_url=entry.data[CONF_URL],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        session=session,
    )

    if not await client.authenticate():
        _LOGGER.error("Failed to authenticate with NesVentory")
        raise ConfigEntryAuthFailed("Invalid credentials for NesVentory")

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = NesVentoryDataUpdateCoordinator(hass, client, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services (only once — check if already registered)
    if not hass.services.has_service(DOMAIN, SERVICE_ADD_QUICK_ITEM):
        _register_services(hass)

    # Re-setup when options change (updates scan interval, dynamic sensors)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update — reload to apply new scan interval and sensor list."""
    await hass.config_entries.async_reload(entry.entry_id)


def _register_services(  # pylint: disable=too-many-statements
    hass: HomeAssistant,
) -> None:
    """Register NesVentory custom services."""

    async def handle_add_quick_item(call: ServiceCall) -> None:
        """Handle the add_quick_item service call."""
        client = _get_client(hass)
        name: str = call.data["name"]
        quantity: int = call.data.get("quantity", 1)
        location: str | None = call.data.get("location")
        category: str | None = call.data.get("category")

        try:
            result = await client.create_item(
                name=name,
                quantity=quantity,
                location=location,
                category=category,
            )
            _LOGGER.info(
                "Created item '%s' in NesVentory (id=%s)",
                name,
                result.get("id"),
            )
            # Refresh coordinator data so sensors update immediately
            for coordinator in hass.data.get(DOMAIN, {}).values():
                await coordinator.async_request_refresh()
        except Exception as err:
            raise HomeAssistantError(f"Failed to add item '{name}': {err}") from err

    async def handle_import_ha_devices(  # pylint: disable=too-many-locals
        call: ServiceCall,
    ) -> None:
        """Handle the import_ha_devices service call."""
        client = _get_client(hass)
        area_id_filter: str | None = call.data.get("area_id")

        device_reg = dr.async_get(hass)
        devices = list(device_reg.devices.values())

        if area_id_filter:
            devices = [d for d in devices if d.area_id == area_id_filter]

        imported = 0
        skipped = 0
        failed = 0

        for device in devices:
            name = device.name_by_user or device.name
            if not name:
                skipped += 1
                continue

            try:
                # Build rich name: "Manufacturer Model - Device Name"
                parts = []
                if device.manufacturer:
                    parts.append(device.manufacturer)
                if device.model:
                    parts.append(device.model)
                item_name = f"{' '.join(parts)} - {name}" if parts else name

                # Determine location from HA area
                location: str | None = None
                if device.area_id:
                    area_reg = ar.async_get(hass)
                    area = area_reg.async_get_area(device.area_id)
                    if area:
                        location = area.name

                await client.create_item(
                    name=item_name,
                    quantity=1,
                    location=location,
                    category="Smart Home Device",
                )
                imported += 1
                _LOGGER.debug("Imported HA device '%s' to NesVentory", item_name)

            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOGGER.warning("Failed to import device '%s': %s", name, err)
                failed += 1

        _LOGGER.info(
            "HA device import complete: %d imported, %d skipped, %d failed",
            imported,
            skipped,
            failed,
        )
        if failed and not imported:
            raise HomeAssistantError(
                f"All {failed} device imports failed. Check logs for details."
            )

        # Refresh coordinator
        for coordinator in hass.data.get(DOMAIN, {}).values():
            await coordinator.async_request_refresh()

    async def handle_sync_ha_areas(_call: ServiceCall) -> None:
        """Handle the sync_ha_areas service call."""
        client = _get_client(hass)
        area_reg = ar.async_get(hass)
        areas = list(area_reg.async_list_areas())

        created = 0
        failed = 0

        # Get existing location names to avoid duplicates
        existing_names: set[str] = set()
        for coordinator in hass.data.get(DOMAIN, {}).values():
            if coordinator.data:
                existing_names = {
                    loc.get("name", "")
                    for loc in coordinator.data.get("locations", [])
                    if loc.get("name")
                }
            break

        for area in areas:
            if area.name in existing_names:
                _LOGGER.debug("Location '%s' already exists, skipping", area.name)
                continue
            try:
                await client.create_location(name=area.name)
                created += 1
                _LOGGER.debug("Created NesVentory location for HA area '%s'", area.name)
            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOGGER.warning(
                    "Failed to create location for area '%s': %s", area.name, err
                )
                failed += 1

        _LOGGER.info("HA areas sync complete: %d created, %d failed", created, failed)
        if failed and not created:
            raise HomeAssistantError(
                f"All {failed} area syncs failed. Check logs for details."
            )

        # Refresh coordinator
        for coordinator in hass.data.get(DOMAIN, {}).values():
            await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_QUICK_ITEM,
        handle_add_quick_item,
        schema=ADD_QUICK_ITEM_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_IMPORT_HA_DEVICES,
        handle_import_ha_devices,
        schema=IMPORT_HA_DEVICES_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SYNC_HA_AREAS,
        handle_sync_ha_areas,
        schema=SYNC_HA_AREAS_SCHEMA,
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading NesVentory integration")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    # Remove services when last entry is unloaded
    if not hass.data.get(DOMAIN):
        for service in (
            SERVICE_ADD_QUICK_ITEM,
            SERVICE_IMPORT_HA_DEVICES,
            SERVICE_SYNC_HA_AREAS,
        ):
            hass.services.async_remove(DOMAIN, service)

    return unload_ok
