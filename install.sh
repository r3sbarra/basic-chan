#!/usr/bin/env bash
# ==============================================================================
# Basic-chan (ベーシック・ちゃん) - Standard Environment Setup & Installer
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-$SCRIPT_DIR/.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}${BLUE}"
cat << "EOF"
            /\_/\
           (     )
          /       \
         /  |   |  \
        (   |___|   )
         \         /
          \_______/
           /     \
          |   |   |
          |   |   |
          |   |   |
         (___|___)
EOF
echo -e "${RESET}"
echo -e "${BOLD}🌸 Installing Basic-chan Core Framework...${RESET}\n"

# 1. Check Python 3.10+
if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not in PATH ($PYTHON_BIN).${RESET}"
    exit 1
fi

PY_MAJOR="$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.major)')"
PY_MINOR="$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.minor)')"

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo -e "${RED}[ERROR] Python 3.10+ is required. Found Python $PY_MAJOR.$PY_MINOR.${RESET}"
    exit 1
fi
echo -e "${GREEN}✓ Python runtime detected:${RESET} Python $PY_MAJOR.$PY_MINOR"

# 2. Virtual Environment Setup
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}⚙ Creating virtual environment at:${RESET} $VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
else
    echo -e "${GREEN}✓ Existing virtual environment found at:${RESET} $VENV_DIR"
fi

VIP="$VENV_DIR/bin/python"
"$VIP" -m pip install --upgrade pip > /dev/null

# 3. Editable Install
echo -e "${BLUE}⚙ Installing basic-chan in editable mode...${RESET}"
"$VIP" -m pip install -e ".[dev]" > /dev/null

echo -e "\n${GREEN}${BOLD}✓ Installation successful for Basic-chan!${RESET}"
echo -e "Run ${BOLD}./setup.sh${RESET} to bootstrap storage and verify tests.\n"
