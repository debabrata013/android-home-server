#!/data/data/com.termux/files/usr/bin/bash

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$BASE_DIR/mdns_server.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "mDNS server is not running."
    exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
    kill -TERM "$PID"

    for i in $(seq 1 10); do
        if ! kill -0 "$PID" 2>/dev/null; then
            break
        fi
        sleep 1
    done
fi

if kill -0 "$PID" 2>/dev/null; then
    echo "Server is still running. Check manually. PID: $PID"
    exit 1
fi

rm -f "$PID_FILE"
echo "mDNS server stopped."
