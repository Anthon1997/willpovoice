from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ICONS_DIR = Path("assets") / "icons"
SOURCE = ICONS_DIR / "logo.png"
OUTPUT = ICONS_DIR / "icon.ico"

SIZES = [16, 32, 48, 64, 128, 256]

# Color corporativo: AZUL MARINO
# Cambia estos valores al RGB exacto de tu marca si lo conoces.
# Ejemplos de azul marino:
#   #001F3F -> (0, 31, 63)
#   #0A2342 -> (10, 35, 66)
#   #14213D -> (20, 33, 61)
NAVY = (0, 31, 63)

ROUNDED = True        # esquinas redondeadas
TRANSPARENT = False   # True si prefieres fondo transparente en vez de azul marino


def draw_wave(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=max(2, size // 5),
        fill=(*NAVY, 255),
    )

    bar_heights = [0.25, 0.5, 0.8, 0.5, 0.25]
    n = len(bar_heights)
    margin = size * 0.18
    usable = size - 2 * margin
    gap = usable / n
    bar_width = gap * 0.5

    for i, h in enumerate(bar_heights):
        bar_h = size * h * 0.7
        x0 = margin + i * gap + (gap - bar_width) / 2
        y0 = (size - bar_h) / 2

        draw.rounded_rectangle(
            [x0, y0, x0 + bar_width, y0 + bar_h],
            radius=max(1, int(bar_width // 2)),
            fill=(255, 255, 255, 255),
        )

    return img


def fit_logo(src: Image.Image, size: int) -> Image.Image:
    if TRANSPARENT:
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    else:
        canvas = Image.new("RGBA", (size, size), (*NAVY, 255))

        if ROUNDED:
            mask = Image.new("L", (size, size), 0)
            d = ImageDraw.Draw(mask)
            d.rounded_rectangle(
                [0, 0, size - 1, size - 1],
                radius=max(2, size // 5),
                fill=255,
            )
            canvas.putalpha(mask)

    ratio = min((size * 0.78) / src.width, (size * 0.78) / src.height)
    w = max(1, int(src.width * ratio))
    h = max(1, int(src.height * ratio))

    logo = src.resize((w, h), Image.LANCZOS)

    canvas.paste(logo, ((size - w) // 2, (size - h) // 2), logo)

    return canvas


def main() -> None:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    if SOURCE.exists():
        print(f"Usando imagen de marca: {SOURCE}")
        src = Image.open(SOURCE).convert("RGBA")
        images = [fit_logo(src, s) for s in SIZES]
    else:
        print("No se encontro logo.png, usando diseno de onda.")
        images = [draw_wave(s) for s in SIZES]

    images[-1].save(
        OUTPUT,
        format="ICO",
        append_images=images[:-1],
    )

    print(f"Icono creado en: {OUTPUT}")


if __name__ == "__main__":
    main()
