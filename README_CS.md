# HA Backup Key Reminder - Připomínka šifrovacího klíče

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/joshuaaaaa/HA-Emergency-Kit.svg)](https://github.com/joshuaaaaa/HA-Emergency-Kit/releases)
[![License](https://img.shields.io/github/license/joshuaaaaa/HA-Emergency-Kit.svg)](LICENSE)

**[English version / Anglická verze](README.md)**

Vlastní integrace pro Home Assistant, která vám připomíná ověření a bezpečné uložení šifrovacího klíče zálohy. Už nikdy nepřijdete o přístup ke svým zálohám!

## Proč tato integrace?

Když povolíte šifrované zálohy v Home Assistant, vygeneruje se šifrovací klíč. **Bez tohoto klíče jsou vaše zálohy naprosto nepoužitelné** - nemůžete je obnovit. Mnoho uživatelů se o tom přesvědčilo na vlastní kůži, když potřebovali obnovit svůj systém, ale nemohli najít šifrovací klíč.

Tato integrace řeší tento problém tím, že:
- Posílá pravidelné připomínky k ověření vašeho šifrovacího klíče
- Upozorní vás při aktualizaci Home Assistant (skvělý čas zkontrolovat zálohu!)
- Podporuje více způsobů oznámení
- Poskytuje senzory pro sledování, kdy byla/bude odeslána poslední/příští připomínka

## Funkce

- **Více způsobů oznámení:**
  - Trvalá oznámení (vestavěná)
  - Oznámení mobilní aplikace
  - E-mail
  - Telegram
  - Slack
  - Discord
  - Pushover
  - HTML5
  - Jakákoli vlastní notify služba

- **Flexibilní frekvence připomínek:**
  - Týdně (7 dní)
  - Měsíčně (30 dní)
  - Půlročně (182 dní)
  - Vlastní interval (1-365 dní)

- **Šablony zpráv:**
  - Statická (výchozí zpráva)
  - Jednoduchá připomínka
  - Podrobná s instrukcemi krok za krokem
  - Naléhavá/kritická připomínka
  - Vlastní zpráva

- **Chytrá oznámení:**
  - Automatická připomínka při aktualizaci Home Assistant
  - Lze vybrat více způsobů oznámení současně

- **Senzory:**
  - Časové razítko posledního oznámení
  - Časové razítko příštího oznámení
  - Dní do další připomínky
  - Celkový počet oznámení
  - Verze HA při posledním oznámení

- **Služby:**
  - `ha_backup_key_reminder.send_reminder` - Ručně odeslat připomínku
  - `ha_backup_key_reminder.reset_timer` - Resetovat časovač bez odeslání oznámení
  - `ha_backup_key_reminder.mark_key_verified` - Označit klíč jako ověřený a zrušit oznámení

## Instalace

### HACS (Doporučeno)

1. Otevřete HACS ve vašem Home Assistant
2. Klikněte na "Integrace"
3. Klikněte na tři tečky v pravém horním rohu
4. Vyberte "Vlastní repozitáře"
5. Přidejte URL tohoto repozitáře: `https://github.com/joshuaaaaa/HA-Emergency-Kit`
6. Vyberte kategorii: "Integrace"
7. Klikněte "Přidat"
8. Vyhledejte "HA Backup Key Reminder"
9. Klikněte "Stáhnout"
10. Restartujte Home Assistant

### Ruční instalace

1. Stáhněte nejnovější verzi ze [stránky vydání](https://github.com/joshuaaaaa/HA-Emergency-Kit/releases)
2. Rozbalte složku `custom_components/ha_backup_key_reminder` do vašeho `config/custom_components/` adresáře
3. Restartujte Home Assistant

## Konfigurace

1. Přejděte do **Nastavení** → **Zařízení a služby**
2. Klikněte na **+ Přidat integraci**
3. Vyhledejte "HA Backup Key Reminder"
4. Postupujte podle průvodce konfigurací:

### Krok 1: Nastavení frekvence
- **Frekvence připomínky**: Jak často posílat připomínky
- **Vlastní interval**: Počet dní (pokud je vybráno "Vlastní")
- **Upozornit při aktualizaci HA**: Odeslat připomínku při změně verze Home Assistant

### Krok 2: Způsoby oznámení
Vyberte jeden nebo více způsobů oznámení z dostupných možností.

### Krok 3: Konfigurace zprávy
- Vyberte předdefinovanou šablonu nebo vytvořte vlastní zprávu

## Senzory

Integrace vytváří následující senzory:

| Senzor | Popis |
|--------|-------|
| `sensor.backup_key_reminder_last_notification` | Časové razítko posledního odeslaného oznámení |
| `sensor.backup_key_reminder_next_notification` | Časové razítko příštího plánovaného oznámení |
| `sensor.backup_key_reminder_days_until_next_reminder` | Zbývající dny do další připomínky |
| `sensor.backup_key_reminder_notification_count` | Celkový počet odeslaných oznámení |
| `sensor.backup_key_reminder_ha_version_at_last_notification` | Verze HA při odeslání posledního oznámení |

## Služby

### Odeslat připomínku
```yaml
service: ha_backup_key_reminder.send_reminder
```
Ručně odešle připomínku šifrovacího klíče zálohy.

### Resetovat časovač
```yaml
service: ha_backup_key_reminder.reset_timer
```
Resetuje časovač připomínky bez odeslání oznámení.

### Označit klíč jako ověřený
```yaml
service: ha_backup_key_reminder.mark_key_verified
```
Označí šifrovací klíč jako ověřený, resetuje časovač a zruší aktivní trvalá oznámení.

## Příklady automatizací

### Odeslat připomínku přes více služeb
```yaml
automation:
  - alias: "Připomínka šifrovacího klíče - Další oznámení"
    trigger:
      - platform: state
        entity_id: sensor.backup_key_reminder_days_until_next_reminder
        to: "0"
    action:
      - service: notify.muj_telefon
        data:
          title: "Připomínka šifrovacího klíče"
          message: "Prosím ověřte váš šifrovací klíč zálohy Home Assistant!"
```

### Zrušit připomínku po potvrzení
```yaml
automation:
  - alias: "Potvrdit připomínku šifrovacího klíče"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "BACKUP_KEY_VERIFIED"
    action:
      - service: ha_backup_key_reminder.mark_key_verified
```

## Kde najít šifrovací klíč zálohy

1. Přejděte do **Nastavení** → **Systém** → **Zálohy**
2. Klikněte na menu se třemi tečkami
3. Vyberte **Stáhnout šifrovací klíč**
4. Uložte tento klíč na bezpečné místo:
   - Správce hesel
   - Zabezpečené cloudové úložiště
   - Fyzická záloha (vytištěná a bezpečně uložená)

## Často kladené otázky

**Otázka: Co se stane, když ztratím šifrovací klíč?**
Odpověď: Bohužel bez šifrovacího klíče nelze šifrované zálohy obnovit. Proto tato integrace existuje - aby této situaci předešla!

**Otázka: Mohu použít více způsobů oznámení?**
Odpověď: Ano! Můžete vybrat více způsobů oznámení a přijímat připomínky přes všechny z nich.

**Otázka: Přistupuje tato integrace k mému šifrovacímu klíči?**
Odpověď: Ne. Tato integrace pouze posílá připomínky. Nepřistupuje, neukládá ani nepřenáší váš šifrovací klíč zálohy.

## Podpora

Pokud narazíte na problémy nebo máte návrhy, prosím [otevřete issue](https://github.com/joshuaaaaa/HA-Emergency-Kit/issues) na GitHubu.

## Licence

Tento projekt je licencován pod MIT licencí - viz soubor [LICENSE](LICENSE) pro detaily.

## Přispívání

Příspěvky jsou vítány! Neváhejte odeslat Pull Request.
