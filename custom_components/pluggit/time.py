"""Switch."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import time as date_time
import logging
import time

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import StateType
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .__init__ import PluggitData
from .const import DOMAIN
from .pypluggit.pluggit import Pluggit

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True)
class PluggitTimeEntityDescription(TimeEntityDescription):
    """Describes Pluggit time entity."""

    set_hour_fn: Callable[[Pluggit, StateType], None]
    set_min_fn: Callable[[Pluggit, StateType], None]
    get_hour_fn: Callable[[Pluggit], StateType]
    get_min_fn: Callable[[Pluggit], StateType]


TIMES: tuple[PluggitTimeEntityDescription, ...] = (
    PluggitTimeEntityDescription(
        key="start_time",
        translation_key="start_time",
        entity_category=EntityCategory.CONFIG,
        set_hour_fn=lambda device, hour: device.set_night_mode_start_hour(hour),
        set_min_fn=lambda device, min: device.set_night_mode_start_min(min),
        get_hour_fn=lambda device: device.get_night_mode_start_hour(),
        get_min_fn=lambda device: device.get_night_mode_start_min(),
    ),
    PluggitTimeEntityDescription(
        key="end_time",
        translation_key="end_time",
        entity_category=EntityCategory.CONFIG,
        set_hour_fn=lambda device, hour: device.set_night_mode_end_hour(hour),
        set_min_fn=lambda device, min: device.set_night_mode_end_min(min),
        get_hour_fn=lambda device: device.get_night_mode_end_hour(),
        get_min_fn=lambda device: device.get_night_mode_end_min(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up time from a config entry."""

    async_add_entities(
        (
            PluggitTime(data=entry.runtime_data, description=description)
            for description in TIMES
        ),
        update_before_add=True,
    )


class PluggitTime(TimeEntity):
    """Pluggit time."""

    def __init__(
        self,
        data: PluggitData,
        description: PluggitTimeEntityDescription,
    ) -> None:
        """Initialise time."""

        self._data = data
        self.entity_description = description
        self._attr_unique_id = f"{data.serial_number}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_available = False
        self._attr_native_value = None
        self._attr_device_info = DeviceInfo(
            name="Pluggit", identifiers={(DOMAIN, str(data.serial_number))}
        )

    def set_value(self, value: date_time) -> None:
        """Update the current value."""
        self.entity_description.set_hour_fn(self._data.pluggit, value.hour)
        self.entity_description.set_min_fn(self._data.pluggit, value.minute)

    def update(self) -> None:
        """Fetch data for time."""
        # If a preset mode is set, there is an update. But this update is to fast,
        # the mode on the device isn't ready. So we wait here 100ms.
        time.sleep(100 / 1000)

        hour = self.entity_description.get_hour_fn(self._data.pluggit)
        minute = self.entity_description.get_min_fn(self._data.pluggit)

        if (hour or minute) is None:
            self._attr_available = False
            self._attr_native_value = None
        else:
            self._attr_available = True
            self._attr_native_value = date_time(hour=hour, minute=minute)
