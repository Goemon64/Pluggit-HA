"""Select."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, SERIAL_NUMBER
from .pypluggit.pluggit import Pluggit, WeekProgram

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up select."""
    data = hass.data[DOMAIN][entry.entry_id]
    pluggit: Pluggit = data[DOMAIN]
    serial_number = data[SERIAL_NUMBER]

    async_add_entities(
        [PluggitSelect(pluggit=pluggit, serial_number=serial_number)],
        update_before_add=True,
    )


class PluggitSelect(SelectEntity):
    """Pluggit Select."""

    OPTIONS = {
        WeekProgram.PROGRAM_1: "1",
        WeekProgram.PROGRAM_2: "2",
        WeekProgram.PROGRAM_3: "3",
        WeekProgram.PROGRAM_4: "4",
        WeekProgram.PROGRAM_5: "5",
        WeekProgram.PROGRAM_6: "6",
        WeekProgram.PROGRAM_7: "7",
        WeekProgram.PROGRAM_8: "8",
        WeekProgram.PROGRAM_9: "9",
        WeekProgram.PROGRAM_10: "10",
        WeekProgram.PROGRAM_11: "11",
    }

    def __init__(
        self,
        pluggit: Pluggit,
        serial_number: int,
    ) -> None:
        """Initialise Pluggit sensor."""
        self._pluggit = pluggit
        self._serial_number = str(serial_number)
        self._attr_unique_id = f"{serial_number}_week_program"
        self._attr_translation_key = "select_week"
        self._attr_current_option = None
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_has_entity_name = True
        self._attr_options = list(self.OPTIONS.values())
        self._attr_available = False
        self._attr_device_info = DeviceInfo(
            name="Pluggit", identifiers={(DOMAIN, self._serial_number)}
        )

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        result = [
            program
            for program, my_option in self.OPTIONS.items()
            if my_option == option
        ]
        self._pluggit.set_week_program(number=result[0])

    def update(self) -> None:
        """Fetch data for select."""

        result = self._pluggit.get_week_program()
        if result is not None:
            self._attr_current_option = self.OPTIONS[result]
            self._attr_available = True
        else:
            self._attr_current_option = None
            self._attr_available = False
