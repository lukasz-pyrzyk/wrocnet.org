"""Render the default share image (og:image) for pages without their own banner."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from generate_meetup_banner import ROOT, banner_logo


SCALE = 2
SIZE = (1200, 630)
WHITE = "#FFFFFF"
MUTED = "#E0CBED"
ACCENT = "#B575DD"
LINE = "#7542AA"
DARK = (16, 9, 35)
# macOS (as in generate_meetup_banner.py) first, then Windows.
FONTS = (
    (Path("/System/Library/Fonts/Supplemental"), "Arial.ttf", "Arial Bold.ttf"),
    (Path("C:/Windows/Fonts"), "arial.ttf", "arialbd.ttf"),
)
# WhatsApp and some other previews crop the image to a centred square,
# so everything that matters has to fit in the middle 630 px.
SQUARE = SIZE[1]


def font(size, bold=False):
    for directory, regular, heavy in FONTS:
        path = directory / (heavy if bold else regular)
        if path.exists():
            return ImageFont.truetype(str(path), size * SCALE)
    raise FileNotFoundError("Arial / Arial Bold not found")


def render(background_path, output_path):
    with Image.open(background_path) as background:
        canvas = ImageOps.fit(
            ImageOps.exif_transpose(background).convert("RGB"),
            (SIZE[0] * SCALE, SIZE[1] * SCALE),
            Image.Resampling.LANCZOS,
            centering=(0.5, 0.75),
        ).convert("RGBA")
    canvas = Image.alpha_composite(canvas, Image.new("RGBA", canvas.size, (*DARK, 110)))

    # Soft dark patch behind the text, so the bridge does not run through it.
    shade = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shade).ellipse((260 * SCALE, 250 * SCALE, 940 * SCALE, 620 * SCALE), fill=(*DARK, 170))
    canvas = Image.alpha_composite(canvas, shade.filter(ImageFilter.GaussianBlur(60 * SCALE)))

    logo_size, logo_top = 210, 62
    left = (SIZE[0] - logo_size) / 2
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        ((left - 14) * SCALE, (logo_top - 14) * SCALE, (left + logo_size + 14) * SCALE, (logo_top + logo_size + 14) * SCALE),
        fill=(181, 117, 221, 110),
    )
    canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(22 * SCALE)))
    logo = banner_logo().resize((logo_size * SCALE, logo_size * SCALE), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, (round(left * SCALE), logo_top * SCALE))

    draw = ImageDraw.Draw(canvas)

    def centred(value, y, size, fill=WHITE, bold=False):
        face = font(size, bold)
        width = draw.textlength(value, font=face) / SCALE
        if width > SQUARE - 60:
            raise ValueError(f"Text does not fit the square crop: {value}")
        draw.text(((SIZE[0] - width) / 2 * SCALE, y * SCALE), value, font=face, fill=fill, anchor="lt")

    centred("Wroc.NET", 300, 84, bold=True)
    centred("Wrocławska Grupa .NET", 398, 36, MUTED)
    draw.line(((SIZE[0] / 2 - 150) * SCALE, 462 * SCALE, (SIZE[0] / 2 + 150) * SCALE, 462 * SCALE), fill=LINE, width=2 * SCALE)
    centred("Otwarte, bezpłatne spotkania od 2007 roku", 484, 28, MUTED)
    centred("wrocnet.org", 548, 26, ACCENT, bold=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").resize(SIZE, Image.Resampling.LANCZOS).save(
        output_path, format="JPEG", quality=92, subsampling=0, optimize=True
    )
    print(f"Saved {output_path} ({SIZE[0]}x{SIZE[1]}, JPEG RGB)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--background", type=Path, default=ROOT / "assets/images/home-wroclaw.webp")
    parser.add_argument("--output", type=Path, default=ROOT / "assets/images/og-default.jpg")
    args = parser.parse_args()
    render(args.background, args.output)
