"""Config flow for HA Backup Key Reminder integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    BooleanSelector,
    TimeSelector,
    TimeSelectorConfig,
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
    CONF_NOTIFICATION_TIME,
    CONF_FOLLOWUP_ENABLED,
    CONF_FOLLOWUP_DELAY,
    FREQUENCY_OPTIONS,
    FREQUENCY_CUSTOM,
    NOTIFICATION_METHODS,
    MESSAGE_TYPES,
    MESSAGE_CUSTOM,
    DEFAULT_FREQUENCY,
    DEFAULT_CUSTOM_DAYS,
    DEFAULT_MESSAGE_TYPE,
    DEFAULT_NOTIFY_ON_UPDATE,
    DEFAULT_NOTIFICATION_TIME,
    DEFAULT_FOLLOWUP_ENABLED,
    DEFAULT_FOLLOWUP_DELAY,
    NOTIFY_PERSISTENT,
)

_LOGGER = logging.getLogger(__name__)


def get_notify_services(hass: HomeAssistant) -> list[str]:
    """Get list of available notify services."""
    services = []
    for service in hass.services.async_services().get("notify", {}):
        services.append(f"notify.{service}")
    return services


class BackupKeyReminderConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Backup Key Reminder."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        # Check if already configured
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_notifications()

        # Get available notify services
        notify_services = get_notify_services(self.hass)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_FREQUENCY, default=DEFAULT_FREQUENCY
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": "week", "label": "Weekly (7 days)"},
                            {"value": "month", "label": "Monthly (30 days)"},
                            {"value": "half_year", "label": "Half-yearly (182 days)"},
                            {"value": "custom", "label": "Custom"},
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="frequency",
                    )
                ),
                vol.Optional(
                    CONF_CUSTOM_DAYS, default=DEFAULT_CUSTOM_DAYS
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=365,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_NOTIFICATION_TIME, default=DEFAULT_NOTIFICATION_TIME
                ): TimeSelector(TimeSelectorConfig()),
                vol.Required(
                    CONF_NOTIFY_ON_UPDATE, default=DEFAULT_NOTIFY_ON_UPDATE
                ): BooleanSelector(),
                vol.Required(
                    CONF_FOLLOWUP_ENABLED, default=DEFAULT_FOLLOWUP_ENABLED
                ): BooleanSelector(),
                vol.Optional(
                    CONF_FOLLOWUP_DELAY, default=DEFAULT_FOLLOWUP_DELAY
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=5,
                        max=120,
                        step=5,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"name": "HA Backup Key Reminder"},
        )

    async def async_step_notifications(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle notification settings step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_message()

        # Get available notify services
        notify_services = get_notify_services(self.hass)

        notification_options = [
            {"value": "persistent_notification", "label": "Persistent Notification"},
        ]

        # Add available notify services
        for service in notify_services:
            service_name = service.replace("notify.", "").replace("_", " ").title()
            notification_options.append({"value": service, "label": service_name})

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_NOTIFICATION_METHODS,
                    default=["persistent_notification"],
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=notification_options,
                        mode=SelectSelectorMode.DROPDOWN,
                        multiple=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="notifications",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_message(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle message configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title="Backup Key Reminder",
                data={},
                options=self._data,
            )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_MESSAGE_TYPE, default=DEFAULT_MESSAGE_TYPE
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": "static", "label": "Static (Default message)"},
                            {"value": "template_simple", "label": "Template: Simple"},
                            {
                                "value": "template_detailed",
                                "label": "Template: Detailed with instructions",
                            },
                            {"value": "template_urgent", "label": "Template: Urgent"},
                            {"value": "custom", "label": "Custom message"},
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="message_type",
                    )
                ),
                vol.Optional(CONF_CUSTOM_MESSAGE, default=""): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT,
                        multiline=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="message",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return BackupKeyReminderOptionsFlow(config_entry)


class BackupKeyReminderOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for HA Backup Key Reminder."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._data: dict[str, Any] = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_notifications()

        current_frequency = self._data.get(CONF_FREQUENCY, DEFAULT_FREQUENCY)
        current_custom_days = self._data.get(CONF_CUSTOM_DAYS, DEFAULT_CUSTOM_DAYS)
        current_notification_time = self._data.get(
            CONF_NOTIFICATION_TIME, DEFAULT_NOTIFICATION_TIME
        )
        current_notify_on_update = self._data.get(
            CONF_NOTIFY_ON_UPDATE, DEFAULT_NOTIFY_ON_UPDATE
        )
        current_followup_enabled = self._data.get(
            CONF_FOLLOWUP_ENABLED, DEFAULT_FOLLOWUP_ENABLED
        )
        current_followup_delay = self._data.get(
            CONF_FOLLOWUP_DELAY, DEFAULT_FOLLOWUP_DELAY
        )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_FREQUENCY, default=current_frequency): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": "week", "label": "Weekly (7 days)"},
                            {"value": "month", "label": "Monthly (30 days)"},
                            {"value": "half_year", "label": "Half-yearly (182 days)"},
                            {"value": "custom", "label": "Custom"},
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="frequency",
                    )
                ),
                vol.Optional(
                    CONF_CUSTOM_DAYS, default=current_custom_days
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=365,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_NOTIFICATION_TIME, default=current_notification_time
                ): TimeSelector(TimeSelectorConfig()),
                vol.Required(
                    CONF_NOTIFY_ON_UPDATE, default=current_notify_on_update
                ): BooleanSelector(),
                vol.Required(
                    CONF_FOLLOWUP_ENABLED, default=current_followup_enabled
                ): BooleanSelector(),
                vol.Optional(
                    CONF_FOLLOWUP_DELAY, default=current_followup_delay
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=5,
                        max=120,
                        step=5,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_notifications(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle notification settings step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_message()

        # Get available notify services
        notify_services = get_notify_services(self.hass)

        notification_options = [
            {"value": "persistent_notification", "label": "Persistent Notification"},
        ]

        for service in notify_services:
            service_name = service.replace("notify.", "").replace("_", " ").title()
            notification_options.append({"value": service, "label": service_name})

        current_methods = self._data.get(
            CONF_NOTIFICATION_METHODS, ["persistent_notification"]
        )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_NOTIFICATION_METHODS,
                    default=current_methods,
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=notification_options,
                        mode=SelectSelectorMode.DROPDOWN,
                        multiple=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="notifications",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_message(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle message configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)

        current_message_type = self._data.get(CONF_MESSAGE_TYPE, DEFAULT_MESSAGE_TYPE)
        current_custom_message = self._data.get(CONF_CUSTOM_MESSAGE, "")

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_MESSAGE_TYPE, default=current_message_type
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": "static", "label": "Static (Default message)"},
                            {"value": "template_simple", "label": "Template: Simple"},
                            {
                                "value": "template_detailed",
                                "label": "Template: Detailed with instructions",
                            },
                            {"value": "template_urgent", "label": "Template: Urgent"},
                            {"value": "custom", "label": "Custom message"},
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="message_type",
                    )
                ),
                vol.Optional(
                    CONF_CUSTOM_MESSAGE, default=current_custom_message
                ): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT,
                        multiline=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="message",
            data_schema=data_schema,
            errors=errors,
        )
