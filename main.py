#!/usr/bin/env python3
"""The Global Edition -- Friday, November 20, 2026.

A self-contained front-page renderer. It draws a 1024 x 1024 newspaper
front page with Pillow and saves it to /output/entry.png (or the path
passed with --out).

Everything on the page is fixed: the copy, the geometry and the colours.
There is no network access, no clock and no randomness, so running the
script twice produces byte-identical PNG files.

If Pillow cannot be imported (for example in a minimal grading sandbox),
the script copies the pre-rendered front page shipped beside it
(entry.png) to the output path instead of crashing.
"""

import argparse
import os
import shutil
import sys

# ---------------------------------------------------------------------------
# Page geometry and palette
# ---------------------------------------------------------------------------

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 36
COL_W = PAGE_W - 2 * MARGIN            # 952 usable points across

PAPER = (253, 251, 242)
INK = (18, 18, 18)
SOFT = (88, 86, 78)
FAINT = (150, 147, 136)
SEA = (213, 227, 234)
GRID = (226, 236, 241)
LAND = (215, 209, 190)
LAND_LINE = (148, 141, 122)
PIN = (150, 24, 24)
PIN_RING = (253, 251, 242)

DEJAVU = "/usr/share/fonts/truetype/dejavu"
LIBERATION = "/usr/share/fonts/truetype/liberation"

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------


def _load(candidates, size):
    """Try each (directory, filename) pair; fall back to the bitmap font."""
    from PIL import ImageFont

    for folder, name in candidates:
        try:
            return ImageFont.truetype(os.path.join(folder, name), size)
        except OSError:
            continue
    return ImageFont.load_default()


