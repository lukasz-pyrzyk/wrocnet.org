#!/usr/bin/env ruby
# frozen_string_literal: true

require "fileutils"
require "digest"
require "time"
require "zlib"

ROOT = File.expand_path("../..", __dir__)
OUTPUT = File.join(__dir__, "2026-09-22-170-otwarcie-sezonu-final-v2.pptx")

SLIDE_W = 13.333
SLIDE_H = 7.5
EMU = 914_400

COLORS = {
  ink: "171219",
  panel: "F4EDF7",
  violet: "641E78",
  purple: "7A248F",
  pink: "D51A96",
  signal: "D51A96",
  white: "FFFFFF",
  muted: "5E5264",
  line: "D8C4DF",
  green: "25D366"
}.freeze

def esc(value)
  value.to_s.gsub("&", "&amp;").gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;")
end

def emu(value)
  (value * EMU).round
end

def rect(id, x, y, w, h, fill:, radius: false, line: nil, transparency: 0, shadow: false)
  geometry = radius ? "roundRect" : "rect"
  alpha = transparency.positive? ? %(<a:alpha val="#{100_000 - transparency * 1_000}"/>) : ""
  outline = line ? %(<a:ln w="12700"><a:solidFill><a:srgbClr val="#{line}"/></a:solidFill></a:ln>) : %(<a:ln><a:noFill/></a:ln>)
  effect = shadow ? %(<a:effectLst><a:outerShdw blurRad="90000" dist="38000" dir="5400000" rotWithShape="0"><a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr></a:outerShdw></a:effectLst>) : ""
  <<~XML
    <p:sp>
      <p:nvSpPr><p:cNvPr id="#{id}" name="Shape #{id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="#{emu(x)}" y="#{emu(y)}"/><a:ext cx="#{emu(w)}" cy="#{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="#{geometry}"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="#{fill}">#{alpha}</a:srgbClr></a:solidFill>#{outline}#{effect}
      </p:spPr>
    </p:sp>
  XML
end

