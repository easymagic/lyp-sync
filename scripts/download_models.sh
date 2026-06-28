#!/usr/bin/env bash
# Download SadTalker model checkpoints (~1.5 GB total).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKPOINTS="$ROOT/checkpoints"
RELEASE="https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc"

mkdir -p "$CHECKPOINTS"

download() {
  local name="$1"
  local url="$2"
  local dest="$CHECKPOINTS/$name"
  if [[ -f "$dest" ]]; then
    echo "  skip (exists): $name"
    return
  fi
  echo "  download: $name"
  curl -L --fail --progress-bar -o "$dest" "$url"
}

echo "==> Downloading SadTalker checkpoints to $CHECKPOINTS"

download "SadTalker_V0.0.2_256.safetensors" \
  "$RELEASE/SadTalker_V0.0.2_256.safetensors"

download "SadTalker_V0.0.2_512.safetensors" \
  "$RELEASE/SadTalker_V0.0.2_512.safetensors"

download "mapping_00109-model.pth.tar" \
  "$RELEASE/mapping_00109-model.pth.tar"

download "mapping_00229-model.pth.tar" \
  "$RELEASE/mapping_00229-model.pth.tar"

echo "==> Checkpoints ready."
