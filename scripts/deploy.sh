#!/usr/bin/env bash
# Deploy the package + macro to your Home Assistant.
# Requires HA_IP, HA_KEY, HA_TOKEN (see scripts/ha.sh). The HA "Terminal & SSH"
# add-on must be installed so the `ha` CLI and SSH are available.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
HA_IP="${HA_IP:-homeassistant.local}"
HA_KEY="${HA_KEY:-$HOME/.ssh/id_ed25519}"
SSH=(ssh -i "$HA_KEY" -p 22 -o BatchMode=yes "root@${HA_IP}")
SCP=(scp -i "$HA_KEY" -P 22 -o BatchMode=yes)

echo "1/6 Backup configuration.yaml"
"${SSH[@]}" 'mkdir -p /config/.navimow_backup && cp /config/configuration.yaml /config/.navimow_backup/configuration.yaml.$(date +%s)'

echo "2/6 Ensure target dirs"
"${SSH[@]}" 'mkdir -p /config/custom_templates /config/packages'

echo "3/6 Copy files"
"${SCP[@]}" "${HERE}/custom_templates/navimow.jinja" "root@${HA_IP}:/config/custom_templates/navimow.jinja"
"${SCP[@]}" "${HERE}/packages/navimow_cut_height.yaml" "root@${HA_IP}:/config/packages/navimow_cut_height.yaml"
"${SCP[@]}" "${HERE}/dashboards/navimow_dashboard.yaml" "root@${HA_IP}:/config/navimow_dashboard.yaml"

echo "4/6 Ensure packages include + dashboard registration in configuration.yaml"
"${SSH[@]}" 'grep -q "packages: !include_dir_named packages" /config/configuration.yaml || printf "\nhomeassistant:\n  packages: !include_dir_named packages\n" >> /config/configuration.yaml'
"${SSH[@]}" 'grep -q "navimow-cut-height:" /config/configuration.yaml || printf "\nlovelace:\n  mode: storage\n  dashboards:\n    navimow-cut-height:\n      mode: yaml\n      title: Navimow\n      icon: mdi:robot-mower\n      show_in_sidebar: true\n      filename: navimow_dashboard.yaml\n" >> /config/configuration.yaml'

echo "5/6 ha core check"
"${SSH[@]}" 'ha core check'

echo "6/6 Restart HA core (packages + dashboard load at startup)"
"${SSH[@]}" 'ha core restart'
echo "Done. Wait ~60s, then set the helper values (packages/navimow_initial_values.md)."
