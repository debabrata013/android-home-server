#!/data/data/com.termux/files/usr/bin/bash

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$BASE_DIR/mdns_server.pid"
LOG_FILE="$BASE_DIR/logs/console.log"

mkdir -p "$BASE_DIR/logs"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")

    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "mDNS server is already running. PID: $OLD_PID"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

nohup python "$BASE_DIR/src/mdns_server.py" \
    >> "$LOG_FILE" 2>&1 < /dev/null &

PID=$!
echo "$PID" > "$PID_FILE"

sleep 2

if kill -0 "$PID" 2>/dev/null; then
    echo "mDNS server started successfully. PID: $PID"
else
    rm -f "$PID_FILE"
    echo "Failed to start mDNS server."
    tail -n 20 "$LOG_FILE"
    exit 1
fi
