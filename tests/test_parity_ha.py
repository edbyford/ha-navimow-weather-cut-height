"""Render the deployed Jinja macro via HA's /api/template and assert it matches
the Python oracle. Skips if HA is unreachable.

Set HA_URL (e.g. http://homeassistant.local:8123) and HA_TOKEN (a long-lived
access token) in the environment before running.
"""
import json
import os
import urllib.request

import pytest

from reference.decision import recommend
from tests import fixtures as fx

HA_URL = os.environ.get("HA_URL", "http://homeassistant.local:8123").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN", "")


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


SCENARIOS = [
    dict(current=30, target=30, protective=50, forecast=fx.HEATWAVE, last_change=fx.LONG_AGO),
    dict(current=50, target=30, protective=50, forecast=fx.CALM, last_change=fx.LONG_AGO),
    dict(current=50, target=30, protective=50, forecast=fx.CALM, last_change=fx.JUST_NOW),
    dict(current=30, target=30, protective=50, forecast=fx.CALM, last_change=fx.LONG_AGO),
    dict(current=35, target=30, protective=50, forecast=fx.HEATWAVE, last_change=fx.LONG_AGO),
]


@pytest.mark.parametrize("s", SCENARIOS)
def test_jinja_matches_oracle(s):
    expected = recommend(now=fx.NOW, **s)
    forecast_json = json.dumps(s["forecast"])
    tmpl = (
        "{% from 'navimow.jinja' import recommend_json %}"
        f"{{{{ recommend_json({s['current']}, {s['target']}, {s['protective']}, "
        f"{forecast_json}, '{fx.NOW}', '{s['last_change']}') }}}}"
    )
    got = json.loads(_render(tmpl))
    assert got["height"] == expected["height"], (s, got, expected)
    assert got["direction"] == expected["direction"], (s, got, expected)
    assert got["stress_days"] == expected["stress_days"], (s, got, expected)
    assert got["can_act"] == expected["can_act"], (s, got, expected)
