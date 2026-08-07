from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUTPUT_DIR = Path("assets") / "icons"

S = 32
ORANGE = (255, 106, 0, 255)
YELLOW = (255, 200, 0, 255)

FRAMES = [
    {"tip": [(16, 2), (9, 14), (23, 14)], "inner": [12, 17, 20, 27]},
    {"tip": [(16, 5), (9, 14), (23, 14)], "inner": [12, 19, 20, 28]},
    {"tip": [(16, 3), (10, 14), (22, 14)], "inner": [13, 18, 19, 27]},
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, frame in enumerate(FRAMES):
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        d.polygon(frame["tip"], fill=ORANGE)
        d.ellipse([8, 12, 24, 28], fill=ORANGE)
        d.ellipse(frame["inner"], fill=YELLOW)

        img.save(OUTPUT_DIR / f"fire_{i}.png")

    print("Fotogramas de fuego creados: fire_0.png, fire_1.png, fire_2.png")


if __name__ == "__main__":
    main()
