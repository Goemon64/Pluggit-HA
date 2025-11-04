"""Valve (Bypass)."""

import logging
import time

from homeassistant.components.valve import ValveEntity, ValveEntityFeature, ValveState
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, SERIAL_NUMBER
from .pypluggit.pluggit import ActiveUnitMode, Pluggit

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up valve."""
    data = hass.data[DOMAIN][entry.entry_id]
    pluggit: Pluggit = data[DOMAIN]
    serial_number = data[SERIAL_NUMBER]

    async_add_entities(
        [PluggitValve(pluggit=pluggit, serial_number=serial_number)],
        update_before_add=True,
    )


class PluggitValve(ValveEntity):
    """Pluggit Valve (Bypass)."""

    def __init__(
        self,
        pluggit: Pluggit,
        serial_number: int,
    ) -> None:
        """Initialise Pluggit valve."""
        self._pluggit = pluggit
        self._serial_number = str(serial_number)
        self._attr_unique_id = f"{serial_number}_manual_bypass"
        self._attr_translation_key = "manual_bypass"
        self._attr_has_entity_name = True
        self._attr_available = False
        self._attr_device_class = None
        self._attr_reports_position = False
        self._attr_entity_registry_enabled_default = False
        self._attr_supported_features = (
            ValveEntityFeature.CLOSE | ValveEntityFeature.OPEN
        )
        self._attr_state = None
        self._attr_device_info = DeviceInfo(
            name="Pluggit", identifiers={(DOMAIN, self._serial_number)}
        )

    @property
    def is_closed(self) -> bool:
        """Return if the valve is closed or not."""
        if self._attr_state == ValveState.CLOSED:
            return True

        return False

    @property
    def is_closing(self) -> bool:
        """Return if the valve is closing or not."""
        if self._attr_state == ValveState.CLOSING:
            return True

        return False

    @property
    def is_opening(self) -> bool:
        """Return if the valve is opening or not."""
        if self._attr_state == ValveState.OPENING:
            return True

        return False

    @property
    def icon(self) -> str | None:
        """Return icon."""
        if self._attr_state in (ValveState.CLOSING, ValveState.OPENING):
            return "mdi:valve"

        return None

    def get_valve_state(self, value: str) -> ValveState | None:
        """Set state for valve."""
        if value == "Closed":
            return ValveState.CLOSED
        if value == "Closing":
            return ValveState.CLOSING
        if value == "Opening":
            return ValveState.OPENING
        if value == "Opened":
            return ValveState.OPEN
        if value == "In Process":
            # State didn't changed, so return actual state
            return self._attr_state

        return None

    def open_valve(self) -> None:
        """Open the valve."""
        self._pluggit.set_unit_mode(ActiveUnitMode.SELECT_MANUAL_BYPASS)

    def close_valve(self) -> None:
        """Close valve."""
        self._pluggit.set_unit_mode(ActiveUnitMode.DESELECT_MANUAL_BYPASS)

    def update(self) -> None:
        """Fetch data for valve."""
        # If the switch is pressed, there is an update for the status, but this update is to fast. So we wait here.
        time.sleep(200 / 1000)

        result = self._pluggit.get_bypass_actual_state()
        if result is not None:
            self._attr_state = self.get_valve_state(result)
            self._attr_available = True
        else:
            self._attr_state = None
            self._attr_available = False
