#!/usr/bin/env bash
# Patch known compatibility issues in SadTalker dependencies.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${VENV:-$ROOT/.venv}"

if [[ ! -d "$VENV" ]]; then
  echo "Error: virtual environment not found at $VENV"
  exit 1
fi

SITE="$VENV/lib/python3.11/site-packages"
DEGRADATIONS="$SITE/basicsr/data/degradations.py"

if [[ -f "$DEGRADATIONS" ]]; then
  if grep -q "functional_tensor import rgb_to_grayscale" "$DEGRADATIONS"; then
    echo "==> Patching basicsr for newer torchvision"
    SITE="$SITE" python3 - <<'PY'
from pathlib import Path
import os

site = Path(os.environ["SITE"])
path = site / "basicsr/data/degradations.py"
text = path.read_text()
old = "from torchvision.transforms.functional_tensor import rgb_to_grayscale"
new = """try:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale
except ImportError:
    from torchvision.transforms.functional import rgb_to_grayscale"""
if old in text:
    path.write_text(text.replace(old, new, 1))
    print(f"  patched {path}")
PY
  else
    echo "  basicsr already patched or layout changed, skipping."
  fi
else
  echo "  basicsr not installed yet, skipping patch."
fi

echo "==> Patches applied."
