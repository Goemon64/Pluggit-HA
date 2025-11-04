"""Button."""

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.dt import as_timestamp, now

from .const import DOMAIN, SERIAL_NUMBER
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
        set_fn=lambda device: device.reset_filter(),
    ),
    PluggitButtonEntityDescription(
        key="date_time",
        translation_key="date_time",
        set_fn=lambda device: device.set_date_time(help_time()),
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
    data = hass.data[DOMAIN][entry.entry_id]
    pluggit: Pluggit = data[DOMAIN]
    serial_number = data[SERIAL_NUMBER]

    async_add_entities(
        (
            PluggitButton(
                pluggit=pluggit, serial_number=serial_number, description=description
            )
            for description in BUTTONS
        ),
        update_before_add=True,
    )


class PluggitButton(ButtonEntity):
    """Pluggit buttons."""

    def __init__(
        self,
        pluggit: Pluggit,
        serial_number: int,
        description: PluggitButtonEntityDescription,
    ) -> None:
        """Initialise Pluggit button."""
        self._pluggit = pluggit
        self.entity_description = description
        self._serial_number = str(serial_number)
        self._attr_unique_id = f"{serial_number}_{description.key}"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_has_entity_name = True
        self._attr_available = False
        self._attr_device_info = DeviceInfo(
            name="Pluggit", identifiers={(DOMAIN, self._serial_number)}
        )

    def press(self) -> None:
        """Handle the button press."""
        self.entity_description.set_fn(self._pluggit)

    def update(self) -> None:
        """Check if button is available."""
        if self._pluggit.get_unit_type() is None:
            self._attr_available = False
        else:
            self._attr_available = True
