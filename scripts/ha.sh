#!/usr/bin/env bash
# Thin helpers for talking to your Home Assistant over SSH and the REST API.
# Set these for your own instance (env vars or edit the defaults):
#   HA_IP    - host/IP reachable from this machine (LAN, VPN, or Tailscale)
#   HA_KEY   - SSH private key for the HA "Terminal & SSH" add-on (root)
#   HA_TOKEN - a long-lived access token (Profile > Long-lived access tokens)
set -euo pipefail
HA_IP="${HA_IP:-homeassistant.local}"
HA_KEY="${HA_KEY:-$HOME/.ssh/id_ed25519}"
HA_TOKEN="${HA_TOKEN:?set HA_TOKEN to a long-lived access token}"
API="http://${HA_IP}:8123/api"

ha_ssh()  { ssh -i "$HA_KEY" -p 22 -o BatchMode=yes -o ConnectTimeout=10 "root@${HA_IP}" "$@"; }
ha_scp()  { scp -i "$HA_KEY" -P 22 -o BatchMode=yes "$1" "root@${HA_IP}:$2"; }
ha_api()  { curl -s --max-time 20 -H "Authorization: Bearer ${HA_TOKEN}" "$@"; }

"$@"
