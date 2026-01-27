# HA Backup Key Reminder

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/joshuaaaaa/HA-Emergency-Kit.svg)](https://github.com/joshuaaaaa/HA-Emergency-Kit/releases)
[![License](https://img.shields.io/github/license/joshuaaaaa/HA-Emergency-Kit.svg)](LICENSE)

**[Česká verze / Czech version](README_CS.md)**

A Home Assistant custom integration that reminds you to verify and safely store your backup encryption key. Never lose access to your backups again!

<img width="453" height="345" alt="Notification Example" src="https://github.com/user-attachments/assets/28fbe67f-dd3b-4769-8ac3-d940d6c65a59" />

## Why This Integration?

When you enable encrypted backups in Home Assistant, an encryption key is generated. **Without this key, your backups are completely useless** - you cannot restore them. Many users have learned this the hard way when they needed to restore their system but couldn't find their encryption key.

This integration solves that problem by:
- Sending periodic reminders to verify your backup key
- Notifying you when Home Assistant is updated (a good time to check your backup!)
- Supporting multiple notification methods
- Providing sensors to track when the last/next reminder was/will be sent

## Features

- **Multiple notification methods:**
  - Persistent notifications (built-in)
  - Mobile app notifications
  - Email
  - Telegram
  - Slack
  - Discord
  - Pushover
  - HTML5
  - Any custom notify service

- **Flexible reminder frequency:**
  - Weekly (7 days)
  - Monthly (30 days)
  - Half-yearly (182 days)
  - Custom interval (1-365 days)

- **Message templates:**
  - Static (default message)
  - Simple reminder
  - Detailed with step-by-step instructions
  - Urgent/critical reminder
  - Custom message

- **Smart notifications:**
  - Automatic reminder when Home Assistant is updated
  - Multiple notification methods can be selected simultaneously

- **Sensors:**
  - Last notification timestamp
  - Next notification timestamp
  - Days until next reminder
  - Total notification count
  - HA version at last notification

- **Buttons:**
  - Send reminder now
  - Mark key as verified

- **Services:**
  - `ha_backup_key_reminder.send_reminder` - Manually send a reminder
  - `ha_backup_key_reminder.reset_timer` - Reset the timer without sending notification
  - `ha_backup_key_reminder.mark_key_verified` - Mark key as verified and dismiss notifications

## Message Templates

### Static (Default)
> Reminder: Please verify you have your Home Assistant backup encryption key safely stored. Without this key, you cannot restore your backups!

### Simple
> Backup Key Reminder: Have you checked your HA encryption key recently? Make sure it's safely stored!

### Detailed with Instructions
> **Home Assistant Backup Key Reminder**
>
> This is a friendly reminder to verify your backup encryption key.
>
> **Why is this important?**
> - Without the encryption key, your backups are useless
> - The key is generated when you enable encrypted backups
> - It cannot be recovered if lost
>
> **Action required:**
> 1. Go to Settings > System > Backups
> 2. Download your encryption key
> 3. Store it in a safe location (password manager, secure drive)
>
> Don't wait until you need to restore!

### Urgent
> **URGENT: Backup Key Verification Required!**
>
> Your Home Assistant backup encryption key needs immediate attention.
> Without this key, ALL your encrypted backups are IRRECOVERABLE.
>
> Please verify NOW that you have your key safely stored!

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/joshuaaaaa/HA-Emergency-Kit`
6. Select category: "Integration"
7. Click "Add"
8. Search for "HA Backup Key Reminder"
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/joshuaaaaa/HA-Emergency-Kit/releases)
2. Extract the `custom_components/ha_backup_key_reminder` folder to your `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "HA Backup Key Reminder"
4. Follow the configuration wizard:

### Step 1: Frequency Settings
- **Reminder frequency**: How often to send reminders
- **Custom interval**: Number of days (if "Custom" is selected)
- **Notify on HA update**: Send reminder when Home Assistant version changes

### Step 2: Notification Methods
Select one or more notification methods from the available options.

### Step 3: Message Configuration
- Choose a predefined template or create your own custom message

## Sensors

The integration creates the following sensors:

| Sensor | Description |
|--------|-------------|
| `sensor.backup_key_reminder_last_notification` | Timestamp of the last sent notification |
| `sensor.backup_key_reminder_next_notification` | Timestamp of the next scheduled notification |
| `sensor.backup_key_reminder_days_until_next_reminder` | Days remaining until the next reminder |
| `sensor.backup_key_reminder_notification_count` | Total number of notifications sent |
| `sensor.backup_key_reminder_ha_version_at_last_notification` | HA version when last notification was sent |

## Buttons

| Button | Description |
|--------|-------------|
| `button.backup_key_reminder_send_reminder_now` | Immediately sends a reminder notification |
| `button.backup_key_reminder_mark_key_verified` | Marks key as verified and resets timer |

## Services

### Send Reminder
```yaml
service: ha_backup_key_reminder.send_reminder
```
Manually sends a backup key reminder notification.

### Reset Timer
```yaml
service: ha_backup_key_reminder.reset_timer
```
Resets the reminder timer without sending a notification.

### Mark Key Verified
```yaml
service: ha_backup_key_reminder.mark_key_verified
```
Marks the encryption key as verified, resets the timer, and dismisses any active persistent notifications.

## Automation Examples

### Send reminder via multiple services
```yaml
automation:
  - alias: "Backup Key Reminder - Additional Notifications"
    trigger:
      - platform: state
        entity_id: sensor.backup_key_reminder_days_until_next_reminder
        to: "0"
    action:
      - service: notify.my_phone
        data:
          title: "Backup Key Reminder"
          message: "Please verify your Home Assistant backup encryption key!"
```

### Dismiss reminder when acknowledged
```yaml
automation:
  - alias: "Acknowledge Backup Key Reminder"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "BACKUP_KEY_VERIFIED"
    action:
      - service: ha_backup_key_reminder.mark_key_verified
```

## Where to Find Your Backup Encryption Key

1. Go to **Settings** → **System** → **Backups**
2. Click on the three dots menu
3. Select **Download encryption key**
4. Store this key in a safe location:
   - Password manager
   - Secure cloud storage
   - Physical backup (printed and stored safely)

## FAQ

**Q: What happens if I lose my encryption key?**
A: Unfortunately, without the encryption key, your encrypted backups cannot be restored. This is why this integration exists - to prevent this situation!

**Q: Can I use multiple notification methods?**
A: Yes! You can select multiple notification methods and receive reminders through all of them.

**Q: Does this integration access my backup key?**
A: No. This integration only sends reminders. It does not access, store, or transmit your backup encryption key.

**Q: How can I send a reminder immediately?**
A: Use the "Send Reminder Now" button in the integration device or call the `ha_backup_key_reminder.send_reminder` service.

## Support

If you encounter any issues or have suggestions, please [open an issue](https://github.com/joshuaaaaa/HA-Emergency-Kit/issues) on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
