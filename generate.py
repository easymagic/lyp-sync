#!/usr/bin/env python3
"""CLI: generate a lip-synced talking-head video from an image and audio file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from lypsync.engine import GenerateOptions, generate
from lypsync.paths import sadtalker_ready, setup_hint


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a lip-synced talking-head video from a portrait and audio."
    )
    parser.add_argument("--image", "-i", required=True, help="Portrait image (jpg/png)")
    parser.add_argument("--audio", "-a", required=True, help="Speech audio (mp3/wav)")
    parser.add_argument("--output", "-o", help="Output MP4 path (default: outputs/<name>_lipsync.mp4)")
    parser.add_argument("--size", type=int, default=256, choices=[256, 512], help="Face render size")
    parser.add_argument(
        "--preprocess",
        default="crop",
        choices=["crop", "extcrop", "resize", "full", "extfull"],
        help="How to crop the source image",
    )
    parser.add_argument("--still", action="store_true", help="Less head motion (good for full-body photos)")
    parser.add_argument("--enhancer", choices=["gfpgan"], help="Optional face enhancer (slower)")
    parser.add_argument("--pose-style", type=int, default=0, help="Pose style index 0-45")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"], help="Override auto-detected device")
    args = parser.parse_args()

    if not sadtalker_ready():
        print(f"Error: {setup_hint()}", file=sys.stderr)
        return 1

    opts = GenerateOptions(
        size=args.size,
        preprocess=args.preprocess,
        still=args.still,
        enhancer=args.enhancer,
        pose_style=args.pose_style,
        batch_size=args.batch_size,
        device=args.device,
    )

    try:
        result = generate(args.image, args.audio, args.output, opts)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved: {result.video_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
