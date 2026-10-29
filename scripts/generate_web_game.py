"""Generate thwip.gif: a Spider-Man style hero swings under your contribution
graph and webs up every day you contributed (each one is a villain).

Run by .github/workflows/update-game.yml every day at 12:00 AM Manila time.
Needs GITHUB_TOKEN and Pillow. Pass --sample to render with made-up data.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

from generate_spider_card import fetch_stats, sample_stats

OUT = os.environ.get("GAME_PATH", "thwip.gif")

W, H = 840, 250
CELL, GAP = 12, 3
STEP = CELL + GAP
GX, GY = 24, 46           # grid origin
GROUND = 222              # y of the rooftop line
HERO_Y = GROUND - 2       # hero's feet

BG = (10, 11, 20)
EMPTY = (27, 31, 58)
SKY_WEB = (30, 40, 85)
CITY = (17, 21, 44)
CITY_LIT = (60, 70, 120)
RED = (226, 54, 54)
RED_DARK = (139, 15, 20)
BLUE = (43, 92, 214)
BLUE_DARK = (11, 29, 79)
WHITE = (240, 240, 245)
WEB = (225, 228, 240)
COCOON = (150, 155, 175)
MUTED = (154, 163, 199)
YELLOW = (255, 210, 80)

VILLAIN_SHADES = [(90, 26, 42), RED_DARK, (192, 36, 43), RED]


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


F_TITLE, F_SMALL = font(15), font(11)


def cell_xy(col, row):
    return GX + col * STEP, GY + row * STEP


def draw_city(d):
    # simple skyline silhouette on the rooftops
    x = 0
    heights = [28, 46, 34, 58, 40, 22, 52, 36, 64, 30, 44, 26, 56, 38, 48, 32]
    i = 0
    while x < W:
        h = heights[i % len(heights)]
        w = 38 + (i * 7) % 20
        top = GROUND - h
        d.rectangle([x, top, x + w, GROUND], fill=CITY)
        for wy in range(top + 6, GROUND - 4, 9):
            for wx in range(x + 5, x + w - 4, 8):
                if (wx * 3 + wy * 7 + i) % 5 == 0:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=CITY_LIT)
        x += w + 3
        i += 1
    d.line([0, GROUND, W, GROUND], fill=BLUE_DARK, width=2)
    d.rectangle([0, GROUND + 1, W, H], fill=(7, 8, 15))


def draw_corner_web(d):
    import math
    cx, cy, r = W, 0, 120
    for k in range(7):
        a = math.pi / 2 + k * (math.pi / 2) / 6
        d.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)], fill=SKY_WEB)
    for ring in range(1, 5):
        rr = r * ring / 4
        pts = [(cx + rr * math.cos(math.pi / 2 + k * (math.pi / 2) / 6),
                cy + rr * math.sin(math.pi / 2 + k * (math.pi / 2) / 6)) for k in range(7)]
        d.line(pts, fill=SKY_WEB)


def draw_villain(d, x, y, level):
    d.rounded_rectangle([x, y, x + CELL - 1, y + CELL - 1], 3, fill=VILLAIN_SHADES[level])
    # angry little eyes
    d.rectangle([x + 3, y + 4, x + 4, y + 6], fill=YELLOW)
    d.rectangle([x + 7, y + 4, x + 8, y + 6], fill=YELLOW)


def draw_webbed(d, x, y, fresh):
    fill = WEB if fresh else COCOON
    d.rounded_rectangle([x, y, x + CELL - 1, y + CELL - 1], 3, fill=BG, outline=fill)
    c = CELL - 1
    d.line([x, y, x + c, y + c], fill=fill)
    d.line([x + c, y, x, y + c], fill=fill)
    d.line([x + c // 2, y, x + c // 2, y + c], fill=fill)
    d.line([x, y + c // 2, x + c, y + c // 2], fill=fill)


def draw_hero(d, cx, feet, pose):
    """Original chunky red/blue web-slinger. pose: 'stand' | 'run' | 'shoot'."""
    # legs (blue)
    if pose == "run":
        d.polygon([(cx - 5, feet - 12), (cx - 1, feet - 12), (cx - 6, feet), (cx - 10, feet)], fill=BLUE)
        d.polygon([(cx + 1, feet - 12), (cx + 5, feet - 12), (cx + 10, feet), (cx + 6, feet)], fill=BLUE)
    else:
        d.rectangle([cx - 6, feet - 12, cx - 2, feet], fill=BLUE)
        d.rectangle([cx + 2, feet - 12, cx + 6, feet], fill=BLUE)
    d.rectangle([cx - 7, feet - 2, cx - 1, feet], fill=RED)   # boots
    d.rectangle([cx + 1, feet - 2, cx + 7, feet], fill=RED)
    # torso: red chest, blue sides
    top = feet - 26
    d.rectangle([cx - 7, top, cx + 7, feet - 12], fill=BLUE)
    d.rectangle([cx - 5, top, cx + 5, feet - 12], fill=RED)
    d.rectangle([cx - 7, feet - 14, cx + 7, feet - 12], fill=RED_DARK)  # belt
    d.point([(cx, top + 4), (cx - 1, top + 5), (cx + 1, top + 5), (cx, top + 6)], fill=(20, 20, 20))
    # arms
    if pose == "shoot":
        d.rectangle([cx + 6, top - 10, cx + 9, top + 3], fill=RED)   # right arm up
        d.rectangle([cx + 6, top - 12, cx + 9, top - 10], fill=BLUE_DARK)
        d.rectangle([cx - 10, top + 1, cx - 7, top + 11], fill=RED)
    else:
        d.rectangle([cx - 10, top + 1, cx - 7, top + 11], fill=RED)
        d.rectangle([cx + 7, top + 1, cx + 10, top + 11], fill=RED)
    # head + mask eyes
    hy = top - 11
    d.ellipse([cx - 7, hy, cx + 7, hy + 12], fill=RED)
    d.line([cx, hy, cx, hy + 12], fill=RED_DARK)
    d.line([cx - 7, hy + 6, cx + 7, hy + 6], fill=RED_DARK)
    d.polygon([(cx - 6, hy + 4), (cx - 1, hy + 6), (cx - 2, hy + 9), (cx - 6, hy + 8)], fill=WHITE)
    d.polygon([(cx + 6, hy + 4), (cx + 1, hy + 6), (cx + 2, hy + 9), (cx + 6, hy + 8)], fill=WHITE)


def hand_pos(cx, feet):
    return cx + 8, feet - 26 - 12


def build(stats):
    days = stats["days"]
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)][-53:]
    peak = max([d["contributionCount"] for d in days] + [1])

    def level(n):
        return min(3, int(4 * n / (peak + 1)))

    # state per cell: None = empty, ("v", lvl) villain, ("w", age) webbed
    state = {}
    for c, week in enumerate(weeks):
        for r, day in enumerate(week):
            if day["contributionCount"]:
                state[(c, r)] = ["v", level(day["contributionCount"])]
    total = len(state)

    base = Image.new("RGB", (W, H), BG)
    bd = ImageDraw.Draw(base)
    draw_corner_web(bd)
    draw_city(bd)
    bd.text((GX, 14), "THWIP LOG", font=F_TITLE, fill=RED)
    bd.text((GX + 100, 17), "// every contribution is a villain", font=F_SMALL, fill=MUTED)

    frames, durations = [], []
    caught = 0

    def frame(hero_x, pose, web=None, ms=60):
        im = base.copy()
        d = ImageDraw.Draw(im)
        d.text((W - 210, 17), f"VILLAINS WEBBED  {caught:>4} / {total}", font=F_SMALL, fill=WHITE)
        for c, week in enumerate(weeks):
            for r in range(len(week)):
                x, y = cell_xy(c, r)
                s = state.get((c, r))
                if s is None:
                    d.rounded_rectangle([x, y, x + CELL - 1, y + CELL - 1], 3, fill=EMPTY)
                elif s[0] == "v":
                    draw_villain(d, x, y, s[1])
                else:
                    draw_webbed(d, x, y, fresh=s[1] < 3)
        if web:
            hx, hy = hand_pos(hero_x, HERO_Y)
            tx, ty = web
            d.line([hx, hy, tx, ty], fill=WEB, width=2)
            d.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], outline=WEB)
        draw_hero(d, hero_x, HERO_Y, pose)
        frames.append(im)
        durations.append(ms)

    def age_webs():
        for s in state.values():
            if s[0] == "w":
                s[1] += 1

    hero_x = GX - 14
    frame(hero_x, "stand", ms=600)

    for c, week in enumerate(weeks):
        col_x = GX + c * STEP + CELL // 2
        targets = sorted((r for r in range(len(week)) if (c, r) in state), reverse=True)
        # run to the column (skip extra frames over empty columns)
        steps = 2 if targets else 1
        for i in range(1, steps + 1):
            hero_x = int(hero_x + (col_x - 8 - hero_x) * i / steps)
            frame(hero_x, "run", ms=45)
            age_webs()
        # fire one web per villain, bottom row first
        for r in targets:
            tx, ty = cell_xy(c, r)
            tx, ty = tx + CELL // 2, ty + CELL // 2
            hx, hy = hand_pos(hero_x, HERO_Y)
            mid = (hx + (tx - hx) // 2, hy + (ty - hy) // 2)
            frame(hero_x, "shoot", web=mid, ms=40)
            frame(hero_x, "shoot", web=(tx, ty), ms=50)
            state[(c, r)] = ["w", 0]
            caught += 1
            age_webs()

    for _ in range(6):
        age_webs()
    frame(hero_x, "stand", ms=400)
    # victory screen
    im = frames[-1].copy()
    d = ImageDraw.Draw(im)
    msg = f"ALL {total} VILLAINS WEBBED!  THWIP!"
    w = d.textlength(msg, font=F_TITLE)
    d.rounded_rectangle([W / 2 - w / 2 - 16, 82, W / 2 + w / 2 + 16, 114], 8, fill=BG, outline=RED, width=2)
    d.text((W / 2 - w / 2, 90), msg, font=F_TITLE, fill=WHITE)
    frames.append(im)
    durations.append(3000)
    return frames, durations


def main():
    stats = sample_stats() if "--sample" in sys.argv else fetch_stats()
    frames, durations = build(stats)
    pal = [f.quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=durations,
                loop=0, optimize=True, disposal=1)
    print(f"wrote {OUT}: {len(frames)} frames, {os.path.getsize(OUT) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
