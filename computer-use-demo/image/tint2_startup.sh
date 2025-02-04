#!/bin/bash
echo "starting tint2 on display :$DISPLAY_NUM ..."

# Wait for Xvfb to be ready
for i in $(seq 1 5); do
    if xdpyinfo >/dev/null 2>&1; then
        break
    fi
    echo "Waiting for Xvfb... ($i/5)"
    sleep 1
done

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
