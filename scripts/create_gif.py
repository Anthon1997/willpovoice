from __future__ import annotations

import colorsys
from pathlib import Path

from PIL import Image, ImageDraw

OUTPUT = Path("assets") / "icons" / "palette.gif"

SIZE = 32
FRAMES = 12


def to_palette(img: Image.Image) -> Image.Image:
    alpha = img.split()[3]
    p = img.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
    mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
    p.paste(255, mask)
    return p


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    frames = []

    for i in range(FRAMES):
        hue = i / FRAMES
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
        color = (int(r * 255), int(g * 255), int(b * 255), 255)

        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.ellipse([2, 2, SIZE - 3, SIZE - 3], fill=color)
        draw.ellipse(
            [SIZE // 3, SIZE // 3, SIZE // 3 + 7, SIZE // 3 + 7],
            fill=(255, 255, 255, 110),
        )

        frames.append(to_palette(img))

    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        transparency=255,
        disposal=2,
    )

    print(f"GIF creado en: {OUTPUT}")


if __name__ == "__main__":
    main()
