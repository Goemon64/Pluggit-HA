"""Fan."""

import logging
import time
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .const import DOMAIN, SERIAL_NUMBER
from .pypluggit.const import CURRENT_UNIT_MODE, ActiveUnitMode, SpeedLevelFan
from .pypluggit.pluggit import Pluggit

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up fan from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    pluggit: Pluggit = data[DOMAIN]
    serial_num = data[SERIAL_NUMBER]

    device = DeviceInfo(
        identifiers={(DOMAIN, str(serial_num))},
        name="Pluggit",
        manufacturer="Pluggit",
        model=pluggit.get_unit_type(),
        sw_version=pluggit.get_firmware_version(),
        serial_number=serial_num,
    )

    async_add_entities(
        [PluggitFan(pluggit=pluggit, device=device)], update_before_add=True
    )


class PluggitFan(FanEntity):
    """Pluggit fan."""

    ORDERED_NAMED_FAN_SPEEDS = [
        SpeedLevelFan.LEVEL_1,
        SpeedLevelFan.LEVEL_2,
        SpeedLevelFan.LEVEL_3,
        SpeedLevelFan.LEVEL_4,
    ]
    SUPPORTED_PRESET_MODES = [
        CURRENT_UNIT_MODE[1],
        CURRENT_UNIT_MODE[2],
        CURRENT_UNIT_MODE[3],
        CURRENT_UNIT_MODE[5],
        CURRENT_UNIT_MODE[6],
        CURRENT_UNIT_MODE[9],
    ]

    def __init__(self, pluggit: Pluggit, device: DeviceInfo) -> None:
        """Initialise Ventilation."""
        self._pluggit = pluggit
        self._speedLevel = SpeedLevelFan.LEVEL_1
        self._currentMode = CURRENT_UNIT_MODE[0]
        self._attr_unique_id = f"{device['serial_number']}_fan"
        self._attr_available = False
        self._attr_has_entity_name = True
        self._attr_device_info = device
        self._attr_translation_key = "ventilation"
        self._attr_supported_features = (
            FanEntityFeature.PRESET_MODE
            | FanEntityFeature.SET_SPEED
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
        )

    def __set_unit_mode(self, mode: ActiveUnitMode, speed: SpeedLevelFan | None = None):
        if self._currentMode is not mode:
            if self._currentMode == CURRENT_UNIT_MODE[6]:
                self._pluggit.set_unit_mode(ActiveUnitMode.END_SUMMER_MODE)
            elif self._currentMode == CURRENT_UNIT_MODE[9]:
                self._pluggit.set_unit_mode(ActiveUnitMode.END_FIREPLACE_MODE)

            time.sleep(100 / 1000)
            self._pluggit.set_unit_mode(mode=mode)

        if speed is not None:
            time.sleep(100 / 1000)
            ret = self._pluggit.get_current_unit_mode()
            if ret == CURRENT_UNIT_MODE[1] or CURRENT_UNIT_MODE[6]:
                self._pluggit.set_speed_level(speed=speed)

    @property
    def is_on(self) -> bool | None:
        """Return true if fan is on."""
        return self._speedLevel.value > 0

    @property
    def percentage(self) -> int | None:
        """Return the speed of the fan in percentage."""
        if self._speedLevel is SpeedLevelFan.LEVEL_0:
            return 0

        return ordered_list_item_to_percentage(
            self.ORDERED_NAMED_FAN_SPEEDS, self._speedLevel
        )

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return len(self.ORDERED_NAMED_FAN_SPEEDS)

    @property
    def preset_mode(self) -> str | None:
        """Return actual preset mode."""
        if self._currentMode in self.SUPPORTED_PRESET_MODES:
            return self._currentMode
        return None

    @property
    def preset_modes(self) -> list[str] | None:
        """Return a list of preset modes."""
        return self.SUPPORTED_PRESET_MODES

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""

        mode = None
        if preset_mode == CURRENT_UNIT_MODE[1]:
            mode = ActiveUnitMode.MANUAL_MODE
        elif preset_mode == CURRENT_UNIT_MODE[2]:
            mode = ActiveUnitMode.DEMAND_MODE
        elif preset_mode == CURRENT_UNIT_MODE[3]:
            mode = ActiveUnitMode.WEEK_PROGRAM_MODE
        elif preset_mode == CURRENT_UNIT_MODE[5]:
            mode = ActiveUnitMode.AWAY_MODE
        elif preset_mode == CURRENT_UNIT_MODE[6]:
            mode = ActiveUnitMode.SUMMER_MODE
        elif preset_mode == CURRENT_UNIT_MODE[9]:
            mode = ActiveUnitMode.FIREPLACE_MODE
        else:
            return

        self.__set_unit_mode(mode=mode)

    def set_percentage(self, percentage: int) -> None:
        """Set fan speed in percentage."""
        active_mode = ActiveUnitMode.MANUAL_MODE
        named_speed = percentage_to_ordered_list_item(
            self.ORDERED_NAMED_FAN_SPEEDS, percentage
        )
        if percentage == 0:
            named_speed = SpeedLevelFan.LEVEL_0

        if self._currentMode == CURRENT_UNIT_MODE[6]:
            active_mode = ActiveUnitMode.SUMMER_MODE

        self.__set_unit_mode(mode=active_mode, speed=named_speed)

    @property
    def icon(self) -> str | None:
        """Return icon depending on speed."""
        if self._speedLevel is SpeedLevelFan.LEVEL_1:
            return "mdi:fan-speed-1"
        if self._speedLevel is SpeedLevelFan.LEVEL_2:
            return "mdi:fan-speed-2"
        if self._speedLevel is SpeedLevelFan.LEVEL_3:
            return "mdi:fan-speed-3"
        if self._speedLevel is SpeedLevelFan.LEVEL_4:
            return "mdi:fan-plus"

        return None

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if preset_mode is not None:
            self.set_preset_mode(preset_mode=preset_mode)
            return

        self._pluggit.set_speed_level(SpeedLevelFan.LEVEL_1)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        self.__set_unit_mode(
            mode=ActiveUnitMode.MANUAL_MODE, speed=SpeedLevelFan.LEVEL_0
        )

    def update(self) -> None:
        """Fetch data for fan."""
        # If a preset mode is set, there is an update. But this update is to fast,
        # the mode on the device isn't ready. So we wait here 100ms.
        time.sleep(100 / 1000)
        try:
            self._speedLevel = SpeedLevelFan(self._pluggit.get_speed_level())
        except ValueError:
            self._speedLevel = None
        self._currentMode = self._pluggit.get_current_unit_mode()

        if self._speedLevel is None or self._currentMode is None:
            self._attr_available = False
        else:
            self._attr_available = True
