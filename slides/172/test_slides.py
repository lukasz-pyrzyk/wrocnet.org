import os
from pathlib import Path
import posixpath
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


DIRECTORY = Path(__file__).resolve().parent
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def slide_text(slide):
    return "\n".join(node.text or "" for node in slide.findall(".//a:t", NS))


class SlidesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = Path(cls.temporary.name) / "slides.pptx"
        subprocess.run(
            [
                os.environ.get("RUBY", "ruby"),
                str(DIRECTORY / "2026-11-17-172-spotkanie.rb"),
                str(cls.output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.archive = zipfile.ZipFile(cls.output)
        cls.addClassCleanup(cls.archive.close)
        cls.slides = [
            ET.fromstring(cls.archive.read(f"ppt/slides/slide{index}.xml"))
            for index in range(1, 15)
        ]

    def test_package_xml_and_relationships(self):
        names = set(self.archive.namelist())
        self.assertIsNone(self.archive.testzip())
        for name in names:
            if name.endswith((".xml", ".rels")):
                root = ET.fromstring(self.archive.read(name))
                if name.endswith(".rels"):
                    identifiers = [relation.get("Id") for relation in root]
                    self.assertEqual(len(identifiers), len(set(identifiers)), name)
                    base = posixpath.dirname(posixpath.dirname(name))
                    for relation in root:
                        if relation.get("TargetMode") != "External":
                            target = posixpath.normpath(
                                posixpath.join(base, relation.get("Target"))
                            )
                            self.assertIn(target, names, (name, target))
        presentation = ET.fromstring(self.archive.read("ppt/presentation.xml"))
        self.assertEqual(len(presentation.findall("p:sldIdLst/p:sldId", NS)), 14)

    def test_shape_ids_alignment_and_bounds(self):
        presentation = ET.fromstring(self.archive.read("ppt/presentation.xml"))
        size = presentation.find("p:sldSz", NS)
        width, height = int(size.get("cx")), int(size.get("cy"))
        self.assertEqual(width * 9, height * 16)
        for index, slide in enumerate(self.slides, 1):
            identifiers = [
                node.get("id") for node in slide.findall(".//p:cNvPr", NS)
            ]
            self.assertEqual(len(identifiers), len(set(identifiers)), index)
            for paragraph in slide.findall(".//a:pPr", NS):
                self.assertIn(paragraph.get("algn"), {"l", "ctr", "r"})
            for transform in slide.findall(".//a:xfrm", NS):
                offset, extent = transform.find("a:off", NS), transform.find("a:ext", NS)
                if offset is None or extent is None:
                    continue
                x, y = int(offset.get("x")), int(offset.get("y"))
                w, h = int(extent.get("cx")), int(extent.get("cy"))
                self.assertGreaterEqual(min(x, y, w, h), 0, index)
                self.assertLessEqual(x + w, width + 1, index)
                self.assertLessEqual(y + h, height + 1, index)

    def test_slide_order_and_numbering(self):
        markers = [
            "172. SPOTKANIE WROC.NET",
            "O grupie",
            "Wspiera nas Devstyle",
            "Spotykamy się regularnie",
            "Pub Wędrówki",
            "Nowe wrocnet.org",
            "Masz temat?",
            "Poznaj organizatorów",
            "Dołącz do społeczności",
            "Zostajemy.",
            "Następne spotkanie",
            "Plan dzisiejszego spotkania",
            "ULTRA-WYDAJNOŚĆ",
            "Zadawajcie pytania.",
        ]
        for index, (slide, marker) in enumerate(zip(self.slides, markers), 1):
            text = slide_text(slide)
            self.assertIn(marker, text)
            self.assertNotIn("SLIDE_NUMBER", text)
            if 2 <= index <= 13:
                self.assertIn(f"{index:02}", text.splitlines())
        self.assertNotIn("ZACZYNAMY O 18:00", slide_text(self.slides[0]))

    def test_partner_logos_and_screenshots_keep_proportions(self):
        expected = {
            "Logo Devstyle": (600, 120),
            "Logo Wrocławski Portal": (600, 532),
            "Logo Fakty Wrocław": (983, 158),
            "Logo PTI Oddział Dolnośląski": (457, 187),
            "Logo dlaStudenta.pl": (2049, 473),
            "Logo Magazyn Programista": (2362, 459),
            "Strona główna wrocnet.org": (1440, 830),
            "Strona Zostań prelegentem": (1440, 830),
        }
        found = set()
        for slide in self.slides:
            for picture in slide.findall(".//p:pic", NS):
                name = picture.find("p:nvPicPr/p:cNvPr", NS).get("name")
                if name in expected:
                    found.add(name)
                    extent = picture.find("p:spPr/a:xfrm/a:ext", NS)
                    width, height = expected[name]
                    self.assertAlmostEqual(
                        int(extent.get("cx")) / int(extent.get("cy")),
                        width / height,
                        places=4,
                        msg=name,
                    )
        self.assertEqual(found, set(expected))

    def test_panel_portraits_and_centering(self):
        panel = self.slides[-1]
        portraits = [
            picture for picture in panel.findall(".//p:pic", NS)
            if picture.find("p:spPr/a:prstGeom", NS).get("prst") == "ellipse"
        ]
        self.assertEqual(len(portraits), 3)
        extents = [
            picture.find("p:spPr/a:xfrm/a:ext", NS).attrib for picture in portraits
        ]
        self.assertTrue(all(extent == extents[0] for extent in extents))
        for shape in panel.findall(".//p:sp", NS):
            if shape.find("p:txBody", NS) is not None:
                text = slide_text(shape)
                if any(name in text for name in ("OLBROMSKI", "GANKIEWICZ", "PYRZYK")):
                    for paragraph in shape.findall(".//a:pPr", NS):
                        self.assertEqual(paragraph.get("algn"), "ctr")

    def test_next_meetup_and_preserved_content(self):
        next_meetup = slide_text(self.slides[10])
        for value in [
            "Czy Result Pattern daje rezultaty?",
            "AI Software Engineering Workflows w praktyce",
            "Melchior Kozar",
            "Hleb Sukrystsik",
            "Łukasz Hałas",
        ]:
            self.assertIn(value, next_meetup)
        self.assertNotIn("Program ogłosimy wkrótce", next_meetup)
        organizers = slide_text(self.slides[7])
        for surname in [
            "Pyrzyk", "Olbromski", "Kowalski", "Trawińska",
            "Zawadzki", "Dłubak", "Pulka", "Wojnarowski",
        ]:
            self.assertIn(surname, organizers)
        self.assertIn("Pierwsze 80 napojów", slide_text(self.slides[4]))
        for value in ["18:15", "19:15", "20:15"]:
            self.assertIn(value, slide_text(self.slides[11]))

    def test_qr_crop_and_readable_type(self):
        whatsapp = self.slides[8]
        picture = next(
            picture for picture in whatsapp.findall(".//p:pic", NS)
            if picture.find("p:nvPicPr/p:cNvPr", NS).get("name").startswith("Kod QR")
        )
        crop = picture.find("p:blipFill/a:srcRect", NS)
        self.assertEqual(int(crop.get("l")), round(227 / 1114 * 100000))
        self.assertEqual(int(crop.get("t")), round(381 / 1139 * 100000))
        fonts = {
            run.find("a:latin", NS).get("typeface")
            for slide in self.slides
            for run in slide.findall(".//a:rPr", NS)
        }
        self.assertEqual(fonts, {"Arial"})
        self.assertNotIn("🍺", slide_text(self.slides[9]))


if __name__ == "__main__":
    unittest.main()
