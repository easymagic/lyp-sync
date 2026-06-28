#!/usr/bin/env bash
# One-time setup for lyp-sync: Python venv, SadTalker backend, model weights.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
THIRD_PARTY="$ROOT/third_party"
SADTALKER="$THIRD_PARTY/SadTalker"

pick_python() {
  for candidate in python3.11 python3.10 python3.12 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      major=$("$candidate" -c 'import sys; print(sys.version_info.major)')
      minor=$("$candidate" -c 'import sys; print(sys.version_info.minor)')
      if [[ "$major" -eq 3 && "$minor" -ge 10 && "$minor" -le 12 ]]; then
        echo "$candidate"
        return
      fi
    fi
  done
  echo ""
}

PYTHON="$(pick_python)"
if [[ -z "$PYTHON" ]]; then
  echo "Error: Python 3.10–3.12 is required."
  echo "Install with: brew install python@3.11"
  exit 1
fi

echo "==> Using $PYTHON ($("$PYTHON" --version))"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Warning: ffmpeg not found. Install with: brew install ffmpeg"
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required."
  exit 1
fi

echo "==> Creating virtual environment at $VENV"
"$PYTHON" -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"

pip install --upgrade pip wheel

echo "==> Installing PyTorch"
if [[ "$(uname -s)" == "Darwin" ]]; then
  pip install torch torchvision torchaudio
else
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
fi

echo "==> Cloning SadTalker"
mkdir -p "$THIRD_PARTY"
if [[ ! -d "$SADTALKER/.git" ]]; then
  git clone --depth 1 https://github.com/OpenTalker/SadTalker.git "$SADTALKER"
else
  echo "  SadTalker already cloned, skipping."
fi

echo "==> Installing SadTalker dependencies"
pip install -r "$SADTALKER/requirements.txt"

echo "==> Installing lyp-sync UI dependencies"
pip install -r "$ROOT/requirements.txt"

echo "==> Patching dependency compatibility"
export VENV
bash "$ROOT/scripts/patch_deps.sh"

echo "==> Upgrading imageio (fixes video save on Python 3.11+)"
pip install 'imageio>=2.31' 'imageio-ffmpeg>=0.4.9'

echo "==> Downloading model checkpoints"
bash "$ROOT/scripts/download_models.sh"

echo ""
echo "Setup complete."
echo ""
echo "Activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "Generate from the command line:"
echo "  python generate.py --image portrait.jpg --audio speech.mp3"
echo ""
echo "Or launch the web UI:"
echo "  python app.py"
echo ""
echo "Note: On Apple Silicon, generation runs on CPU/MPS and may take several minutes."
