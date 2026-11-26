"""Render a Meetup banner from a meeting post.

The banner has a fixed left column (logo, issue number, date, venue, partner
logos). Only the right column changes with the talk layout, and the script
detects which layout a post uses:

- ``solo_panel`` - talks[0] has one speaker, talks[1] has three (the 172 shape).
- ``two_talks`` - two solo talks, or a solo and a two-speaker talk in either order (173).

The two_talks layout preserves the post's order, with equal title sizes (an optional ``banner_title`` on a talk replaces a title too long for two lines) and
equal-height regions for both talks. Sessions sit directly on the shared
background, without rectangular frames or solid panels, as in banner 172.
All text must remain at least 10 px at a 358 px preview width. Missing portraits
use a text-only speaker block, never a placeholder silhouette. The legacy
solo_panel composition is preserved.

Anything else raises rather than guessing. Portraits are cropped per speaker
where a manual crop is registered in PORTRAIT_CROPS; square headshots need none
because ImageOps.fit centres them.

Usage: ``generate_meetup_banner.py _posts/<post>.md``. It reads the shared background
(office/content/images/meetup-background.png, or the event's own ``<date>-<nr>-meetup-background.png``
if one exists) and writes a single banner to assets/images/, which
the website and Meetup both use. ``--generate-background`` creates the background
first (Azure Foundry image model, credentials only from IMG_AI_MODEL_* variables). Normally reuse the saved file instead: a new
generation gives a different image. The saved PNG already includes the tone
correction in ``tone_background``.

Requires Python 3, Pillow and PyYAML.
"""

import argparse
import base64
import datetime
import io
import json
import os
import re
import urllib.request
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

# Prompt sent to the image model: no text, people or logos, so no personal data
# or local materials leave the machine.
BACKGROUND_PROMPT = (
    "Abstract widescreen 16:9 background for a tech meetup banner, dark and moody. Color palette: very dark "
    "navy blue at the left edge, rich deep purple through the middle, no pink and no magenta. The right half "
    "shows a softly blurred out-of-focus laptop keyboard with subtle warm copper-orange highlights on the keys, "
    "low contrast, fading into dark violet. Smooth, calm and minimal, with large uncluttered areas so text "
    "can be placed on top. No text, no letters, no logos, no people, no UI."
)
SHARED_BACKGROUND = "meetup-background.png"
BACKGROUND_SIZE = "1536x1024"
# Light correction of the raw model output: nudge the hue away from pink and dim it slightly.
HUE_SHIFT, VALUE_SCALE, SATURATION_SCALE = -4, 0.9, 1.0

PORTRAIT_CROPS = {
    "piotr-gankiewicz": (0.10, 0, 0.90, 0.80),
    "lukasz-olbromski": (0.125, 0, 0.825, 0.70),
    "lukasz-pyrzyk": (0.10, 0, 0.80, 0.70),
}

# Legacy composition for exactly five supporting partners (banners 172 and the
# first 173): a tall Wroc.NET-style mark on the left plus a 2x2 grid.
PARTNER_POSITIONS = (
    (341, 506, 300, 58),
    (180, 600, 96, 96),
    (320, 571, 137, 38),
    (481, 571, 137, 38),
    (320, 629, 137, 38),
    (481, 629, 137, 38),
)

# solo_panel only: any number of supporting partners other than five goes into
# a grid of equal white boxes under a smaller strategic logo. two_talks uses
# band_positions instead.
GRID_COLUMNS = 3
GRID_LEFT, GRID_RIGHT = 50, 576
GRID_TOP, GRID_BOTTOM = 526, 662
GRID_GAP = 7
MAX_SUPPORTING = 12
MEDIA_ROLE = "Patron medialny"


