"""Render a Meetup banner with one speaker and a three-person panel."""

import argparse
import datetime
import re
from pathlib import Path

import yaml
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SCALE = 2
SIZE = (1200, 675)
WHITE = "#FFFFFF"
MUTED = "#E0CBED"
ACCENT = "#B575DD"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
PORTRAIT_CROPS = {
    "piotr-gankiewicz": (0.10, 0, 0.90, 0.80),
    "lukasz-olbromski": (0.125, 0, 0.825, 0.70),
    "lukasz-pyrzyk": (0.10, 0, 0.80, 0.70),
}


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def local_image(path):
    source = ROOT / path.lstrip("/")
    with Image.open(source) as image:
        return ImageOps.exif_transpose(image).convert("RGBA")


def banner_logo():
    logo = local_image("/assets/images/logo.png")
    mask_scale = 8
    mask = Image.new("L", (logo.width * mask_scale, logo.height * mask_scale), 0)
    # The source's outermost pixels contain a white matte; trim only that rim.
    bounds = tuple(value * mask_scale for value in (2, 2, logo.width - 3, logo.height - 3))
    ImageDraw.Draw(mask).ellipse(bounds, fill=255)
    mask = mask.resize(logo.size, Image.Resampling.BOX)
    logo.putalpha(ImageChops.multiply(logo.getchannel("A"), mask))
    return logo


