#!/usr/bin/env python3
"""Normalize the visible scale of the ten current macaron concept assets."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class Asset:
    slug: str
    source_pattern: str


ASSETS = (
    Asset("workshop", "Frozen Rabbit Workshop -*.png"),
    Asset("tome", "Frozen Rabbit Tome -*.png"),
    Asset("boundary-notes", "Boundary Notes -*.png"),
    Asset("emu-rabbit", "Emu Rabbit Github io -*.png"),
    Asset("link-array", "LinkArray -*.png"),
    Asset("nanb", "nAnB -*.png"),
    Asset("vue-router-rule", "Vue Router Rule -*.png"),
    Asset("dandelifeon", "Dandelifeon -*.png"),
    Asset("75-alchohol", "75 Alchohol -*.png"),
    Asset("50-hiragana-test", "50 Hiragana Test -*.png"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path(".agents/designs"))
    parser.add_argument("--output-dir", type=Path, default=Path("assets/macarons"))
    parser.add_argument("--canvas-size", type=int, default=1254)
    parser.add_argument("--target-max-edge", type=int, default=1050)
    parser.add_argument("--alpha-threshold", type=int, default=8)
    return parser.parse_args()


def find_source(source_dir: Path, pattern: str) -> Path:
    matches = list(source_dir.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one source matching {pattern!r}, found {len(matches)}"
        )
    return matches[0]


def visible_bbox(image: Image.Image, threshold: int) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > threshold else 0)
    bbox = mask.getbbox()
    if bbox is None:
        raise RuntimeError("Image has no visible pixels above the alpha threshold")
    return bbox


def normalize(
    source: Path,
    destination: Path,
    canvas_size: int,
    target_max_edge: int,
    alpha_threshold: int,
) -> tuple[int, int, int, int]:
    with Image.open(source) as opened:
        image = opened.convert("RGBA")

    bbox = visible_bbox(image, alpha_threshold)
    subject = image.crop(bbox)
    scale = target_max_edge / max(subject.size)
    resized_size = tuple(max(1, round(side * scale)) for side in subject.size)
    subject = subject.resize(resized_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset = tuple((canvas_size - side) // 2 for side in resized_size)
    canvas.alpha_composite(subject, offset)

    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="PNG", optimize=True)
    return visible_bbox(canvas, alpha_threshold)


def main() -> None:
    args = parse_args()
    if args.target_max_edge > args.canvas_size:
        raise ValueError("target-max-edge must fit within canvas-size")

    for asset in ASSETS:
        source = find_source(args.source_dir, asset.source_pattern)
        destination = args.output_dir / f"{asset.slug}.png"
        bbox = normalize(
            source,
            destination,
            args.canvas_size,
            args.target_max_edge,
            args.alpha_threshold,
        )
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        print(
            f"{asset.slug}: {source.name} -> {destination} "
            f"bbox={bbox} size={width}x{height} max={max(width, height)}"
        )


if __name__ == "__main__":
    main()
