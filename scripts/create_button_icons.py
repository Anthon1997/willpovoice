from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ICONS = Path("assets") / "icons"
S = 32
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def new_img():
    return Image.new("RGBA", (S, S), CLEAR)


def play():
    img = new_img()
    d = ImageDraw.Draw(img)
    d.polygon([(10, 7), (25, 16), (10, 25)], fill=WHITE)
    return img


def pause():
    img = new_img()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([9, 7, 13, 25], radius=2, fill=WHITE)
    d.rounded_rectangle([19, 7, 23, 25], radius=2, fill=WHITE)
    return img


def save():
    img = new_img()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, 26, 26], radius=3, fill=WHITE)
    d.rectangle([17, 6, 23, 13], fill=CLEAR)
    d.rectangle([10, 17, 22, 26], fill=CLEAR)
    d.rectangle([19, 7, 21, 11], fill=WHITE)
    return img


def folder():
    img = new_img()
    d = ImageDraw.Draw(img)
    d.polygon([(5, 9), (12, 9), (14, 12), (27, 12), (27, 24), (5, 24)], fill=WHITE)
    return img


def theme():
    img = new_img()
    d = ImageDraw.Draw(img)
    d.ellipse([7, 7, 25, 25], fill=WHITE)
    d.ellipse([13, 5, 31, 23], fill=CLEAR)
    return img


def exit_icon():
    img = new_img()
    d = ImageDraw.Draw(img)
    d.arc([8, 8, 24, 24], 300, 240, fill=WHITE, width=3)
    d.line([16, 4, 16, 14], fill=WHITE, width=3)
    return img


def main():
    ICONS.mkdir(parents=True, exist_ok=True)
    play().save(ICONS / "play.png")
    pause().save(ICONS / "pause.png")
    save().save(ICONS / "save.png")
    folder().save(ICONS / "folder.png")
    theme().save(ICONS / "theme.png")
    exit_icon().save(ICONS / "exit.png")
    print("Iconos de botones creados.")


if __name__ == "__main__":
    main()
