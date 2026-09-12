"""basic_chan.scaffolding.scripts_gen — Standard script generator (install.sh, setup.sh, start.sh)."""

from __future__ import annotations


def generate_install_sh(chan_name: str, chan_slug: str, ascii_banner: str = "") -> str:
    escaped_banner = ascii_banner.strip()
    return f"""#!/usr/bin/env bash
# ==============================================================================
# {chan_name} ({chan_slug}) - Standard Environment Setup & Installer
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
VENV_DIR="${{VENV_DIR:-$SCRIPT_DIR/.venv}}"
PYTHON_BIN="${{PYTHON_BIN:-python3}}"

BOLD="\\033[1m"
GREEN="\\033[0;32m"
BLUE="\\033[0;34m"
RED="\\033[0;31m"
RESET="\\033[0m"

echo -e "${{BOLD}}${{BLUE}}"
cat << "EOF"
{escaped_banner}
EOF
echo -e "${{RESET}}"
echo -e "${{BOLD}}🌸 Installing {chan_name}...${{RESET}}\\n"

# 1. Check Python 3.10+
if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo -e "${{RED}}[ERROR] Python 3 is not installed or not in PATH ($PYTHON_BIN).${{RESET}}"
    exit 1
fi

PY_MAJOR="$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.major)')"
PY_MINOR="$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.minor)')"

if [ "$PY_MAJOR" -lt 3 ] || {{ [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }}; then
    echo -e "${{RED}}[ERROR] Python 3.10+ is required.${{RESET}}"
    exit 1
fi
echo -e "${{GREEN}}✓ Python runtime detected:${{RESET}} Python $PY_MAJOR.$PY_MINOR"

# 2. Virtual Environment Setup
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${{BLUE}}⚙ Creating virtual environment at:${{RESET}} $VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
else
    echo -e "${{GREEN}}✓ Existing virtual environment found at:${{RESET}} $VENV_DIR"
fi

VIP="$VENV_DIR/bin/python"
"$VIP" -m pip install --upgrade pip > /dev/null

# 3. Editable Install
echo -e "${{BLUE}}⚙ Installing package in editable mode...${{RESET}}"
"$VIP" -m pip install -e ".[dev]" > /dev/null

echo -e "\\n${{GREEN}}${{BOLD}}✓ Installation successful for {chan_name}!${{RESET}}"
echo -e "Run ${{BOLD}}./setup.sh${{RESET}} to bootstrap storage and verify tests.\\n"
"""


def generate_setup_sh(chan_name: str, chan_slug: str) -> str:
    return f"""#!/usr/bin/env bash
# ==============================================================================
# {chan_name} ({chan_slug}) - One-time Project Bootstrap & Self-Verification
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
VENV_DIR="${{VENV_DIR:-$SCRIPT_DIR/.venv}}"
VIP="$VENV_DIR/bin/python"

if [ ! -x "$VIP" ]; then
    echo "[ERROR] Virtualenv not found. Please run ./install.sh first."
    exit 1
fi

echo "==> 1/4 Bootstrapping directories"
mkdir -p "$SCRIPT_DIR/data" "$SCRIPT_DIR/reports" "$SCRIPT_DIR/assets" "$SCRIPT_DIR/.chan_snapshots"

echo "==> 2/4 Verifying imports & sisters"
"$VIP" -c "
import {chan_slug.replace('-', '_')}
print('✓ Module import successful')
"

echo "==> 3/4 Running self-tests"
if [ -d "$SCRIPT_DIR/tests" ]; then
    "$VIP" -m pytest "$SCRIPT_DIR/tests" -q
fi

echo "==> 4/4 Setup complete!"
"""


def generate_start_sh(chan_name: str, chan_slug: str) -> str:
    return f"""#!/usr/bin/env bash
# ==============================================================================
# {chan_name} ({chan_slug}) - Interactive Console Launcher
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
VIP="$SCRIPT_DIR/.venv/bin/python"

if [ ! -x "$VIP" ]; then
    echo "Virtual environment missing. Running ./install.sh..."
    "$SCRIPT_DIR/install.sh"
fi

if [ $# -gt 0 ]; then
    exec "$VIP" -m {chan_slug.replace('-', '_')}.cli.app "$@"
fi

echo "🌸 {chan_name} Console"
echo "1) Run Status"
echo "2) Discover Sisters"
echo "3) List Tools"
echo "4) Launch MCP Server"
echo "5) Run Tests"
read -rp "Select option [1-5]: " choice

case "$choice" in
    1) exec "$VIP" -m {chan_slug.replace('-', '_')}.cli.app status ;;
    2) exec "$VIP" -m {chan_slug.replace('-', '_')}.cli.app sisters ;;
    3) exec "$VIP" -m {chan_slug.replace('-', '_')}.cli.app tools ;;
    4) exec "$VIP" -m {chan_slug.replace('-', '_')}.cli.app mcp ;;
    5) exec "$VIP" -m pytest tests/ -v ;;
    *) echo "Exiting." ;;
esac
"""
