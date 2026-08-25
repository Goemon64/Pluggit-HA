"""Switch."""

from collections.abc import Callable
from dataclasses import dataclass
import logging
import time
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import StateType
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .__init__ import PluggitData
from .const import DOMAIN
from .pypluggit.const import ActiveUnitMode
from .pypluggit.pluggit import Pluggit

_LOGGER = logging.getLogger(__name__)
# pylint: disable=unnecessary-lambda


@dataclass(kw_only=True)
class PluggitSwitchEntityDescription(SwitchEntityDescription):
    """Describes Pluggit switch entity."""

    on_fn: Callable[[Pluggit], None]
    off_fn: Callable[[Pluggit], None]
    get_fn: Callable[[Pluggit], StateType]
    is_on: Callable[[StateType], bool]
    set_icon: Callable[[StateType], str]


SWITCHES: tuple[PluggitSwitchEntityDescription, ...] = (
    PluggitSwitchEntityDescription(
        key="night_mode",
        translation_key="night_mode",
        entity_category=EntityCategory.CONFIG,
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:weather-night",
        on_fn=lambda device: device.set_unit_mode(ActiveUnitMode.NIGHT_MODE),
        off_fn=lambda device: device.set_unit_mode(ActiveUnitMode.END_NIGHT_MODE),
        get_fn=lambda device: device.get_night_mode_state(),
        is_on=lambda value: help_night_mode(value),
        set_icon=None,
    ),
)


def help_night_mode(value: int) -> bool | None:
    """Is night mode on."""

    ret: bool

    if value == 0:
        ret = False
    elif value == 1:
        ret = True
    else:
        ret = None

    return ret


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch from a config entry."""

    async_add_entities(
        (
            PluggitSwitch(data=entry.runtime_data, description=description)
            for description in SWITCHES
        ),
        update_before_add=True,
    )


class PluggitSwitch(SwitchEntity):
    """Pluggit switch."""

    def __init__(
        self,
        data: PluggitData,
        description: PluggitSwitchEntityDescription,
    ) -> None:
        """Initialise switch."""

        self._data = data
        self.entity_description = description
        self._attr_unique_id = f"{data.serial_number}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_available = False
        self._attr_is_on = False
        self._attr_native_value = 0
        self._attr_device_info = DeviceInfo(
            name="Pluggit", identifiers={(DOMAIN, str(data.serial_number))}
        )

    @property
    def icon(self) -> str | None:
        """Return icon."""
        if self.entity_description.set_icon is not None:
            return self.entity_description.set_icon(self._attr_native_value)

        return self.entity_description.icon

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self.entity_description.on_fn(self._data.pluggit)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self.entity_description.off_fn(self._data.pluggit)

    def update(self) -> None:
        """Fetch data for switch."""
        # If the switch is pressed, there is an update for the status, but this update is to fast. So we wait here.
        time.sleep(100 / 1000)

        self._attr_native_value = self.entity_description.get_fn(self._data.pluggit)

        if self._attr_native_value is None:
            self._attr_available = False
            self._attr_is_on = None
        else:
            self._attr_available = True
            self._attr_is_on = self.entity_description.is_on(self._attr_native_value)
