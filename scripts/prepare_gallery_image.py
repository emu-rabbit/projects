from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageOps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a gallery image to a metadata-free, web-ready WebP asset.",
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--max-width", type=int, default=1920)
    parser.add_argument("--quality", type=int, default=88)
    parser.add_argument(
        "--extract-light-background",
        action="store_true",
        help=(
            "Replace a light, warm background connected to the image edges with "
            "transparent pixels while preserving enclosed light details."
        ),
    )
    parser.add_argument(
        "--alpha-from",
        type=Path,
        help=(
            "Use the foreground silhouette extracted from another same-size image as "
            "this image's alpha channel."
        ),
    )
    return parser.parse_args()


def extract_light_background(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    pixels = rgb.load()
    width, height = rgb.size
    background = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def is_light_warm(x: int, y: int) -> bool:
        red, green, blue = pixels[x, y]
        return (
            min(red, green, blue) >= 90
            and max(red, green, blue) - min(red, green, blue) <= 110
            and red + 5 >= green
            and green + 5 >= blue
        )

    def enqueue(x: int, y: int) -> None:
        index = y * width + x
        if not background[index] and is_light_warm(x, y):
            background[index] = 1
            queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)

    while queue:
        x, y = queue.popleft()
        for next_y in range(max(0, y - 1), min(height, y + 2)):
            for next_x in range(max(0, x - 1), min(width, x + 2)):
                enqueue(next_x, next_y)

    alpha = Image.frombytes(
        "L",
        (width, height),
        bytes(0 if is_background else 255 for is_background in background),
    )
    rgba = rgb.convert("RGBA")
    rgba.putalpha(alpha)
    return rgba


def main() -> None:
    args = parse_args()

    with Image.open(args.source) as source:
        image = ImageOps.exif_transpose(source)
        if args.extract_light_background:
            image = extract_light_background(image)
        if args.alpha_from:
            with Image.open(args.alpha_from) as alpha_source:
                alpha_image = extract_light_background(ImageOps.exif_transpose(alpha_source))
            if alpha_image.size != image.size:
                raise ValueError("--alpha-from image must have the same dimensions as the source")
            image = image.convert("RGBA")
            image.putalpha(alpha_image.getchannel("A"))
        if image.width > args.max_width:
            height = round(image.height * args.max_width / image.width)
            image = image.resize((args.max_width, height), Image.Resampling.LANCZOS)

        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")

        args.destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(
            args.destination,
            format="WEBP",
            quality=args.quality,
            method=6,
        )

    source_bytes = args.source.stat().st_size
    destination_bytes = args.destination.stat().st_size
    print(
        f"{args.destination}: {image.width}x{image.height}, "
        f"{source_bytes} -> {destination_bytes} bytes",
    )


if __name__ == "__main__":
    main()
