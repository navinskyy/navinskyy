"""Pixel-art toolkit: palette, a 5x7 bitmap font, original hero sprites and
scene pieces. Everything is drawn at a low base resolution and scaled up with
nearest-neighbour so pixels stay crisp."""

import random

from PIL import Image, ImageDraw


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# palette (Brand New Day), plus a few night-city tints
RED = rgb("#C1121F")
CRIMSON = rgb("#7F101A")
BLUE = rgb("#145DA0")
MIDNIGHT = rgb("#08182D")
BLACK = rgb("#080A0F")
WHITE = rgb("#F1F3F5")
SILVER = rgb("#A9B0BB")
NAVY = rgb("#0E2240")
NIGHT = rgb("#0B1426")
STEEL = rgb("#1B3358")
GLOW = rgb("#3A1020")
WINDOW = rgb("#F2D388")
WINDOW_DIM = rgb("#6B5A3A")
MOON = rgb("#F4EEDC")
MOON_SHADE = rgb("#CFC6AE")
WEB = rgb("#E9EDF2")
ROOF = rgb("#05070B")

# ---- 5x7 bitmap font ------------------------------------------------------------
_F = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "11111 00100 00100 00100 00100 00100 11111", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    "-": "00000 00000 00000 11111 00000 00000 00000", ".": "00000 00000 00000 00000 00000 01100 01100",
    "·": "00000 00000 00000 01100 01100 00000 00000", "'": "00100 00100 01000 00000 00000 00000 00000",
    "&": "01100 10010 10100 01000 10101 10010 01101", "/": "00001 00010 00010 00100 01000 01000 10000",
    ":": "00000 01100 01100 00000 01100 01100 00000", ",": "00000 00000 00000 00000 01100 00100 01000",
    "!": "00100 00100 00100 00100 00100 00000 00100", " ": "00000 00000 00000 00000 00000 00000 00000",
}
FONT = {k: [row for row in v.split()] for k, v in _F.items()}


def text_width(s, scale=1, spacing=1):
    return len(s) * (5 * scale + spacing) - spacing


def draw_text(img, s, x, y, color, scale=1, spacing=1, shadow=None, outline=None):
    """Bitmap text with optional drop shadow (color, dx, dy) and 1px outline."""
    px = img.load()
    w, h = img.size

    def put(cx, cy, col):
        for dy in range(scale):
            for dx in range(scale):
                X, Y = cx + dx, cy + dy
                if 0 <= X < w and 0 <= Y < h:
                    px[X, Y] = col

    def cells():
        cx = x
        for ch in s.upper():
            for r, row in enumerate(FONT.get(ch, FONT[" "])):
                for c, bit in enumerate(row):
                    if bit == "1":
                        yield cx + c * scale, y + r * scale
            cx += 5 * scale + spacing

    pts = list(cells())
    if outline:
        for X, Y in pts:
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    for dy in range(scale):
                        for dx in range(scale):
                            if 0 <= X + dx + ox < w and 0 <= Y + dy + oy < h:
                                px[X + dx + ox, Y + dy + oy] = outline
    if shadow:
        col, sdx, sdy = shadow
        for X, Y in pts:
            put(X + sdx, Y + sdy, col)
    for X, Y in pts:
        put(X, Y, color)


# ---- hero sprites (original design) -------------------------------------------
# R red  r crimson  B blue  b midnight  W white lens  K black  . transparent
_SPR = {
    # swinging: right arm up holding the line, knees tucked, facing right
    "swing": """
.............KR.
............KRR.
...KKKKK....KRB.
..KRRRRRK..KRB..
.KRRRRRRRK.KRB..
.KRKWWRWWKKRB...
.KRWWWRWWWKRB...
.KRKWWRWWKRR....
..KRRRRRRKR.....
...KKRRRK.......
..BBRRRRRBB.....
.BBRRRKRRRBB....
BB.RRKKKRR.BB...
RR.RRRKRRR..RR..
...BBBBBBB......
..BBBB.BBBB.....
.BBB....BBB.....
.BB......BBR....
RRB.......RRR...
RR.........RR...
""",
    # crouched on a ledge, facing the viewer
    "perch": """
......KKKKK......
.....KRRRRRK.....
....KRRRRRRRK....
....KWWKRKWWK....
....KWWWRWWWK....
....KRWWRWWRK....
.....KRRRRRK.....
..BBBKRRRRRKBBB..
.BRRBRRRKRRRBRRB.
BRR.BRRKKKRRB.RRB
BR..BBRRKRRBB..RB
RR..BBBBBBBBB..RR
...BBB.....BBB...
..BBR.......RBB..
.RRR.........RRR.
""",
}
_COL = {"R": RED, "r": CRIMSON, "B": BLUE, "b": MIDNIGHT, "W": WHITE, "K": BLACK}


