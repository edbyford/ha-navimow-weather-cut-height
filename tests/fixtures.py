"""Synthetic daily forecasts for the decision tests. Dates are fixed."""


def day(temperature, templow=12.0, precipitation=0.0):
    return {"temperature": temperature, "templow": templow, "precipitation": precipitation}


CALM = [day(18), day(19, precipitation=2.5), day(17), day(20), day(16), day(19)]
HEATWAVE = [day(21), day(27), day(29, precipitation=0.0), day(28), day(22), day(20)]
HOT_BUT_WET = [day(28, precipitation=4.0), day(19), day(18), day(20), day(17), day(16)]

NOW = "2026-06-15T09:00:00"
LONG_AGO = "2026-05-01T09:00:00"   # always settled
JUST_NOW = "2026-06-14T09:00:00"   # not settled
