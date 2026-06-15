# Navimow weather-aware cutting height

A small Home Assistant setup that adjusts a Segway Navimow's cutting height to the
weather, so you keep the lawn low without scalping it during hot, dry spells. It
raises the height when a heatwave is forecast and steps it back down to your
target once the weather is kind again, respecting the one-third mowing rule.

It is **decision-only**. The current Navimow integration does not expose cutting
height, so Home Assistant works out the right height and sends you a notification;
you set it in the Navimow app and tap a button to confirm. Nothing is sent to the
mower automatically. If a way to set Navimow height from HA appears, this would
drop the manual step.

> This is shared as a reference for how I did it, not a turnkey add-on. There is
> no live mower or account attached. You wire it into your own Home Assistant and
> change the entity names to match your setup.

## How it works

- You set a **target** height (your normal cut) and a **protective** height
  (raised, for heat). The system tracks the **current** height itself, since it
  cannot read it from the mower.
- Each day it reads your weather entity's daily forecast. A day counts as
  heat-stress if it is hot and dry (defaults: max temp at or above 26 C, and
  under 1 mm rain), within a forecast window (default 5 days).
- If heat stress is coming, it recommends jumping to the protective height
  (raising never stresses grass, so it is instant).
- When the week is calm, it steps the height **down** by the one-third rule
  (never removing more than a third of the blade at once), one step at a time,
  waiting a settle period between steps so the mower actually reaches the new
  height across the whole lawn before the next step.
- All thresholds are Home Assistant helpers you can tune in the UI.

The decision logic lives in one place as a Python function
(`reference/decision.py`), and the deployed Home Assistant version is a Jinja
macro (`custom_templates/navimow.jinja`) that mirrors it. A parity test renders
the deployed macro through HA's `/api/template` and checks it matches the Python
oracle, so the two cannot drift.

## Layout

- `reference/decision.py` - the decision logic in Python (the test oracle).
- `custom_templates/navimow.jinja` - the same logic as a Jinja macro (deployed).
- `packages/navimow_cut_height.yaml` - helpers, the sensor, automations, and the
  notification + confirm flow. Change `weather.home` and the notify service to
  your own.
- `dashboards/` - a card and a small dashboard with the recommendation and the
  Mark applied / Snooze buttons.
- `tests/` - unit tests for the logic, and a live parity test.
- `scripts/` - SSH/API helper and a deploy script (set `HA_IP`, `HA_KEY`,
  `HA_TOKEN`).

## Setup

1. Edit `packages/navimow_cut_height.yaml`: set your daily-forecast weather
   entity (replace `weather.home`) and your notify service.
2. Copy `custom_templates/navimow.jinja` to `/config/custom_templates/`,
   `packages/navimow_cut_height.yaml` to `/config/packages/`, and
   `dashboards/navimow_dashboard.yaml` to `/config/`.
3. Enable packages and register the dashboard in `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   lovelace:
     mode: storage
     dashboards:
       navimow-cut-height:
         mode: yaml
         title: Navimow
         icon: mdi:robot-mower
         show_in_sidebar: true
         filename: navimow_dashboard.yaml
   ```
4. Restart Home Assistant, then set the helper values (see
   `packages/navimow_initial_values.md`).

`scripts/deploy.sh` automates steps 2-4 if you have the Terminal & SSH add-on.

## Confirming a change

When you get the notification, set the height in the Navimow app, then tap
**Mark applied** on the dashboard card so the tracked height advances. There are
also **Snooze 3 hours** and **Snooze 2 days** buttons. The reminder recurs
(daytime) while a change is still pending, and always shows the latest
recommendation.

Note: notification action buttons need your phone to reach Home Assistant. If
they do not (for example a cloudhook that is not active), use the dashboard
buttons instead, which work over whatever connection loads the HA app.

## Test

    python3 -m venv .venv && .venv/bin/pip install pytest
    .venv/bin/python -m pytest          # unit tests; live parity test runs if HA_URL/HA_TOKEN set

## Requirements

- Home Assistant 2026.1 or newer (trigger-based template entities with an
  `action:` block).
- A weather entity that provides a daily forecast with temperature and
  precipitation.

## Licence

MIT. See `LICENSE`.
