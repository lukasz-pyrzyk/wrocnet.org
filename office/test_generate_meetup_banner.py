import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image

import generate_meetup_banner as banner


class BannerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def render(self, number, date, post=None):
        output = self.directory / f"{number}.jpg"
        with contextlib.redirect_stdout(io.StringIO()):
            banner.render(
                post or banner.ROOT / f"_posts/{date}-{number}-spotkanie-wroclawskiej-grupy-net.md",
                banner.ROOT / f"office/content/images/{date}-{number}-meetup-background.png",
                output,
            )
        return output

    def test_supported_layouts(self):
        for counts, expected in [
            ((1, 3), "solo_panel"),
            ((1, 2), "two_talks"),
            ((2, 1), "two_talks"),
        ]:
            with self.subTest(counts=counts):
                talks = [{"speaker_ids": ["person"] * count} for count in counts]
                self.assertEqual(banner.detect_layout(talks), expected)

    def test_unsupported_layouts(self):
        for counts in [(), (1,), (1, 1), (2, 2), (3, 1), (1, 3, 1)]:
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                banner.detect_layout([{"speaker_ids": ["person"] * count} for count in counts])

    def test_mobile_font_threshold(self):
        banner.validate_mobile_text(34)
        for size in (20, 22, 27, 33):
            with self.subTest(size=size), self.assertRaisesRegex(ValueError, "minimum is 10 px"):
                banner.validate_mobile_text(size)

    def test_render_both_layouts(self):
        for number, date in [("172", "2026-11-17"), ("173", "2026-12-15")]:
            with self.subTest(number=number):
                with Image.open(self.render(number, date)) as image:
                    self.assertEqual(image.size, (1200, 675))
                    self.assertEqual(image.mode, "RGB")
                    self.assertFalse(image.getexif())

    def test_placeholder_is_not_opened(self):
        with patch.object(banner, "local_image", wraps=banner.local_image) as local_image:
            self.render("173", "2026-12-15")
        paths = [call.args[0] for call in local_image.call_args_list]
        self.assertTrue(any("hleb-sukrystsik.jpg" in path for path in paths))
        self.assertFalse(any(Path(path).stem == "placeholder" for path in paths))

    def test_two_talks_text_uses_mobile_guard(self):
        with patch.object(banner, "validate_mobile_text", wraps=banner.validate_mobile_text) as guard:
            self.render("173", "2026-12-15")
        self.assertGreaterEqual(guard.call_count, 10)
        self.assertTrue(all(call.args[0] >= 34 for call in guard.call_args_list))

    def test_reversed_talk_order_renders(self):
        filename = "2026-12-15-173-spotkanie-wroclawskiej-grupy-net.md"
        source = (banner.ROOT / "_posts" / filename).read_text(encoding="utf-8")
        post = yaml.safe_load(source.split("---", 2)[1])
        post["talks"].reverse()
        path = self.directory / filename
        path.write_text(f"---\n{yaml.safe_dump(post, allow_unicode=True)}---\n", encoding="utf-8")
        self.assertTrue(self.render("173", "2026-12-15", post=path).is_file())

    def test_invalid_speaker_data_is_not_hidden(self):
        original_loader = banner.load_yaml
        for field, value, error in [
            ("nazwisko", "LongSurname" * 20, ValueError),
            ("photo", "/assets/images/speakers/nonexistent-test-photo.jpg", FileNotFoundError),
        ]:
            with self.subTest(field=field):
                speakers = original_loader(banner.ROOT / "_data/speakers.yml")
                person = next(person for person in speakers if person["id"] == "hleb-sukrystsik")
                person[field] = value

                def load_yaml(path):
                    return speakers if path.name == "speakers.yml" else original_loader(path)

                with patch.object(banner, "load_yaml", side_effect=load_yaml), self.assertRaises(error):
                    self.render("173", "2026-12-15")

    def test_long_title_fails_instead_of_shrinking(self):
        filename = "2026-12-15-173-spotkanie-wroclawskiej-grupy-net.md"
        source = (banner.ROOT / "_posts" / filename).read_text(encoding="utf-8")
        post = yaml.safe_load(source.split("---", 2)[1])
        post["talks"][0]["title"] = "Long presentation title " * 20
        path = self.directory / filename
        path.write_text(f"---\n{yaml.safe_dump(post, allow_unicode=True)}---\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "more than 2 lines"):
            self.render("173", "2026-12-15", post=path)


if __name__ == "__main__":
    unittest.main()
