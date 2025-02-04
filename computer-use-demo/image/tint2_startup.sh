#!/bin/bash
start_time=$(date +%s.%N)
echo "starting tint2 on display :$DISPLAY_NUM ..."

# Start tint2 and capture its stderr
tint2 -c $HOME/.config/tint2/tint2rc 2>/tmp/tint2_stderr.log &

# Wait for tint2 window properties to appear
timeout=300
while [ $timeout -gt 0 ]; do
    if xdotool search --class "tint2" >/dev/null 2>&1; then
        break
    fi
    sleep 0.1
    timeout=$((timeout - 1))
done

if [ $timeout -eq 0 ]; then
    echo "tint2 stderr output:" >&2
    cat /tmp/tint2_stderr.log >&2
    exit 1
fi

# Remove the temporary stderr log file
rm /tmp/tint2_stderr.log

end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
echo "tint2 startup completed in $duration seconds"
