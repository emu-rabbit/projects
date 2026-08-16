"""Turn the approved generated rabbit-window artwork into a clean RGBA decal.

The image generator preview contains a baked neutral checkerboard rather than
an alpha channel.  This script removes only the bright, low-chroma background
connected to the canvas edge, preserving enclosed ivory areas such as the
rabbit.  It then crops the artwork to its visible bounds with transparent
padding so Blender maps the full arch instead of the original square canvas.
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


def remove_connected_checkerboard(image: Image.Image) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    height, width, _ = rgb.shape
    channel_range = rgb.max(axis=2).astype(np.int16) - rgb.min(axis=2).astype(np.int16)
    brightness = rgb.mean(axis=2)
    background_candidate = (channel_range <= 18) & (brightness >= 218)

    outside = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    def enqueue(x: int, y: int) -> None:
        if background_candidate[y, x] and not outside[y, x]:
            outside[y, x] = True
            queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)

    while queue:
        x, y = queue.popleft()
        if x > 0:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y > 0:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)

    alpha = np.where(outside, 0, 255).astype(np.uint8)
    rgba = np.dstack((rgb, alpha))
    return Image.fromarray(rgba, mode="RGBA")


def crop_with_padding(image: Image.Image, padding: int) -> Image.Image:
    alpha = np.asarray(image.getchannel("A"))
    ys, xs = np.nonzero(alpha)
    if not len(xs):
        raise ValueError("No visible artwork remained after background removal")

    left = int(xs.min())
    top = int(ys.min())
    right = int(xs.max()) + 1
    bottom = int(ys.max()) + 1
    cropped = image.crop((left, top, right, bottom))
    padded = Image.new(
        "RGBA",
        (cropped.width + padding * 2, cropped.height + padding * 2),
        (0, 0, 0, 0),
    )
    padded.alpha_composite(cropped, (padding, padding))
    return padded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--padding", type=int, default=18)
    args = parser.parse_args()

    source = Image.open(args.source)
    prepared = crop_with_padding(remove_connected_checkerboard(source), args.padding)
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    prepared.save(args.destination, optimize=True)
    print(
        f"Prepared {args.destination} as {prepared.width}x{prepared.height} RGBA "
        f"from {source.width}x{source.height}"
    )


if __name__ == "__main__":
    main()
