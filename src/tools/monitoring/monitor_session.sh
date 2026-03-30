#!/bin/bash
#
# monitor_session.sh - A robust script to monitor and log all activity
# from a specified TTY session non-intrusively.
#
# Description:
# This script attaches to a given TTY and captures all standard output and
# standard error, redirecting it to a timestamped log file. It runs as a
# background process, allowing the user to continue their work without
# interruption. It includes functions to start, stop, and check the
# status of the monitoring process.

# --- Configuration ---
LOG_DIR="$HOME/tty_logs"
PID_FILE="/tmp/tty_monitor.pid"
DEFAULT_TTY=$(tty)

# --- Functions ---

# Show script usage
usage() {
    echo "Usage: $0 {start [TTY] | stop | status | view}"
    echo "  start [TTY]: Start monitoring a terminal session."
    echo "               If TTY is not specified, it defaults to the current session."
    echo "  stop: Stop the currently running monitoring process."
    echo "  status: Check if the monitoring process is active."
    echo "  view: View the latest log file using 'less'."
    exit 1
}

# Start the monitoring process
start_monitor() {
    local target_tty="$1"
    
    if [ -z "$target_tty" ]; then
        target_tty="$DEFAULT_TTY"
    fi

    if [ ! -e "$target_tty" ]; then
        echo "Error: TTY '$target_tty' does not exist."
        exit 1
    fi

    if [ -f "$PID_FILE" ]; then
        echo "Error: Monitoring is already running (PID $(cat "$PID_FILE"))."
        exit 1
    fi

    mkdir -p "$LOG_DIR"
    local log_file="$LOG_DIR/session_$(date +%Y%m%d_%H%M%S)_$(basename "$target_tty").log"

    echo "Starting monitoring on $target_tty..."
    echo "Log file: $log_file"

    # Redirect strace output to the log file in the background
    strace -p $(ps -ft "$target_tty" | awk 'NR>1 {print $2}') -e read,write --decode-fds=all -o "$log_file" &
    
    local strace_pid=$!
    echo $strace_pid > "$PID_FILE"

    if [ $? -eq 0 ]; then
        echo "Monitoring started successfully (PID: $strace_pid)."
    else
        echo "Error: Failed to start monitoring."
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Stop the monitoring process
stop_monitor() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Monitoring is not currently running."
        exit 1
    fi

    local pid=$(cat "$PID_FILE")
    if ps -p $pid > /dev/null; then
        echo "Stopping monitoring process (PID: $pid)..."
        kill $pid
        rm -f "$PID_FILE"
        echo "Monitoring stopped."
    else
        echo "Warning: PID file found, but no matching process is running."
        rm -f "$PID_FILE"
    fi
}

# Check the status of the monitoring process
check_status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Monitoring is not running."
        exit 0
    fi

    local pid=$(cat "$PID_FILE")
    if ps -p $pid > /dev/null; then
        echo "Monitoring is active (PID: $pid)."
    else
        echo "Monitoring is stopped, but PID file exists. Cleaning up."
        rm -f "$PID_FILE"
    fi
}

# View the latest log file
view_log() {
    local latest_log=$(ls -t "$LOG_DIR" | head -n 1)
    if [ -z "$latest_log" ]; then
        echo "No log files found in $LOG_DIR."
        exit 1
    fi
    
    echo "Viewing log: $LOG_DIR/$latest_log"
    less "$LOG_DIR/$latest_log"
}

# --- Main Logic ---

case "$1" in
    start)
        start_monitor "$2"
        ;;
    stop)
        stop_monitor
        ;;
    status)
        check_status
        ;;
    view)
        view_log
        ;;
    *)
        usage
        ;;
esac

exit 0