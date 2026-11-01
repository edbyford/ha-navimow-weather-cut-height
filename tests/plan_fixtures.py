"""Synthetic daily weather for the year-round plan tests: 21 past days, today, 5 ahead."""

N = 27
TODAY = 21


def weather(mean, max_=None, rain=0.0, et0=1.0, overrides=None):
    """Flat weather at `mean` °C. overrides: {index: dict(mean=, max_=, rain=, et0=)}."""
    d = {
        "temperature_2m_mean": [float(mean)] * N,
        "temperature_2m_max": [float(max_ if max_ is not None else mean + 4)] * N,
        "precipitation_sum": [float(rain)] * N,
        "et0_fao_evapotranspiration": [float(et0)] * N,
    }
    for k, o in (overrides or {}).items():
        if "mean" in o: d["temperature_2m_mean"][k] = float(o["mean"])
        if "max_" in o: d["temperature_2m_max"][k] = float(o["max_"])
        if "rain" in o: d["precipitation_sum"][k] = float(o["rain"])
        if "et0" in o: d["et0_fao_evapotranspiration"][k] = float(o["et0"])
    return d
