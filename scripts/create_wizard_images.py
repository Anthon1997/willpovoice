from __future__ import annotations

from pathlib import Path

from PIL import Image

ICONS = Path("assets") / "icons"
LOGO = ICONS / "logo.png"

NAVY = (0, 31, 63)


def base_logo(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (*NAVY, 255))

    if LOGO.exists():
        src = Image.open(LOGO).convert("RGBA")
        ratio = min((size * 0.8) / src.width, (size * 0.8) / src.height)
        w = max(1, int(src.width * ratio))
        h = max(1, int(src.height * ratio))
        logo = src.resize((w, h), Image.LANCZOS)
        img.paste(logo, ((size - w) // 2, (size - h) // 2), logo)

    return img


def fit_canvas(w: int, h: int) -> Image.Image:
    canvas = Image.new("RGB", (w, h), NAVY)
    logo = base_logo(min(w, h))
    x = (w - logo.width) // 2
    y = (h - logo.height) // 2
    canvas.paste(logo.convert("RGB"), (x, y))
    return canvas


def main() -> None:
    ICONS.mkdir(parents=True, exist_ok=True)
    fit_canvas(164, 314).save(ICONS / "wizard.bmp")
    fit_canvas(55, 58).save(ICONS / "wizard_small.bmp")
    print("Imagenes del asistente creadas.")


if __name__ == "__main__":
    main()
