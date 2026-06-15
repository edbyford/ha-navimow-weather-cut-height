# First-run values (set once in HA UI, Settings > Devices & Services > Helpers)

- navimow_target_height: your normal cut height, e.g. 50
- navimow_protective_height: raised height for heat spells, must be ABOVE target, e.g. 70
- navimow_current_height: the height the mower is actually set to right now
- navimow_heat_temp_c: 26   (a day at/above this and dry counts as heat stress)
- navimow_dry_mm: 1         (a day with less rain than this counts as dry)
- navimow_cool_temp_c: 22
- navimow_wet_mm: 2
- navimow_window_days: 5    (how many forecast days to look ahead)
- navimow_cycle_days: 1.5   (how long one full mow of your lawn takes)
- navimow_coverage_cycles: 2
- navimow_recovery_buffer_days: 2
- navimow_height_step_mm: 5 (your mower's height increment)
- navimow_last_height_change: set to now
- navimow_notify_service: notify.mobile_app_your_phone
