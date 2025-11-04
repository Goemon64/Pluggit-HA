"""Numbers."""

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import StateType
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, SERIAL_NUMBER
from .pypluggit.pluggit import Pluggit

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True)
class PluggitNumberEntityDescription(NumberEntityDescription):
    """Describes Pluggit number entity."""

    get_fn: Callable[[Pluggit], StateType]
    set_fn: Callable[[Pluggit, StateType], None]


NUMBERS: tuple[PluggitNumberEntityDescription, ...] = (
    PluggitNumberEntityDescription(
        key="bypass_tmin",
        translation_key="bypass_tmin",
        device_class=NumberDeviceClass.TEMPERATURE,
        mode=NumberMode.AUTO,
        native_max_value=15,
        native_min_value=12,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        get_fn=lambda device: device.get_bypass_tmin(),
        set_fn=lambda device, temp: device.set_bypass_tmin(temp),
    ),
    PluggitNumberEntityDescription(
        key="bypass_tmax",
        translation_key="bypass_tmax",
        device_class=NumberDeviceClass.TEMPERATURE,
        mode=NumberMode.AUTO,
        native_max_value=27,
        native_min_value=21,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        get_fn=lambda device: device.get_bypass_tmax(),
        set_fn=lambda device, temp: device.set_bypass_tmax(temp),
    ),
    PluggitNumberEntityDescription(
        key="bypass_tmin_summer",
        translation_key="bypass_tmin_summer",
        device_class=NumberDeviceClass.TEMPERATURE,
        mode=NumberMode.AUTO,
        native_max_value=17,
        native_min_value=12,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        get_fn=lambda device: device.get_bypass_tmin_summer(),
        set_fn=lambda device, temp: device.set_bypass_tmin_summer(temp),
    ),
    PluggitNumberEntityDescription(
        key="bypass_tmax_summer",
        translation_key="bypass_tmax_summer",
        device_class=NumberDeviceClass.TEMPERATURE,
        mode=NumberMode.AUTO,
        native_max_value=30,
        native_min_value=21,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        get_fn=lambda device: device.get_bypass_tmax_summer(),
        set_fn=lambda device, temp: device.set_bypass_tmax_summer(temp),
    ),
    PluggitNumberEntityDescription(
        key="filter_time",
        translation_key="filter_time",
        device_class=NumberDeviceClass.DURATION,
        mode=NumberMode.AUTO,
        native_max_value=360,
        native_min_value=0,
        native_unit_of_measurement=UnitOfTime.DAYS,
        get_fn=lambda device: device.get_filter_time(),
        set_fn=lambda device, temp: device.set_default_filter_time(int(temp)),
    ),
    PluggitNumberEntityDescription(
        key="bypass_manual_timeout",
        translation_key="bypass_manual_timeout",
        device_class=NumberDeviceClass.DURATION,
        mode=NumberMode.AUTO,
        native_max_value=480,
        native_min_value=60,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_registry_enabled_default=False,
        get_fn=lambda device: device.get_bypass_manual_timeout(),
        set_fn=lambda device, temp: device.set_bypass_manual_timeout(int(temp)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up numbers from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    pluggit: Pluggit = data[DOMAIN]
    serial_number = data[SERIAL_NUMBER]

    async_add_entities(
        (
            PluggitSensor(
                pluggit=pluggit, serial_number=serial_number, description=description
            )
            for description in NUMBERS
        ),
        update_before_add=True,
    )


class PluggitSensor(NumberEntity):
    """Pluggit numbers."""

    def __init__(
        self,
        pluggit: Pluggit,
        serial_number: int,
        description: PluggitNumberEntityDescription,
    ) -> None:
        """Initialise Pluggit sensor."""
        self._pluggit = pluggit
        self.entity_description = description
        self._serial_number = str(serial_number)
        self._attr_unique_id = f"{serial_number}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_available = False
        self._attr_device_info = DeviceInfo(
            name="Pluggit", identifiers={(DOMAIN, self._serial_number)}
        )

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.entity_description.set_fn(self._pluggit, value)

    def update(self) -> None:
        """Fetch data for numbers."""

        self._attr_native_value = self.entity_description.get_fn(self._pluggit)

        if self._attr_native_value is None:
            self._attr_available = False
        else:
            self._attr_available = True
