#!/usr/bin/env python3
"""Draw the front page of Friday 20 November 2026 as one 1024x1024 PNG.

Every story on the page comes from reporting published on that day
(Reuters, AP, WSJ, CNN, The Times, BBC, Sensor Tower): the first-ever
Trump-Xi-Putin three-way summit in Shenzhen, the World Court's genocide
ruling on Myanmar, the market sell-off and Anthropic's record IPO, the
Houthi missile strike on Riyadh's tallest tower, Ukraine's third strike
on the Kerch Bridge in four days, GTA 6's launch day, and Nvidia's
California subpoena — plus a world map with eight datelines, six feature
cards, twelve one-line briefings and a markets strip.

Drawn entirely with Pillow; no network, no external assets, no clock:
running it twice writes byte-identical output. If Pillow is not
available in the sandbox, the pre-rendered entry.png shipped next to
this file (drawn by this same program) is copied instead, so the run
still produces the same bytes.
"""
import os
import shutil

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - sandbox without Pillow
    Image = None

SIDE = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
TARGET = os.path.join(OUT_DIR, "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# ---- palette -------------------------------------------------------------
PAPER = (247, 242, 230)
PAGE_CARD = (255, 253, 247)
INK = (26, 26, 26)
BODY = (60, 60, 58)
NAVY = (18, 38, 64)
CRIMSON = (164, 28, 32)
GOLD = (184, 136, 28)
SLATE = (92, 90, 82)
RULE = (200, 190, 164)
OCEAN = (168, 197, 219)
LAND = (140, 161, 122)
LAND_EDGE = (94, 116, 82)
PIN = (178, 34, 34)

MARGIN = 30
CONTENT_W = SIDE - 2 * MARGIN

# ---- copy ----------------------------------------------------------------
LEAD = {
    "kicker": "LEAD STORY  ·  SHENZHEN, CHINA",
    "headline": "Trump, Xi and Putin hold first three-way summit in Shenzhen",
    "deck": "Ninety minutes at Kylin Villa end in a joint declaration — "
            "\u201ca nuclear war cannot be won and must never be fought\u201d — "
            "with nuclear risk talks, UN reform and more refined-oil "
            "supply. No deal on Ukraine.",
}

# (x, y, legend label) — pins are numbered on the map; the legend below it
# names each one. Coordinates are my own rough stylised world map.
PINS = [
    (862, 352, "SHENZHEN — three-way summit"),
    (500, 342, "THE HAGUE — genocide ruling"),
    (216, 348, "NEW YORK — markets fall"),
    (624, 378, "RIYADH — tower hit by missile"),
    (592, 340, "KERCH — bridge struck again"),
    (884, 340, "TOKYO — 13,000 protest"),
    (430, 344, "GREENLAND — U.S. access, 109–0"),
    (150, 360, "LAS VEGAS — Grand Prix"),
]

CARDS = [
    ("THE HAGUE", "World Court: Myanmar guilty of Rohingya genocide",
     "First ruling of its kind against a state over the 2017 campaign; "
     "refugees in Bangladesh cheer."),
    ("NEW YORK", "Markets tumble: S&P 500 falls 2.02%",
     "A fifth straight loss; the Dow drops 1,101 points, below 50,000; "
     "the Nasdaq falls 2.25%."),
    ("RIYADH", "Houthi missile damages Riyadh's tallest tower",
     "80-storey PIF Tower hit on 19 Nov; no injuries reported. "
     "Houthis claim four Saudi targets."),
    ("KYIV", "Ukraine hits Kerch Bridge a third time in four days",
     "Putin vows a harsher response; allies meet in Berlin, ready to "
     "talk — no Yalta-style deal."),
    ("LOS ANGELES", "GTA 6 launch: $2.36bn on day one",
     "Sensor Tower: 24.6m copies in 24 hours — the biggest game launch "
     "ever. Metacritic: 99."),
    ("SANTA CLARA", "Nvidia faces California subpoena over chips",
     "State AG probes the chipmaker as the U.S. approves Nvidia and AMD "
     "chip sales to China."),
]

BRIEFS = [
    ("SAN SALVADOR", "Bukele expected to formalise a third-term bid."),
    ("COPENHAGEN", "Denmark backs U.S. access to Greenland, 109–0."),
    ("TOKYO", "13,000 protest in Tokyo against the Takaichi government."),
    ("MENLO PARK", "Meta reviews its 2030 climate goals."),
    ("LAS VEGAS", "Formula 1 races under the lights on the Strip."),
    ("WASHINGTON", "White House fires the national cyber chief."),
    ("WASHINGTON", "Senate rejects the war-powers resolution, 48–51."),
    ("BEIJING", "U.S. approves sale of ~880,000 AI chips to Chinese firms."),
    ("BERLIN", "Allies meet, ready to talk to Russia; no Yalta-style deal."),
    ("DHAKA", "Rohingya refugees in Bangladesh cheer the ICJ ruling."),
    ("SHENZHEN", "Summit ends with no agreement on Ukraine."),
    ("NEW YORK", "Anthropic IPO values the AI firm at about $1.3tn."),
]

MARKETS = [
    "S&P 500 \u25bc2.02%",
    "DOW \u22121,101 (\u22122.19%)",
    "NASDAQ \u25bc2.25%",
    "NIKKEI \u25bc4.1%",
    "ANT $97.17 \u25b217% (IPO $83)",
]

FOOTER = ("All events of Friday 20 November 2026  ·  Sources: Reuters, AP, "
          "WSJ, CNN, The Times, BBC, Sensor Tower")


# ---- helpers -------------------------------------------------------------
def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, face, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    out = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=face) <= max_w:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def fit_lines(draw, text, face, max_w, max_lines):
    """Wrap to at most max_lines, trimming the last line with an ellipsis."""
    lines = wrap_text(draw, text, face, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + " \u2026", font=face) > max_w:
        lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
    lines[-1] = (lines[-1] + " \u2026").strip()
    return lines


