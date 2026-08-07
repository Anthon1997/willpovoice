from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUTPUT_DIR = Path("assets") / "icons"

DOTS = {
    "dot_es": (46, 160, 67),
    "dot_desktop": (31, 111, 235),
    "dot_en": (140, 140, 150),
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, rgb in DOTS.items():
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        d.ellipse([6, 6, 26, 26], fill=(*rgb, 255))
        d.ellipse([10, 9, 17, 16], fill=(255, 255, 255, 110))

        img.save(OUTPUT_DIR / f"{name}.png")

    print("Puntos de color creados: dot_es, dot_desktop, dot_en")


if __name__ == "__main__":
    main()
