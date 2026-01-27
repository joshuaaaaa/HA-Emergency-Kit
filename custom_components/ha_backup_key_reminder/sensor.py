"""Sensor platform for HA Backup Key Reminder."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    SENSOR_LAST_NOTIFICATION,
    SENSOR_NEXT_NOTIFICATION,
    SENSOR_DAYS_UNTIL_NEXT,
    SENSOR_NOTIFICATION_COUNT,
    SENSOR_HA_VERSION,
    ATTR_FREQUENCY_DAYS,
)
from .coordinator import BackupKeyReminderCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        LastNotificationSensor(coordinator, entry),
        NextNotificationSensor(coordinator, entry),
        DaysUntilNextSensor(coordinator, entry),
        NotificationCountSensor(coordinator, entry),
        HAVersionSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class BackupKeyReminderSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Backup Key Reminder sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BackupKeyReminderCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Backup Key Reminder",
            "manufacturer": "Community",
            "model": "Backup Key Reminder",
            "sw_version": "1.0.0",
        }


class LastNotificationSensor(BackupKeyReminderSensorBase):
    """Sensor showing when the last notification was sent."""

    _attr_name = "Last Notification"
    _attr_icon = "mdi:clock-check-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: BackupKeyReminderCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, SENSOR_LAST_NOTIFICATION)

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("last_notification")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs[ATTR_FREQUENCY_DAYS] = self.coordinator.data.get("frequency_days")
        return attrs


class NextNotificationSensor(BackupKeyReminderSensorBase):
    """Sensor showing when the next notification will be sent."""

    _attr_name = "Next Notification"
    _attr_icon = "mdi:clock-alert-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: BackupKeyReminderCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, SENSOR_NEXT_NOTIFICATION)

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("next_notification")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs[ATTR_FREQUENCY_DAYS] = self.coordinator.data.get("frequency_days")
        return attrs


class DaysUntilNextSensor(BackupKeyReminderSensorBase):
    """Sensor showing days until the next notification."""

    _attr_name = "Days Until Next Reminder"
    _attr_icon = "mdi:calendar-clock"
    _attr_native_unit_of_measurement = "days"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: BackupKeyReminderCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, SENSOR_DAYS_UNTIL_NEXT)

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("days_until_next", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            next_notification = self.coordinator.data.get("next_notification")
            if next_notification:
                attrs["next_notification"] = next_notification.isoformat()
            attrs[ATTR_FREQUENCY_DAYS] = self.coordinator.data.get("frequency_days")
        return attrs


class NotificationCountSensor(BackupKeyReminderSensorBase):
    """Sensor showing total notification count."""

    _attr_name = "Notification Count"
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "notifications"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: BackupKeyReminderCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, SENSOR_NOTIFICATION_COUNT)

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("notification_count", 0)
        return 0


class HAVersionSensor(BackupKeyReminderSensorBase):
    """Sensor showing HA version at last notification."""

    _attr_name = "HA Version at Last Notification"
    _attr_icon = "mdi:home-assistant"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: BackupKeyReminderCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, SENSOR_HA_VERSION)

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("ha_version_at_last_notification")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs["current_ha_version"] = self.coordinator.data.get(
                "current_ha_version"
            )
            ha_version_last = self.coordinator.data.get(
                "ha_version_at_last_notification"
            )
            current = self.coordinator.data.get("current_ha_version")
            if ha_version_last and current:
                attrs["version_changed"] = ha_version_last != current
        return attrs
