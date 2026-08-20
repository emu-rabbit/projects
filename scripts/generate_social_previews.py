#!/usr/bin/env python3
"""Generate localized 1200x630 social preview cards from canonical macaron art."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "src" / "data" / "seo.json"
FONT_PATH = ROOT / "assets" / "fonts" / "emu-portfolio-round-subset.woff2"
OUTPUT_ROOT = ROOT / "public" / "social"
HOME_PRODUCT_SHOT = ROOT / "assets" / "seo" / "home-macaron-product-shot.png"
CANVAS_SIZE = (1200, 630)
INK = "#3f352f"
INK_SOFT = "#75665d"
PAPER = "#f7f2e9"
ACCENT = "#a97355"
HOME_PANEL_BOX = (580, 65, 1170, 565)
HOME_PANEL_SIZE = (
    HOME_PANEL_BOX[2] - HOME_PANEL_BOX[0],
    HOME_PANEL_BOX[3] - HOME_PANEL_BOX[1],
)
HOME_PANEL_RADIUS = 52
PROJECT_HEADING_LINES = {
    "window-notes": {
        "zh": ["絵夢羽さ沂的", "窗邊手記"],
        "en": ["Emu-Rabbit's", "Window Notes"],
    },
    "boundary-notes": {
        "zh": ["兔子的", "祕密檔案"],
        "en": ["Bunny's", "Secret File"],
    },
    "frozen-rabbit-workshop": {
        "zh": ["冷凍兔肉的", "巧匠工坊"],
        "en": ["Frozen Rabbit's", "Workshop"],
    },
    "frozen-rabbit-tome": {
        "zh": ["冷凍兔肉的", "大地秘笈"],
        "en": ["Frozen Rabbit's", "Tome"],
    },
    "link-array": {"zh": ["LinkArray"], "en": ["LinkArray"]},
    "vue-router-rule": {"zh": ["Vue Router", "Rule"], "en": ["Vue Router", "Rule"]},
    "dandelifeon": {"zh": ["Dandelifeon"], "en": ["Dandelifeon"]},
    "nanb": {"zh": ["nAnB"], "en": ["nAnB"]},
    "75-alchohol": {"zh": ["75% Alchohol"], "en": ["75% Alchohol"]},
    "50-hiragana-test": {"zh": ["50 Hiragana", "Test"], "en": ["50 Hiragana", "Test"]},
}


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def text_width(draw: ImageDraw.ImageDraw, value: str, text_font: ImageFont.FreeTypeFont) -> float:
    box = draw.textbbox((0, 0), value, font=text_font)
    return box[2] - box[0]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    value: str,
    text_font: ImageFont.FreeTypeFont,
    max_width: int,
    language: str,
) -> list[str]:
    tokens = list(value) if language == "zh" else value.split(" ")
    separator = "" if language == "zh" else " "
    lines: list[str] = []
    current = ""

    for token in tokens:
        candidate = f"{current}{separator if current else ''}{token}"
        if current and text_width(draw, candidate, text_font) > max_width:
            lines.append(current)
            current = token
        else:
            current = candidate

    if current:
        lines.append(current)
    return lines


def fit_heading(
    draw: ImageDraw.ImageDraw,
    value: str,
    language: str,
    max_width: int,
    max_lines: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    initial_size = 66 if language == "zh" else 58
    for size in range(initial_size, 39, -2):
        heading_font = font(size)
        lines = wrap_text(draw, value, heading_font, max_width, language)
        if len(lines) <= max_lines:
            return heading_font, lines
    heading_font = font(40)
    return heading_font, wrap_text(draw, value, heading_font, max_width, language)[:max_lines]


def fit_fixed_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    language: str,
    max_width: int,
) -> ImageFont.FreeTypeFont:
    initial_size = 66 if language == "zh" else 58
    for size in range(initial_size, 39, -2):
        heading_font = font(size)
        if all(text_width(draw, line, heading_font) <= max_width for line in lines):
            return heading_font
    return font(40)


def add_soft_shape(canvas: Image.Image, box: tuple[int, int, int, int], fill: str, blur: int) -> None:
    shape = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shape).rounded_rectangle(box, radius=90, fill=fill)
    canvas.alpha_composite(shape.filter(ImageFilter.GaussianBlur(blur)))


def paste_with_shadow(canvas: Image.Image, artwork: Image.Image, position: tuple[int, int]) -> None:
    shadow = Image.new("RGBA", artwork.size, (0, 0, 0, 0))
    shadow.putalpha(artwork.getchannel("A").filter(ImageFilter.GaussianBlur(14)))
    tinted_shadow = Image.new("RGBA", artwork.size, (75, 55, 45, 72))
    tinted_shadow.putalpha(shadow.getchannel("A").point(lambda alpha: round(alpha * 0.15)))
    canvas.alpha_composite(tinted_shadow, (position[0] + 6, position[1] + 12))
    canvas.alpha_composite(artwork, position)


def load_macaron(relative_path: str, size: int) -> Image.Image:
    source = Image.open(ROOT / relative_path).convert("RGBA")
    source.thumbnail((size, size), Image.Resampling.LANCZOS)
    return source


def draw_brand(draw: ImageDraw.ImageDraw, language: str, site_locale: dict[str, object]) -> None:
    label = str(site_locale["siteName"])
    draw.ellipse((82, 526, 96, 540), fill=ACCENT)
    draw.ellipse((103, 526, 117, 540), fill="#d4a98d")
    draw.ellipse((124, 526, 138, 540), fill="#6f8c78")
    draw.text((82, 558), label, font=font(25 if language == "zh" else 23), fill=INK_SOFT)


def draw_text_block(
    canvas: Image.Image,
    language: str,
    category: str,
    heading: str,
    site_locale: dict[str, object],
    heading_lines: list[str] | None = None,
) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.text((82, 92), category, font=font(25), fill=ACCENT)
    if heading_lines:
        lines = heading_lines
        heading_font = fit_fixed_lines(draw, lines, language, 500)
    else:
        heading_font, lines = fit_heading(draw, heading, language, 500, 3)
    y = 148
    spacing = round(heading_font.size * 1.20)
    for line in lines:
        draw.text((78, y), line, font=heading_font, fill=INK)
        y += spacing
    draw.line((82, min(y + 18, 450), 236, min(y + 18, 450)), fill="#c9aa97", width=3)
    draw_brand(draw, language, site_locale)


def generate_project_card(project: dict[str, object], language: str, site_locale: dict[str, object]) -> Image.Image:
    locale = project["locales"][language]
    canvas = Image.new("RGBA", CANVAS_SIZE, PAPER)
    palette = str(project["palette"])
    panel_rgb = tuple(
        round(value * 0.76 + paper * 0.24)
        for value, paper in zip(
            tuple(int(palette.lstrip("#")[index : index + 2], 16) for index in (0, 2, 4)),
            hex_to_rgb(PAPER),
            strict=True,
        )
    )
    add_soft_shape(canvas, (646, 78, 1176, 575), (86, 68, 57, 38), 24)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((640, 65, 1170, 565), radius=78, fill=(*panel_rgb, 240), outline="#ffffff", width=2)
    artwork = load_macaron(str(project["asset"]), 440)
    paste_with_shadow(canvas, artwork, (685, 95))
    draw_text_block(
        canvas,
        language,
        str(locale["category"]),
        str(locale["heading"]),
        site_locale,
        PROJECT_HEADING_LINES[str(project["slug"])][language],
    )
    return canvas.convert("RGB")


def generate_home_card(content: dict[str, object], language: str) -> Image.Image:
    site_locale = content["site"]["locales"][language]
    canvas = Image.new("RGBA", CANVAS_SIZE, PAPER)
    add_soft_shape(canvas, (586, 79, 1176, 575), (86, 68, 57, 42), 24)
    product_source = Image.open(HOME_PRODUCT_SHOT).convert("RGB")
    target_ratio = HOME_PANEL_SIZE[0] / HOME_PANEL_SIZE[1]
    crop_width = product_source.width
    crop_height = round(crop_width / target_ratio)
    crop_top = min(
        max(
            0,
            round((product_source.height - crop_height) / 2 + product_source.height * 0.02),
        ),
        product_source.height - crop_height,
    )
    product_crop = product_source.crop(
        (0, crop_top, crop_width, crop_top + crop_height)
    )
    product_shot = product_crop.resize(HOME_PANEL_SIZE, Image.Resampling.LANCZOS)
    product_shot_rgba = product_shot.convert("RGBA")
    mask = Image.new("L", product_shot_rgba.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, HOME_PANEL_SIZE[0] - 1, HOME_PANEL_SIZE[1] - 1),
        radius=HOME_PANEL_RADIUS,
        fill=255,
    )
    product_shot_rgba.putalpha(mask)
    canvas.alpha_composite(product_shot_rgba, HOME_PANEL_BOX[:2])
    ImageDraw.Draw(canvas).rounded_rectangle(
        HOME_PANEL_BOX,
        radius=HOME_PANEL_RADIUS,
        outline="#ffffff",
        width=2,
    )

    heading_lines = (
        ["想從哪顆", "開始吃呢？"]
        if language == "zh"
        else ["Which one will", "you try first?"]
    )

    draw_text_block(
        canvas,
        language,
        str(site_locale["category"]),
        str(site_locale["heading"]),
        site_locale,
        heading_lines,
    )
    return canvas.convert("RGB")


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all",
        action="store_true",
        help="Also generate the ten project-specific previews for each language.",
    )
    args = parser.parse_args()
    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    expected_assets = [ROOT / project["asset"] for project in content["projects"]]
    missing_assets = [str(path.relative_to(ROOT)) for path in expected_assets if not path.is_file()]
    if missing_assets:
        raise FileNotFoundError(f"Missing social preview assets: {', '.join(missing_assets)}")
    if not HOME_PRODUCT_SHOT.is_file():
        raise FileNotFoundError(f"Missing homepage product shot: {HOME_PRODUCT_SHOT.relative_to(ROOT)}")

    for language in ("zh", "en"):
        output_directory = OUTPUT_ROOT / language
        output_directory.mkdir(parents=True, exist_ok=True)
        generate_home_card(content, language).save(output_directory / "home.png", optimize=True)
        if args.all:
            site_locale = content["site"]["locales"][language]
            for project in content["projects"]:
                card = generate_project_card(project, language, site_locale)
                card.save(output_directory / f"{project['slug']}.png", optimize=True)

    count = 22 if args.all else 2
    print(f"Generated {count} localized social previews in {OUTPUT_ROOT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