def render(post_path, background_path, output_path):
    match = re.fullmatch(r"\d{4}-\d{2}-\d{2}-(\d+)-spotkanie-.*\.md", post_path.name)
    if not match:
        raise ValueError("Expected a numbered meeting post filename")
    number = match.group(1)
    sections = post_path.read_text(encoding="utf-8").split("---", 2)
    if len(sections) != 3 or sections[0].strip():
        raise ValueError("Post must start with YAML front matter")
    post = yaml.safe_load(sections[1])
    talks = post["talks"]
    if len(talks) != 2 or len(talks[0]["speaker_ids"]) != 1 or len(talks[1]["speaker_ids"]) != 3:
        raise ValueError("This layout requires one solo talk and one three-person panel")
    speakers = {person["id"]: person for person in load_yaml(ROOT / "_data/speakers.yml")}
    venue = load_yaml(ROOT / "_data/location.yml")["venue"]
    partners = load_yaml(ROOT / "_data/partners.yml")
    partner_list = partners["strategic"] + partners["supporting"]
    if len(partners["strategic"]) != 1 or len(partners["supporting"]) != 2:
        raise ValueError("This layout requires one strategic and two supporting partner logos")
    date = post["date"]
    if not isinstance(date, datetime.date):
        date = datetime.date.fromisoformat(date)
    time = datetime.time.fromisoformat(post["time"])

    with Image.open(background_path) as background:
        canvas = ImageOps.fit(
            background.convert("RGB"),
            (SIZE[0] * SCALE, SIZE[1] * SCALE),
            Image.Resampling.LANCZOS,
            centering=(0.5, 0.65),
        ).convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (25, 9, 42, 70))
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    def font(size, bold=False):
        return ImageFont.truetype(
            str(FONT_DIR / ("Arial Bold.ttf" if bold else "Arial.ttf")), size * SCALE
        )

    def text(value, x, y, size, fill=WHITE, bold=False, max_width=None):
        face = font(size, bold)
        bounds = draw.textbbox((0, 0), value, font=face, anchor="lt")
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        if max_width is not None and width > max_width * SCALE:
            raise ValueError(f"Text is too wide for its column: {value}")
        if x < 0 or y < 0 or x * SCALE + width > canvas.width or y * SCALE + height > canvas.height:
            raise ValueError(f"Text extends beyond the banner: {value}")
        draw.text((x * SCALE, y * SCALE), value, font=face, fill=fill, anchor="lt")

    def paragraph(value, x, y, size, width, max_lines, bold=False, fill=WHITE):
        lines = []
        line = ""
        for word in value.split():
            candidate = f"{line} {word}".strip()
            if line and draw.textlength(candidate, font=font(size, bold)) > width * SCALE:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        if len(lines) > max_lines:
            raise ValueError(f"Text needs more than {max_lines} lines: {value}")
        for index, line in enumerate(lines):
            text(line, x, y + index * (size + 7), size, fill, bold, width)

    def paste(image, x, y, width, height):
        image = ImageOps.contain(image, (width * SCALE, height * SCALE), Image.Resampling.LANCZOS)
        canvas.alpha_composite(image, (round(x * SCALE), round(y * SCALE)))

    def portrait(speaker_id, x, y, diameter):
        person = speakers[speaker_id]
        if not person.get("photo"):
            raise ValueError(f"Missing photo for {speaker_id}")
        image = local_image(person["photo"])
        crop = PORTRAIT_CROPS.get(speaker_id)
        if crop is not None:
            image = image.crop(tuple(round(v * image.size[i % 2]) for i, v in enumerate(crop)))
        image = ImageOps.fit(image, (diameter * SCALE, diameter * SCALE), Image.Resampling.LANCZOS)
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, image.width - 1, image.height - 1), fill=255)
        image.putalpha(mask)
        draw.ellipse(
            (x * SCALE - 3, y * SCALE - 3, (x + diameter) * SCALE + 3, (y + diameter) * SCALE + 3),
            fill=ACCENT,
        )
        canvas.alpha_composite(image, (x * SCALE, y * SCALE))

    paste(banner_logo(), 42, 62, 185, 185)
    draw.rectangle((126 * SCALE, 252 * SCALE, 263 * SCALE, 340 * SCALE), outline="#7542AA", width=3 * SCALE)
    text(number, 144, 269, 57, bold=True, max_width=112)
    text("spotkanie", 282, 251, 42, max_width=290)
    text("Wroc.NET", 282, 300, 42, max_width=290)
    text(f"{date:%d.%m.%Y} | {time:%H:%M}", 126, 372, 27, max_width=435)
    draw.line((126 * SCALE, 420 * SCALE, 556 * SCALE, 420 * SCALE), fill="#7542AA", width=2 * SCALE)
    text(f'{venue["name"]}, Wrocław', 126, 442, 25, max_width=435)

    solo_id = talks[0]["speaker_ids"][0]
    solo = speakers[solo_id]
    portrait(solo_id, 622, 87, 132)
    text(f'{solo["imie"]} {solo["nazwisko"]}', 782, 100, 31, bold=True, max_width=375)
    paragraph(talks[0]["title"], 782, 151, 26, 370, 3)

    text("PANEL DYSKUSYJNY", 622, 315, 23, ACCENT, True, 535)
    paragraph(talks[1]["title"], 622, 357, 29, 535, 2, bold=True)
    for index, speaker_id in enumerate(talks[1]["speaker_ids"]):
        person = speakers[speaker_id]
        x = 632 + index * 181
        portrait(speaker_id, x + 20, 470, 110)
        for line_index, value in enumerate((person["imie"], person["nazwisko"])):
            width = draw.textlength(value, font=font(20, True)) / SCALE
            text(value, x + 75 - width / 2, 598 + line_index * 25, 20, bold=True, max_width=160)

    partner_positions = ((341, 538, 300, 64), (263, 610, 100, 36), (407, 610, 125, 36))
    for partner, (center_x, center_y, width, height) in zip(partner_list, partner_positions):
        logo = local_image(partner["logo"])
        if partner["name"] == "devstyle":
            white_logo = Image.new("RGBA", logo.size, WHITE)
            white_logo.putalpha(logo.getchannel("A"))
            logo = white_logo
        if partner["name"] == "hued.me":
            # This PNG has opaque, near-black padding rather than transparency.
            background = Image.new("RGB", logo.size, logo.getpixel((0, 0))[:3])
            difference = ImageChops.difference(logo.convert("RGB"), background).convert("L")
            logo.putalpha(difference.point(lambda value: 255 if value > 3 else 0))
        bounds = logo.getbbox()
        if bounds is None:
            raise ValueError(f'Empty partner logo: {partner["name"]}')
        logo = logo.crop(bounds)
        fitted = ImageOps.contain(logo, (width * SCALE, height * SCALE), Image.Resampling.LANCZOS)
        canvas.alpha_composite(
            fitted,
            (round(center_x * SCALE - fitted.width / 2), round(center_y * SCALE - fitted.height / 2)),
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").resize(SIZE, Image.Resampling.LANCZOS).save(
        output_path, format="JPEG", quality=95, subsampling=0
    )
    print(f"Saved {output_path} ({SIZE[0]}x{SIZE[1]}, JPEG RGB)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("post", type=Path)
    parser.add_argument("--background", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    render(args.post, args.background, args.output)
