#!/bin/bash

# Set timezone from environment variable (default: America/Toronto)
TZ=${TZ:-America/Toronto}
export TZ
ln -sf /usr/share/zoneinfo/$TZ /etc/localtime
echo $TZ > /etc/timezone

# Get screenshot interval from environment variable (default: 60 minutes)
SCREENSHOT_INTERVAL=${SCREENSHOT_INTERVAL:-60}

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

# Create log file if it doesn't exist
touch /var/log/cron.log

# Setup cron job with proper environment
(
    echo "SHELL=/bin/bash"
    echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    echo "TZ=$TZ"
    echo "$CRON_EXPR python /app/screenshot.py >> /var/log/cron.log 2>&1"
) | crontab -

# List cron jobs for debugging
echo "Cron jobs configured:"
crontab -l

# Start cron service (not in foreground to avoid PID 1 issues)
service cron start

# Check if cron is running
if ! pgrep -x "cron" > /dev/null; then
    echo "Cron failed to start"
    exit 1
fi

# Keep the script running by tailing the log
exec tail -f /var/log/cron.log