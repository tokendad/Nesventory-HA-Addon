"""Tests for NesVentory config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# validate_input
# ---------------------------------------------------------------------------


class TestValidateInput:
    """Tests for config_flow.validate_input()."""

    async def test_success(self):
        """Returns title dict on valid credentials."""
        from custom_components.nesventory.config_flow import validate_input

        mock_hass = MagicMock()
        data = {
            "url": "http://localhost:8001",
            "username": "admin",
            "password": "secret",
        }

        with patch(
            "custom_components.nesventory.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch(
            "custom_components.nesventory.config_flow.NesVentoryApiClient"
        ) as MockClient:
            MockClient.return_value.authenticate = AsyncMock(return_value=True)
            MockClient.return_value.test_connection = AsyncMock(return_value=True)

            result = await validate_input(mock_hass, data)

        assert result == {"title": "NesVentory"}

    async def test_invalid_auth_raises(self):
        """Raises InvalidAuth when authenticate() returns False."""
        from custom_components.nesventory.config_flow import (
            InvalidAuth,
            validate_input,
        )

        with patch(
            "custom_components.nesventory.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch(
            "custom_components.nesventory.config_flow.NesVentoryApiClient"
        ) as MockClient:
            MockClient.return_value.authenticate = AsyncMock(return_value=False)

            with pytest.raises(InvalidAuth):
                await validate_input(MagicMock(), {"url": "", "username": "", "password": ""})

    async def test_cannot_connect_raises(self):
        """Raises CannotConnect when test_connection() returns False."""
        from custom_components.nesventory.config_flow import (
            CannotConnect,
            validate_input,
        )

        with patch(
            "custom_components.nesventory.config_flow.async_get_clientsession",
            return_value=MagicMock(),
        ), patch(
            "custom_components.nesventory.config_flow.NesVentoryApiClient"
        ) as MockClient:
            MockClient.return_value.authenticate = AsyncMock(return_value=True)
            MockClient.return_value.test_connection = AsyncMock(return_value=False)

            with pytest.raises(CannotConnect):
                await validate_input(MagicMock(), {"url": "", "username": "", "password": ""})


# ---------------------------------------------------------------------------
# ConfigFlow.async_step_user
# ---------------------------------------------------------------------------


class TestConfigFlow:
    """Tests for ConfigFlow.async_step_user()."""

    def _make_flow(self):
        """Instantiate ConfigFlow with all HA methods mocked."""
        from custom_components.nesventory.config_flow import ConfigFlow

        flow = ConfigFlow()
        flow.hass = MagicMock()
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        return flow

    async def test_no_input_shows_form(self):
        """No user_input → show form with no errors."""
        flow = self._make_flow()
        result = await flow.async_step_user(None)

        flow.async_show_form.assert_called_once()
        call_kwargs = flow.async_show_form.call_args.kwargs
        assert call_kwargs["step_id"] == "user"
        assert call_kwargs["errors"] == {}

    async def test_valid_input_creates_entry(self):
        """Valid user_input → create entry with unique ID set."""
        flow = self._make_flow()
        user_input = {
            "url": "http://localhost:8001",
            "username": "admin",
            "password": "secret",
        }

        with patch(
            "custom_components.nesventory.config_flow.validate_input",
            new=AsyncMock(return_value={"title": "NesVentory"}),
        ):
            result = await flow.async_step_user(user_input)

        flow.async_set_unique_id.assert_awaited_once_with(user_input["url"])
        flow._abort_if_unique_id_configured.assert_called_once()
        flow.async_create_entry.assert_called_once_with(
            title="NesVentory", data=user_input
        )
        assert result["type"] == "create_entry"

    async def test_invalid_auth_error(self):
        """InvalidAuth → errors["base"] == "invalid_auth", re-shows form."""
        from custom_components.nesventory.config_flow import InvalidAuth

        flow = self._make_flow()

        with patch(
            "custom_components.nesventory.config_flow.validate_input",
            new=AsyncMock(side_effect=InvalidAuth),
        ):
            result = await flow.async_step_user(
                {"url": "x", "username": "u", "password": "p"}
            )

        call_kwargs = flow.async_show_form.call_args.kwargs
        assert call_kwargs["errors"]["base"] == "invalid_auth"

    async def test_cannot_connect_error(self):
        """CannotConnect → errors["base"] == "cannot_connect", re-shows form."""
        from custom_components.nesventory.config_flow import CannotConnect

        flow = self._make_flow()

        with patch(
            "custom_components.nesventory.config_flow.validate_input",
            new=AsyncMock(side_effect=CannotConnect),
        ):
            result = await flow.async_step_user(
                {"url": "x", "username": "u", "password": "p"}
            )

        call_kwargs = flow.async_show_form.call_args.kwargs
        assert call_kwargs["errors"]["base"] == "cannot_connect"

    async def test_unknown_error(self):
        """Unexpected exception → errors["base"] == "unknown", re-shows form."""
        flow = self._make_flow()

        with patch(
            "custom_components.nesventory.config_flow.validate_input",
            new=AsyncMock(side_effect=RuntimeError("boom")),
        ):
            result = await flow.async_step_user(
                {"url": "x", "username": "u", "password": "p"}
            )

        call_kwargs = flow.async_show_form.call_args.kwargs
        assert call_kwargs["errors"]["base"] == "unknown"


# ---------------------------------------------------------------------------
# OptionsFlowHandler.async_step_init
# ---------------------------------------------------------------------------


class TestOptionsFlowHandler:
    """Tests for OptionsFlowHandler.async_step_init()."""

    def _make_handler(self, coord_data=None):
        """Instantiate OptionsFlowHandler with all HA methods mocked."""
        from custom_components.nesventory.config_flow import OptionsFlowHandler
        from custom_components.nesventory.const import DOMAIN

        config_entry = MagicMock()
        config_entry.entry_id = "entry-001"
        config_entry.options = {}

        handler = OptionsFlowHandler(config_entry)
        mock_coordinator = MagicMock()
        mock_coordinator.data = coord_data
        handler.hass = MagicMock()
        handler.hass.data = {DOMAIN: {"entry-001": mock_coordinator}}
        handler.async_show_form = MagicMock(return_value={"type": "form"})
        handler.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        return handler

    async def test_no_input_shows_form(self):
        """No user_input → shows init form."""
        handler = self._make_handler()
        result = await handler.async_step_init(None)

        handler.async_show_form.assert_called_once()
        call_kwargs = handler.async_show_form.call_args.kwargs
        assert call_kwargs["step_id"] == "init"

    async def test_populates_categories_from_coordinator(self):
        """Loads category names from coordinator data into available choices."""
        coord_data = {
            "categories": [{"name": "Electronics"}, {"name": "Supplies"}],
            "locations": [],
        }
        handler = self._make_handler(coord_data)
        await handler.async_step_init(None)

        assert "Electronics" in handler._available_categories
        assert "Supplies" in handler._available_categories

    async def test_populates_locations_from_coordinator(self):
        """Loads location names from coordinator data into available choices."""
        coord_data = {
            "locations": [{"name": "Kitchen"}, {"name": "Garage"}],
            "categories": [],
        }
        handler = self._make_handler(coord_data)
        await handler.async_step_init(None)

        assert "Kitchen" in handler._available_locations
        assert "Garage" in handler._available_locations

    async def test_save_user_input_creates_entry(self):
        """Submitting user_input creates the config entry."""
        from custom_components.nesventory.const import (
            CONF_SCAN_INTERVAL,
            CONF_TRACKED_CATEGORIES,
            CONF_TRACKED_LOCATIONS,
        )

        handler = self._make_handler()
        user_input = {
            CONF_SCAN_INTERVAL: 120,
            CONF_TRACKED_CATEGORIES: ["Electronics"],
            CONF_TRACKED_LOCATIONS: [],
        }
        result = await handler.async_step_init(user_input)

        handler.async_create_entry.assert_called_once_with(title="", data=user_input)
        assert result["type"] == "create_entry"
