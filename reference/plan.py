"""Year-round cut-height plan (test oracle).

The Jinja macro `cut_height_plan()` in custom_templates/cut_height.jinja mirrors this
function; tests/test_parity_plan_ha.py checks that they agree.

It is evaluated once a day (in the evening) on daily weather arrays covering at least
the 20 days before today and, ideally, the next 4. It reads its state (three latches,
two dates) and returns the new state plus tomorrow's height. The caller stores the new
state and applies the height.

Everything is driven by T7, the mean of the last 7 daily mean air temperatures
(today included). The thresholds come from docs/seasonal-cut-height-research.md.
"""
import math
from datetime import date, timedelta

DEFAULTS = dict(
    target=50,        # summer height (mm)
    winter=55,        # autumn/winter height (mm)
    protective=70,    # heat / drought height (mm)
    grow=10.0,        # T7 at or above: growing, lowering allowed
    slow=6.0,         # T7 below: winter pause
    resume=8.0,       # pause ends after 5 days at or above this; below it, winter height
    autumn=12.0,      # from September, T7 below this raises to winter height
    heat_max=27.0,    # a forecast day with max at or above this is heat
    heat_mean=25.0,   # ... or with mean at or above this
    dry_deficit=45.0, # 21-day evapotranspiration minus rain (mm) for a dry spell
)

DRY_WARM = 14.0       # a dry spell only counts when T7 is at least this
DRY_RELEASE_MM = 10.0 # rain over 3 days that ends a dry spell
HEAT_HOLD_DAYS = 3    # protective height held this long after forecast heat
LOWER_EVERY_DAYS = 2  # at most one 5 mm step down per this many days
STEP_MM = 5
WINTER_FLOOR_MM = 40  # never below this from October to March


def _mean(xs):
    return sum(xs) / len(xs)


def plan(*, daily, i, height, today, latch=False, pause=False, dry=False,
         heat_until="1970-01-01", last_lower="1970-01-01", p=None):
    """daily: dict of lists with keys temperature_2m_mean, temperature_2m_max,
    precipitation_sum, et0_fao_evapotranspiration. i: index of today (>= 20).
    today, heat_until, last_lower: 'YYYY-MM-DD'."""
    p = {**DEFAULTS, **(p or {})}
    tm = [float(x or 0) for x in daily["temperature_2m_mean"]]
    tx = [float(x or 0) for x in daily["temperature_2m_max"]]
    rain = [float(x or 0) for x in daily["precipitation_sum"]]
    et0 = [float(x or 0) for x in daily["et0_fao_evapotranspiration"]]
    month = int(today[5:7])

    t7 = _mean(tm[i - 6:i + 1])
    warm5 = all(_mean(tm[k - 6:k + 1]) >= p["resume"] for k in range(i - 4, i + 1))
    heat_ahead = any(tx[k] >= p["heat_max"] or tm[k] >= p["heat_mean"]
                     for k in range(i, min(i + 5, len(tm))))
    deficit = sum(et0[i - 20:i + 1]) - sum(rain[i - 20:i + 1])
    rain3 = sum(rain[i - 2:i + 1])

    # Winter pause: on below `slow`; off after 5 days at >= `resume`, never in Dec or Jan.
    if t7 < p["slow"]:
        pause = True
    elif pause and warm5 and month not in (12, 1):
        pause = False

    # Winter height latch: set Sep-Dec below `autumn`; cleared Feb-Aug once growing.
    if month in (9, 10, 11, 12) and t7 < p["autumn"]:
        latch = True
    elif month in (2, 3, 4, 5, 6, 7, 8) and t7 >= p["grow"] and not pause:
        latch = False

    # Dry spell: big 21-day water deficit while warm; ends after enough rain.
    if deficit >= p["dry_deficit"] and t7 >= DRY_WARM:
        dry = True
    if dry and rain3 >= DRY_RELEASE_MM:
        dry = False

    if heat_ahead:
        heat_until = (date.fromisoformat(today) + timedelta(days=HEAT_HOLD_DAYS)).isoformat()
    heat = today <= heat_until

    if heat or dry:
        want, why = p["protective"], "heat" if heat else "dry spell"
    elif latch or t7 < p["resume"] or (height >= p["winter"] and t7 < p["grow"]):
        want, why = p["winter"], "winter" if latch else "cool spell"
    else:
        want, why = p["target"], "growing"
    if month in (10, 11, 12, 1, 2, 3):
        want = max(want, WINTER_FLOOR_MM)

    since_lower = (date.fromisoformat(today) - date.fromisoformat(last_lower)).days
    if want > height:
        nxt = want
    elif (want < height and t7 >= p["grow"] and not heat and not dry and not pause
          and since_lower >= LOWER_EVERY_DAYS):
        nxt = max(want, height - STEP_MM)
    else:
        nxt = height

    return dict(t7=round(t7, 1), warm5=warm5, deficit=round(deficit, 1),
                rain3=round(rain3, 1), heat_ahead=heat_ahead, heat=heat,
                heat_until=heat_until, latch=latch, pause=pause, dry=dry,
                want=int(want), next=int(nxt), height=height, why=why)
