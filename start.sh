#!/bin/bash

# Set timezone from environment variable (default: America/Toronto)
TZ=${TZ:-America/Toronto}
export TZ
ln -sf /usr/share/zoneinfo/$TZ /etc/localtime
echo $TZ > /etc/timezone

# Get screenshot interval from environment variable (default: 60 minutes)
SCREENSHOT_INTERVAL=${SCREENSHOT_INTERVAL:-60}

# Create initial screenshot on startup
python /app/screenshot.py

# Convert interval to cron expression
if [ "$SCREENSHOT_INTERVAL" -lt 60 ]; then
    # For intervals less than 60 minutes, run every N minutes
    CRON_EXPR="*/$SCREENSHOT_INTERVAL * * * *"
elif [ "$SCREENSHOT_INTERVAL" -eq 60 ]; then
    # Hourly
    CRON_EXPR="0 * * * *"
elif [ "$SCREENSHOT_INTERVAL" -lt 1440 ]; then
    # For intervals in hours
    HOURS=$((SCREENSHOT_INTERVAL / 60))
    CRON_EXPR="0 */$HOURS * * *"
else
    # Daily at midnight
    CRON_EXPR="0 0 * * *"
fi

echo "Screenshot interval: $SCREENSHOT_INTERVAL minutes"
echo "Cron expression: $CRON_EXPR"

# Setup cron job
echo "$CRON_EXPR python /app/screenshot.py >> /var/log/cron.log 2>&1" | crontab -

# Start cron daemon
cron

# Keep the script running
tail -f /var/log/cron.log