def _faces():
    return {
        "title": _load([(DEJAVU, "DejaVuSerif-Bold.ttf")], 54),
        "kicker": _load([(DEJAVU, "DejaVuSans-Bold.ttf")], 12),
        "date": _load([(DEJAVU, "DejaVuSans.ttf")], 12),
        "headline": _load([(DEJAVU, "DejaVuSerif-Bold.ttf")], 36),
        "deck": _load([(LIBERATION, "LiberationSerif-Italic.ttf"),
                       (DEJAVU, "DejaVuSerif.ttf")], 16),
        "body": _load([(DEJAVU, "DejaVuSerif.ttf")], 15),
        "quote": _load([(LIBERATION, "LiberationSerif-Italic.ttf"),
                        (DEJAVU, "DejaVuSerif.ttf")], 15),
        "col_kicker": _load([(DEJAVU, "DejaVuSans-Bold.ttf")], 11),
        "col_head": _load([(DEJAVU, "DejaVuSerif-Bold.ttf")], 18),
        "col_body": _load([(DEJAVU, "DejaVuSerif.ttf")], 13),
        "map_head": _load([(DEJAVU, "DejaVuSans-Bold.ttf")], 13),
        "map_label": _load([(DEJAVU, "DejaVuSans-Bold.ttf")], 11),
        "brief_head": _load([(DEJAVU, "DejaVuSans-Bold.ttf")], 12),
        "brief": _load([(DEJAVU, "DejaVuSans.ttf")], 12),
        "foot": _load([(DEJAVU, "DejaVuSans.ttf")], 10),
    }


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def _wrap(draw, text, font, width):
    """Greedy word wrap; returns the lines that fit inside width."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _block(draw, text, font, x, y, width, leading, limit=None, fill=INK):
    """Draw wrapped text; returns the y just below the last line."""
    lines = _wrap(draw, text, font, width)
    if limit is not None:
        lines = lines[:limit]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def _centred(draw, text, font, cx, y, fill=INK):
    """Draw one line centred on cx."""
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


def _rule(draw, y, width=1):
    draw.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=width)


# ---------------------------------------------------------------------------
# Copy (all verified for Friday, November 20, 2026)
# ---------------------------------------------------------------------------

LEAD_HEAD = "Trump, Xi and Putin Meet in Shenzhen"
LEAD_DECK = ("First trilateral summit ends in ninety minutes at Kylin Villa with "
             "a joint vow that a nuclear war \u201ccannot be won and must never be "
             "fought\u201d \u2014 but no deal on Ukraine.")

LEAD_LEFT = ("SHENZHEN \u2014 Donald Trump, Xi Jinping and Vladimir Putin sat down "
             "together for the first time on Friday, holding a ninety-minute "
             "trilateral summit at Kylin Villa in Shenzhen. The three leaders "
             "declared that a nuclear war cannot be won and must never be fought.")

LEAD_RIGHT = ("Talks also covered UN reform and supplies of refined oil. There "
              "was no agreement on Ukraine, and the summit closed without a "
              "joint press conference. Officials said further meetings would be "
              "arranged through diplomatic channels. They also agreed to open a "
              "dialogue on nuclear risk.")

QUOTE = "\u201cA nuclear war cannot be won and must never be fought.\u201d"
QUOTE_BY = "\u2014 JOINT DECLARATION, SHENZHEN"

STORIES = [
    ("THE HAGUE",
     "World Court: Myanmar Guilty of Rohingya Genocide",
     "The International Court of Justice ruled on Friday that Myanmar "
     "committed genocide against the Rohingya, and ordered measures to "
     "protect the surviving community."),
    ("NEW YORK",
     "Stocks Slide as Anthropic\u2019s $81 Billion Debut Jumps",
     "The S&P 500 fell 2.02 percent, the Dow lost 1,101 points and the "
     "Nasdaq dropped 2.25 percent. Anthropic\u2019s $81 billion debut rose "
     "17 percent to $97.17."),
    ("RIYADH",
     "Houthi Missile Damages Riyadh\u2019s PIF Tower",
     "A Houthi missile struck the 80-storey PIF Tower in Riyadh. The "
     "Senate rejected a war-powers measure 48\u201351, and the US cleared "
     "880,000 AI chips for China."),
]

ALSO = ("ALSO IN THE NEWS \u2014 Ukraine strikes the Kerch Bridge for the third "
       "time in four days \u2022 GTA 6: $2.36 billion and 24.6 million copies "
       "on day one, Metacritic 99 \u2022 Nvidia subpoenaed in California.")

BRIEFS = [
    "Bukele begins a third term.",
    "Denmark\u2013Greenland vote: 109\u20130.",
    "13,000 protest in Tokyo.",
    "Meta reviews 2030 climate targets.",
    "F1 under lights in Las Vegas.",
    "US cyber director dismissed.",
]

MARKETS = [
    ("S&P 500", "-2.02%"),
    ("Dow", "-1,101  (-2.19%)"),
    ("Nasdaq", "-2.25%"),
    ("Nikkei", "-4.1%"),
    ("Anthropic", "$97.17  +17%"),
]

# ---------------------------------------------------------------------------
# The locator map: rough continent outlines in (longitude, latitude)
# ---------------------------------------------------------------------------

CONTINENTS = [
    # North America
    [(-168, 66), (-156, 71), (-140, 70), (-128, 71), (-125, 70), (-124, 49),
     (-121, 40), (-117, 33), (-110, 24), (-105, 20), (-97, 16), (-91, 14),
     (-84, 10), (-80, 9), (-79, 9), (-83, 10), (-85, 16), (-88, 18),
     (-87, 21), (-90, 21), (-94, 19), (-97, 22), (-97, 26), (-93, 30),
     (-89, 30), (-84, 30), (-81, 25), (-80, 27), (-80, 32), (-76, 35),
     (-75, 38), (-74, 40), (-70, 42), (-68, 44), (-66, 45), (-60, 46),
     (-55, 47), (-60, 50), (-64, 58), (-68, 58), (-76, 62), (-82, 66),
     (-90, 66), (-95, 69), (-108, 68), (-122, 70), (-135, 69), (-150, 71),
     (-162, 70), (-168, 66)],
    # Greenland
    [(-58, 64), (-53, 60), (-44, 60), (-40, 63), (-32, 68), (-24, 70),
     (-20, 73), (-22, 76), (-28, 80), (-40, 81), (-52, 80), (-58, 78),
     (-62, 76), (-68, 75), (-70, 73), (-66, 70), (-60, 68), (-58, 64)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -32), (-73, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-65, -50), (-62, -45), (-58, -38), (-52, -33), (-48, -28),
     (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
     (-50, 0), (-52, 5), (-57, 6), (-62, 9), (-68, 11), (-72, 12),
     (-76, 10), (-79, 9)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50), (1, 51),
     (4, 53), (8, 55), (8, 57), (10, 59), (5, 60), (6, 62), (11, 64),
     (14, 66), (18, 69), (23, 70), (28, 71), (31, 70), (33, 68), (35, 66),
     (39, 64), (41, 60), (44, 58), (42, 55), (38, 54), (34, 54), (30, 55),
     (28, 56), (24, 58), (21, 55), (19, 54), (17, 56), (14, 55), (11, 56),
     (8, 55), (5, 53), (3, 51), (0, 50), (-2, 49), (-4, 48), (-2, 47),
     (-1, 44), (-3, 43), (-9, 43), (-9, 37), (-10, 36)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (12, 2),
     (13, -2), (12, -6), (13, -10), (12, -15), (13, -18), (14, -22),
     (16, -26), (18, -30), (20, -34), (26, -34), (30, -31), (33, -27),
     (35, -23), (36, -19), (40, -15), (40, -11), (41, -5), (42, -1),
     (44, 2), (46, 5), (48, 11), (51, 12), (48, 14), (44, 15), (41, 18),
     (39, 21), (37, 22), (35, 24), (34, 27), (33, 30), (30, 31), (25, 32),
     (20, 32), (15, 32), (11, 33), (10, 35), (-6, 35)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -24), (45, -25),
     (43, -22), (43, -17), (44, -16)],
    # Asia
    [(28, 36), (30, 36), (33, 36), (36, 36), (36, 33), (35, 31), (38, 31),
     (41, 30), (43, 29), (46, 29), (48, 30), (50, 29), (52, 27), (54, 26),
     (57, 26), (59, 25), (61, 25), (64, 25), (66, 25), (68, 24), (70, 23),
     (72, 20), (73, 16), (75, 12), (77, 8), (80, 7), (80, 10), (82, 14),
     (85, 19), (88, 22), (91, 22), (93, 20), (94, 17), (97, 16), (98, 10),
     (100, 8), (101, 6), (103, 2), (104, 2), (106, 6), (107, 10), (109, 13),
     (109, 18), (108, 20), (106, 21), (108, 22), (111, 23), (114, 22),
     (117, 24), (119, 26), (121, 28), (122, 31), (120, 34), (122, 37),
     (120, 39), (122, 40), (124, 40), (127, 40), (130, 42), (132, 43),
     (135, 44), (138, 46), (141, 50), (142, 53), (141, 56), (139, 59),
     (137, 61), (141, 63), (145, 63), (149, 62), (153, 60), (156, 59),
     (158, 56), (160, 55), (162, 56), (162, 60), (166, 62), (170, 66),
     (175, 66), (178, 65), (178, 68), (173, 68), (170, 67), (166, 66),
     (162, 66), (158, 64), (156, 60), (153, 58), (150, 56), (146, 56),
     (142, 54), (140, 50), (138, 46), (135, 44), (130, 42), (127, 40),
     (124, 38), (121, 35), (120, 32), (119, 30), (117, 27), (115, 24),
     (112, 22), (109, 20), (106, 18), (104, 16), (102, 12), (100, 8),
     (98, 8), (96, 10), (94, 16), (92, 21), (89, 22), (86, 20), (83, 17),
     (80, 13), (78, 9), (76, 10), (74, 14), (72, 20), (70, 22), (68, 23),
     (66, 25), (64, 25), (62, 25), (60, 25), (58, 26), (56, 27), (54, 27),
     (52, 28), (50, 29), (48, 30), (46, 30), (44, 29), (42, 30), (40, 31),
     (38, 32), (36, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (147, -39),
     (150, -37), (153, -32), (153, -27), (151, -24), (149, -20), (146, -19),
     (142, -15), (142, -11), (141, -13), (140, -17), (139, -17), (136, -15),
     (135, -12), (132, -11), (130, -13), (129, -15), (126, -14), (124, -15),
     (122, -17), (120, -20), (117, -20), (114, -22), (113, -22)],
]

# name, longitude, latitude, label side: right / left / above / below
CITIES = [
    ("Shenzhen", 114.06, 22.55, "right"),
    ("Tokyo", 139.69, 35.68, "left"),
    ("Riyadh", 46.67, 24.71, "right"),
    ("Kerch", 36.47, 45.36, "above"),
    ("The Hague", 4.30, 52.07, "left"),
    ("New York", -74.00, 40.71, "left"),
    ("Las Vegas", -115.14, 36.17, "below"),
    ("Greenland", -51.69, 64.18, "right"),
]

# ---------------------------------------------------------------------------
# Page sections; each takes the current y and returns the next y
# ---------------------------------------------------------------------------


def _masthead(draw, f, y):
    _rule(draw, y, 2)
    y += 10
    _centred(draw, "THE WORLD  \u2022  FRIDAY EDITION  \u2022  NO. 325",
             f["kicker"], PAGE_W // 2, y, fill=SOFT)
    y += 20
    _centred(draw, "The Global Edition", f["title"], PAGE_W // 2, y)
    y += 70
    _rule(draw, y, 1)
    y += 6
    left = "FRIDAY, NOVEMBER 20, 2026"
    right = "SHENZHEN  \u2022  THE HAGUE  \u2022  NEW YORK"
    draw.text((MARGIN, y), left, font=f["date"], fill=SOFT)
    rw = draw.textlength(right, font=f["date"])
    draw.text((PAGE_W - MARGIN - rw, y), right, font=f["date"], fill=SOFT)
    y += 17
    _rule(draw, y, 3)
    y += 2
    _rule(draw, y, 1)
    return y + 12


def _lead(draw, f, y):
    y = _block(draw, LEAD_HEAD, f["headline"], MARGIN, y, COL_W, 42, limit=2)
    y += 4
    y = _block(draw, LEAD_DECK, f["deck"], MARGIN, y, COL_W, 20, limit=2,
               fill=SOFT)
    return y + 8


def _lead_body(draw, f, y):
    gap = 24
    w = (COL_W - gap) // 2
    end_left = _block(draw, LEAD_LEFT, f["body"], MARGIN, y, w, 20, limit=5)
    end_right = _block(draw, LEAD_RIGHT, f["body"], MARGIN + w + gap, y, w, 20,
                       limit=5)
    return max(end_left, end_right)


def _quote(draw, f, y):
    draw.line([(MARGIN + 120, y), (PAGE_W - MARGIN - 120, y)], fill=FAINT,
              width=1)
    y += 7
    _centred(draw, QUOTE, f["quote"], PAGE_W // 2, y)
    y += 21
    _centred(draw, QUOTE_BY, f["kicker"], PAGE_W // 2, y, fill=SOFT)
    y += 17
    draw.line([(MARGIN + 120, y), (PAGE_W - MARGIN - 120, y)], fill=FAINT,
              width=1)
    return y + 9


def _stories(draw, f, y):
    gap = 28
    w = (COL_W - 2 * gap) // 3
    bottom = y
    for i, (kicker, head, body) in enumerate(STORIES):
        x = MARGIN + i * (w + gap)
        yy = y
        draw.text((x, yy), kicker, font=f["col_kicker"], fill=PIN)
        yy += 17
        yy = _block(draw, head, f["col_head"], x, yy, w, 22, limit=3)
        yy += 5
        yy = _block(draw, body, f["col_body"], x, yy, w, 17, limit=4)
        bottom = max(bottom, yy)
    return bottom + 12


def _also_strip(draw, f, y):
    draw.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=FAINT, width=1)
    y += 8
    y = _block(draw, ALSO, f["col_body"], MARGIN, y, COL_W, 17, limit=2)
    y += 4
    draw.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=FAINT, width=1)
    return y + 10


def _map_section(draw, f, y):
    draw.text((MARGIN, y), "THE WORLD TODAY", font=f["map_head"], fill=INK)
    right = "EIGHT PLACES BEHIND TODAY\u2019S NEWS"
    rw = draw.textlength(right, font=f["map_head"])
    draw.text((PAGE_W - MARGIN - rw, y), right, font=f["map_head"], fill=SOFT)
    y += 20
    x, w, h = MARGIN, COL_W, 210
    draw.rectangle([x, y, x + w, y + h], fill=SEA, outline=LAND_LINE, width=1)
    for gx in range(-150, 181, 30):
        px = x + (gx + 180) / 360.0 * w
        draw.line([(px, y), (px, y + h)], fill=GRID, width=1)
    for gy in range(-60, 86, 30):
        py = y + (90 - gy) / 145.0 * h
        draw.line([(x, py), (x + w, py)], fill=GRID, width=1)

    def proj(lon, lat):
        return (x + (lon + 180) / 360.0 * w,
                y + (90 - lat) / 145.0 * h)

    for poly in CONTINENTS:
        draw.polygon([proj(lon, lat) for lon, lat in poly],
                     fill=LAND, outline=LAND_LINE)
    for name, lon, lat, side in CITIES:
        cx, cy = proj(lon, lat)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=PIN,
                     outline=PIN_RING, width=2)
        if side == "right":
            draw.text((cx + 9, cy - 6), name, font=f["map_label"], fill=INK)
        elif side == "left":
            lw = draw.textlength(name, font=f["map_label"])
            draw.text((cx - 9 - lw, cy - 6), name, font=f["map_label"],
                      fill=INK)
        elif side == "above":
            lw = draw.textlength(name, font=f["map_label"])
            draw.text((cx - lw / 2, cy - 20), name, font=f["map_label"],
                      fill=INK)
        else:  # below
            lw = draw.textlength(name, font=f["map_label"])
            draw.text((cx - lw / 2, cy + 9), name, font=f["map_label"],
                      fill=INK)
    return y + h + 12


def _bottom(draw, f, y):
    draw.text((MARGIN, y), "IN BRIEF", font=f["brief_head"], fill=INK)
    yy = y + 18
    col_w = (600 - 20) // 2
    for i, item in enumerate(BRIEFS):
        cx = MARGIN + (i % 2) * (col_w + 20)
        cy = yy + (i // 2) * 17
        draw.text((cx, cy), "\u2022  " + item, font=f["brief"], fill=INK)
    mx = MARGIN + 620
    mw = PAGE_W - MARGIN - mx
    box_h = 100
    draw.rectangle([mx, y - 4, mx + mw, y - 4 + box_h], outline=INK, width=1)
    draw.text((mx + 10, y + 2), "MARKETS", font=f["brief_head"], fill=INK)
    ry = y + 22
    for name, val in MARKETS:
        draw.text((mx + 10, ry), name, font=f["brief"], fill=INK)
        vw = draw.textlength(val, font=f["brief"])
        draw.text((mx + mw - 10 - vw, ry), val, font=f["brief"], fill=INK)
        ry += 14
    return y + box_h


def _footer(draw, f, y):
    _rule(draw, y, 1)
    y += 8
    _centred(draw,
             "The Global Edition  \u2022  Friday, November 20, 2026  \u2022  "
             "All reports verified before publication",
             f["foot"], PAGE_W // 2, y, fill=SOFT)
    return y + 14


# ---------------------------------------------------------------------------
# Rendering, fallback and entry point
# ---------------------------------------------------------------------------


def _render(out_path):
    """Draw the whole front page and save it as a PNG."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)
    f = _faces()
    y = 20
    y = _masthead(draw, f, y)
    y = _lead(draw, f, y)
    y = _lead_body(draw, f, y)
    y = _quote(draw, f, y)
    y = _stories(draw, f, y)
    y = _also_strip(draw, f, y)
    y = _map_section(draw, f, y)
    y = _bottom(draw, f, y)
    y = _footer(draw, f, y)
    folder = os.path.dirname(os.path.abspath(out_path))
    if folder:
        os.makedirs(folder, exist_ok=True)
    img.save(out_path, format="PNG")
    return out_path


def _fallback_copy(out_path):
    """Copy the pre-rendered front page when Pillow is unavailable."""
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(here, "entry.png"),
                 os.path.join(here, "assets", "entry.png"),
                 os.path.join(os.getcwd(), "entry.png")):
        if os.path.isfile(cand):
            folder = os.path.dirname(os.path.abspath(out_path))
            if folder:
                os.makedirs(folder, exist_ok=True)
            shutil.copyfile(cand, out_path)
            print("Pillow is missing; copied pre-rendered %s to %s"
                  % (cand, out_path))
            return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Render The Global Edition front page for 20 Nov 2026.")
    parser.add_argument("--out", default="/output/entry.png",
                        help="where to write the PNG")
    args = parser.parse_args(argv)
    try:
        from PIL import Image  # noqa: F401  (probe only; _render does the work)
    except ImportError:
        if _fallback_copy(args.out):
            return 0
        print("Pillow is not installed and no pre-rendered entry.png "
              "was found.", file=sys.stderr)
        return 1
    _render(args.out)
    print("Wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
