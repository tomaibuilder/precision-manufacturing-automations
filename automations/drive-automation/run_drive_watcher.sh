#!/bin/bash
# Cron wrapper for Drive Invoice Watcher
# Add to crontab: 0 * * * * /path/to/run_drive_watcher.sh
#
# Runs the watcher once (--once mode) and logs output.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV="$PROJECT_ROOT/venv/bin/activate"

source "$VENV"
python3 "$SCRIPT_DIR/drive_invoice_watcher.py" --once