def centred(draw, y, text, face, fill):
    w = draw.textlength(text, font=face)
    draw.text(((SIDE - w) / 2, y), text, font=face, fill=fill)


def section_head(draw, y, text):
    face = load(SANS_B, 14)
    draw.text((MARGIN, y), text, font=face, fill=NAVY)
    w = draw.textlength(text, font=face)
    draw.rectangle([MARGIN, y + 21, MARGIN + w, y + 24], fill=GOLD)


def draw_masthead(draw):
    draw.rectangle([0, 0, SIDE, 3], fill=NAVY)
    title = load(SERIF_B, 50)
    centred(draw, 16, "THE WORLD IN ONE PAGE", title, NAVY)
    date_face = load(SANS_B, 20)
    centred(draw, 80, "FRIDAY,  20 NOVEMBER 2026", date_face, CRIMSON)
    tag_face = load(SANS, 13)
    centred(draw, 106,
            "O N E   D A Y   ·   O N E   P A G E   ·   T H E   W O R L D ' S   N E W S",
            tag_face, SLATE)
    draw.rectangle([MARGIN, 130, SIDE - MARGIN, 133], fill=NAVY)
    draw.rectangle([MARGIN, 135, SIDE - MARGIN, 136], fill=GOLD)


def draw_lead(draw):
    y = 150
    draw.rectangle([MARGIN, y, MARGIN + 5, y + 132], fill=CRIMSON)
    x = MARGIN + 18
    kicker = load(SANS_B, 13)
    draw.text((x, y), LEAD["kicker"], font=kicker, fill=CRIMSON)
    head = load(SERIF_B, 30)
    lines = fit_lines(draw, LEAD["headline"], head, CONTENT_W - 18, 2)
    yy = y + 20
    for line in lines:
        draw.text((x, yy), line, font=head, fill=INK)
        yy += 36
    deck = load(SANS, 15)
    dlines = fit_lines(draw, LEAD["deck"], deck, CONTENT_W - 18, 2)
    yy += 2
    for line in dlines:
        draw.text((x, yy), line, font=deck, fill=BODY)
        yy += 20


def draw_map(draw):
    top = 326
    bottom = 470
    section_head(draw, 304, "WHERE IT HAPPENED")
    draw.rectangle([MARGIN, top, SIDE - MARGIN, bottom], fill=OCEAN,
                   outline=RULE, width=1)
    continents = [
        # North America
        [(78, 330), (140, 318), (215, 320), (268, 334), (284, 352),
         (254, 370), (224, 378), (196, 396), (152, 400), (106, 390),
         (72, 368), (60, 346)],
        # South America
        [(242, 400), (286, 396), (310, 408), (300, 428), (276, 446),
         (252, 436), (240, 416)],
        # Europe
        [(472, 322), (526, 314), (560, 322), (574, 334), (546, 348),
         (506, 348), (480, 336)],
        # Africa
        [(480, 358), (546, 354), (580, 368), (600, 390), (576, 422),
         (532, 436), (496, 414), (478, 384)],
        # Asia
        [(582, 316), (682, 308), (800, 312), (904, 322), (934, 340),
         (904, 362), (860, 378), (800, 390), (730, 394), (662, 384),
         (616, 360), (586, 336)],
        # Japan
        [(882, 330), (898, 336), (892, 350), (876, 346)],
        # Oceania
        [(800, 418), (864, 412), (894, 424), (874, 442), (826, 442),
         (802, 430)],
    ]
    for poly in continents:
        draw.polygon(poly, fill=LAND, outline=LAND_EDGE)
    num_face = load(SANS_B, 11)
    for num, (px, py, _label) in enumerate(PINS, start=1):
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=PIN,
                     outline=(255, 255, 255), width=2)
        digit = str(num)
        dw = draw.textlength(digit, font=num_face)
        draw.text((px - dw / 2, py - 8), digit, font=num_face,
                  fill=(255, 255, 255))
    legend_face = load(SANS, 11)
    legend = "   ·   ".join("%d %s" % (n, label)
                            for n, (_x, _y, label) in enumerate(PINS, start=1))
    legend_lines = fit_lines(draw, legend, legend_face, CONTENT_W, 2)
    yy = 476
    for line in legend_lines:
        draw.text((MARGIN, yy), line, font=legend_face, fill=NAVY)
        yy += 14


