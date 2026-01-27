"""Data coordinator for HA Backup Key Reminder."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval, async_call_later
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.persistent_notification import (
    async_create as async_create_notification,
)
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_NOTIFICATION_METHODS,
    CONF_FREQUENCY,
    CONF_CUSTOM_DAYS,
    CONF_MESSAGE_TYPE,
    CONF_CUSTOM_MESSAGE,
    CONF_NOTIFY_ON_UPDATE,
    CONF_NOTIFICATION_TIME,
    CONF_FOLLOWUP_ENABLED,
    CONF_FOLLOWUP_DELAY,
    FREQUENCY_OPTIONS,
    FREQUENCY_CUSTOM,
    NOTIFY_PERSISTENT,
    MESSAGE_CUSTOM,
    DEFAULT_MESSAGES_EN,
    DEFAULT_MESSAGES_CS,
    ATTR_LAST_NOTIFIED,
    ATTR_NEXT_NOTIFICATION,
    ATTR_NOTIFICATION_COUNT,
    ATTR_HA_VERSION,
    DEFAULT_FREQUENCY,
    DEFAULT_CUSTOM_DAYS,
    DEFAULT_MESSAGE_TYPE,
    DEFAULT_NOTIFICATION_TIME,
    DEFAULT_FOLLOWUP_ENABLED,
    DEFAULT_FOLLOWUP_DELAY,
)

_LOGGER = logging.getLogger(__name__)


class BackupKeyReminderCoordinator(DataUpdateCoordinator):
    """Coordinator for HA Backup Key Reminder."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        store: Store,
        stored_data: dict[str, Any],
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.entry = entry
        self.store = store
        self._stored_data = stored_data
        self._unsub_timer: callable | None = None
        self._unsub_followup: callable | None = None
        self._last_notified: datetime | None = None
        self._notification_count: int = 0
        self._ha_version_at_last_notification: str | None = None

        # Load stored data
        self._load_stored_data()

    def _load_stored_data(self) -> None:
        """Load data from storage."""
        if self._stored_data:
            last_notified_str = self._stored_data.get(ATTR_LAST_NOTIFIED)
            if last_notified_str:
                try:
                    self._last_notified = datetime.fromisoformat(last_notified_str)
                except (ValueError, TypeError):
                    self._last_notified = None

            self._notification_count = self._stored_data.get(ATTR_NOTIFICATION_COUNT, 0)
            self._ha_version_at_last_notification = self._stored_data.get(ATTR_HA_VERSION)

    async def _async_save_data(self) -> None:
        """Save data to storage."""
        data = {
            ATTR_LAST_NOTIFIED: (
                self._last_notified.isoformat() if self._last_notified else None
            ),
            ATTR_NOTIFICATION_COUNT: self._notification_count,
            ATTR_HA_VERSION: self._ha_version_at_last_notification,
        }
        await self.store.async_save(data)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data for the coordinator."""
        frequency_days = self._get_frequency_days()
        next_notification = self._calculate_next_notification()
        days_until_next = self._calculate_days_until_next()

        return {
            "last_notification": self._last_notified,
            "next_notification": next_notification,
            "days_until_next": days_until_next,
            "notification_count": self._notification_count,
            "ha_version_at_last_notification": self._ha_version_at_last_notification,
            "current_ha_version": HA_VERSION,
            "frequency_days": frequency_days,
        }

    def _get_frequency_days(self) -> int:
        """Get the frequency in days."""
        options = self.entry.options
        frequency = options.get(CONF_FREQUENCY, DEFAULT_FREQUENCY)

        if frequency == FREQUENCY_CUSTOM or frequency == "custom":
            return options.get(CONF_CUSTOM_DAYS, DEFAULT_CUSTOM_DAYS)

        return FREQUENCY_OPTIONS.get(frequency, 30)

    def _get_notification_time(self) -> tuple[int, int]:
        """Get configured notification time (hour, minute)."""
        options = self.entry.options
        time_str = options.get(CONF_NOTIFICATION_TIME, DEFAULT_NOTIFICATION_TIME)
        try:
            if isinstance(time_str, dict):
                # TimeSelector returns dict with hours/minutes
                return time_str.get("hours", 9), time_str.get("minutes", 0)
            elif isinstance(time_str, str):
                parts = time_str.split(":")
                return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, IndexError):
            pass
        return 9, 0  # Default to 9:00

    def _calculate_next_notification(self) -> datetime | None:
        """Calculate the next notification datetime."""
        if not self._last_notified:
            # First run - schedule for configured time today or tomorrow
            now = dt_util.now()
            hour, minute = self._get_notification_time()
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time

        frequency_days = self._get_frequency_days()
        hour, minute = self._get_notification_time()
        next_date = self._last_notified + timedelta(days=frequency_days)
        return next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    def _calculate_days_until_next(self) -> int:
        """Calculate days until next notification."""
        next_notification = self._calculate_next_notification()
        if not next_notification:
            return 0

        now = dt_util.now()
        if next_notification <= now:
            return 0

        delta = next_notification - now
        return max(0, delta.days)

    def _get_language(self) -> str:
        """Get the current HA language."""
        return self.hass.config.language or "en"

    def _get_messages_for_language(self) -> dict[str, str]:
        """Get message templates for current language."""
        lang = self._get_language()
        if lang.startswith("cs"):
            return DEFAULT_MESSAGES_CS
        # Default to English for all other languages
        return DEFAULT_MESSAGES_EN

    def _get_title(self) -> str:
        """Get localized notification title."""
        lang = self._get_language()
        if lang.startswith("cs"):
            return "Připomínka šifrovacího klíče"
        return "Backup Key Reminder"

    def _get_message(self) -> str:
        """Get the notification message based on configuration and language."""
        options = self.entry.options
        message_type = options.get(CONF_MESSAGE_TYPE, DEFAULT_MESSAGE_TYPE)

        if message_type == MESSAGE_CUSTOM:
            custom_message = options.get(CONF_CUSTOM_MESSAGE, "")
            if custom_message:
                return custom_message

        # Use messages based on HA language setting
        messages = self._get_messages_for_language()
        return messages.get(message_type, messages["static"])

    def _get_version_update_message(self) -> str:
        """Get localized version update message."""
        lang = self._get_language()
        base_message = self._get_message()

        if lang.startswith("cs"):
            return (
                f"Home Assistant byl aktualizován z verze "
                f"{self._ha_version_at_last_notification} na {HA_VERSION}.\n\n"
                f"Toto je vhodný čas ověřit váš šifrovací klíč zálohy!\n\n"
                f"{base_message}"
            )
        return (
            f"Home Assistant has been updated from "
            f"{self._ha_version_at_last_notification} to {HA_VERSION}.\n\n"
            f"This is a good time to verify your backup encryption key!\n\n"
            f"{base_message}"
        )

    async def send_reminder(self, force: bool = False, is_followup: bool = False) -> None:
        """Send the reminder notification."""
        if not force and not is_followup:
            next_notification = self._calculate_next_notification()
            now = dt_util.now()
            if next_notification and next_notification > now:
                _LOGGER.debug(
                    "Skipping notification, next scheduled for %s", next_notification
                )
                return

        message = self._get_message()
        options = self.entry.options
        notification_methods = options.get(
            CONF_NOTIFICATION_METHODS, [NOTIFY_PERSISTENT]
        )

        # Add follow-up indicator to message if this is a follow-up
        if is_followup:
            lang = self._get_language()
            if lang.startswith("cs"):
                message = f"[OPAKOVANÁ PŘIPOMÍNKA]\n\n{message}"
            else:
                message = f"[FOLLOW-UP REMINDER]\n\n{message}"

        for method in notification_methods:
            await self._send_notification(method, message)

        # Only update tracking data for first notification, not follow-up
        if not is_followup:
            self._last_notified = dt_util.now()
            self._notification_count += 1
            self._ha_version_at_last_notification = HA_VERSION
            await self._async_save_data()
            await self.async_refresh()

            # Schedule follow-up if enabled
            await self._schedule_followup()

        _LOGGER.info(
            "Backup key reminder %s sent via %s",
            "(follow-up)" if is_followup else "",
            notification_methods,
        )

    async def _schedule_followup(self) -> None:
        """Schedule follow-up notification if enabled."""
        options = self.entry.options
        followup_enabled = options.get(CONF_FOLLOWUP_ENABLED, DEFAULT_FOLLOWUP_ENABLED)

        if not followup_enabled:
            return

        # Cancel any existing follow-up
        if self._unsub_followup:
            self._unsub_followup()
            self._unsub_followup = None

        followup_delay = options.get(CONF_FOLLOWUP_DELAY, DEFAULT_FOLLOWUP_DELAY)
        _LOGGER.debug("Scheduling follow-up reminder in %d minutes", followup_delay)

        @callback
        def _async_followup_callback(_now: datetime) -> None:
            """Handle follow-up notification."""
            self._unsub_followup = None
            self.hass.async_create_task(self.send_reminder(force=True, is_followup=True))

        self._unsub_followup = async_call_later(
            self.hass,
            timedelta(minutes=followup_delay),
            _async_followup_callback,
        )

    async def _send_notification(self, method: str, message: str) -> None:
        """Send notification via specified method."""
        title = self._get_title()

        if method == NOTIFY_PERSISTENT:
            async_create_notification(
                self.hass,
                message,
                title=title,
                notification_id=f"{DOMAIN}_reminder",
            )
        elif method.startswith("notify."):
            # Use notify service
            service_data = {
                "message": message,
                "title": title,
            }
            try:
                await self.hass.services.async_call(
                    "notify",
                    method.replace("notify.", ""),
                    service_data,
                    blocking=True,
                )
            except Exception as err:
                _LOGGER.error("Failed to send notification via %s: %s", method, err)

    async def check_and_send_reminder(self) -> None:
        """Check if reminder should be sent and send it."""
        await self.send_reminder(force=False)

    async def _check_and_send_if_time(self) -> None:
        """Check if it's time to send reminder based on configured time."""
        next_notification = self._calculate_next_notification()
        if not next_notification:
            return

        now = dt_util.now()
        # Check if we're within 15 minutes of the scheduled time
        time_diff = (now - next_notification).total_seconds()
        if 0 <= time_diff <= 900:  # Within 15 minutes after scheduled time
            await self.send_reminder(force=False)

    async def check_ha_version_change(self) -> None:
        """Check if HA version has changed and send notification."""
        options = self.entry.options
        if not options.get(CONF_NOTIFY_ON_UPDATE, True):
            return

        if (
            self._ha_version_at_last_notification
            and self._ha_version_at_last_notification != HA_VERSION
        ):
            _LOGGER.info(
                "HA version changed from %s to %s, sending reminder",
                self._ha_version_at_last_notification,
                HA_VERSION,
            )
            version_message = self._get_version_update_message()
            notification_methods = options.get(
                CONF_NOTIFICATION_METHODS, [NOTIFY_PERSISTENT]
            )
            for method in notification_methods:
                await self._send_notification(method, version_message)

            self._ha_version_at_last_notification = HA_VERSION
            await self._async_save_data()

    async def reset_timer(self) -> None:
        """Reset the notification timer."""
        self._last_notified = dt_util.now()
        await self._async_save_data()
        await self.async_refresh()
        _LOGGER.info("Backup key reminder timer reset")

    async def mark_key_verified(self) -> None:
        """Mark the key as verified (resets timer and dismisses notification)."""
        self._last_notified = dt_util.now()
        await self._async_save_data()
        await self.async_refresh()

        # Dismiss persistent notification
        from homeassistant.components.persistent_notification import (
            async_dismiss as async_dismiss_notification,
        )

        async_dismiss_notification(self.hass, f"{DOMAIN}_reminder")
        _LOGGER.info("Backup key marked as verified, timer reset")

    async def schedule_reminder_check(self) -> None:
        """Schedule periodic reminder checks."""
        # Cancel any existing timer
        if self._unsub_timer:
            self._unsub_timer()

        # Check every 15 minutes for more accurate time-based notifications
        self._unsub_timer = async_track_time_interval(
            self.hass,
            self._async_scheduled_check,
            timedelta(minutes=15),
        )

    @callback
    def _async_scheduled_check(self, now: datetime) -> None:
        """Handle scheduled check."""
        self.hass.async_create_task(self._check_and_send_if_time())

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
        if self._unsub_followup:
            self._unsub_followup()
            self._unsub_followup = None

    @property
    def last_notified(self) -> datetime | None:
        """Return the last notification datetime."""
        return self._last_notified

    @property
    def notification_count(self) -> int:
        """Return the notification count."""
        return self._notification_count

    @property
    def ha_version_at_last_notification(self) -> str | None:
        """Return the HA version at last notification."""
        return self._ha_version_at_last_notification
