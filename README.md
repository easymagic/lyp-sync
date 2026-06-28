# lyp-sync

Local AI lip-sync: turn a **portrait image** and **speech audio** (MP3 or WAV) into a talking-head video — fully offline on your machine.

Powered by [SadTalker](https://github.com/OpenTalker/SadTalker) (CVPR 2023).

## What you need

| Requirement | Notes |
|-------------|-------|
| Python 3.10–3.12 | 3.14 is not supported by ML dependencies |
| ffmpeg | `brew install ffmpeg` |
| git | To clone SadTalker |
| ~2 GB disk | Models + Python packages |
| GPU (optional) | NVIDIA CUDA speeds things up; Apple Silicon runs on CPU/MPS |

## Quick start (macOS / Linux)

```bash
# 1. Install system deps (macOS)
brew install python@3.11 ffmpeg git

# 2. Run one-time setup (~5–15 min depending on network)
bash scripts/setup.sh

# 3. Activate the environment
source .venv/bin/activate

# 4a. Web UI
python app.py
# Open http://127.0.0.1:7860

# 4b. Command line
python generate.py --image path/to/face.jpg --audio path/to/speech.mp3
```

Output videos are saved to `outputs/` by default.

## Inputs

**Image** — A clear front-facing portrait (JPG, PNG, WEBP). Works best with a visible face and neutral lighting.

**Audio** — Any speech recording in MP3, WAV, M4A, FLAC, or OGG. The audio is converted to 16 kHz mono WAV automatically.

## CLI options

```bash
python generate.py \
  --image portrait.png \
  --audio narration.mp3 \
  --output my_video.mp4 \
  --size 512 \
  --preprocess full \
  --still \
  --enhancer gfpgan
```

| Flag | Description |
|------|-------------|
| `--size 256\|512` | Face render resolution (512 = sharper, slower) |
| `--preprocess crop\|full\|...` | `full` keeps the whole body in frame |
| `--still` | Reduces head motion (good for full-body photos) |
| `--enhancer gfpgan` | Face quality boost (slower, downloads extra weights on first run) |
| `--device cpu\|cuda\|mps` | Override auto-detected compute device |

## Project layout

```
lyp-sync/
├── app.py              # Gradio web UI
├── generate.py         # CLI entry point
├── scripts/
│   ├── setup.sh        # One-time install
│   └── download_models.sh
├── src/lypsync/        # Wrapper around SadTalker
├── third_party/SadTalker/   # Cloned by setup (gitignored)
├── checkpoints/        # Downloaded models (gitignored)
├── outputs/            # Generated videos
└── results/            # SadTalker temp output
```

## Apple Silicon notes

- Setup uses CPU/MPS inference. A 10-second clip typically takes **3–10 minutes** on an M1/M2.
- For faster results, use `--size 256` and skip `--enhancer gfpgan`.
- Set `LYPSYNC_DEVICE=mps` to prefer Metal acceleration where supported.

## Troubleshooting

**"SadTalker is not installed"** — Run `bash scripts/setup.sh`.

**ffmpeg errors on MP3** — Install ffmpeg: `brew install ffmpeg`.

**Face not detected** — Use a clearer front-facing photo, or try `--preprocess resize`.

**Out of memory** — Use `--size 256`, reduce `--batch-size 1`, and avoid `--enhancer gfpgan`.

## License

This wrapper is MIT. SadTalker has its own license — see [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker).
