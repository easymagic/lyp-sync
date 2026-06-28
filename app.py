#!/usr/bin/env python3
"""Gradio web UI for lyp-sync."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import gradio as gr

from lypsync.engine import GenerateOptions, generate
from lypsync.paths import resolve_device, sadtalker_ready, setup_hint


def _run(
    image_path: str | None,
    audio_path: str | None,
    size: int,
    preprocess: str,
    still: bool,
    enhancer: str | None,
    pose_style: int,
):
    if not sadtalker_ready():
        raise gr.Error(setup_hint())
    if not image_path:
        raise gr.Error("Upload a portrait image.")
    if not audio_path:
        raise gr.Error("Upload an audio file (MP3 or WAV).")

    enh = None if enhancer == "none" else enhancer
    opts = GenerateOptions(
        size=size,
        preprocess=preprocess,
        still=still,
        enhancer=enh,
        pose_style=pose_style,
    )
    result = generate(image_path, audio_path, options=opts)
    return str(result.video_path)


def build_ui() -> gr.Blocks:
    device = resolve_device()
    ready = sadtalker_ready()

    with gr.Blocks(title="lyp-sync", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# lyp-sync\n"
            "Local AI lip-sync: upload a **portrait image** and **speech audio** (MP3 or WAV) "
            "to generate a talking-head video.\n\n"
            f"Device: `{device}` · Backend: SadTalker · "
            + ("Ready" if ready else f"**Not installed** — {setup_hint()}")
        )

        with gr.Row():
            with gr.Column():
                image = gr.Image(label="Portrait image", type="filepath", sources=["upload"])
                audio = gr.Audio(label="Speech audio", type="filepath", sources=["upload"])
            with gr.Column():
                size = gr.Radio([256, 512], value=256, label="Face resolution")
                preprocess = gr.Radio(
                    ["crop", "resize", "full", "extcrop", "extfull"],
                    value="crop",
                    label="Image preprocess",
                )
                still = gr.Checkbox(label="Still mode (less head motion)", value=False)
                enhancer = gr.Radio(["none", "gfpgan"], value="none", label="Face enhancer")
                pose_style = gr.Slider(0, 45, step=1, value=0, label="Pose style")
                submit = gr.Button("Generate lip-sync video", variant="primary")

        output = gr.Video(label="Result")

        submit.click(
            fn=_run,
            inputs=[image, audio, size, preprocess, still, enhancer, pose_style],
            outputs=[output],
        )

    return demo


def main() -> None:
    demo = build_ui()
    demo.queue().launch(server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    main()
