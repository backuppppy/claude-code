#!/bin/bash
# ZeroClaw Daemon Launcher
# Runs ZeroClaw as a background agent

LOG_DIR="${HOME}/.zeroclaw/logs"
LOG_FILE="${LOG_DIR}/zeroclaw-daemon.log"
PID_FILE="${HOME}/.zeroclaw/zeroclaw-daemon.pid"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function: start daemon
start_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "❌ Daemon already running (PID: $PID)"
            return 1
        else
            echo "⚠️  Stale PID file, cleaning up..."
            rm -f "$PID_FILE"
        fi
    fi

    echo "🚀 Starting ZeroClaw daemon..."
    nohup zeroclaw agent -a agggeeeenttt -m "monitor" \
        > "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    echo "✅ Daemon started (PID: $(cat $PID_FILE))"
    echo "📝 Logs: $LOG_FILE"
}

# Function: stop daemon
stop_daemon() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ No daemon running"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⛔ Stopping daemon (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "✅ Daemon stopped"
    else
        echo "❌ Daemon not found (PID: $PID)"
        rm -f "$PID_FILE"
    fi
}

# Function: check status
check_status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "⊘ No daemon running"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Daemon running (PID: $PID)"
        echo "📝 Recent logs:"
        tail -5 "$LOG_FILE"
    else
        echo "❌ Daemon stopped (stale PID: $PID)"
        rm -f "$PID_FILE"
    fi
}

# Main
case "${1:-status}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        stop_daemon
        sleep 1
        start_daemon
        ;;
    status|*)
        check_status
        ;;
esac
