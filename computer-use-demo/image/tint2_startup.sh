#!/bin/bash
echo "starting tint2 on display :$DISPLAY_NUM ..."

# Wait for Xvfb to be fully ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if DISPLAY=:$DISPLAY_NUM xdpyinfo >/dev/null 2>&1; then
        break
    fi
    echo "Waiting for Xvfb to be ready... (attempt $((attempt + 1))/$max_attempts)"
    sleep 1
    ((attempt++))
done

if [ $attempt -eq $max_attempts ]; then
    echo "Error: Xvfb not ready after $max_attempts seconds" >&2
    exit 1
fi

# Set DISPLAY explicitly
export DISPLAY=:$DISPLAY_NUM

# Start tint2 and capture its stderr
tint2 -c $HOME/.config/tint2/tint2rc 2>/tmp/tint2_stderr.log &

# Wait for tint2 window properties to appear
timeout=30
while [ $timeout -gt 0 ]; do
    if xdotool search --class "tint2" >/dev/null 2>&1; then
        break
    fi
    sleep 1
    ((timeout--))
done

if [ $timeout -eq 0 ]; then
    echo "tint2 stderr output:" >&2
    cat /tmp/tint2_stderr.log >&2
    exit 1
fi

# Remove the temporary stderr log file
rm /tmp/tint2_stderr.log
