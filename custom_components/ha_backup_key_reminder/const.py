"""Constants for the HA Backup Key Reminder integration."""
from typing import Final

DOMAIN: Final = "ha_backup_key_reminder"

# Configuration keys
CONF_NOTIFICATION_METHODS: Final = "notification_methods"
CONF_FREQUENCY: Final = "frequency"
CONF_CUSTOM_DAYS: Final = "custom_days"
CONF_MESSAGE_TYPE: Final = "message_type"
CONF_CUSTOM_MESSAGE: Final = "custom_message"
CONF_NOTIFY_ON_UPDATE: Final = "notify_on_update"
CONF_NOTIFY_SERVICES: Final = "notify_services"
CONF_NOTIFICATION_TIME: Final = "notification_time"
CONF_FOLLOWUP_ENABLED: Final = "followup_enabled"
CONF_FOLLOWUP_DELAY: Final = "followup_delay"

# Frequency options (in days)
FREQUENCY_WEEK: Final = 7
FREQUENCY_MONTH: Final = 30
FREQUENCY_HALF_YEAR: Final = 182
FREQUENCY_CUSTOM: Final = "custom"

FREQUENCY_OPTIONS: Final = {
    "week": FREQUENCY_WEEK,
    "month": FREQUENCY_MONTH,
    "half_year": FREQUENCY_HALF_YEAR,
    "custom": FREQUENCY_CUSTOM,
}

# Notification methods
NOTIFY_PERSISTENT: Final = "persistent_notification"
NOTIFY_MOBILE: Final = "mobile_app"
NOTIFY_EMAIL: Final = "email"
NOTIFY_TELEGRAM: Final = "telegram"
NOTIFY_SLACK: Final = "slack"
NOTIFY_DISCORD: Final = "discord"
NOTIFY_PUSHOVER: Final = "pushover"
NOTIFY_HTML5: Final = "html5"
NOTIFY_CUSTOM: Final = "custom_notify"

NOTIFICATION_METHODS: Final = [
    NOTIFY_PERSISTENT,
    NOTIFY_MOBILE,
    NOTIFY_EMAIL,
    NOTIFY_TELEGRAM,
    NOTIFY_SLACK,
    NOTIFY_DISCORD,
    NOTIFY_PUSHOVER,
    NOTIFY_HTML5,
    NOTIFY_CUSTOM,
]

# Message types
MESSAGE_STATIC: Final = "static"
MESSAGE_TEMPLATE_SIMPLE: Final = "template_simple"
MESSAGE_TEMPLATE_DETAILED: Final = "template_detailed"
MESSAGE_TEMPLATE_URGENT: Final = "template_urgent"
MESSAGE_CUSTOM: Final = "custom"

MESSAGE_TYPES: Final = [
    MESSAGE_STATIC,
    MESSAGE_TEMPLATE_SIMPLE,
    MESSAGE_TEMPLATE_DETAILED,
    MESSAGE_TEMPLATE_URGENT,
    MESSAGE_CUSTOM,
]

# Default messages (English)
DEFAULT_MESSAGES_EN: Final = {
    MESSAGE_STATIC: (
        "Reminder: Please verify you have your Home Assistant backup encryption key safely stored. "
        "Without this key, you cannot restore your backups!"
    ),
    MESSAGE_TEMPLATE_SIMPLE: (
        "Backup Key Reminder: Have you checked your HA encryption key recently? "
        "Make sure it's safely stored!"
    ),
    MESSAGE_TEMPLATE_DETAILED: (
        "Home Assistant Backup Key Reminder\n\n"
        "This is a friendly reminder to verify your backup encryption key.\n\n"
        "Why is this important?\n"
        "- Without the encryption key, your backups are useless\n"
        "- The key is generated when you enable encrypted backups\n"
        "- It cannot be recovered if lost\n\n"
        "Action required:\n"
        "1. Go to Settings > System > Backups\n"
        "2. Download your encryption key\n"
        "3. Store it in a safe location (password manager, secure drive)\n\n"
        "Don't wait until you need to restore!"
    ),
    MESSAGE_TEMPLATE_URGENT: (
        "URGENT: Backup Key Verification Required!\n\n"
        "Your Home Assistant backup encryption key needs immediate attention.\n"
        "Without this key, ALL your encrypted backups are IRRECOVERABLE.\n\n"
        "Please verify NOW that you have your key safely stored!"
    ),
}

