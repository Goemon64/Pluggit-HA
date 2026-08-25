"""The Pluggit integration."""

from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONFIG_HOST, SERIAL_NUMBER
from .pypluggit.pluggit import Pluggit

PLATFORMS = [
    Platform.BUTTON,
    Platform.FAN,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TIME,
    Platform.VALVE,
]
_LOGGER = logging.getLogger(__name__)


@dataclass
class PluggitData:
    """Runtime data for the Pluggit integration."""

    pluggit: Pluggit
    serial_number: str


type PluggitConfigEntry = ConfigEntry[PluggitData]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up pluggit from a config entry."""

    entry.runtime_data = PluggitData(
        pluggit=Pluggit(entry.data[CONFIG_HOST]),
        serial_number=entry.data[SERIAL_NUMBER],
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload pluggit config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
