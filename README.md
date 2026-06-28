# lyp-sync

Lip-sync talking-head video from a **portrait image** + **speech audio** (MP3/WAV), powered by [SadTalker](https://github.com/OpenTalker/SadTalker) on **Google Colab**.

## Quick start

1. Open the notebook in Colab:

   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/easymagic/lyp-sync/blob/main/lyp_sync.ipynb)

2. **Runtime → Change runtime type → T4 GPU → Save**
3. Run all cells top to bottom
4. Upload your image and audio when prompted
5. Download the generated MP4

## Inputs

| File | Format | Notes |
|------|--------|-------|
| Portrait | JPG, PNG, WEBP | Clear front-facing face works best |
| Audio | MP3, WAV, M4A | Speech audio drives lip sync |

## Settings (cell 5)

| Option | Default | Description |
|--------|---------|-------------|
| `size` | 256 | Face resolution (512 = sharper, slower) |
| `preprocess` | crop | Use `full` to keep entire body in frame |
| `still_mode` | false | Less head motion |
| `use_enhancer` | false | GFPGAN face boost (slower) |
| `batch_size` | 2 | Lower if you hit GPU memory errors |

## Expected speed (Colab free T4)

| Audio length | Approx. time |
|--------------|--------------|
| 10 seconds | 2–5 min |
| 60 seconds | 10–30 min |
| 3 minutes | 30–60 min |

## Free tier limits

- GPU access is not guaranteed — reconnect if you get CPU only
- Sessions disconnect after ~90 min idle (max ~12 hours)
- Download your video before closing the tab

## License

SadTalker has its own license — see [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker).
