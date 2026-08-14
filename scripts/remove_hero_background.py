from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


MARKER = (1, 2, 3)


def remove_connected_background(source: Path, destination: Path) -> None:
    image = Image.open(source).convert("RGB")
    flooded = image.copy()

    # The generated backdrop is nearly uniform and connected around the subject.
    # Flooding from every corner removes only that exterior region, so enclosed
    # pale details such as the rabbit and white macaron remain untouched.
    for seed in (
        (0, 0),
        (image.width - 1, 0),
        (0, image.height - 1),
        (image.width - 1, image.height - 1),
    ):
        if flooded.getpixel(seed) != MARKER:
            ImageDraw.floodfill(flooded, seed, MARKER, thresh=112)

    flooded_pixels = np.asarray(flooded)
    exterior = np.all(flooded_pixels == np.asarray(MARKER), axis=2)
    alpha = Image.fromarray(np.where(exterior, 0, 255).astype(np.uint8), mode="L")
    alpha = (
        alpha.filter(ImageFilter.MinFilter(13))
        .filter(ImageFilter.MaxFilter(3))
        .filter(ImageFilter.GaussianBlur(0.65))
    )

    result = image.convert("RGBA")
    result.putalpha(alpha)
    destination.parent.mkdir(parents=True, exist_ok=True)
    result.save(destination, "WEBP", quality=88, method=6)


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove the connected backdrop from the hero artwork.")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    remove_connected_background(args.source, args.destination)


if __name__ == "__main__":
    main()