def sprite(name, flip=False, vflip=False):
    rows = [r for r in _SPR[name].strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    img = Image.new("RGBA", (w, len(rows)), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in _COL:
                px[x, y] = _COL[ch] + (255,)
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if vflip:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img


SWING_HAND = (14, 0)  # where the web line leaves the "swing" sprite

# ---- scene pieces --------------------------------------------------------------
_BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def sky(img, stops, y0=0, y1=None):
    """Ordered-dither vertical gradient through colour stops [(pos 0..1, rgb), ...]."""
    w, h = img.size
    y1 = h if y1 is None else y1
    px = img.load()
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                a, ca = stops[i]
                b, cb = stops[i + 1]
                f = (t - a) / max(1e-6, b - a)
                break
        for x in range(w):
            pick = cb if f * 16 > _BAYER[y % 4][x % 4] + .5 else ca
            px[x, y] = pick


def moon(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MOON)
    for y in range(cy - r, cy + r + 1):  # soft shadow on the left limb
        half = int((r * r - (y - cy) ** 2) ** .5)
        d.point([(cx - half, y), (cx - half + 1, y)], fill=MOON_SHADE)
    for ox, oy, rr in ((-3, -2, 2), (3, 3, 1), (-1, 4, 1), (4, -4, 1)):
        d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=MOON_SHADE)


def building(d, rnd, x, top, w, base, body, lit=0.12, win=WINDOW, dim=WINDOW_DIM, ledge=None, antenna=False,
             water_tower=False):
    d.rectangle([x, top, x + w - 1, base], fill=body)
    if ledge:
        d.rectangle([x - 1, top, x + w, top + 1], fill=ledge)
    for wy in range(top + 4, base - 2, 4):
        for wx in range(x + 2, x + w - 2, 3):
            r = rnd.random()
            if r < lit:
                d.point((wx, wy), fill=win)
            elif r < lit * 2.2:
                d.point((wx, wy), fill=dim)
    if antenna:
        d.line([x + w // 2, top - 9, x + w // 2, top - 1], fill=body)
        d.point((x + w // 2, top - 10), fill=RED)
    if water_tower:
        tx = x + w - 9
        d.rectangle([tx, top - 7, tx + 5, top - 3], fill=body)
        d.polygon([(tx - 1, top - 7), (tx + 2, top - 10), (tx + 6, top - 7)], fill=body)
        d.line([tx, top - 3, tx, top - 1], fill=body)
        d.line([tx + 5, top - 3, tx + 5, top - 1], fill=body)


def skyline(d, rnd, w, base, hmin, hmax, wmin, wmax, body, lit, ledge=None, extras=True):
    x = rnd.randint(-8, 0)
    while x < w:
        bw = rnd.randint(wmin, wmax)
        bh = rnd.randint(hmin, hmax)
        building(d, rnd, x, base - bh, bw, base, body, lit, ledge=ledge,
                 antenna=extras and rnd.random() < .15, water_tower=extras and rnd.random() < .2)
        x += bw + rnd.randint(0, 2)


def stars(img, n, ymax, seed, colors=(SILVER, SILVER, WHITE)):
    """Scatter stars on open sky only, so none land next to lettering or rooftops.
    Call after everything else is drawn."""
    rnd = random.Random(seed)
    px = img.load()
    w, h = img.size

    def open_sky(x, y):
        return 5 <= x < w - 5 and all(sum(px[x + dx, y + dy]) < 90 for dx in range(-5, 6) for dy in range(-5, 6)
                                        if 0 <= y + dy < h)

    placed, tries = 0, 0
    while placed < n and tries < n * 40:
        tries += 1
        x, y = rnd.randrange(w), rnd.randrange(max(1, ymax))
        if open_sky(x, y):
            px[x, y] = rnd.choice(colors)
            placed += 1


def upscale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def new(w, h, color=BLACK):
    img = Image.new("RGB", (w, h), color)
    return img, ImageDraw.Draw(img)
