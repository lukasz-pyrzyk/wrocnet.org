"""Render a Meetup banner for a meetup with one two-speaker talk and one solo talk.

This is the 173 layout, derived from generate_meetup_banner.py (which handles
"one solo talk + three-person panel"). Differences:

- Talk layout: talks[0] has TWO speakers, talks[1] has ONE. The two-speaker talk
  gets the prominent slot on the right, the solo talk the lower band.
- Fonts: falls back to Liberation Sans (metrically compatible with Arial, full
  Polish coverage) because this host has no Arial. Arial is used when present,
  so the output still matches the 172 banner on the machine that produced it.
- Portrait crops: per-speaker crops removed for the new speakers; ImageOps.fit
  centres them, which is correct for the square headshots we received.
"""

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

# Prefer the real Arial when this runs on macOS (as the 172 banner did); fall
# back to Liberation Sans elsewhere. Both are metric-compatible.
FONT_CANDIDATES = {
    False: [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/opt/data/libreoffice/opt/libreoffice26.2/share/fonts/truetype/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    ],
    True: [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/opt/data/libreoffice/opt/libreoffice26.2/share/fonts/truetype/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ],
}

PORTRAIT_CROPS = {}


def resolve_font(bold):
    for candidate in FONT_CANDIDATES[bold]:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"No usable font found for bold={bold}")


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
    if len(talks) != 2 or len(talks[0]["speaker_ids"]) != 2 or len(talks[1]["speaker_ids"]) != 1:
        raise ValueError("This layout requires one two-speaker talk and one solo talk")
    speakers = {person["id"]: person for person in load_yaml(ROOT / "_data/speakers.yml")}
    venue = load_yaml(ROOT / "_data/location.yml")["venue"]
    partners = load_yaml(ROOT / "_data/partners.yml")
    partner_list = partners["strategic"] + partners["supporting"]
    if len(partners["strategic"]) != 1 or len(partners["supporting"]) != 5:
        raise ValueError("This layout requires one strategic and five supporting partner logos")
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
        return ImageFont.truetype(str(resolve_font(bold)), size * SCALE)

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

    # Left column: issue number, date, venue.
    paste(banner_logo(), 42, 62, 185, 185)
    draw.rectangle((126 * SCALE, 252 * SCALE, 263 * SCALE, 340 * SCALE), outline="#7542AA", width=3 * SCALE)
    text(number, 144, 269, 57, bold=True, max_width=112)
    text("spotkanie", 282, 251, 42, max_width=290)
    text("Wroc.NET", 282, 300, 42, max_width=290)
    text(f"{date:%d.%m.%Y} | {time:%H:%M}", 126, 372, 27, max_width=435)
    draw.line((126 * SCALE, 420 * SCALE, 556 * SCALE, 420 * SCALE), fill="#7542AA", width=2 * SCALE)
    text(f'{venue["name"]}, Wrocław', 126, 442, 25, max_width=435)

    # Right column, upper band: the two-speaker talk (the headline session).
    # Two portraits side by side; captions sit under each portrait and are
    # clamped to the portrait slot so the names cannot collide.
    duo_ids = talks[0]["speaker_ids"]
    # Captions measured: "Hleb Sukrystsik" is ~150 px at size 20, so the slot
    # must be wider than that or the two names overlap, which an earlier pass did.
    duo_slot = 205
    for index, speaker_id in enumerate(duo_ids):
        person = speakers[speaker_id]
        slot_x = 620 + index * duo_slot
        portrait(speaker_id, slot_x, 80, 132)
        caption = f'{person["imie"]} {person["nazwisko"]}'
        # Captions can be wider than the 132 px portrait; centre on the portrait
        # and let it extend slightly, but never into the neighbouring slot.
        width = draw.textlength(caption, font=font(20, True)) / SCALE
        text(
            caption,
            slot_x + 66 - width / 2,
            224,
            20,
            bold=True,
            max_width=duo_slot,
        )
    paragraph(talks[0]["title"], 622, 262, 27, 540, 3, bold=True)

    # Lower band: the solo talk.
    solo_id = talks[1]["speaker_ids"][0]
    solo = speakers[solo_id]
    portrait(solo_id, 622, 420, 110)
    text(f'{solo["imie"]} {solo["nazwisko"]}', 748, 432, 24, bold=True, max_width=400)
    paragraph(talks[1]["title"], 748, 468, 22, 415, 3)

    partner_positions = (
        (341, 506, 300, 58),
        (180, 600, 96, 96),
        (320, 571, 137, 38),
        (481, 571, 137, 38),
        (320, 629, 137, 38),
        (481, 629, 137, 38),
    )
    for partner, (center_x, center_y, width, height) in zip(partner_list, partner_positions):
        logo = local_image(partner["logo"])
        if partner in partners["strategic"]:
            white_logo = Image.new("RGBA", logo.size, WHITE)
            white_logo.putalpha(logo.getchannel("A"))
            logo = white_logo
        else:
            draw.rounded_rectangle(
                (
                    (center_x - width / 2 - 6) * SCALE,
                    (center_y - height / 2 - 6) * SCALE,
                    (center_x + width / 2 + 6) * SCALE,
                    (center_y + height / 2 + 6) * SCALE,
                ),
                radius=4 * SCALE,
                fill=WHITE,
            )
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