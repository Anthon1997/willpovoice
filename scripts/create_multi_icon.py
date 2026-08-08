from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUTPUT_DIR = Path("assets") / "icons"

BLUE = (31, 111, 235, 255)
GREEN = (46, 160, 67, 255)
WHITE = (255, 255, 255, 200)
ORANGE = (255, 106, 0, 255)
YELLOW = (255, 200, 0, 255)

FRAMES = [
    {"tip": [(24, 1), (20, 8), (28, 8)], "inner": [22, 6, 26, 12]},
    {"tip": [(24, 3), (20, 8), (28, 8)], "inner": [22, 7, 26, 13]},
    {"tip": [(24, 2), (21, 8), (27, 8)], "inner": [22, 6, 26, 12]},
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, frame in enumerate(FRAMES):
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        d.ellipse([3, 7, 25, 29], fill=BLUE)
        d.ellipse([7, 11, 13, 17], fill=GREEN)
        d.ellipse([14, 18, 21, 25], fill=GREEN)
        d.ellipse([3, 7, 25, 29], outline=WHITE, width=1)
        d.line([3, 18, 25, 18], fill=WHITE, width=1)
        d.ellipse([9, 7, 19, 29], outline=WHITE, width=1)

        d.polygon(frame["tip"], fill=ORANGE)
        d.ellipse([20, 6, 28, 14], fill=ORANGE)
        d.ellipse(frame["inner"], fill=YELLOW)

        img.save(OUTPUT_DIR / f"multi_{i}.png")

    print("Iconos globo+fuego creados: multi_0, multi_1, multi_2")


if __name__ == "__main__":
    main()
