"""Button."""

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.dt import as_timestamp, now

from .__init__ import PluggitData
from .const import DOMAIN
from .pypluggit.pluggit import Pluggit

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True)
class PluggitButtonEntityDescription(ButtonEntityDescription):
    """Describes Pluggit button entity."""

    set_fn: Callable[[Pluggit], None]


BUTTONS: tuple[PluggitButtonEntityDescription, ...] = (
    PluggitButtonEntityDescription(
        key="filter_reset",
        translation_key="filter_reset",
        entity_category=EntityCategory.CONFIG,
        set_fn=lambda device: device.reset_filter(),
    ),
    PluggitButtonEntityDescription(
        key="date_time",
        translation_key="date_time",
        entity_category=EntityCategory.CONFIG,
        set_fn=lambda device: device.set_date_time(help_time()),
    ),
    PluggitButtonEntityDescription(
        key="reset_alarm",
        translation_key="reset_alarm",
        entity_category=EntityCategory.DIAGNOSTIC,
        set_fn=lambda device: device.set_alarm_acknowledge(
            device.get_last_active_alarm()
        ),
    ),
)


def help_time() -> int:
    """Get local time in seconds."""
    time = now()
    return int(as_timestamp(time) + time.utcoffset().total_seconds())


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up buttons from a config entry."""

    async_add_entities(
        (
            PluggitButton(data=entry.runtime_data, description=description)
            for description in BUTTONS
        ),
        update_before_add=True,
    )


class PluggitButton(ButtonEntity):
    """Pluggit buttons."""

    def __init__(
        self,
        data: PluggitData,
        description: PluggitButtonEntityDescription,
    ) -> None:
        """Initialise Pluggit button."""
        self._data = data
        self.entity_description = description
        self._attr_unique_id = f"{data.serial_number}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_available = False
        self._attr_device_info = DeviceInfo(
            name="Pluggit", identifiers={(DOMAIN, str(data.serial_number))}
        )

    def press(self) -> None:
        """Handle the button press."""
        self.entity_description.set_fn(self._data.pluggit)

    def update(self) -> None:
        """Check if button is available."""
        if self._data.pluggit.get_unit_type() is None:
            self._attr_available = False
        else:
            self._attr_available = True