def draw_cards(draw):
    section_head(draw, 516, "SIX STORIES THAT DEFINED THE DAY")
    gap = 13
    cw = (CONTENT_W - 2 * gap) // 3
    rows = [(538, 646), (654, 762)]
    for idx, (kicker, title, body) in enumerate(CARDS):
        col = idx % 3
        row = idx // 3
        y0, y1 = rows[row]
        x0 = MARGIN + col * (cw + gap)
        x1 = x0 + cw
        draw.rectangle([x0, y0, x1, y1], fill=PAGE_CARD, outline=RULE, width=1)
        draw.rectangle([x0, y0, x1, y0 + 3], fill=NAVY)
        kx = x0 + 12
        kick = load(SANS_B, 11)
        draw.text((kx, y0 + 10), kicker, font=kick, fill=CRIMSON)
        head = load(SERIF_B, 16)
        lines = fit_lines(draw, title, head, cw - 24, 2)
        yy = y0 + 28
        for line in lines:
            draw.text((kx, yy), line, font=head, fill=INK)
            yy += 20
        body_face = load(SANS, 12)
        blines = fit_lines(draw, body, body_face, cw - 24, 3)
        yy += 4
        for line in blines:
            draw.text((kx, yy), line, font=body_face, fill=BODY)
            yy += 15


def draw_briefs(draw):
    section_head(draw, 774, "THE DAY IN BRIEF")
    col_w = (CONTENT_W - 24) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + 24
    row_h = 22
    y_start = 798
    bold = load(SANS_B, 13)
    plain = load(SANS, 13)
    for idx, (place, text) in enumerate(BRIEFS):
        col = 0 if idx < 6 else 1
        row = idx if idx < 6 else idx - 6
        x = left_x if col == 0 else right_x
        y = y_start + row * row_h
        head = place + " — "
        hw = draw.textlength(head, font=bold)
        draw.text((x, y), head, font=bold, fill=NAVY)
        body_lines = fit_lines(draw, text, plain, col_w - hw, 1)
        draw.text((x + hw, y), body_lines[0], font=plain, fill=INK)


def draw_markets(draw):
    y0, y1 = 942, 976
    draw.rectangle([MARGIN, y0, SIDE - MARGIN, y1], fill=NAVY)
    items = "   ·   ".join(MARKETS)
    face = None
    for size in (14, 13, 12):
        face = load(SANS_B, size)
        if draw.textlength(items, font=face) <= CONTENT_W - 16:
            break
    w = draw.textlength(items, font=face)
    draw.text(((SIDE - w) / 2, y0 + 10), items, font=face,
              fill=(255, 255, 255))


def draw_footer(draw):
    face = load(SANS, 11)
    centred(draw, 988, FOOTER, face, SLATE)


def draw_image():
    canvas = Image.new("RGB", (SIDE, SIDE), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw_masthead(draw)
    draw_lead(draw)
    draw_map(draw)
    draw_cards(draw)
    draw_briefs(draw)
    draw_markets(draw)
    draw_footer(draw)
    return canvas


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    if Image is None:
        # No Pillow in this sandbox: ship the pre-rendered image.
        shutil.copyfile(os.path.join(HERE, "entry.png"), TARGET)
    else:
        draw_image().save(TARGET, format="PNG")
    with open(TARGET, "rb") as fh:
        blob = fh.read()
    import hashlib
    print("wrote %s (%d bytes) sha256=%s"
          % (TARGET, len(blob), hashlib.sha256(blob).hexdigest()))


if __name__ == "__main__":
    build()
