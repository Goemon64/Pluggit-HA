"""The Pluggit config flow."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONFIG_HOST, DOMAIN, SERIAL_NUMBER
from .pypluggit.pluggit import Pluggit

_LOGGER = logging.getLogger(__name__)


async def _validate_input(data: dict[str, Any]) -> str:
    """Check for Host and try to get serial number."""

    host = data[CONFIG_HOST]
    pluggit = Pluggit(host)

    return pluggit.get_serial_number()


class PluggitConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Pluggit."""

    VERSION = 1

    STEP_USER_DATA_SCHEMA = vol.Schema(
        {vol.Required(CONFIG_HOST, description={"suggested_value": "192.168.0.1"}): str}
    )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step for initially adding a device."""
        return await self._async_handle_step(user_input, step_id="user")

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step for reconfiguring an existing device."""
        return await self._async_handle_step(user_input, step_id="reconfigure")

    async def _async_handle_step(
        self, user_input: dict[str, Any] | None, step_id: str
    ) -> ConfigFlowResult:
        """Shared logic for both User and Reconfigure steps."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the device
            ret = await _validate_input(user_input)
            if ret is None:
                errors[CONFIG_HOST] = "invalid_host"
                return self.async_show_form(
                    step_id=step_id,
                    data_schema=self.STEP_USER_DATA_SCHEMA,
                    errors=errors,
                )

            # Set the unique ID based on the device serial number
            await self.async_set_unique_id(str(ret))
            user_input[SERIAL_NUMBER] = ret

            # Check if a config entry with this unique ID already exists
            existing_entry = None
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                if entry.unique_id == str(ret):
                    existing_entry = entry
                    break
            if existing_entry:
                # Update the existing entry & reload
                self.hass.config_entries.async_update_entry(
                    existing_entry, data=user_input
                )
                await self.hass.config_entries.async_reload(existing_entry.entry_id)
                return self.async_abort(reason="reconfigured")

            # No existing entry → create a new config entry
            return self.async_create_entry(title=f"Pluggit {ret}", data=user_input)

        # Show the form if no input has been provided yet
        return self.async_show_form(
            step_id=step_id, data_schema=self.STEP_USER_DATA_SCHEMA, errors=errors
        )
