# First-run values

YAML helpers without `initial:` start at their slider minimum, then keep whatever you set
across restarts. Set these once after the first load (Settings > Devices & Services >
Helpers, or `input_number.set_value`):

| Helper | Value | Meaning |
| --- | --- | --- |
| `input_number.cut_height_target` | 50 | summer height (mm) |
| `input_number.cut_height_winter` | 55 | autumn and winter height (mm) |
| `input_number.cut_height_protective` | 70 | heat and dry-spell height (mm) |
| `input_number.cut_height_grow_temp` | 10 | 7-day mean (°C) at or above which grass is growing and lowering is allowed |
| `input_number.cut_height_slow_temp` | 6 | 7-day mean (°C) below which mowing pauses for winter |
| `input_number.cut_height_resume_temp` | 8 | pause ends after 5 days at or above this (not in Dec or Jan) |
| `input_number.cut_height_autumn_temp` | 12 | from September, below this go to the winter height |
| `input_number.cut_height_heat_max_temp` | 27 | a forecast day this hot (max) counts as heat |
| `input_number.cut_height_heat_mean_temp` | 25 | ... or this hot (daily mean) |
| `input_number.cut_height_dry_deficit` | 45 | 21-day evapotranspiration minus rain (mm) for a dry spell |

New YAML `input_datetime`s start at **today**, not 1970. Set
`input_datetime.cut_height_heat_until` and `input_datetime.cut_height_last_lower` to
`1970-01-01`, or the first day will think there is a heat hold and refuse to lower.
