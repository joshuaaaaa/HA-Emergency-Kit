"""HA Backup Key Reminder integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    EVENT_HOMEASSISTANT_STARTED,
    Platform,
    __version__ as HA_VERSION,
)
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.components.persistent_notification import (
    async_create as async_create_notification,
    async_dismiss as async_dismiss_notification,
)

from .const import (
    DOMAIN,
    CONF_NOTIFICATION_METHODS,
    CONF_FREQUENCY,
    CONF_CUSTOM_DAYS,
    CONF_MESSAGE_TYPE,
    CONF_CUSTOM_MESSAGE,
    CONF_NOTIFY_ON_UPDATE,
    CONF_NOTIFY_SERVICES,
    FREQUENCY_OPTIONS,
    FREQUENCY_CUSTOM,
    NOTIFY_PERSISTENT,
    MESSAGE_CUSTOM,
    DEFAULT_MESSAGES_EN,
    DEFAULT_MESSAGES_CS,
    SERVICE_SEND_REMINDER,
    SERVICE_RESET_TIMER,
    SERVICE_MARK_KEY_VERIFIED,
    STORAGE_KEY,
    STORAGE_VERSION,
    ATTR_LAST_NOTIFIED,
    ATTR_NEXT_NOTIFICATION,
    ATTR_NOTIFICATION_COUNT,
    ATTR_HA_VERSION,
)
from .coordinator import BackupKeyReminderCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HA Backup Key Reminder component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Backup Key Reminder from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize storage
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    stored_data = await store.async_load() or {}

    # Initialize coordinator
    coordinator = BackupKeyReminderCoordinator(hass, entry, store, stored_data)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "store": store,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_register_services(hass, coordinator)

    # Schedule reminder check
    await coordinator.schedule_reminder_check()

    # Check for HA version changes
    if entry.options.get(CONF_NOTIFY_ON_UPDATE, True):
        await coordinator.check_ha_version_change()

    # Listen for HA start event
    @callback
    def async_on_ha_start(event):
        """Handle HA start event."""
        hass.async_create_task(coordinator.check_and_send_reminder())

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, async_on_ha_start)

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator = data["coordinator"]
        await coordinator.async_shutdown()

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_register_services(
    hass: HomeAssistant, coordinator: BackupKeyReminderCoordinator
) -> None:
    """Register integration services."""

    async def handle_send_reminder(call: ServiceCall) -> None:
        """Handle the send_reminder service call."""
        await coordinator.send_reminder(force=True)

    async def handle_reset_timer(call: ServiceCall) -> None:
        """Handle the reset_timer service call."""
        await coordinator.reset_timer()

    async def handle_mark_key_verified(call: ServiceCall) -> None:
        """Handle the mark_key_verified service call."""
        await coordinator.mark_key_verified()

    hass.services.async_register(DOMAIN, SERVICE_SEND_REMINDER, handle_send_reminder)
    hass.services.async_register(DOMAIN, SERVICE_RESET_TIMER, handle_reset_timer)
    hass.services.async_register(
        DOMAIN, SERVICE_MARK_KEY_VERIFIED, handle_mark_key_verified
    )
