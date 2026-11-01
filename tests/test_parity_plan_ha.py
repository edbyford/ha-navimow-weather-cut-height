"""Render the year-round Jinja macro (from this repo, not the deployed copy) through
HA's /api/template and assert it matches reference/plan.py. Read-only: nothing is
installed or changed on HA. Skips unless HA_TOKEN is set.

Set HA_URL (e.g. http://homeassistant.local:8123) and HA_TOKEN (a long-lived access
token) in the environment before running.
"""
import json
import os
import pathlib
import random
import urllib.request
from datetime import date, timedelta

import pytest

from reference.plan import DEFAULTS, plan
from tests.plan_fixtures import N, TODAY, weather

HA_URL = os.environ.get("HA_URL", "http://homeassistant.local:8123").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN", "")
MACRO = (pathlib.Path(__file__).parent.parent / "custom_templates" / "cut_height.jinja").read_text()
MACRO = MACRO.split("{% macro cut_height_plan_live")[0]
KEYS = ["temperature_2m_mean", "temperature_2m_max", "precipitation_sum", "et0_fao_evapotranspiration"]


def _render(template):
    if not HA_TOKEN:
        pytest.skip("set HA_URL and HA_TOKEN to run the live parity test")
    req = urllib.request.Request(
        f"{HA_URL}/api/template",
        data=json.dumps({"template": template}).encode(),
        headers={"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode()
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"HA unreachable: {e}")


def _random_case(seed):
    rng = random.Random(seed)
    today = (date(2026, 1, 1) + timedelta(days=rng.randrange(365))).isoformat()
    base = rng.uniform(2, 22)
    d = {
        "temperature_2m_mean": [round(base + rng.uniform(-4, 4), 1) for _ in range(N)],
        "precipitation_sum": [round(max(0, rng.uniform(-6, 8)), 1) for _ in range(N)],
        "et0_fao_evapotranspiration": [round(rng.uniform(0, 5), 2) for _ in range(N)],
    }
    d["temperature_2m_max"] = [round(t + rng.uniform(2, 9), 1) for t in d["temperature_2m_mean"]]
    t = date.fromisoformat(today)
    return dict(daily=d, height=rng.choice(range(40, 80, 5)), today=today,
                latch=rng.random() < 0.5, pause=rng.random() < 0.3, dry=rng.random() < 0.2,
                heat_until=(t + timedelta(days=rng.randrange(-5, 3))).isoformat(),
                last_lower=(t - timedelta(days=rng.randrange(0, 5))).isoformat())


CASES = [
    dict(daily=weather(15), height=60, today="2026-06-10"),
    dict(daily=weather(11), height=50, today="2026-09-25"),
    dict(daily=weather(5), height=55, today="2026-11-25", latch=True),
    dict(daily=weather(10), height=55, today="2026-12-20", latch=True, pause=True),
    dict(daily=weather(8.5), height=55, today="2027-02-20", latch=True, pause=True),
    dict(daily=weather(18, overrides={TODAY + 3: dict(max_=29)}), height=50, today="2026-07-01"),
    dict(daily=weather(18, et0=4.0), height=50, today="2026-07-20"),
] + [_random_case(s) for s in range(40)]


@pytest.mark.parametrize("c", CASES)
def test_jinja_matches_oracle(c):
    c = {"latch": False, "pause": False, "dry": False,
         "heat_until": "1970-01-01", "last_lower": "1970-01-01", **c}
    expected = plan(i=TODAY, p=DEFAULTS, **c)
    args = ", ".join([
        json.dumps({k: c["daily"][k] for k in KEYS}), str(TODAY), str(c["height"]),
        str(int(c["today"][5:7])), json.dumps(c["today"]),
        json.dumps(c["latch"]), json.dumps(c["pause"]), json.dumps(c["dry"]),
        json.dumps(c["heat_until"]), json.dumps(c["last_lower"]), json.dumps(DEFAULTS),
    ])
    got = json.loads(_render(MACRO + "{{ cut_height_plan(" + args + ") }}"))
    for k in ("next", "want", "why", "latch", "pause", "dry", "heat", "heat_until", "warm5", "heat_ahead"):
        assert got[k] == expected[k], (k, c["today"], got, expected)
