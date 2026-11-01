from reference.plan import plan
from tests.plan_fixtures import TODAY, weather


def run(d, today, height, **state):
    return plan(daily=d, i=TODAY, height=height, today=today, **state)


def test_growing_summer_steps_down_to_target():
    r = run(weather(15), "2026-06-10", 60)
    assert (r["want"], r["next"], r["why"]) == (50, 55, "growing")


def test_lowering_waits_two_days_between_steps():
    r = run(weather(15), "2026-06-10", 55, last_lower="2026-06-09")
    assert r["next"] == 55
    r = run(weather(15), "2026-06-10", 55, last_lower="2026-06-08")
    assert r["next"] == 50


def test_autumn_raise_latches_winter_height():
    r = run(weather(11), "2026-09-25", 50)
    assert r["latch"] is True
    assert (r["want"], r["next"], r["why"]) == (55, 55, "winter")


def test_latch_holds_through_a_mild_november_week():
    r = run(weather(13), "2026-11-05", 55, latch=True)
    assert r["latch"] is True and r["next"] == 55


def test_no_lowering_when_cold():
    r = run(weather(9), "2026-11-05", 60, latch=True)
    assert (r["want"], r["next"]) == (55, 60)


def test_winter_pause_below_six():
    r = run(weather(5), "2026-11-25", 55, latch=True)
    assert r["pause"] is True


def test_pause_never_lifts_in_december_or_january():
    for today in ("2026-12-20", "2027-01-15"):
        r = run(weather(10), today, 55, latch=True, pause=True)
        assert r["pause"] is True, today


def test_pause_lifts_from_february_after_five_warm_days():
    r = run(weather(8.5), "2027-02-20", 55, latch=True, pause=True)
    assert r["pause"] is False
    assert r["latch"] is True          # T7 < grow: keep the winter height
    assert r["next"] == 55


def test_pause_needs_five_warm_days():
    d = weather(8.5, overrides={TODAY - 2: dict(mean=-5)})
    assert run(d, "2027-02-20", 55, latch=True, pause=True)["pause"] is True


def test_spring_clears_latch_and_steps_down():
    r = run(weather(11), "2027-04-01", 55, latch=True)
    assert r["latch"] is False
    assert (r["want"], r["next"]) == (50, 50)


def test_cool_spell_in_summer_raises():
    r = run(weather(7), "2026-06-10", 50)
    assert (r["want"], r["next"], r["why"]) == (55, 55, "cool spell")


def test_forecast_heat_raises_and_holds():
    d = weather(18, overrides={TODAY + 3: dict(max_=29)})
    r = run(d, "2026-07-01", 50)
    assert (r["next"], r["why"], r["heat_until"]) == (70, "heat", "2026-07-04")
    # heat gone from the forecast, still inside the hold: no lowering
    r = run(weather(18), "2026-07-03", 70, heat_until="2026-07-04")
    assert r["heat"] is True and r["next"] == 70


def test_heat_beyond_five_days_is_ignored():
    d = weather(18, overrides={TODAY + 5: dict(max_=30)})
    assert run(d, "2026-07-01", 50)["heat"] is False


def test_dry_spell_needs_warmth_and_ends_with_rain():
    r = run(weather(18, et0=4.0), "2026-07-20", 50)
    assert r["dry"] is True and r["next"] == 70
    r = run(weather(12, et0=4.0), "2026-05-01", 50)
    assert r["dry"] is False
    d = weather(18, et0=4.0, overrides={TODAY: dict(rain=12)})
    r = run(d, "2026-07-25", 70, dry=True)
    assert r["dry"] is False


def test_winter_floor_forty():
    p = dict(target=30, winter=35)
    r = plan(daily=weather(9), i=TODAY, height=30, today="2026-11-10", p=p)
    assert r["want"] == 40