def partner_positions(supporting_count):
    """Return (center_x, center_y, width, height) for strategic + supporting logos."""
    if supporting_count == 5:
        return PARTNER_POSITIONS
    if not 1 <= supporting_count <= MAX_SUPPORTING:
        raise ValueError(f"Cannot lay out {supporting_count} supporting partners")
    rows = -(-supporting_count // GRID_COLUMNS)
    box_w = (GRID_RIGHT - GRID_LEFT - GRID_GAP * (GRID_COLUMNS - 1)) / GRID_COLUMNS
    box_h = (GRID_BOTTOM - GRID_TOP - GRID_GAP * (rows - 1)) / rows
    positions = [(313, 494, 280, 44)]
    for index in range(supporting_count):
        row, col = divmod(index, GRID_COLUMNS)
        in_row = min(GRID_COLUMNS, supporting_count - row * GRID_COLUMNS)
        row_left = GRID_LEFT + (GRID_RIGHT - GRID_LEFT - in_row * box_w - (in_row - 1) * GRID_GAP) / 2
        x = row_left + col * (box_w + GRID_GAP) + box_w / 2
        y = GRID_TOP + row * (box_h + GRID_GAP) + box_h / 2
        positions.append((round(x), round(y), round(box_w - 12), round(box_h - 12)))
    return tuple(positions)


def tone_background(image):
    """Nudge the raw model output away from pink and dim it slightly."""
    hue, saturation, value = image.convert("RGB").convert("HSV").split()
    hue = hue.point(lambda x: (x + HUE_SHIFT) % 256)
    saturation = saturation.point(lambda x: min(255, int(x * SATURATION_SCALE)))
    value = value.point(lambda x: int(x * VALUE_SCALE))
    return Image.merge("HSV", (hue, saturation, value)).convert("RGB")


def generate_background(output_path):
    """Generate a background with the image model and save it, toned, to output_path."""
    try:
        endpoint = os.environ["IMG_AI_MODEL_ENDPOINT"]
        key = os.environ["IMG_AI_MODEL_APIKEY"]
        model = os.environ["IMG_AI_MODEL_NAME"]
    except KeyError as error:
        raise RuntimeError(f"Missing environment variable {error.args[0]}") from None
    body = json.dumps(
        {"model": model, "prompt": BACKGROUND_PROMPT, "size": BACKGROUND_SIZE, "n": 1, "quality": "medium"}
    ).encode()
    request = urllib.request.Request(
        endpoint, body, {"Content-Type": "application/json", "api-key": key}
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        data = json.load(response)["data"][0]
    raw = base64.b64decode(data["b64_json"])
    with Image.open(io.BytesIO(raw)) as image:
        toned = tone_background(image)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    toned.save(output_path, format="PNG")
    print(f"Saved {output_path} ({toned.width}x{toned.height})")


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


BAND_TOP, BAND_BOTTOM = 498, 654
BAND_GRID_LEFT, BAND_GRID_RIGHT = 410, 1158
BAND_GAP = 8


def band_positions(supporting_count):
    """Bottom band for two_talks: strategic logo left, supporting logos in two rows."""
    if not 1 <= supporting_count <= MAX_SUPPORTING:
        raise ValueError(f"Cannot lay out {supporting_count} supporting partners")
    columns = -(-supporting_count // 2)
    box_w = (BAND_GRID_RIGHT - BAND_GRID_LEFT - BAND_GAP * (columns - 1)) / columns
    rows = 1 if supporting_count == 1 else 2
    box_h = (BAND_BOTTOM - BAND_TOP - BAND_GAP * (rows - 1)) / rows
    positions = [(226, (BAND_TOP + BAND_BOTTOM) // 2, 300, 66)]
    for index in range(supporting_count):
        row, col = divmod(index, columns)
        in_row = min(columns, supporting_count - row * columns)
        row_left = BAND_GRID_LEFT + (BAND_GRID_RIGHT - BAND_GRID_LEFT - in_row * box_w - (in_row - 1) * BAND_GAP) / 2
        x = row_left + col * (box_w + BAND_GAP) + box_w / 2
        y = BAND_TOP + row * (box_h + BAND_GAP) + box_h / 2
        positions.append((round(x), round(y), round(box_w - 12), round(box_h - 12)))
    return tuple(positions)


def detect_layout(talks):
    """Return the layout name for a post's talks, or raise if unsupported."""
    if len(talks) != 2:
        raise ValueError("Expected exactly two talks")
    first = len(talks[0]["speaker_ids"])
    second = len(talks[1]["speaker_ids"])
    if first == 1 and second == 3:
        return "solo_panel"
    if (first, second) in ((1, 1), (1, 2), (2, 1)):
        return "two_talks"
    raise ValueError(
        "Unsupported talk layout: expected one solo talk plus a three-person "
        f"panel, or two talks of one or two speakers each, not both two (got {first} and {second})"
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
    # Sessions without speakers (e.g. an open discussion) stay in the post but not on the banner.
    talks = [talk for talk in post["talks"] if talk.get("speaker_ids")]
    layout = detect_layout(talks)
    speakers = {person["id"]: person for person in load_yaml(ROOT / "_data/speakers.yml")}
    venue = load_yaml(ROOT / "_data/location.yml")["venue"]
    partners = load_yaml(ROOT / "_data/partners.yml")
    # Media patrons are left off the banner; they stay on the website and in the announcement.
    partners["supporting"] = [p for p in partners["supporting"] if p.get("role") != MEDIA_ROLE]
    if not partners["supporting"]:
        raise ValueError(f'No supporting partners left after skipping role "{MEDIA_ROLE}"')
    partner_list = partners["strategic"] + partners["supporting"]
    if len(partners["strategic"]) != 1:
        raise ValueError("This layout requires exactly one strategic partner logo")
    date = post["date"]
    if not isinstance(date, datetime.date):
        date = datetime.date.fromisoformat(date)
    time = datetime.time.fromisoformat(post["time"])

    positions = (
        band_positions(len(partners["supporting"]))
        if layout == "two_talks"
        else partner_positions(len(partners["supporting"]))
    )

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
    if layout == "two_talks":
        paste(banner_logo(), 42, 40, 170, 170)
        draw.rectangle((236 * SCALE, 52 * SCALE, 373 * SCALE, 136 * SCALE), outline="#7542AA", width=3 * SCALE)
        number_box = (236, 52, 373, 136)
        number_bounds = draw.textbbox((0, 0), number, font=font(57, True), anchor="lt")
        text(
            number,
            (number_box[0] + number_box[2]) / 2 - (number_bounds[0] + number_bounds[2]) / 2 / SCALE,
            (number_box[1] + number_box[3]) / 2 - (number_bounds[1] + number_bounds[3]) / 2 / SCALE,
            57,
            bold=True,
            max_width=112,
        )
        text("spotkanie", 392, 46, 42, max_width=220)
        text("Wroc.NET", 392, 94, 42, max_width=220)
        text(f"{date:%d.%m.%Y} | {time:%H:%M}", 236, 176, 40, max_width=370)
        draw.line((236 * SCALE, 238 * SCALE, 600 * SCALE, 238 * SCALE), fill="#7542AA", width=2 * SCALE)
        paragraph(f'{venue["name"]}, Wrocław', 236, 256, 36, 370, 2)
    else:
        paste(banner_logo(), 42, 62, 185, 185)
        draw.rectangle((126 * SCALE, 252 * SCALE, 263 * SCALE, 340 * SCALE), outline="#7542AA", width=3 * SCALE)
        text(number, 144, 269, 57, bold=True, max_width=112)
        text("spotkanie", 282, 251, 42, max_width=290)
        text("Wroc.NET", 282, 300, 42, max_width=290)
        text(f"{date:%d.%m.%Y} | {time:%H:%M}", 126, 372, 27, max_width=435)
        draw.line((126 * SCALE, 420 * SCALE, 556 * SCALE, 420 * SCALE), fill="#7542AA", width=2 * SCALE)
        text(f'{venue["name"]}, Wrocław', 126, 442, 25, max_width=435)

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
        for talk, top in zip(talks, (40, 278)):
            paragraph(talk.get("banner_title", talk["title"]), 622, top, 38, 530, 2, bold=True)
            ids = talk["speaker_ids"]
            if len(ids) == 2:
                for index, speaker_id in enumerate(ids):
                    speaker_block(speaker_id, 622 + index * 274, top + 110, 256, split_name=True)
            else:
                speaker_block(ids[0], 622, top + 110, 530)

    for partner, (center_x, center_y, width, height) in zip(partner_list, positions):
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


def paths_for(post_path, generating=False):
    """Return (background, output) for a post: one banner file, served on the website and used on Meetup."""
    stem = "-".join(post_path.name.split("-")[:4])
    images = ROOT / "office/content/images"
    event_background = images / f"{stem}-meetup-background.png"
    # Banners 172 and 173 keep their own backgrounds; every newer one reuses the shared file.
    background = event_background if event_background.exists() or generating else images / SHARED_BACKGROUND
    return background, ROOT / f"assets/images/{stem}-meetup.jpg"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("post", type=Path)
    parser.add_argument(
        "--generate-background",
        action="store_true",
        help="generate a new background first (overwrites the saved one; needs IMG_AI_MODEL_* variables)",
    )
    args = parser.parse_args()
    background, output = paths_for(args.post, args.generate_background)
    if args.generate_background:
        generate_background(background)
    render(args.post, background, output)
