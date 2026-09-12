#!/usr/bin/env bash
# ==============================================================================
# Basic-chan (ベーシック・ちゃん) - Bootstrap & Verification
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-$SCRIPT_DIR/.venv}"
VIP="$VENV_DIR/bin/python"

if [ ! -x "$VIP" ]; then
    echo "[ERROR] Virtualenv not found. Please run ./install.sh first."
    exit 1
fi

echo "==> 1/4 Bootstrapping directories"
mkdir -p "$SCRIPT_DIR/data" "$SCRIPT_DIR/reports" "$SCRIPT_DIR/assets" "$SCRIPT_DIR/.chan_snapshots"

echo "==> 2/4 Verifying basic_chan imports & dynamic sisters"
"$VIP" -c "
import basic_chan
from basic_chan import BaseChan, ChanIdentity

ident = ChanIdentity(name='Basic-chan', slug='basic-chan', japanese_name='ベーシック・ちゃん')
class Chan(BaseChan):
    def initialize(self): pass

c = Chan(identity=ident, project_root='$SCRIPT_DIR')
sisters = c.sisters.discover_all()
print(f'✓ basic_chan OK — {len(sisters)} sisters discovered: {[s.slug for s in sisters]}')
"

echo "==> 3/4 Running self-tests"
if [ -d "$SCRIPT_DIR/tests" ]; then
    "$VIP" -m pytest "$SCRIPT_DIR/tests" -q
fi

echo "==> 4/4 Setup complete!"
