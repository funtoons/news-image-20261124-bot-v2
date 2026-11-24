#!/usr/bin/env python3
"""News24 v2 - "THE WORLD TODAY", Tuesday 24 November 2026.

Draws a one-page newspaper (1024x1024) with a hand-written 5x7 pixel
font. Standard library only: the PNG encoder is struct + zlib.

Structure: a day-tag system (every story carries a pill showing WHEN it
happened: SAT 21 / SUN 22 / MON 23 / TUE 24), a data-picture hero on the
Asian markets rally after Nvidia reinstated Jensen Huang, three
second-row stories (Hormuz, Ukraine, Mediterranean) and four third-row
cells (EU sanctions, COP31, Gaza, Korea).

All numbers verified against live reporting on 24 Nov 2026 (closes):
KOSPI +6.3%, Nikkei +3.9%, Taiwan +9.1%, Nasdaq +6.5%, Nvidia +31.5%
to $165.05, Brent $88.71 (-0.7%, near three-month low). CENTCOM had not
responded to the IRGC mine claim at build time, so Hormuz stays
attributed and UNVERIFIED. No bigger Tuesday event had broken, so the
markets chart stays the hero.

Deterministic and offline: two runs write byte-identical files.
Writes entry.png to MAKEFUN_OUTPUT_DIR, else /output, else ./out.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (244, 239, 227)
INK = (20, 20, 20)
RED = (179, 32, 31)
NAVY = (27, 63, 107)
AMBER = (217, 162, 27)
RULE = (138, 133, 119)
SEA = (47, 111, 168)
PALE = (207, 201, 184)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 pixel font. Each glyph is 7 rows; each row is 5 bits, MSB left.
# Space is all zeros. Only the characters this newspaper uses are here.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "\u00b7": (0, 0, 0, 0x0C, 0x0C, 0, 0),
}


def text_width(text, s):
    """Pixel width of text at scale s (6s per character)."""
    return len(text) * 6 * s


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split(" ")
        line = ""
        for word in words:
            if line and len(line) + 1 + len(word) > max_chars:
                lines.append(line)
                line = word
            elif line:
                line = line + " " + word
            else:
                line = word
        if line:
            lines.append(line)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def fill_rect(self, x, y, w, h, color):
        r, g, b = color
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes((r, g, b)) * (x1 - x0)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:base + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def border(self, x, y, w, h, color, thick=2):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def text(self, x, y, s, color, txt):
        """Draw text at scale s; one char is 6s wide, 7s tall."""
        for ci, ch in enumerate(txt):
            glyph = FONT.get(ch)
            if glyph is None:
                raise ValueError("no glyph for %r" % ch)
            cx = x + ci * 6 * s
            for row in range(7):
                bits = glyph[row]
                if not bits:
                    continue
                for col in range(5):
                    if bits & (0x10 >> col):
                        self.fill_rect(cx + col * s, y + row * s, s, s, color)

    def text_centre(self, cx, y, s, color, txt):
        self.text(cx - text_width(txt, s) // 2, y, s, color, txt)


def pill(cv, x, y, s, txt, fill=None, fg=INK, outline=None):
    """A day/attribution tag. Returns its pixel width."""
    pad_x = 4 * s
    w = text_width(txt, s) + 2 * pad_x
    h = 11 * s
    if fill is not None:
        cv.fill_rect(x, y, w, h, fill)
    if outline is not None:
        cv.border(x, y, w, h, outline, thick=2)
    cv.text(x + pad_x, y + 2 * s, s, fg, txt)
    return w


# ---------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, cv):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    row_bytes = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * row_bytes:(y + 1) * row_bytes]
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- masthead
def draw_masthead(cv):
    cv.text_centre(W // 2, 18, 9, INK, "THE WORLD TODAY")
    cv.hline(24, 98, 976, INK, thick=2)
    cv.hline(24, 104, 976, INK, thick=2)


def draw_dateline(cv):
    # Left: the date, red. Right: a two-line tag legend — the label on top,
    # the three day pills below it (the bar is too narrow for all of them
    # on one line at these scales).
    cv.text(24, 116, 4, RED, "TUESDAY 24 NOVEMBER 2026")
    cv.text(1000 - text_width("TAGS = WHEN IT HAPPENED", 2), 111, 2, INK,
            "TAGS = WHEN IT HAPPENED")
    pw = 88  # pill width for a 6-char tag at scale 2
    x = 1000 - (3 * pw + 2 * 8)
    pill(cv, x, 127, 2, "SUN 22", fill=None, fg=RULE, outline=RULE)
    pill(cv, x + pw + 8, 127, 2, "MON 23", fill=NAVY, fg=WHITE)
    pill(cv, x + 2 * pw + 16, 127, 2, "TUE 24", fill=RED, fg=WHITE)
    cv.hline(24, 152, 976, RULE, thick=2)


# ---------------------------------------------------------------- hero
def draw_hero(cv):
    # Tag row.
    pill(cv, 24, 158, 3, "TUE 24", fill=RED, fg=WHITE)
    cv.text(172, 164, 3, INK, "MARKETS \u00b7 ASIA")
    # Headline.
    cv.text(24, 198, 8, INK, "HUANG'S COMEBACK")
    cv.text(24, 258, 8, INK, "SENDS ASIA SOARING")
    # Deck.
    cv.text(24, 330, 3, INK, "NVIDIA'S NEAR-$1TN REBOUND GOES GLOBAL")
    # Bar chart, one common scale: 380 px = 31.5%.
    bar_x = 132
    max_w = 380
    scale = max_w / 31.5

    def bar_row(y, name, value, pct, color):
        cv.text(24, y + 1, 2, INK, name)
        w = max(2, int(round(pct * scale)))
        cv.fill_rect(bar_x, y, w, 16, color)
        cv.text(bar_x + w + 8, y - 1, 3, INK, value)

    cv.text(24, 362, 2, NAVY, "MONDAY, NEW YORK")
    bar_row(382, "NVIDIA", "+31.5%", 31.5, NAVY)
    bar_row(408, "NASDAQ", "+6.5%", 6.5, NAVY)
    cv.text(24, 434, 2, RED, "TUESDAY, ASIA")
    bar_row(454, "TAIWAN", "+9.1%", 9.1, RED)
    bar_row(480, "SEOUL", "+6.3%", 6.3, RED)
    bar_row(506, "TOKYO", "+3.9%", 3.9, RED)
    cv.text(24, 524, 1, RULE, "TUESDAY CLOSES. REUTERS, AP.")
    # Fact box.
    cv.border(640, 362, 360, 160, INK, thick=2)
    box_lines = [
        "MON: NVIDIA REINSTATES",
        "CEO HUANG, 11 DAYS AFTER",
        "HE QUIT. SHARES +31.5%",
        "TO $165.05.",
        "TUE: SEOUL HALTS TRADING",
        "5 MIN AS CHIPS SURGE.",
        "TUE: US BLACKLISTS MEGASPEED,",
        "FIRM AT CENTRE OF SPY PROBE.",
    ]
    for i, line in enumerate(box_lines):
        cv.text(652, 372 + i * 18, 2, INK, line)


# ---------------------------------------------------------------- visuals
def draw_tankers(cv, x, y, w, h):
    """Three small tanker silhouettes with amber flame blocks."""
    hull_w = (w - 2 * 10) // 3
    for i in range(3):
        hx = x + i * (hull_w + 10)
        hy = y + h - 18
        cv.fill_rect(hx, hy, hull_w, 12, SEA)
        # Bow: a triangle of sea blue.
        for r in range(6):
            cv.fill_rect(hx + hull_w, hy + 6 + r, 6 - r, 1, SEA)
        # Deck block + amber flame.
        cv.fill_rect(hx + 6, hy - 8, 10, 8, INK)
        cv.fill_rect(hx + 8, hy - 16, 6, 8, AMBER)
        cv.fill_rect(hx + 9, hy - 20, 4, 4, AMBER)
    cv.hline(x, y + h - 4, w, RULE, thick=2)


def draw_building(cv, x, y, w, h):
    """A five-storey block with its top-right corner knocked out."""
    cv.fill_rect(x, y, w, h, INK)
    # Window grid in paper colour.
    for floor in range(5):
        for col in range(4):
            wx = x + 8 + col * ((w - 16) // 4)
            wy = y + 6 + floor * ((h - 12) // 5)
            cv.fill_rect(wx, wy, 8, 6, PAPER)
    # Missing corner: paper-coloured triangle over the top right.
    for r in range(22):
        cv.fill_rect(x + w - 22 + r, y + r, 22 - r, 1, PAPER)
    # Amber rubble at the foot of the damage.
    cv.fill_rect(x + w - 26, y + 22, 8, 4, AMBER)
    cv.fill_rect(x + w - 18, y + 28, 6, 4, AMBER)


def draw_hull(cv, x, y, w, h):
    """A capsized hull: upside down, red keel line on top."""
    # Hull body: wide at the top (the upturned bottom), narrowing down.
    top_w = w
    bot_w = w // 2
    rows = h - 8
    for r in range(rows):
        ww = top_w - (top_w - bot_w) * r // rows
        cv.fill_rect(x + (w - ww) // 2, y + 8 + r, ww, 1, INK)
    # Red keel line along the top edge.
    cv.fill_rect(x, y + 4, w, 4, RED)
    # A small mast stub pointing down into the water.
    cv.fill_rect(x + w // 2 - 2, y + h - 8, 4, 8, INK)


def draw_down_arrow(cv, x, y, w, h, color):
    """A filled downward triangle."""
    for r in range(h):
        ww = w * (r + 1) // h
        cv.fill_rect(x + (w - ww) // 2, y + r, ww, 1, color)


# ---------------------------------------------------------------- row 2
def draw_row2(cv):
    cols = [24, 356, 688]
    inner = [c + 8 for c in cols]
    # Tag rows.
    pill(cv, inner[0], 534, 2, "TUE 24", fill=RED, fg=WHITE)
    pill(cv, inner[0] + 96, 534, 2, "UNVERIFIED", fill=None, fg=INK,
         outline=INK)
    pill(cv, inner[1], 534, 2, "MON 23", fill=NAVY, fg=WHITE)
    pill(cv, inner[2], 534, 2, "SUN 22", fill=None, fg=RULE, outline=RULE)
    pill(cv, inner[2] + 96, 534, 2, "KYIV'S CLAIM", fill=None, fg=INK,
         outline=INK)
    # Headlines, scale 4, up to 3 lines.
    headlines = [
        ["IRAN SAYS 3", "TANKERS HIT", "HORMUZ MINES"],
        ["DRONES KILL", "14 NEAR KYIV"],
        ["KYIV SAYS IT", "SANK WARSHIP", "IN BENGHAZI"],
    ]
    for ci, lines in enumerate(headlines):
        for li, line in enumerate(lines):
            cv.text(inner[ci], 566 + li * 30, 4, INK, line)
    # Visuals + big stats (zone y 664-720).
    draw_tankers(cv, inner[0], 664, 110, 56)
    cv.text(inner[0] + 122, 666, 2, INK, "BRENT")
    cv.text(inner[0] + 122, 684, 5, INK, "$88.7")
    draw_down_arrow(cv, inner[0] + 278, 690, 16, 22, RED)
    draw_building(cv, inner[1], 664, 130, 56)
    cv.text(inner[1] + 220, 684, 5, INK, "14")
    draw_hull(cv, inner[2], 668, 90, 48)
    cv.text(inner[2] + 98, 686, 4, INK, "7 DRONES")
    # Bodies, scale 2, 24 chars/line.
    bodies = [
        "GUARD NAVY CLAIM, NOT CONFIRMED. OIL AT 3-MONTH LOW. "
        "US BLOCKADE 130+ DAYS.",
        "11 DIED IN DYMER BLOCK. ZELENSKY: NEW STRIKES COMING, "
        "SEND PATRIOTS.",
        "RUSSIAN CORVETTE HIT IN LIBYAN PORT. UN WANTS PROBE.",
    ]
    for ci, body in enumerate(bodies):
        for li, line in enumerate(wrap(body, 24)):
            cv.text(inner[ci], 728 + li * 16, 2, INK, line)


# ---------------------------------------------------------------- row 3
def draw_row3(cv):
    cells = [24, 272, 520, 768]
    inner = [c + 8 for c in cells]
    tags = [
        ("MON 23", NAVY, WHITE),
        ("SUN 22", None, RULE),
        ("MON 23", NAVY, WHITE),
        ("TUE 24", RED, WHITE),
    ]
    for ci, (txt, fill, fg) in enumerate(tags):
        if fill is None:
            pill(cv, inner[ci], 804, 2, txt, fill=None, fg=fg, outline=RULE)
        else:
            pill(cv, inner[ci], 804, 2, txt, fill=fill, fg=fg)
    headlines = [
        ["EU PROPOSES", "22ND RUSSIA", "SANCTIONS"],
        ["COP31 ENDS", "WITH NO", "DEAL"],
        ["TOXIC SIGNS", "IN 99% OF", "GAZA: OXFAM"],
        ["RUSSIAN JETS", "NEAR KOREAN", "ISLAND"],
    ]
    for ci, lines in enumerate(headlines):
        for li, line in enumerate(lines):
            cv.text(inner[ci], 834 + li * 20, 3, INK, line)
    bodies = [
        "NO RUSSIAN-FLAG ATHLETES. 60 BANKS.",
        "EU REJECTED TEXT WITHOUT FOSSIL FUELS.",
        "ISRAEL CALLS IT BIASED.",
        "SEOUL SCRAMBLES. ALERT MIX-UP.",
    ]
    for ci, body in enumerate(bodies):
        for li, line in enumerate(wrap(body, 18)):
            cv.text(inner[ci], 902 + li * 16, 2, INK, line)


# ---------------------------------------------------------------- ticker
def draw_ticker(cv):
    cv.fill_rect(24, 968, 976, 34, PALE)
    ticker = (
        "ALSO: CROWDSTRIKE TO BUY ZSCALER, $43.9BN (MON) | "
        "RUSSIA HITS ZAPORIZHZHIA: 2 KILLED, 22 HURT (TUE) | "
        "INDONESIA CANDY FIRE: 34 MISSING (SAT)"
    )
    for li, line in enumerate(wrap(ticker, 76)):
        cv.text(32, 972 + li * 16, 2, INK, line)
    cv.text(24, 1008, 1, INK,
            "SOURCES: AFP, AP, REUTERS, KOREA TIMES, AL JAZEERA, "
            "UN NEWS, CBS, ABC.")


# ---------------------------------------------------------------- build
def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_dateline(cv)
    draw_hero(cv)
    draw_row2(cv)
    draw_row3(cv)
    draw_ticker(cv)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, build())
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
