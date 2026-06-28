from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

SUPPORTED_AUDIO = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus"}


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def prepare_audio(audio_path: str | Path) -> Path:
    """Normalize audio to 16 kHz mono WAV for SadTalker."""
    source = Path(audio_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Audio file not found: {source}")

    suffix = source.suffix.lower()
    if suffix not in SUPPORTED_AUDIO:
        raise ValueError(
            f"Unsupported audio format '{suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_AUDIO))}"
        )

    if suffix == ".wav" and _is_wav_16k_mono(source):
        return source

    if not _ffmpeg_available():
        raise RuntimeError(
            "ffmpeg is required to convert MP3 and other formats to WAV. "
            "Install with: brew install ffmpeg"
        )

    tmp = Path(tempfile.mkstemp(suffix=".wav", prefix="lypsync_")[1])
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-vn",
        str(tmp),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg failed to convert audio:\n{proc.stderr}")
    return tmp


def _is_wav_16k_mono(path: Path) -> bool:
    try:
        import wave

        with wave.open(str(path), "rb") as wf:
            return wf.getnchannels() == 1 and wf.getframerate() == 16000
    except Exception:
        return False
