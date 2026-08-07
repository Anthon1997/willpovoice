from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUTPUT = Path("assets") / "icons" / "spectrum.gif"

W, H = 132, 64
BARS = 12
FRAMES = 16

BAR_COLOR = (255, 255, 255, 255)


def to_palette(img: Image.Image) -> Image.Image:
    alpha = img.split()[3]
    p = img.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
    mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
    p.paste(255, mask)
    return p


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    frames = []

    for f in range(FRAMES):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        t = (f / FRAMES) * 2 * math.pi
        slot = (W - 8) / BARS
        bar_w = slot * 0.6

        for i in range(BARS):
            wave = abs(math.sin(t + i * 0.8))
            wave2 = 0.6 + 0.4 * math.sin(t * 2 + i * 1.7)
            h_norm = 0.15 + 0.85 * wave * wave2
            bar_h = max(4, int(h_norm * (H - 8)))

            x0 = 4 + i * slot + (slot - bar_w) / 2
            y0 = H - 4 - bar_h

            draw.rounded_rectangle(
                [x0, y0, x0 + bar_w, y0 + bar_h],
                radius=max(1, int(bar_w // 2)),
                fill=BAR_COLOR,
            )

        frames.append(to_palette(img))

    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
        transparency=255,
        disposal=2,
    )

    print(f"Espectro creado en: {OUTPUT}")


if __name__ == "__main__":
    main()