# Default messages (Czech)
DEFAULT_MESSAGES_CS: Final = {
    MESSAGE_STATIC: (
        "Připomínka: Zkontrolujte prosím, zda máte bezpečně uložený šifrovací klíč zálohy "
        "Home Assistant. Bez tohoto klíče nemůžete obnovit své zálohy!"
    ),
    MESSAGE_TEMPLATE_SIMPLE: (
        "Připomínka šifrovacího klíče: Zkontrolovali jste nedávno svůj HA šifrovací klíč? "
        "Ujistěte se, že je bezpečně uložen!"
    ),
    MESSAGE_TEMPLATE_DETAILED: (
        "Připomínka šifrovacího klíče Home Assistant\n\n"
        "Toto je přátelská připomínka k ověření vašeho šifrovacího klíče zálohy.\n\n"
        "Proč je to důležité?\n"
        "- Bez šifrovacího klíče jsou vaše zálohy nepoužitelné\n"
        "- Klíč je vygenerován při zapnutí šifrovaných záloh\n"
        "- V případě ztráty jej nelze obnovit\n\n"
        "Požadovaná akce:\n"
        "1. Přejděte do Nastavení > Systém > Zálohy\n"
        "2. Stáhněte si šifrovací klíč\n"
        "3. Uložte jej na bezpečné místo (správce hesel, zabezpečený disk)\n\n"
        "Nečekejte, až budete potřebovat obnovit zálohu!"
    ),
    MESSAGE_TEMPLATE_URGENT: (
        "NALÉHAVÉ: Vyžadováno ověření šifrovacího klíče!\n\n"
        "Váš šifrovací klíč zálohy Home Assistant vyžaduje okamžitou pozornost.\n"
        "Bez tohoto klíče jsou VŠECHNY vaše šifrované zálohy NEOBNOVITELNÉ.\n\n"
        "Prosím ověřte NYNÍ, že máte klíč bezpečně uložen!"
    ),
}

# Sensor types
SENSOR_LAST_NOTIFICATION: Final = "last_notification"
SENSOR_NEXT_NOTIFICATION: Final = "next_notification"
SENSOR_DAYS_UNTIL_NEXT: Final = "days_until_next"
SENSOR_NOTIFICATION_COUNT: Final = "notification_count"
SENSOR_HA_VERSION: Final = "ha_version_at_last_notification"

# Attributes
ATTR_LAST_NOTIFIED: Final = "last_notified"
ATTR_NEXT_NOTIFICATION: Final = "next_notification"
ATTR_NOTIFICATION_COUNT: Final = "notification_count"
ATTR_HA_VERSION: Final = "ha_version"
ATTR_FREQUENCY_DAYS: Final = "frequency_days"

# Services
SERVICE_SEND_REMINDER: Final = "send_reminder"
SERVICE_RESET_TIMER: Final = "reset_timer"
SERVICE_MARK_KEY_VERIFIED: Final = "mark_key_verified"

# Storage
STORAGE_KEY: Final = f"{DOMAIN}.storage"
STORAGE_VERSION: Final = 1

# Default values
DEFAULT_FREQUENCY: Final = "month"
DEFAULT_CUSTOM_DAYS: Final = 30
DEFAULT_MESSAGE_TYPE: Final = MESSAGE_TEMPLATE_SIMPLE
DEFAULT_NOTIFY_ON_UPDATE: Final = True
DEFAULT_NOTIFICATION_TIME: Final = "09:00"
DEFAULT_FOLLOWUP_ENABLED: Final = False
DEFAULT_FOLLOWUP_DELAY: Final = 30  # minutes
