from reference.decision import recommend
from tests import fixtures as fx


def base(**over):
    kw = dict(current=50, target=30, protective=50,
              forecast=fx.CALM, now=fx.NOW, last_change=fx.LONG_AGO)
    kw.update(over)
    return kw


def test_forecast_unavailable_holds():
    r = recommend(**base(forecast=[], current=40))
    assert r["height"] == 40
    assert r["direction"] == "idle"
    assert r["reason"] == "forecast unavailable"
    assert r["can_act"] is False
    assert r["settle_days"] == 5


def test_raise_when_heatwave_forecast():
    r = recommend(**base(current=30, target=30, protective=50, forecast=fx.HEATWAVE))
    assert r["height"] == 50
    assert r["direction"] == "raise"
    assert r["stress_days"] == 3
    assert "heat stress" in r["reason"]
    assert r["can_act"] is True


def test_hot_but_wet_is_not_stress():
    r = recommend(**base(current=30, target=30, protective=50, forecast=fx.HOT_BUT_WET))
    assert r["stress_days"] == 0
    assert r["direction"] == "idle"
    assert r["can_act"] is False


def test_step_down_from_protective_when_settled():
    r = recommend(**base(current=50, target=30, protective=50,
                         forecast=fx.CALM, last_change=fx.LONG_AGO))
    assert r["height"] == 35      # 50 - floor(50/3)=34, rounded up to 35
    assert r["direction"] == "lower"
    assert r["can_act"] is True


def test_step_down_lands_on_target():
    r = recommend(**base(current=35, target=30, protective=50,
                         forecast=fx.CALM, last_change=fx.LONG_AGO))
    assert r["height"] == 30      # 35 - floor(35/3)=24 -> 25, floored at target 30
    assert r["direction"] == "lower"


def test_hold_when_not_yet_settled():
    r = recommend(**base(current=50, target=30, protective=50,
                         forecast=fx.CALM, last_change=fx.JUST_NOW))
    assert r["height"] == 50
    assert r["direction"] == "hold"
    assert "settling" in r["reason"]
    assert r["can_act"] is False


def test_idle_at_target_when_calm():
    r = recommend(**base(current=30, target=30, protective=50, forecast=fx.CALM))
    assert r["height"] == 30
    assert r["direction"] == "idle"
    assert r["can_act"] is False
    assert r["steps_remaining"] == 0


def test_heat_returns_mid_descent_raises_again():
    r = recommend(**base(current=35, target=30, protective=50, forecast=fx.HEATWAVE))
    assert r["height"] == 50
    assert r["direction"] == "raise"
    assert r["can_act"] is True


def test_steps_remaining_counts_full_descent():
    r = recommend(**base(current=50, target=30, protective=50,
                         forecast=fx.CALM, last_change=fx.LONG_AGO))
    assert r["steps_remaining"] == 1   # recommended 35; 35 -> 30 is one more


def test_step_never_below_min_or_target():
    r = recommend(**base(current=22, target=20, protective=50,
                         forecast=fx.CALM, last_change=fx.LONG_AGO))
    assert r["height"] == 20


def test_tall_grass_single_step_within_one_third():
    r = recommend(**base(current=95, target=30, protective=95,
                         forecast=fx.CALM, last_change=fx.LONG_AGO))
    assert r["height"] == 65            # 95-31=64 -> up to 65; removes 30 (< one third)
    assert (95 - r["height"]) <= 95 // 3
