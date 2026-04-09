#!/bin/bash

NGINX_CONF="/etc/nginx/nginx.conf"
API1="10.0.1.212:5000"
API2="10.0.1.103:5000"
LOG_FILE="/var/log/nginx/access.log"
STATE_FILE="/tmp/nginx_autoscale_state"

UP_THRESHOLD=50
DOWN_THRESHOLD=10
INTERVAL=5

if [ ! -f "$STATE_FILE" ]; then
  echo "single" > "$STATE_FILE"
fi

LAST_COUNT=$(wc -l < "$LOG_FILE")

while true; do
  sleep $INTERVAL

  CURRENT_COUNT=$(wc -l < "$LOG_FILE")
  DELTA=$((CURRENT_COUNT - LAST_COUNT)) # Number of requests 
  LAST_COUNT=$CURRENT_COUNT

  STATE=$(cat "$STATE_FILE")

  # SCALE UP
  if [ "$STATE" = "single" ] && [ "$DELTA" -gt "$UP_THRESHOLD" ]; then  #si numero de requests es mayor a 50, se escala
    echo "High load detected: $DELTA requests"
    echo "Scaling UP..."

    sudo sed -i "/server $API1;/a \        server $API2;" "$NGINX_CONF"
    sudo nginx -t && sudo systemctl reload nginx

    echo "double" > "$STATE_FILE"
    echo "Scale-up complete."
  fi

  # SCALE DOWN
  if [ "$STATE" = "double" ] && [ "$DELTA" -lt "$DOWN_THRESHOLD" ]; then #si numero de requests es menor a 10, se escala hacia abajo
    echo "Low load detected: $DELTA requests"
    echo "Scaling DOWN..."

    sudo sed -i "/server $API2;/d" "$NGINX_CONF"
    sudo nginx -t && sudo systemctl reload nginx

    echo "single" > "$STATE_FILE"
    echo "Scale-down complete."
  fi

done