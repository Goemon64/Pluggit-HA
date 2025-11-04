"""The Pluggit config flow."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONFIG_HOST, DOMAIN, SERIAL_NUMBER
from .pypluggit.pluggit import Pluggit

_LOGGER = logging.getLogger(__name__)


async def validate_input(data: dict[str, Any]) -> str:
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
        """Show form and get host address."""
        errors = {}

        if user_input is not None:
            ret = await validate_input(user_input)
            errors[CONFIG_HOST] = "No valid host or connection!"
            if ret is not None:
                user_input[SERIAL_NUMBER] = ret
                await self.async_set_unique_id(str(ret))
                return self.async_create_entry(title="Pluggit", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=self.STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show form for reconfigure host address."""
        errors = {}

        if user_input is not None:
            ret = await validate_input(user_input)
            errors[CONFIG_HOST] = "No valid host or connection!"
            if ret is not None:
                user_input[SERIAL_NUMBER] = ret
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    data_updates=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure", data_schema=self.STEP_USER_DATA_SCHEMA, errors=errors
        )
