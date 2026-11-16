"""Bake circular portraits into PNG alpha instead of PDF clipping paths."""

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps


def prepare_portrait(source, destination):
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGBA")
        size = min(1024, image.width, image.height)
        portrait = ImageOps.fit(image, (size, size), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4))
    ImageDraw.Draw(mask).ellipse((2, 2, size * 4 - 3, size * 4 - 3), fill=255)
    mask = mask.resize((size, size), Image.Resampling.LANCZOS)
    portrait.putalpha(ImageChops.multiply(portrait.getchannel("A"), mask))
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    portrait.save(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    arguments = parser.parse_args()
    prepare_portrait(arguments.source, arguments.destination)
