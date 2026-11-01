"""Replay the year-round plan over past weather for your own location.

    python -m tools.replay --lat 51.5 --lon -0.1 --start 2024-09-01 --end 2026-08-31 [--height 50] [--csv out.csv]

Fetches daily weather from the Open-Meteo archive (free, no key; nothing is stored
unless you pass --csv), runs reference/plan.py once per evening as the package does,
applies each change the next morning, and prints per season (September to August):
when the winter pause ran, every height change, and roughly how many questions you
would have been asked. Use it to tune the thresholds before installing.
"""
import argparse
import csv
import json
import urllib.parse
import urllib.request
from collections import defaultdict

from reference.plan import plan

DAILY = ["temperature_2m_mean", "temperature_2m_max", "precipitation_sum", "et0_fao_evapotranspiration"]


def fetch(lat, lon, start, end):
    q = urllib.parse.urlencode(dict(latitude=lat, longitude=lon, start_date=start, end_date=end,
                                    daily=",".join(DAILY), timezone="auto"))
    with urllib.request.urlopen(f"https://archive-api.open-meteo.com/v1/archive?{q}", timeout=60) as r:
        return json.load(r)["daily"]


def replay(daily, height):
    state = dict(latch=False, pause=False, dry=False, heat_until="1970-01-01", last_lower="1970-01-01")
    pending, rows, descent_to = None, [], None
    for i in range(21, len(daily["time"])):
        today = daily["time"][i]
        applied = None
        if pending is not None:
            if pending < height:
                state["last_lower"] = today
            height = applied = pending
            pending = None
        was_paused = state["pause"]
        r = plan(daily=daily, i=i, height=height, today=today, **state)
        state.update({k: r[k] for k in ("latch", "pause", "dry", "heat_until")})
        asked = r["pause"] != was_paused  # pausing or resuming the schedule is asked about too
        if r["next"] != height:
            pending = r["next"]
            # A step-down is asked about once per descent; raises always ask.
            lowering = pending < height
            asked = asked or not lowering or descent_to != r["want"]
            descent_to = r["want"] if lowering else None
        rows.append(dict(date=today, t7=r["t7"], height=height, applied=applied or "",
                         want=r["want"], why=r["why"], paused=int(r["pause"]), asked=int(asked)))
    return rows


def season(day):
    y, m = int(day[:4]), int(day[5:7])
    return f"{y}/{(y + 1) % 100:02d}" if m >= 9 else f"{y - 1}/{y % 100:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--start", required=True, help="YYYY-MM-DD; the first 21 days only warm up")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--height", type=int, default=50, help="mower height at the start (mm)")
    ap.add_argument("--csv", help="write each day to this file")
    a = ap.parse_args()
    rows = replay(fetch(a.lat, a.lon, a.start, a.end), a.height)
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    by = defaultdict(list)
    for r in rows:
        by[season(r["date"])].append(r)
    for s, rs in by.items():
        paused = [r["date"] for r in rs if r["paused"]]
        changes = [f"{r['date'][5:]}→{r['applied']}" for r in rs if r["applied"] != ""]
        print(f"\n{s}: {len(rs)} days, {sum(r['asked'] for r in rs)} questions, {len(changes)} height changes")
        if paused:
            print(f"  winter pause: {len(paused)} days, {paused[0]} to {paused[-1]}")
        print("  " + ", ".join(changes))


if __name__ == "__main__":
    main()
