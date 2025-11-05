"""Sensors."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util.dt import DEFAULT_TIME_ZONE, now

from .const import DOMAIN, SERIAL_NUMBER
from .pypluggit.pluggit import (
    BYPASS_STATE,
    CURRENT_UNIT_MODE,
    DEGREE_OF_DIRTINESS,
    Pluggit,
    SpeedLevelFan,
)

_LOGGER = logging.getLogger(__name__)
# pylint: disable=unnecessary-lambda
# SCAN_INTERVAL = timedelta(seconds=20)


@dataclass(kw_only=True)
class PluggitSensorEntityDescription(SensorEntityDescription):
    """Describes Pluggit sensor entity."""

    value_fn: Callable[[Pluggit], StateType]
    icon_fn: Callable[[StateType], str]


SENSORS: tuple[PluggitSensorEntityDescription, ...] = (
    PluggitSensorEntityDescription(
        key="T1",
        translation_key="t1_outdoor",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.get_temperature_t1(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="T2",
        translation_key="t2_supply",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.get_temperature_t2(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="T3",
        translation_key="t3_extract",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.get_temperature_t3(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="T4",
        translation_key="t4_exhaust",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.get_temperature_t4(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="work_time",
        translation_key="work_time",
        entity_category=EntityCategory.DIAGNOSTIC,
        # device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:progress-clock",
        value_fn=lambda device: device.get_work_time(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="filter_remain",
        translation_key="filter_remain",
        # device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        value_fn=lambda device: device.get_remaining_filter_time(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="filter_dirtiness",
        translation_key="filter_dirtiness",
        device_class=SensorDeviceClass.ENUM,
        options=list(DEGREE_OF_DIRTINESS.values()),
        icon="mdi:liquid-spot",
        value_fn=lambda device: device.get_filter_dirtiness(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="bypass_state",
        translation_key="bypass_state",
        device_class=SensorDeviceClass.ENUM,
        options=list(BYPASS_STATE.values()),
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.get_bypass_actual_state(),
        icon_fn=lambda value: set_bypass_icon(value),
    ),
    PluggitSensorEntityDescription(
        key="get_time",
        translation_key="get_time",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        state_class=None,
        entity_registry_enabled_default=False,
        value_fn=lambda device: help_time(device.get_date_time()),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="get_unit_mode",
        translation_key="unit_mode",
        device_class=SensorDeviceClass.ENUM,
        options=list(CURRENT_UNIT_MODE.values()),
        icon="mdi:information-outline",
        value_fn=lambda device: device.get_current_unit_mode(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="get_spped_level",
        translation_key="speed_level",
        device_class=SensorDeviceClass.ENUM,
        options=[e.value for e in SpeedLevelFan],
        entity_registry_enabled_default=False,
        icon="mdi:fan",
        value_fn=lambda device: device.get_speed_level(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="get_humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.get_humidity(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="get_voc",
        translation_key="voc",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.get_voc(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="get_fan_1",
        translation_key="fan1",
        device_class=None,
        native_unit_of_measurement="rpm",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.get_fan_speed_1(),
        icon_fn=None,
    ),
    PluggitSensorEntityDescription(
        key="get_fan_2",
        translation_key="fan2",
        device_class=None,
        native_unit_of_measurement="rpm",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.get_fan_speed_2(),
        icon_fn=None,
    ),
)


def set_bypass_icon(value: str) -> str | None:
    """Set icon for manual bypass."""

    if value == "Closed":
        return "mdi:valve-closed"
    if value in ("In Process", "Closing", "Opening"):
        return "mdi:valve"
    if value == "Opened":
        return "mdi:valve-open"

    # if the connection is lost, this icon is set as a standard
    return "mdi:valve-closed"


def help_time(local_time: int) -> datetime | None:
    """Get time from local seconds."""
    if local_time is None:
        return None

    return datetime.fromtimestamp(
        local_time - now().utcoffset().total_seconds(), tz=DEFAULT_TIME_ZONE
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    pluggit: Pluggit = data[DOMAIN]
    serial_number = data[SERIAL_NUMBER]

    async_add_entities(
        (
            PluggitSensor(
                pluggit=pluggit, serial_number=serial_number, description=description
            )
            for description in SENSORS
        ),
        update_before_add=True,
    )


class PluggitSensor(SensorEntity):
    """Pluggit sensors."""

    def __init__(
        self,
        pluggit: Pluggit,
        serial_number: int,
        description: PluggitSensorEntityDescription,
    ) -> None:
        """Initialise Pluggit sensor."""
        self._pluggit = pluggit
        self.entity_description = description
        self._serial_number = str(serial_number)
        self._attr_unique_id = f"{serial_number}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_available = False
        self._attr_device_info = DeviceInfo(
            name="Pluggit", identifiers={(DOMAIN, self._serial_number)}
        )

    @property
    def icon(self) -> str | None:
        """Return icon."""
        if self.entity_description.icon_fn is not None:
            return self.entity_description.icon_fn(self._attr_native_value)

        return self.entity_description.icon

    def update(self) -> None:
        """Fetch data for sensors."""

        self._attr_native_value = self.entity_description.value_fn(self._pluggit)

        if self._attr_native_value is None:
            self._attr_available = False
        else:
            self._attr_available = True
