#!/bin/bash

NGINX_CONF="/etc/nginx/nginx.conf"
API1="10.0.1.212:5000"
API2="10.0.1.103:5000"
LOG_FILE="/var/log/nginx/access.log"
STATE_FILE="/tmp/nginx_autoscale_state"

THRESHOLD=50
INTERVAL=5

if [ ! -f "$STATE_FILE" ]; then
  echo "single" > "$STATE_FILE"
fi

LAST_COUNT=$(wc -l < "$LOG_FILE")

while true; do
  sleep $INTERVAL

  CURRENT_COUNT=$(wc -l < "$LOG_FILE")
  DELTA=$((CURRENT_COUNT - LAST_COUNT))
  LAST_COUNT=$CURRENT_COUNT

  STATE=$(cat "$STATE_FILE")

  if [ "$STATE" = "single" ] && [ "$DELTA" -gt "$THRESHOLD" ]; then
    echo "High load detected: $DELTA requests in $INTERVAL seconds"
    echo "Adding second API to NGINX upstream..."

    sudo sed -i "/server $API1;/a \        server $API2;" "$NGINX_CONF"
    sudo nginx -t && sudo systemctl reload nginx

    echo "double" > "$STATE_FILE"
    echo "Scale-up complete."
  fi
done