# stops: array of [position 0-100, hex, alpha 0-100 (optional)]
def gradient_rect(id, x, y, w, h, stops:, angle: 5400000)
  gs_list = stops.map do |pos, hex, alpha|
    alpha_xml = alpha ? %(<a:alpha val="#{(alpha * 1000).round}"/>) : ""
    %(<a:gs pos="#{(pos * 1000).round}"><a:srgbClr val="#{hex}">#{alpha_xml}</a:srgbClr></a:gs>)
  end.join
  <<~XML
    <p:sp>
      <p:nvSpPr><p:cNvPr id="#{id}" name="Gradient #{id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="#{emu(x)}" y="#{emu(y)}"/><a:ext cx="#{emu(w)}" cy="#{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:gradFill rotWithShape="1"><a:gsLst>#{gs_list}</a:gsLst><a:lin ang="#{angle}" scaled="1"/></a:gradFill>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
    </p:sp>
  XML
end

def ellipse(id, x, y, w, h, fill:, line: nil)
  outline = line ? %(<a:ln w="19050"><a:solidFill><a:srgbClr val="#{line}"/></a:solidFill></a:ln>) : %(<a:ln><a:noFill/></a:ln>)
  <<~XML
    <p:sp>
      <p:nvSpPr><p:cNvPr id="#{id}" name="Circle #{id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="#{emu(x)}" y="#{emu(y)}"/><a:ext cx="#{emu(w)}" cy="#{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="#{fill}"/></a:solidFill>#{outline}
      </p:spPr>
    </p:sp>
  XML
end

def text(id, value, x, y, w, h, size: 24, color: COLORS[:ink], bold: false, align: "l", valign: "ctr", font: "Arial", margin: 0.08)
  paragraphs = value.to_s.split("\n", -1).map do |line|
    %(<a:p><a:pPr algn="#{align}"/><a:r><a:rPr lang="pl-PL" sz="#{size * 100}" b="#{bold ? 1 : 0}"><a:solidFill><a:srgbClr val="#{color}"/></a:solidFill><a:latin typeface="#{font}"/></a:rPr><a:t>#{esc(line)}</a:t></a:r><a:endParaRPr lang="pl-PL" sz="#{size * 100}"/></a:p>)
  end.join
  <<~XML
    <p:sp>
      <p:nvSpPr><p:cNvPr id="#{id}" name="Text #{id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="#{emu(x)}" y="#{emu(y)}"/><a:ext cx="#{emu(w)}" cy="#{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>
      <p:txBody><a:bodyPr anchor="#{valign}" lIns="#{emu(margin)}" rIns="#{emu(margin)}" tIns="#{emu(margin)}" bIns="#{emu(margin)}"/><a:lstStyle/>#{paragraphs}</p:txBody>
    </p:sp>
  XML
end

def line(id, x1, y1, x2, y2, color: COLORS[:line], width: 1.5)
  <<~XML
    <p:sp>
      <p:nvSpPr><p:cNvPr id="#{id}" name="Line #{id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="#{emu(x1)}" y="#{emu(y1)}"/><a:ext cx="#{emu(x2 - x1)}" cy="#{emu(y2 - y1)}"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="#{(width * 12_700).round}"><a:solidFill><a:srgbClr val="#{color}"/></a:solidFill></a:ln></p:spPr>
    </p:sp>
  XML
end

def picture(id, relationship_id, x, y, w, h, name = "Image")
  <<~XML
    <p:pic>
      <p:nvPicPr><p:cNvPr id="#{id}" name="#{esc(name)}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
      <p:blipFill><a:blip r:embed="#{relationship_id}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
      <p:spPr><a:xfrm><a:off x="#{emu(x)}" y="#{emu(y)}"/><a:ext cx="#{emu(w)}" cy="#{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:ln><a:noFill/></a:ln></p:spPr>
    </p:pic>
  XML
end

def base(slide_number, kicker, title)
  shapes = []
  shapes << rect(2, 0, 0, SLIDE_W, SLIDE_H, fill: COLORS[:white])
  shapes << gradient_rect(3, 0, 0, SLIDE_W, 0.07, stops: [[0, "000000", 22], [100, "000000", 0]])
  shapes << text(5, kicker.upcase, 0.78, 0.40, 8.9, 0.30, size: 10, color: COLORS[:violet], bold: true)
  shapes << text(6, title, 0.78, 0.78, 10.8, 0.76, size: 30, bold: true)
  shapes << text(7, format("%02d", slide_number), 11.52, 0.43, 0.95, 0.62, size: 28, color: COLORS[:purple], bold: true, align: "r")
  shapes << line(8, 0.78, 6.91, 12.53, 6.91, color: COLORS[:line], width: 1)
  shapes << text(9, "Łukasz Pyrzyk  ·  Wroc.NET", 0.78, 7.05, 4.3, 0.20, size: 9, color: COLORS[:muted])
  shapes
end

def browser_frame(id, x, y, w, h, path, heading, body, accent: COLORS[:signal])
  items = []
  items << rect(id, x, y, w, h, fill: "FBF9FC", line: COLORS[:line])
  items << rect(id + 1, x, y, w, 0.48, fill: COLORS[:violet])
  items << rect(id + 2, x + 0.18, y + 0.17, 0.1, 0.1, fill: "EC547A", radius: true)
  items << rect(id + 3, x + 0.34, y + 0.17, 0.1, 0.1, fill: "F2B34F", radius: true)
  items << rect(id + 4, x + 0.50, y + 0.17, 0.1, 0.1, fill: "5CC47B", radius: true)
  items << text(id + 5, "wrocnet.org#{path}", x + 0.83, y + 0.10, w - 1.08, 0.26, size: 10, color: COLORS[:white])
  items << rect(id + 6, x + 0.26, y + 0.77, 0.08, h - 1.03, fill: accent)
  items << text(id + 7, heading, x + 0.58, y + 0.76, w - 0.95, 0.76, size: 22, color: COLORS[:violet], bold: true)
  items << text(id + 8, body, x + 0.58, y + 1.63, w - 0.95, h - 1.92, size: 14, color: "423747", valign: "t")
  items
end

def slide_xml(shapes)
  <<~XML
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
      <p:cSld><p:spTree>
        <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
        <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
        #{shapes.join}
      </p:spTree></p:cSld>
      <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
    </p:sld>
  XML
end

slides = []
images = {}

def add_image(images, slide_images, path)
  absolute = File.join(ROOT, path)
  raise "Missing image: #{absolute}" unless File.file?(absolute)

  media = images[path] ||= begin
    extension = File.extname(path).downcase.delete_prefix(".")
    extension = "jpg" if extension == "jpeg"
    stem = File.basename(path, File.extname(path)).gsub(/[^a-zA-Z0-9_-]/, "-")
    fingerprint = Digest::SHA256.file(absolute).hexdigest[0, 8]
    { name: "#{stem}-#{fingerprint}.#{extension}", path: absolute }
  end
  relationship_id = "rId#{100 + images.keys.index(path)}"
  slide_images << [relationship_id, media]
  relationship_id
end

# 1. Welcome
slide_images = []
panel_bg_rid = add_image(images, slide_images, "slides/170/assets/images/panel-gradient-cover.jpg")
logo_rid = add_image(images, slide_images, "assets/images/logo.png")
pyrzyk_cover_rid = add_image(images, slide_images, "assets/images/organizers/lukasz-pyrzyk.jpg")
olbromski_cover_rid = add_image(images, slide_images, "assets/images/organizers/lukasz-olbromski.jpg")
s = []
s << rect(2, 0, 0, SLIDE_W, SLIDE_H, fill: "160E22")
s << gradient_rect(3, 0, 0, SLIDE_W, 0.07, stops: [[0, "000000", 22], [100, "000000", 0]])
s << picture(4, panel_bg_rid, 8.56, 0.13, 4.77, 7.37, "Grafika panelu")
s << text(6, "170. SPOTKANIE WROC.NET", 0.82, 0.55, 6.8, 0.34, size: 11, color: COLORS[:signal], bold: true)
s << text(7, "OTWARCIE\nSEZONU", 0.78, 1.18, 7.25, 1.72, size: 49, color: COLORS[:white], bold: true)
s << text(8, "2026 / 2027", 0.82, 3.02, 6.80, 0.60, size: 26, color: COLORS[:signal], bold: true)
s << text(10, "PANEL DYSKUSYJNY", 0.82, 4.30, 6.80, 0.34, size: 12, color: COLORS[:muted], bold: true)
s << text(11, "Kod staniał.\nOdpowiedzialność nie.", 0.82, 4.70, 7.10, 1.05, size: 28, color: COLORS[:white], bold: true)
s << text(12, "22 WRZEŚNIA 2026  ·  18:30  ·  PUB WĘDRÓWKI", 0.82, 6.62, 7.20, 0.34, size: 12, color: COLORS[:white], bold: true)
s << text(13, "Łukasz Pyrzyk", 0.82, 7.10, 3.1, 0.20, size: 9, color: COLORS[:muted])
s << picture(14, logo_rid, 10.39, 0.52, 1.10, 1.10, "Wroc.NET logo")
s << rect(15, 8.95, 2.03, 1.78, 1.78, fill: COLORS[:white], shadow: true)
s << picture(16, pyrzyk_cover_rid, 9.06, 2.14, 1.56, 1.56, "Łukasz Pyrzyk")
s << rect(17, 11.10, 2.03, 1.78, 1.78, fill: COLORS[:white], shadow: true)
s << picture(18, olbromski_cover_rid, 11.21, 2.14, 1.56, 1.56, "Łukasz Olbromski")
s << text(19, "Łukasz Pyrzyk", 8.82, 4.02, 2.02, 0.34, size: 12, color: COLORS[:white], bold: true, align: "c")
s << text(20, "Łukasz Olbromski", 10.98, 4.02, 2.12, 0.34, size: 12, color: COLORS[:white], bold: true, align: "c")
s << text(21, "DYSKUSJA\nZACZYNA SIĘ\nOD WAS", 9.02, 6.00, 3.85, 0.95, size: 19, color: COLORS[:white], bold: true, align: "c")
slides << [slide_xml(s), slide_images]

# 2. Dates
s = base(2, "Sezon 2026/2027", "Spotykamy się regularnie")
s << text(10, "Po dzisiejszym otwarciu: zawsze trzeci wtorek miesiąca.", 0.78, 1.92, 11.5, 0.48, size: 17, color: COLORS[:muted])
dates = [["22 WRZ", "otwarcie", true], ["20 PAŹ", "3. wtorek", false], ["17 LIS", "3. wtorek", false], ["15 GRU", "3. wtorek", false]]
s << line(11, 1.36, 3.37, 11.97, 3.37, color: COLORS[:line], width: 2)
dates.each_with_index do |(date, label, special), index|
  x = 0.96 + index * 3.10
  dot_fill = special ? COLORS[:signal] : COLORS[:violet]
  s << ellipse(20 + index * 3, x + 0.77, 3.13, 0.48, 0.48, fill: dot_fill, line: COLORS[:white])
  s << text(21 + index * 3, date, x, 2.45, 2.02, 0.48, size: 25, color: special ? COLORS[:signal] : COLORS[:ink], bold: true, align: "c")
  s << text(22 + index * 3, label, x, 3.88, 2.02, 0.34, size: 12, color: COLORS[:muted], bold: special, align: "c")
end
s << rect(40, 2.02, 5.07, 9.28, 0.88, fill: COLORS[:panel])
s << text(41, "18:30  ·  PUB WĘDRÓWKI  ·  UL. PODWALE 37/38", 2.25, 5.27, 8.82, 0.42, size: 16, color: COLORS[:violet], bold: true, align: "c")
slides << [slide_xml(s), []]

# 3. Venue
s = base(3, "Nasze miejsce", "Pub Wędrówki")
s << text(10, "UL. PODWALE 37/38  ·  WROCŁAW", 0.78, 1.94, 7.0, 0.40, size: 15, color: COLORS[:violet], bold: true)
s << text(11, "Nie ma pizzy.", 0.78, 2.70, 8.20, 0.78, size: 37, color: COLORS[:ink], bold: true)
s << text(12, "Bar działa.", 0.78, 3.54, 8.20, 0.78, size: 37, color: COLORS[:violet], bold: true)
s << rect(13, 9.54, 2.66, 2.63, 2.14, fill: COLORS[:violet])
s << text(14, "PIWO\nI NAPOJE", 9.82, 3.08, 2.07, 1.20, size: 21, color: COLORS[:white], bold: true, align: "c")
s << text(16, "Na miejscu nie zamówimy jedzenia. Piwo i inne napoje są za darmo*", 0.78, 5.16, 10.65, 0.43, size: 16, color: COLORS[:muted])
s << text(17, "Po części oficjalnej zostajemy na rozmowy.", 0.78, 5.72, 10.65, 0.43, size: 16, color: COLORS[:ink], bold: true)
s << text(18, "* aż wyczerpiemy limit od naszego sponsora. Może dzisiaj się uda? ;)", 0.78, 6.14, 10.65, 0.32, size: 11, color: COLORS[:muted])
slides << [slide_xml(s), []]

# 4. Attendance list
s = base(4, "Na koniec spotkania", "Lista obecności = udział w losowaniu")
s << text(10, "WPISUJESZ SIĘ", 0.78, 2.14, 5.45, 0.72, size: 34, color: COLORS[:violet], bold: true)
s << text(11, "Bierzesz udział w losowaniu nagród.", 0.78, 3.00, 6.40, 0.52, size: 21, color: COLORS[:ink], bold: true)
s << rect(12, 7.58, 2.03, 4.66, 3.62, fill: COLORS[:violet])
s << text(13, "LOSOWANIE", 7.96, 2.50, 3.90, 0.42, size: 15, color: COLORS[:signal], bold: true, align: "c")
s << text(14, "NA KONIEC\nSPOTKANIA", 7.96, 3.17, 3.90, 1.12, size: 29, color: COLORS[:white], bold: true, align: "c")
s << text(15, "Do wygrania są różne nagrody.\nNajczęściej książki od sponsorów.", 0.78, 4.42, 6.42, 0.96, size: 18, color: COLORS[:muted], valign: "t")
slides << [slide_xml(s), []]

# 5. Sponsor
s = base(5, "Partner strategiczny", "Wspiera nas Devstyle")
s << text(10, "DZIĘKUJEMY ZA WSPARCIE\nWROC.NET", 0.78, 2.17, 5.60, 1.02, size: 27, color: COLORS[:violet], bold: true, valign: "t")
s << text(11, "Devstyle jest partnerem strategicznym\nnaszej społeczności.", 0.78, 3.60, 5.72, 0.92, size: 19, color: COLORS[:ink], valign: "t")
s << rect(14, 7.28, 2.00, 4.96, 4.15, fill: COLORS[:panel])
slide_images = []
devstyle_rid = add_image(images, slide_images, "assets/images/partners/devstyle.png")
s << picture(15, devstyle_rid, 7.69, 3.37, 4.14, 0.83, "Logo Devstyle")
s << text(16, "PARTNERZY WSPIERAJĄCY", 0.78, 4.50, 5.60, 0.28, size: 11, color: COLORS[:muted], bold: true)
helion_rid = add_image(images, slide_images, "assets/images/partners/helion.jpg")
hued_rid = add_image(images, slide_images, "assets/images/partners/hued-me.png")
s << picture(17, helion_rid, 0.78, 4.85, 1.60, 0.53, "Logo Helion")
s << text(18, "partner nagród", 0.78, 5.40, 1.90, 0.26, size: 10, color: COLORS[:muted])
s << picture(19, hued_rid, 2.63, 4.89, 0.46, 0.46, "Logo hued.me")
s << text(20, "hued.me — partner medialny", 2.63, 5.40, 2.60, 0.26, size: 10, color: COLORS[:muted])
s << text(13, "https://devstyle.pl/", 0.78, 5.85, 5.60, 0.42, size: 16, color: COLORS[:violet], bold: true)
slides << [slide_xml(s), slide_images]

# 6. Website overview
s = base(6, "Nowość", "Nowe wrocnet.org")
slide_images = []
home_rid = add_image(images, slide_images, "slides/170/assets/images/wrocnet-home.png")
s << rect(10, 0.72, 2.02, 8.12, 4.24, fill: COLORS[:panel], line: COLORS[:line])
s << picture(11, home_rid, 0.78, 2.08, 8.00, 4.12, "Strona główna wrocnet.org")
s << rect(12, 9.10, 2.02, 3.14, 4.24, fill: COLORS[:panel])
s << text(13, "PROŚCIEJ", 9.42, 2.40, 2.52, 0.46, size: 20, color: COLORS[:signal], bold: true)
s << text(14, "Spotkania, ludzie\ni historia grupy\nw jednym miejscu.", 9.42, 3.10, 2.48, 1.62, size: 19, bold: true, valign: "t")
s << text(16, "wrocnet.org", 9.42, 5.46, 2.48, 0.40, size: 16, color: COLORS[:violet], bold: true)
s << text(17, "https://wrocnet.org", 0.78, 6.38, 8.00, 0.24, size: 10, color: COLORS[:muted], align: "c")
slides << [slide_xml(s), slide_images]

# 7. Become a speaker
s = base(7, "wrocnet.org", "Masz temat? Zostań prelegentem")
slide_images = []
speaker_page_rid = add_image(images, slide_images, "slides/170/assets/images/wrocnet-zostan-prelegentem.png")
speaker_panel_rid = add_image(images, slide_images, "slides/170/assets/images/panel-speaker.jpg")
s << rect(10, 0.72, 2.02, 8.12, 4.24, fill: COLORS[:panel], line: COLORS[:line])
s << picture(11, speaker_page_rid, 0.78, 2.08, 8.00, 4.12, "Strona Zostań prelegentem")
s << picture(12, speaker_panel_rid, 9.10, 2.02, 3.14, 4.24, "Grafika mikrofonu")
s << rect(16, 9.10, 2.02, 3.14, 4.24, fill: COLORS[:violet], transparency: 30)
s << text(13, "MASZ POMYSŁ?", 9.42, 2.42, 2.52, 0.46, size: 18, color: COLORS[:signal], bold: true)
s << text(14, "Nie musisz mieć\ngotowej prezentacji.", 9.42, 3.10, 2.50, 1.10, size: 20, color: COLORS[:white], bold: true, valign: "t")
s << text(15, "Zgłoś temat.\nPomożemy dalej.", 9.42, 4.53, 2.48, 0.82, size: 16, color: COLORS[:white], valign: "t")
s << text(17, "https://wrocnet.org", 0.78, 6.38, 8.00, 0.24, size: 10, color: COLORS[:muted], align: "c")
slides << [slide_xml(s), slide_images]

# 8. Organizers
s = base(8, "wrocnet.org", "Poznaj organizatorów")
slide_images = []
organizers_page_rid = add_image(images, slide_images, "slides/170/assets/images/wrocnet-organizatorzy.png")
s << rect(10, 0.72, 2.02, 8.12, 4.24, fill: COLORS[:panel], line: COLORS[:line])
s << picture(11, organizers_page_rid, 0.78, 2.08, 8.00, 4.12, "Strona Organizatorzy")
s << rect(12, 9.10, 2.02, 3.14, 4.24, fill: COLORS[:panel])
s << text(13, "LUDZIE ZA WROC.NET", 9.42, 2.42, 2.52, 0.70, size: 18, color: COLORS[:signal], bold: true, valign: "t")
s << text(14, "Poznaj aktualnych\ni byłych organizatorów społeczności.", 9.42, 3.43, 2.48, 1.30, size: 18, bold: true, valign: "t")
s << text(16, "wrocnet.org/organizatorzy/", 9.42, 5.46, 2.48, 0.42, size: 11, color: COLORS[:violet], bold: true)
s << text(17, "https://wrocnet.org", 0.78, 6.38, 8.00, 0.24, size: 10, color: COLORS[:muted], align: "c")
slides << [slide_xml(s), slide_images]

# 9. Speakers archive
s = base(9, "wrocnet.org", "Wystąpili u nas")
slide_images = []
speakers_page_rid = add_image(images, slide_images, "slides/170/assets/images/wrocnet-wystapili-u-nas.png")
s << rect(10, 0.72, 2.02, 8.12, 4.24, fill: COLORS[:panel], line: COLORS[:line])
s << picture(11, speakers_page_rid, 0.78, 2.08, 8.00, 4.12, "Strona Wystąpili u nas")
s << rect(12, 9.10, 2.02, 3.14, 4.24, fill: COLORS[:panel])
s << text(13, "156", 9.42, 2.34, 2.50, 0.72, size: 34, color: COLORS[:violet], bold: true)
s << text(14, "PRELEGENTÓW", 9.42, 3.00, 2.50, 0.30, size: 11, color: COLORS[:muted], bold: true)
s << text(15, "233", 9.42, 3.62, 2.50, 0.72, size: 34, color: COLORS[:signal], bold: true)
s << text(16, "SESJE", 9.42, 4.28, 2.50, 0.30, size: 11, color: COLORS[:muted], bold: true)
s << text(18, "Wyszukuj i wracaj\ndo wcześniejszych tematów.", 9.42, 5.39, 2.48, 0.62, size: 13, color: COLORS[:ink], bold: true, valign: "t")
s << text(19, "https://wrocnet.org", 0.78, 6.38, 8.00, 0.24, size: 10, color: COLORS[:muted], align: "c")
slides << [slide_xml(s), slide_images]

# 10. WhatsApp
s = base(10, "Bądźmy w kontakcie", "Dołącz do społeczności na WhatsAppie")
slide_images = []
qr_rid = add_image(images, slide_images, "slides/170/assets/images/whatsappgrupa.jpeg")
whatsapp_panel_rid = add_image(images, slide_images, "slides/170/assets/images/panel-whatsapp.jpg")
s << rect(10, 0.78, 2.01, 4.33, 4.33, fill: COLORS[:panel])
s << picture(11, qr_rid, 0.92, 2.15, 4.05, 4.05, "Kod QR społeczności WhatsApp")
s << picture(12, whatsapp_panel_rid, 5.42, 2.01, 6.82, 4.33, "Grafika panelu")
s << text(13, "ZESKANUJ KOD", 5.86, 2.48, 5.90, 0.46, size: 16, color: COLORS[:signal], bold: true)
s << text(14, "Wrocławska\nGrupa .NET", 5.86, 3.10, 5.74, 1.20, size: 35, color: COLORS[:white], bold: true)
s << text(15, "Ogłoszenia, rozmowy i kontakt między spotkaniami.", 5.86, 4.69, 5.52, 0.82, size: 18, color: COLORS[:white], valign: "t")
s << text(17, "wrocnet.org/whatsapp", 5.86, 5.82, 5.52, 0.34, size: 13, color: COLORS[:signal], bold: true)
slides << [slide_xml(s), slide_images]

# 11. After party
s = base(11, "Po części oficjalnej", "Zostajemy. Bo tak trzeba.")
s << text(10, "🍺 Piwo. 💬 Rozmowy. 🤝 Networking.", 0.78, 2.00, 10.9, 0.60, size: 26, color: COLORS[:ink], bold: true)
s << text(11, "A czasem — całkiem serio — nowa praca.", 0.78, 2.68, 10.9, 0.55, size: 21, color: COLORS[:violet], bold: true)
s << rect(12, 0.78, 3.68, 10.90, 1.85, fill: COLORS[:violet])
s << text(13, "PONOĆ NAJWIĘKSZE KARIERY ZACZYNAJĄ SIĘ\nPRZY BARZE, NIE NA LINKEDIN", 1.10, 3.95, 10.30, 0.95, size: 24, color: COLORS[:white], bold: true, valign: "t")
s << text(14, "(przynajmniej tak mówią ci, którzy zostali dłużej)", 1.10, 4.95, 10.30, 0.42, size: 14, color: COLORS[:signal], bold: true, valign: "t")
s << text(15, "Zostań chwilę dłużej — może właśnie tu jest Twoja następna okazja.", 0.78, 5.85, 10.9, 0.45, size: 16, color: COLORS[:muted])
slides << [slide_xml(s), []]

# 12. Panel
s = base(12, "Dzisiejszy panel", "Kod staniał. Odpowiedzialność nie.")
s << text(10, "Co znaczy być inżynierem\nw erze agentów AI?", 0.78, 1.95, 6.45, 1.12, size: 25, color: COLORS[:violet], bold: true)
s << text(11, "ARCHITEKTURA  ·  SPECYFIKACJA  ·  DOMENA\nOCENA  ·  ODPOWIEDZIALNOŚĆ", 0.78, 3.15, 6.25, 0.70, size: 12, color: COLORS[:muted], bold: true)
s << rect(12, 0.78, 4.23, 6.38, 1.46, fill: COLORS[:violet])
s << text(13, "UCZESTNICY TEŻ SĄ PRELEGENTAMI", 1.05, 4.39, 5.84, 0.36, size: 16, color: COLORS[:white], bold: true)
s << text(14, "Pytajcie, dorzucajcie kontrargumenty i doświadczenia.\nLoża szyderców również mile widziana :)", 1.05, 4.81, 5.84, 0.61, size: 12, color: COLORS[:white])
slide_images = []
pyrzyk_rid = add_image(images, slide_images, "assets/images/organizers/lukasz-pyrzyk.jpg")
olbromski_rid = add_image(images, slide_images, "assets/images/organizers/lukasz-olbromski.jpg")
s << rect(15, 7.78, 2.03, 2.06, 2.06, fill: COLORS[:white], shadow: true)
s << picture(16, pyrzyk_rid, 7.91, 2.16, 1.80, 1.80, "Łukasz Pyrzyk")
s << rect(17, 10.15, 2.03, 2.06, 2.06, fill: COLORS[:white], shadow: true)
s << picture(18, olbromski_rid, 10.28, 2.16, 1.80, 1.80, "Łukasz Olbromski")
s << text(19, "Łukasz Pyrzyk", 7.72, 4.28, 2.18, 0.35, size: 13, bold: true, align: "c")
s << text(20, "Łukasz Olbromski", 10.02, 4.28, 2.32, 0.35, size: 13, bold: true, align: "c")
s << text(21, "+ WY  ·  ZACZYNAMY", 7.82, 5.16, 4.28, 0.55, size: 23, color: COLORS[:signal], bold: true, align: "c")
slides << [slide_xml(s), slide_images]

files = {}

files["[Content_Types].xml"] = <<~XML
  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Default Extension="png" ContentType="image/png"/>
    <Default Extension="jpg" ContentType="image/jpeg"/>
    <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
    <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
    <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
    <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
    <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
    <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
    <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
    <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
    <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
    #{slides.each_index.map { |index| %(<Override PartName="/ppt/slides/slide#{index + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>) }.join("\n  ")}
  </Types>
XML

files["_rels/.rels"] = <<~XML
  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
  </Relationships>
XML

files["docProps/core.xml"] = <<~XML
  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>Otwarcie sezonu Wroc.NET 2026/2027</dc:title><dc:creator>Łukasz Pyrzyk</dc:creator><cp:lastModifiedBy>Łukasz Pyrzyk</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">2026-09-21T12:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-09-21T12:00:00Z</dcterms:modified>
  </cp:coreProperties>
XML

files["docProps/app.xml"] = <<~XML
  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft Office PowerPoint</Application><PresentationFormat>Widescreen</PresentationFormat><Slides>#{slides.length}</Slides><Notes>0</Notes><HiddenSlides>0</HiddenSlides><Company>Wroc.NET</Company><AppVersion>16.0000</AppVersion></Properties>
XML

slide_ids = slides.each_index.map { |index| %(<p:sldId id="#{256 + index}" r:id="rId#{index + 2}"/>) }.join
files["ppt/presentation.xml"] = <<~XML
  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>#{slide_ids}</p:sldIdLst><p:sldSz cx="#{emu(SLIDE_W)}" cy="#{emu(SLIDE_H)}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>
XML

presentation_rels = [%(<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>)]
slides.each_index { |index| presentation_rels << %(<Relationship Id="rId#{index + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide#{index + 1}.xml"/>) }
presentation_rels << %(<Relationship Id="rId#{slides.length + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>)
presentation_rels << %(<Relationship Id="rId#{slides.length + 3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>)
presentation_rels << %(<Relationship Id="rId#{slides.length + 4}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>)
files["ppt/_rels/presentation.xml.rels"] = %(<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">#{presentation_rels.join}</Relationships>)

files["ppt/slideMasters/slideMaster1.xml"] = <<~XML
  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld name="Wroc.NET"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>
XML
files["ppt/slideMasters/_rels/slideMaster1.xml.rels"] = %(<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>)
files["ppt/slideLayouts/slideLayout1.xml"] = %(<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>)
files["ppt/slideLayouts/_rels/slideLayout1.xml.rels"] = %(<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>)

files["ppt/theme/theme1.xml"] = <<~XML
  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Wroc.NET"><a:themeElements><a:clrScheme name="Wroc.NET"><a:dk1><a:srgbClr val="160E22"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="23152F"/></a:dk2><a:lt2><a:srgbClr val="F7F3F8"/></a:lt2><a:accent1><a:srgbClr val="641E78"/></a:accent1><a:accent2><a:srgbClr val="F13BB8"/></a:accent2><a:accent3><a:srgbClr val="8B2BBE"/></a:accent3><a:accent4><a:srgbClr val="25D366"/></a:accent4><a:accent5><a:srgbClr val="B9ADBF"/></a:accent5><a:accent6><a:srgbClr val="6E347E"/></a:accent6><a:hlink><a:srgbClr val="F13BB8"/></a:hlink><a:folHlink><a:srgbClr val="8B2BBE"/></a:folHlink></a:clrScheme><a:fontScheme name="Wroc.NET"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Wroc.NET"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="accent1"/></a:solidFill><a:solidFill><a:schemeClr val="accent2"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>
XML
files["ppt/presProps.xml"] = %(<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>)
files["ppt/viewProps.xml"] = %(<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:normalViewPr/><p:slideViewPr/><p:notesTextViewPr/><p:gridSpacing cx="72008" cy="72008"/></p:viewPr>)
files["ppt/tableStyles.xml"] = %(<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>)

slides.each_with_index do |(xml, slide_images), index|
  files["ppt/slides/slide#{index + 1}.xml"] = xml
  relationships = [%(<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>)]
  slide_images.each do |relationship_id, media|
    relationships << %(<Relationship Id="#{relationship_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/#{media[:name]}"/>)
  end
  files["ppt/slides/_rels/slide#{index + 1}.xml.rels"] = %(<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">#{relationships.join}</Relationships>)
end

images.each_value { |media| files["ppt/media/#{media[:name]}"] = File.binread(media[:path]) }

def dos_time(time)
  (time.hour << 11) | (time.min << 5) | (time.sec / 2)
end

def dos_date(time)
  ((time.year - 1980) << 9) | (time.month << 5) | time.day
end

timestamp = Time.local(2026, 9, 21, 12, 0, 0)
archive = +"".b
central = +"".b
entries = 0

files.each do |name, content|
  filename = name.encode(Encoding::UTF_8).b
  data = content.b
  checksum = Zlib.crc32(data)
  offset = archive.bytesize
  archive << [0x04034b50, 20, 0x0800, 0, dos_time(timestamp), dos_date(timestamp), checksum, data.bytesize, data.bytesize, filename.bytesize, 0].pack("VvvvvvVVVvv")
  archive << filename << data
  central << [0x02014b50, 20, 20, 0x0800, 0, dos_time(timestamp), dos_date(timestamp), checksum, data.bytesize, data.bytesize, filename.bytesize, 0, 0, 0, 0, 0, offset].pack("VvvvvvvVVVvvvvvVV")
  central << filename
  entries += 1
end

central_offset = archive.bytesize
archive << central
archive << [0x06054b50, 0, 0, entries, entries, central.bytesize, central_offset, 0].pack("VvvvvVVv")

FileUtils.mkdir_p(File.dirname(OUTPUT))
File.binwrite(OUTPUT, archive)
puts "Created #{OUTPUT} (#{slides.length} slides)"