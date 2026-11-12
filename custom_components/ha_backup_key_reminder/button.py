"""Button platform for HA Backup Key Reminder."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BackupKeyReminderCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    buttons = [
        SendReminderButton(coordinator, entry),
        MarkKeyVerifiedButton(coordinator, entry),
    ]

    async_add_entities(buttons)


class BackupKeyReminderButtonBase(ButtonEntity):
    """Base class for Backup Key Reminder buttons."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BackupKeyReminderCoordinator,
        entry: ConfigEntry,
        button_type: str,
    ) -> None:
        """Initialize the button."""
        self.coordinator = coordinator
        self._entry = entry
        self._button_type = button_type
        self._attr_unique_id = f"{entry.entry_id}_{button_type}"
        self._attr_translation_key = button_type
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Backup Key Reminder",
            "manufacturer": "Community",
            "model": "Backup Key Reminder",
            "sw_version": "1.0.1",
        }


class SendReminderButton(BackupKeyReminderButtonBase):
    """Button to send reminder immediately."""

    _attr_icon = "mdi:bell-ring"

    def __init__(
        self, coordinator: BackupKeyReminderCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry, "send_reminder_now")

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.send_reminder(force=True)


class MarkKeyVerifiedButton(BackupKeyReminderButtonBase):
    """Button to mark key as verified."""

    _attr_icon = "mdi:check-decagram"

    def __init__(
        self, coordinator: BackupKeyReminderCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry, "mark_key_verified")

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.mark_key_verified()
