from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THIRD_PARTY = ROOT / "third_party"
SADTALKER_DIR = THIRD_PARTY / "SadTalker"
CHECKPOINTS_DIR = ROOT / "checkpoints"
RESULTS_DIR = ROOT / "results"
OUTPUTS_DIR = ROOT / "outputs"


def ensure_dirs() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def sadtalker_ready() -> bool:
    inference = SADTALKER_DIR / "inference.py"
    ckpt_256 = CHECKPOINTS_DIR / "SadTalker_V0.0.2_256.safetensors"
    mapping_a = CHECKPOINTS_DIR / "mapping_00109-model.pth.tar"
    mapping_b = CHECKPOINTS_DIR / "mapping_00229-model.pth.tar"
    return inference.is_file() and ckpt_256.is_file() and mapping_a.is_file() and mapping_b.is_file()


def setup_hint() -> str:
    script = ROOT / "scripts" / "setup.sh"
    return f"Run setup first: bash {script}"


def resolve_device() -> str:
    override = os.environ.get("LYPSYNC_DEVICE", "").strip().lower()
    if override in {"cpu", "cuda", "mps"}:
        return override

    try:
        import torch
    except ImportError:
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"
