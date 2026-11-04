# Navimow cut height, year round

A small Home Assistant setup that sets a Segway Navimow's cutting height from the
weather, all year: lower in summer, higher for autumn and winter, raised for heat and
dry spells, and a winter pause when the grass stops growing. It asks you first and
then does it itself.

> This is shared as a reference for how I did it, not a turnkey add-on. You wire it
> into your own Home Assistant and change the entity names to match your setup.

**What changed (November 2026).** Version 1 (tag [`v1`](../../tree/v1)) was
summer-only and decision-only: it worked out a height for hot spells and reminded you
to set it in the Navimow app. Two things changed:

- Community integrations now expose the height as a number entity that Home Assistant
  can set, so the manual step is gone. I use
  [ilguala/navimow_pro](https://github.com/ilguala/navimow_pro) ("Navimow (Private)"),
  the most actively maintained one, since 4 November 2026. Before that I used
  [Navimow HA Pro](https://github.com/ericallard3414-arch/navimow-ha-pro), and the
  package works with that too (see *Requirements*).
- An automatic height has to be right in every season, not just in summer, so the
  rules were redone from the horticultural sources for autumn, winter, frost and spring.
  The research, with citations, is in
  [`docs/seasonal-cut-height-research.md`](docs/seasonal-cut-height-research.md).

## How it decides

Everything keys off **T7**, the mean of the last 7 daily mean air temperatures.

| Season | Rule | Default |
| --- | --- | --- |
| Summer | normal height | 50 mm |
| Heat | forecast max ≥ 27 °C or mean ≥ 25 °C in the next 5 days; held 3 days after | 70 mm |
| Dry spell | 21-day evapotranspiration minus rain ≥ 45 mm while T7 ≥ 14 °C; ends after 10 mm of rain in 3 days | 70 mm |
| Autumn | from September once T7 < 12 °C (and any time T7 < 8 °C) | 55 mm |
| Winter pause | mowing schedule off once T7 < 6 °C; back on after 5 days at T7 ≥ 8 °C, never in December or January | |
| Spring | winter height kept until T7 ≥ 10 °C from February, then down | 50 mm |

- **Raise at once; lower slowly:** at most 5 mm every 2 days, and only while T7 ≥ 10 °C
  with no heat, dry spell or pause. Never below 40 mm from October to March.
- Frost, snow, rain and heat on the day are left to the mower's own delay settings.
- Why these numbers: RHS (+5 mm for winter, mow above about 7 °C), Navimow and
  Husqvarna guidance on cold, the 6 °C base used for turf growing-degree days, and an
  Oregon State/USGA study on traffic over frost. The research doc has the sources and
  where they disagree (for example, Purdue argues against raising the height in drought
  on lawns that aren't watered).

## Ask, then apply

- **An hour before the mower's first mowing window** of the day, the plan for the day is
  fixed. The window is read from the mower's own schedule (`sensor.<mower>_schedule`), so the timing follows any change you make in the app; with no windows
  it uses 10:00. If anything changes (a new height, or pausing or resuming the schedule)
  you get one phone notification with **Apply now** and **Skip 2 days**.
- With no answer, it's applied **5 minutes before the window** if the mower is docked,
  otherwise at its next dock.
- The height is read back from the mower 4 minutes later, after the integration has
  stopped showing the value it just sent, and you're told if it didn't take.
- A step-down (say 70 → 50 mm over 8 days) is asked about once, not at every step.
- The schedule is only switched back on if this switched it off.

## Weather

Daily data from [Open-Meteo](https://open-meteo.com/) (free, no key) for your Home
zone's coordinates: the past 21 days (temperature, rain, evapotranspiration) and 6 days
of forecast. A normal weather entity has no past rain or evapotranspiration, which the
dry-spell rule needs. No location is stored in these files; the URL is built from
`zone.home`.

## Tested

- `reference/plan.py` is the logic in Python; `custom_templates/cut_height.jinja` is the
  same logic as a Jinja macro (what Home Assistant runs).
- `tests/test_plan.py`: unit tests for each season's rules.
- `tests/test_parity_plan_ha.py`: renders the macro on a live Home Assistant and checks
  it matches the Python for 47 cases (7 fixed, 40 random). Read-only.
- `tools/replay.py`: replays the rules day by day over past weather for any location,
  so you can see what they would have done before installing. On two years of weather
  for a site in southern England it gave one winter pause each winter (about late
  November to late February or March) and roughly 11 to 16 questions a year. Running
  the macro on Home Assistant over the same 747 days gave the same answers every day.

## Layout

- `packages/cut_height_year_round.yaml`: the Open-Meteo sensor, the plan sensor,
  helpers and tunables, the notify script and the three automations.
- `custom_templates/cut_height.jinja`: the decision macro.
- `reference/plan.py`: the same decision in Python (the test oracle).
- `tools/replay.py`: replay over past weather.
- `dashboards/cut_height_card.yaml`: an entities card.
- `docs/seasonal-cut-height-research.md`: the research.
- `scripts/`: SSH/API helper and a deploy script (set `HA_IP`, `HA_KEY`, `HA_TOKEN`).

## Setup

1. Install [navimow_pro](https://github.com/ilguala/navimow_pro) (HACS custom repository)
   and check you have `number.<mower>_cutting_height`, `lawn_mower.<mower>`,
   `switch.<mower>_mowing_schedule_enabled` and `sensor.<mower>_schedule`.
2. In `packages/cut_height_year_round.yaml` and `custom_templates/cut_height.jinja`,
   replace `navimow` in those entity IDs with your mower's name, and
   `notify.mobile_app_your_phone` with your notify service.
3. Make sure your Home zone is where the lawn is (Settings > Areas & zones).
4. Copy `custom_templates/cut_height.jinja` to `/config/custom_templates/` and
   `packages/cut_height_year_round.yaml` to `/config/packages/`, with packages enabled:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
5. Check the config and restart (or reload custom templates, the `input_*` helpers,
   `rest`, `template`, `script` and `automation`).
6. Set the helper values in `packages/cut_height_initial_values.md`, including resetting
   two date helpers.

`scripts/deploy.sh` does steps 4 and 5 if you have the Terminal & SSH add-on.

Notification buttons need your phone to reach Home Assistant. If they don't, the
change still happens 5 minutes before the first mow. To hold changes without the button, set
`input_datetime.cut_height_skip_until` (it's on the card).

## Test

    python3 -m venv .venv && .venv/bin/pip install pytest
    .venv/bin/python -m pytest          # unit tests; live parity test runs if HA_URL/HA_TOKEN set
    .venv/bin/python -m tools.replay --lat 51.5 --lon -0.12 --start 2024-09-01 --end 2026-08-31

## Requirements

- Home Assistant 2026.1 or newer.
- [ilguala/navimow_pro](https://github.com/ilguala/navimow_pro) 0.8.3 or newer. It's
  unofficial and uses Segway's private app cloud, so it can break if Segway changes it.
  Tested on an X450 ([navimow_pro#33](https://github.com/ilguala/navimow_pro/issues/33)):
  height reads and writes work.
- **Or Navimow HA Pro.** Rename two entities in the package, template and card:
  `number.<mower>_global_cutting_height` and `switch.<mower>_mowing_schedule`. The schedule
  match works with either. On **X-series mowers with metric decks (e.g. X450)**, HA Pro
  0.9.0 sends the height in a format these mowers misread, so most heights are ignored
  (and 80/85 mm land as 50/55). That's fixed in
  [navimow-ha-pro#46](https://github.com/ericallard3414-arch/navimow-ha-pro/pull/46), not yet
  released. The read-back tells you when a height didn't take.

## Licence

MIT. See `LICENSE`.
