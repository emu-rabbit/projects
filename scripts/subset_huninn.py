"""Build the site's small, renamed Huninn-derived WOFF2 subset."""

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
TEXT_SOURCES = (
    ROOT / "index.html",
    *sorted((ROOT / "src").rglob("*.vue")),
    *sorted((ROOT / "src/data").rglob("*.ts")),
)
FAMILY_NAME = "Emu Portfolio Round"
POSTSCRIPT_NAME = "EmuPortfolioRound-Regular"


def collect_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in TEXT_SOURCES)


def rename_subset(font: TTFont) -> None:
    name_table = font["name"]
    for name_id in (1, 2, 3, 4, 6):
        name_table.removeNames(nameID=name_id)

    values = {
        1: FAMILY_NAME,
        2: "Regular",
        3: f"{FAMILY_NAME} Regular 1.0",
        4: FAMILY_NAME,
        6: POSTSCRIPT_NAME,
    }
    for name_id, value in values.items():
        name_table.setName(value, name_id, 3, 1, 0x409)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("font", type=Path, help="Path to jf open 粉圓 2.1 TTF")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "assets/fonts/emu-portfolio-round-subset.woff2",
    )
    args = parser.parse_args()

    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
    options.name_languages = ["*"]
    options.recommended_glyphs = True
    options.notdef_glyph = True
    options.notdef_outline = True

    font = TTFont(args.font)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=collect_text())
    subsetter.subset(font)
    rename_subset(font)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    font.flavor = "woff2"
    font.save(args.out)


if __name__ == "__main__":
    main()
