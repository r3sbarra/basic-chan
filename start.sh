#!/usr/bin/env bash
# ==============================================================================
# Basic-chan (ベーシック・ちゃん) - Interactive Console Launcher
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIP="$SCRIPT_DIR/.venv/bin/python"

if [ ! -x "$VIP" ]; then
    echo "Virtual environment missing. Running ./install.sh..."
    "$SCRIPT_DIR/install.sh"
fi

if [ $# -gt 0 ]; then
    exec "$VIP" -m basic_chan.cli.app "$@"
fi

echo "🌸 Basic-chan Console"
echo "1) Status & Health"
echo "2) Discover Sisters"
echo "3) List Tool Capabilities"
echo "4) Launch MCP Server (stdio)"
echo "5) Run Tests"
read -rp "Select option [1-5]: " choice

case "$choice" in
    1) exec "$VIP" -m basic_chan.cli.app status ;;
    2) exec "$VIP" -m basic_chan.cli.app sisters ;;
    3) exec "$VIP" -m basic_chan.cli.app tools ;;
    4) exec "$VIP" -m basic_chan.cli.app mcp ;;
    5) exec "$VIP" -m pytest tests/ -v ;;
    *) echo "Exiting." ;;
esac
