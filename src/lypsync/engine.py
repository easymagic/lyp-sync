from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .audio import prepare_audio
from .paths import (
    CHECKPOINTS_DIR,
    OUTPUTS_DIR,
    RESULTS_DIR,
    SADTALKER_DIR,
    ensure_dirs,
    resolve_device,
    sadtalker_ready,
    setup_hint,
)

SUPPORTED_IMAGE = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass
class GenerateOptions:
    size: int = 256
    preprocess: str = "crop"
    still: bool = False
    enhancer: str | None = None
    pose_style: int = 0
    batch_size: int = 2
    expression_scale: float = 1.0
    device: str | None = None


@dataclass
class GenerateResult:
    video_path: Path
    duration_seconds: float | None = None


def validate_image(image_path: str | Path) -> Path:
    source = Path(image_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Image file not found: {source}")
    if source.suffix.lower() not in SUPPORTED_IMAGE:
        raise ValueError(
            f"Unsupported image format '{source.suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_IMAGE))}"
        )
    return source


def generate(
    image_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path | None = None,
    options: GenerateOptions | None = None,
) -> GenerateResult:
    if not sadtalker_ready():
        raise RuntimeError(f"SadTalker is not installed. {setup_hint()}")

    opts = options or GenerateOptions()
    image = validate_image(image_path)
    ensure_dirs()

    prepared_audio = prepare_audio(audio_path)
    cleanup_audio = prepared_audio.suffix == ".wav" and str(prepared_audio).startswith(
        tempfile.gettempdir()
    )

    device = opts.device or resolve_device()
    use_cpu_flag = device in {"cpu", "mps"}

    if output_path is None:
        stem = Path(audio_path).stem
        output_path = OUTPUTS_DIR / f"{stem}_lipsync.mp4"
    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(SADTALKER_DIR / "inference.py"),
        "--driven_audio",
        str(prepared_audio),
        "--source_image",
        str(image),
        "--checkpoint_dir",
        str(CHECKPOINTS_DIR),
        "--result_dir",
        str(RESULTS_DIR),
        "--size",
        str(opts.size),
        "--preprocess",
        opts.preprocess,
        "--pose_style",
        str(opts.pose_style),
        "--batch_size",
        str(opts.batch_size),
        "--expression_scale",
        str(opts.expression_scale),
    ]

    if opts.still:
        cmd.append("--still")
    if opts.enhancer:
        cmd.extend(["--enhancer", opts.enhancer])
    if use_cpu_flag:
        cmd.append("--cpu")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SADTALKER_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    if device == "mps":
        env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(SADTALKER_DIR),
            env=env,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                "SadTalker inference failed.\n"
                f"stdout:\n{proc.stdout}\n"
                f"stderr:\n{proc.stderr}"
            )

        generated = _find_latest_result(proc.stdout)
        if generated is None or not generated.is_file():
            raise RuntimeError(
                "SadTalker finished but no output video was found.\n"
                f"stdout:\n{proc.stdout}\n"
                f"stderr:\n{proc.stderr}"
            )

        shutil.copy2(generated, output)
        return GenerateResult(video_path=output)
    finally:
        if cleanup_audio:
            prepared_audio.unlink(missing_ok=True)


def _find_latest_result(stdout: str) -> Path | None:
    for line in stdout.splitlines():
        marker = "The generated video is named:"
        if marker in line:
            raw = line.split(marker, 1)[1].strip()
            return Path(raw)
    candidates = sorted(RESULTS_DIR.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None
