"""Render a Meetup banner from a meeting post.

The banner has a fixed left column (logo, issue number, date, venue, partner
logos). Only the right column changes with the talk layout, and the script
detects which layout a post uses:

- ``solo_panel`` - talks[0] has one speaker, talks[1] has three (the 172 shape).
- ``two_talks`` - one solo talk and one two-speaker talk, in either order (173).

The two_talks layout preserves the post's order, with equal title sizes and
equal-height regions for both talks. Sessions sit directly on the shared
background, without rectangular frames or solid panels, as in banner 172.
All text must remain at least 10 px at a 358 px preview width. Missing portraits
use a text-only speaker block, never a placeholder silhouette. The legacy
solo_panel composition is preserved.

Anything else raises rather than guessing. Portraits are cropped per speaker
where a manual crop is registered in PORTRAIT_CROPS; square headshots need none
because ImageOps.fit centres them.

Requires Python 3, Pillow and PyYAML.
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
PREVIEW_WIDTH = 358
MIN_PREVIEW_FONT = 10

# Arial where it exists (macOS, as the 172 banner was made); Liberation Sans
# otherwise. The two are metric-compatible, so the composition is unchanged.
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

PORTRAIT_CROPS = {
    "piotr-gankiewicz": (0.10, 0, 0.90, 0.80),
    "lukasz-olbromski": (0.125, 0, 0.825, 0.70),
    "lukasz-pyrzyk": (0.10, 0, 0.80, 0.70),
}

PARTNER_POSITIONS = (
    (341, 506, 300, 58),
    (180, 600, 96, 96),
    (320, 571, 137, 38),
    (481, 571, 137, 38),
    (320, 629, 137, 38),
    (481, 629, 137, 38),
)


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
    # The source's outermost pixels contain a white matte; trim only that rim.
    bounds = tuple(value * mask_scale for value in (2, 2, logo.width - 3, logo.height - 3))
    ImageDraw.Draw(mask).ellipse(bounds, fill=255)
    mask = mask.resize(logo.size, Image.Resampling.BOX)
    logo.putalpha(ImageChops.multiply(logo.getchannel("A"), mask))
    return logo


def detect_layout(talks):
    """Return the layout name for a post's talks, or raise if unsupported."""
    if len(talks) != 2:
        raise ValueError("Expected exactly two talks")
    first = len(talks[0]["speaker_ids"])
    second = len(talks[1]["speaker_ids"])
    if first == 1 and second == 3:
        return "solo_panel"
    if (first, second) in ((1, 2), (2, 1)):
        return "two_talks"
    raise ValueError(
        "Unsupported talk layout: expected one solo talk plus a three-person "
        f"panel, or a solo and a two-speaker talk in either order (got {first} and {second})"
    )


def validate_mobile_text(size):
    preview_size = size * PREVIEW_WIDTH / SIZE[0]
    if preview_size < MIN_PREVIEW_FONT:
        raise ValueError(
            f"Text would render at {preview_size:.1f} px in a {PREVIEW_WIDTH} px "
            f"preview; minimum is {MIN_PREVIEW_FONT} px. Change the layout, not the font size."
        )


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
    layout = detect_layout(talks)
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
        if layout == "two_talks":
            validate_mobile_text(size)
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
        if not person.get("photo") or Path(person["photo"]).stem == "placeholder":
            raise ValueError(f"No real portrait for {speaker_id}; use a text-only speaker block")
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

    def speaker_block(speaker_id, x, y, width, split_name=False):
        person = speakers[speaker_id]
        photo = person.get("photo")
        if photo and Path(photo).stem != "placeholder":
            portrait(speaker_id, x, y, 76)
            x += 92
            width -= 92
        else:
            print(f"No portrait for {speaker_id}; rendering a text-only speaker block")
        if split_name:
            text(person["imie"], x, y + 4, 34, MUTED, max_width=width)
            text(person["nazwisko"], x, y + 45, 34, MUTED, max_width=width)
        else:
            paragraph(f'{person["imie"]} {person["nazwisko"]}', x, y + 18, 34, width, 2, fill=MUTED)

    # Left column: issue number, date, venue.
    paste(banner_logo(), 42, 62, 185, 185)
    draw.rectangle((126 * SCALE, 252 * SCALE, 263 * SCALE, 340 * SCALE), outline="#7542AA", width=3 * SCALE)
    text(number, 144, 269, 57, bold=True, max_width=112)
    text("spotkanie", 282, 251, 42, max_width=290)
    text("Wroc.NET", 282, 300, 42, max_width=290)
    text(f"{date:%d.%m.%Y} | {time:%H:%M}", 126, 372, 34 if layout == "two_talks" else 27, max_width=435)
    draw.line((126 * SCALE, 420 * SCALE, 556 * SCALE, 420 * SCALE), fill="#7542AA", width=2 * SCALE)
    text(
        f'{venue["name"]}, Wrocław',
        126,
        432 if layout == "two_talks" else 442,
        34 if layout == "two_talks" else 25,
        max_width=435,
    )

    if layout == "solo_panel":
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
    else:
        for talk, top in zip(talks, (56, 346)):
            paragraph(talk["title"], 622, top + 24, 34, 530, 2, bold=True)
            ids = talk["speaker_ids"]
            if len(ids) == 2:
                for index, speaker_id in enumerate(ids):
                    speaker_block(speaker_id, 622 + index * 274, top + 144, 256, split_name=True)
            else:
                speaker_block(ids[0], 622, top + 144, 530)

    for partner, (center_x, center_y, width, height) in zip(partner_list, PARTNER_POSITIONS):
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
    print(f"Saved {output_path} ({SIZE[0]}x{SIZE[1]}, JPEG RGB, {layout})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("post", type=Path)
    parser.add_argument("--background", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    render(args.post, args.background, args.output)