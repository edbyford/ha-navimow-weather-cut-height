"""Canonical weather-aware cut-height decision logic (test oracle).

The Jinja macro in custom_templates/navimow.jinja mirrors this function;
tests/test_parity_ha.py enforces that they agree.
"""
import math
from datetime import date, datetime

MIN_MM = 20
MAX_MM = 95


def _clamp(v):
    return max(MIN_MM, min(MAX_MM, int(round(v))))


def _to_date(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(value).date()


def _down_step(current, target, height_step):
    """One-third step down, rounded up to height_step, floored at target,
    always making at least one height_step of progress."""
    raw = current - (current // 3)
    stepped = math.ceil(raw / height_step) * height_step
    if stepped >= current:
        stepped = current - height_step
    return max(target, stepped)


def _steps_to_target(current, target, height_step):
    n, h = 0, current
    while h > target and n < 50:
        h = _down_step(h, target, height_step)
        n += 1
    return n


def recommend(*, current, target, protective, forecast, now, last_change,
              heat_temp_c=26, dry_mm=1.0, cool_temp_c=22, wet_mm=2.0,
              window_days=5, cycle_days=1.5, coverage_cycles=2,
              recovery_buffer_days=2, height_step=5):
    settle_days = math.ceil(coverage_cycles * cycle_days + recovery_buffer_days)
    result = {"height": current, "direction": "idle", "reason": "",
              "stress_days": 0, "steps_remaining": 0,
              "settle_days": settle_days, "can_act": False}

    if not forecast:
        result["reason"] = "forecast unavailable"
        return result

    window = forecast[:window_days]
    stress_days = sum(
        1 for d in window
        if d.get("temperature") is not None
        and d["temperature"] >= heat_temp_c
        and (d.get("precipitation") or 0) < dry_mm
    )
    result["stress_days"] = stress_days

    days_since = (_to_date(now) - _to_date(last_change)).days if last_change else 9999
    settled = days_since >= settle_days

    if stress_days > 0 and current < protective:
        result.update(
            height=_clamp(protective), direction="raise",
            reason=f"heat stress: {stress_days} hot/dry day(s) in next {window_days}d",
        )
    elif stress_days == 0 and current > target and settled:
        result.update(
            height=_clamp(_down_step(current, target, height_step)),
            direction="lower", reason="calm week, step down toward target",
        )
    elif stress_days == 0 and current > target and not settled:
        result.update(
            height=current, direction="hold",
            reason=f"settling, {settle_days - days_since}d to next step",
        )
    elif current <= target:
        result.update(height=current, direction="idle", reason="at target, calm")
    else:
        result.update(height=current, direction="hold", reason="holding")

    result["steps_remaining"] = _steps_to_target(result["height"], target, height_step)
    result["can_act"] = result["height"] != current
    return result
