"""Config flow for NesVentory integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api_client import NesVentoryApiClient
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_TRACKED_CATEGORIES,
    CONF_TRACKED_LOCATIONS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Args:
        hass: HomeAssistant instance
        data: User input data

    Returns:
        Dictionary with title for the config entry

    Raises:
        CannotConnect: If connection fails
        InvalidAuth: If authentication fails

    """
    session = async_get_clientsession(hass)
    client = NesVentoryApiClient(
        base_url=data[CONF_URL],
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        session=session,
    )

    if not await client.authenticate():
        raise InvalidAuth

    if not await client.test_connection():
        raise CannotConnect

    return {"title": "NesVentory"}


class ConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):  # pylint: disable=too-few-public-methods
    """Handle a config flow for NesVentory."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class OptionsFlowHandler(
    config_entries.OptionsFlow
):  # pylint: disable=too-few-public-methods
    """Handle NesVentory options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        self._available_categories: list[str] = []
        self._available_locations: list[str] = []

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        # Fetch available categories and locations for the selector
        coordinator = self.hass.data[DOMAIN].get(self._config_entry.entry_id)
        if coordinator and coordinator.data:
            self._available_categories = sorted(
                {
                    cat.get("name", "")
                    for cat in coordinator.data.get("categories", [])
                    if cat.get("name")
                }
            )
            self._available_locations = sorted(
                {
                    loc.get("name", "")
                    for loc in coordinator.data.get("locations", [])
                    if loc.get("name")
                }
            )

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_scan_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        current_tracked_categories = self._config_entry.options.get(
            CONF_TRACKED_CATEGORIES, []
        )
        current_tracked_locations = self._config_entry.options.get(
            CONF_TRACKED_LOCATIONS, []
        )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=current_scan_interval
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=30, max=3600, step=30, mode=NumberSelectorMode.BOX
                    )
                ),
                vol.Optional(
                    CONF_TRACKED_CATEGORIES, default=current_tracked_categories
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=self._available_categories,
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                ),
                vol.Optional(
                    CONF_TRACKED_LOCATIONS, default=current_tracked_locations
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=self._available_locations,
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate invalid authentication."""
