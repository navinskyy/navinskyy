"""Generate the pixel-art pieces of the profile:
  assets/hero.gif, assets/hero.png   animated header (+ still for reduced motion)
  assets/act-1.png .. act-6.png      act title cards
  assets/portrait.png                Act I portrait
  assets/footer.png                  closing card

They don't depend on GitHub data, so run by hand after changing them:
    python scripts/generate_pixel_art.py
"""

import math
import os
import random

from PIL import Image, ImageDraw

from pixel import (BLACK, BLUE, CRIMSON, GLOW, MIDNIGHT, NAVY, NIGHT, RED, ROOF, SILVER, STEEL, SWING_HAND, WEB,
                   WHITE, WINDOW, building, draw_text, moon, new, sky, skyline, sprite, stars, text_width, upscale)

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
SCALE = 4
HEADER_SCALE = 5


def save(img, name, **kw):
    path = os.path.join(ASSETS, name)
    img.save(path, **kw)
    print(f"wrote assets/{name} ({os.path.getsize(path) / 1024:.0f} KB)")


def night(w, h, seed, horizon=1.0):
    img, d = new(w, h)
    sky(img, [(0, BLACK), (.45, MIDNIGHT), (.8 * horizon, NAVY), (1, GLOW)])
    return img, d, random.Random(seed)


# ---- header -------------------------------------------------------------------------

W, H = 256, 104
ANCHOR_Y = 52
ANCHORS = [-50, 10, 70, 130, 190, 250, 310]
ROPE = 26
SWING_DEG = 52
ARC_FRAMES, FLIGHT_FRAMES = 11, 3


def header_background():
    img, d, rnd = night(W, H, 3)
    moon(d, 236, 26, 9)
    skyline(d, random.Random(8), W, H, 28, 54, 12, 22, STEEL, .04, extras=True)
    skyline(d, random.Random(9), W, H, 12, 36, 10, 18, NIGHT, .10, extras=True)
    for ax in ANCHORS[1:-1]:  # the towers the hero swings from
        building(d, rnd, ax - 7, ANCHOR_Y, 15, H, ROOF, .14, ledge=STEEL, antenna=ax == 130)
    d.rectangle([0, 99, W, H], fill=ROOF)
    d.line([0, 99, W, 99], fill=STEEL)
    # title block
    kicker = "A NEW BEGINNING · THE SAME RESPONSIBILITY"
    draw_text(img, kicker, (W - text_width(kicker)) // 2, 4, SILVER)
    title = "NAVINSKYY"
    tw = text_width(title, 3, 3)
    draw_text(img, title, (W - tw) // 2, 15, WHITE, 3, 3, shadow=(RED, 2, 2), outline=BLACK)
    sub = "BRAND NEW DAY"
    draw_text(img, sub, (W - text_width(sub, 1, 3)) // 2, 42, RED, 1, 3, outline=BLACK)
    stars(img, 34, 50, 3)
    return img


def hero_path():
    """(hand_x, hand_y, anchor or None, pose, rotation) per frame: pendulum arcs joined by short flips."""
    frames = []
    for i, ax in enumerate(ANCHORS):
        for f in range(ARC_FRAMES):
            t = f / (ARC_FRAMES - 1)
            th = math.radians(-SWING_DEG * math.cos(math.pi * t))  # slow at the ends, fast at the bottom
            frames.append((ax + ROPE * math.sin(th), ANCHOR_Y + ROPE * math.cos(th), ax, "swing", 0))
        if i < len(ANCHORS) - 1:  # release, flip, catch the next line
            x0 = ax + ROPE * math.sin(math.radians(SWING_DEG))
            x1 = ANCHORS[i + 1] - ROPE * math.sin(math.radians(SWING_DEG))
            y0 = ANCHOR_Y + ROPE * math.cos(math.radians(SWING_DEG))
            for f in range(1, FLIGHT_FRAMES + 1):
                t = f / (FLIGHT_FRAMES + 1)
                frames.append((x0 + (x1 - x0) * t, y0 - 3 * math.sin(math.pi * t), None, "flip", -90 * f))
    return frames


def header():
    bg = header_background()
    hero = sprite("swing")
    frames = []
    rnd = random.Random(2)
    px = bg.load()

    def open_sky(x, y):  # only twinkle where there's nothing but dark sky around
        return 5 <= x < W - 5 and all(sum(px[x + dx, y + dy]) < 90 for dx in range(-5, 6) for dy in range(-5, 6)
                                        if 0 <= y + dy < H)

    twinkle = []
    while len(twinkle) < 7:
        x, y = rnd.randrange(2, W - 2), rnd.randrange(2, 50)
        if open_sky(x, y):
            twinkle.append((x, y))
    for i, (hx, hy, ax, pose, rot) in enumerate(hero_path()):
        im = bg.copy()
        d = ImageDraw.Draw(im)
        for k, (sx, sy) in enumerate(twinkle):
            if (i // 4 + k) % 3 == 0:
                d.point((sx, sy), fill=WHITE)
        hx, hy = round(hx), round(hy)
        if ax is not None:
            d.line([ax, ANCHOR_Y, hx, hy], fill=WEB)
            im.paste(hero, (hx - SWING_HAND[0], hy - SWING_HAND[1]), hero)
        else:
            spr = hero.rotate(rot, expand=True)
            im.paste(spr, (hx - spr.width // 2, hy - spr.height // 2), spr)
        frames.append(im)
    # shared palette keeps colours stable from frame to frame
    pal = frames[len(frames) // 2].quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = [upscale(f.quantize(palette=pal, dither=Image.Dither.NONE), HEADER_SCALE) for f in frames]
    save(out[0], "hero.gif", save_all=True, append_images=out[1:], duration=60, loop=0, optimize=True, disposal=1)
    still = frames[ARC_FRAMES + FLIGHT_FRAMES + ARC_FRAMES // 2 + 1 + (ARC_FRAMES + FLIGHT_FRAMES)]
    save(upscale(still, HEADER_SCALE), "hero.png", optimize=True)


# ---- act cards ----------------------------------------------------------------------

CW, CH = 320, 40


def vignette_origin(img, d, x):
    building(d, random.Random(1), x + 4, 26, 30, CH, ROOF, .1, ledge=STEEL)
    p = sprite("perch")
    img.paste(p, (x + 11, 26 - p.height), p)


def vignette_arsenal(img, d, x):
    # laptop with code on screen
    d.rectangle([x + 6, 9, x + 36, 28], fill=BLACK)
    d.rectangle([x + 8, 11, x + 34, 26], fill=MIDNIGHT)
    for i, (w, c) in enumerate([(14, RED), (20, SILVER), (10, BLUE), (17, SILVER), (8, RED)]):
        d.line([x + 10 + (i % 2) * 2, 13 + i * 3, x + 10 + w, 13 + i * 3], fill=c)
    d.rectangle([x + 3, 29, x + 39, 31], fill=STEEL)
    d.rectangle([x + 3, 32, x + 39, 32], fill=BLACK)


def vignette_bugle(img, d, x):
    d.rectangle([x + 6, 8, x + 38, 34], fill=WHITE)
    d.rectangle([x + 9, 33, x + 41, 35], fill=SILVER)
    draw_text(img, "BUGLE", x + 8, 10, BLACK, 1, 1)
    d.rectangle([x + 8, 19, x + 20, 27], fill=SILVER)
    for i in range(4):
        d.line([x + 22, 19 + i * 2, x + 36, 19 + i * 2], fill=SILVER)
    d.line([x + 8, 30, x + 36, 30], fill=SILVER)


def vignette_missions(img, d, x):
    rnd = random.Random(4)
    building(d, rnd, x + 2, 22, 12, CH, ROOF, .15)
    building(d, rnd, x + 16, 14, 14, CH, ROOF, .15, antenna=True)
    building(d, rnd, x + 32, 24, 10, CH, ROOF, .15)
    # map pin over the tall one
    d.ellipse([x + 18, 1, x + 28, 11], fill=RED)
    d.polygon([(x + 19, 8), (x + 27, 8), (x + 23, 15)], fill=RED)
    d.ellipse([x + 21, 4, x + 25, 8], fill=WHITE)


def vignette_web(img, d, x):
    cx, cy = x + 44, 0
    for a in range(90, 181, 18):
        r = math.radians(a)
        d.line([cx, cy, cx + 40 * math.cos(r), cy + 40 * math.sin(r)], fill=SILVER)
    for rr in (10, 19, 28, 37):
        pts = [(cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a))) for a in range(90, 181, 18)]
        d.line(pts, fill=SILVER)
    d.line([x + 20, 0, x + 20, 22], fill=WEB)
    d.rectangle([x + 18, 23, x + 22, 27], fill=RED)
    d.point([(x + 17, 24), (x + 23, 24), (x + 17, 26), (x + 23, 26), (x + 16, 28), (x + 24, 28)], fill=RED)


def vignette_signal(img, d, x):
    # searchlight beam into the clouds with the spider sign
    d.polygon([(x + 4, CH), (x + 10, CH), (x + 32, 16), (x + 22, 8)], fill=STEEL)
    d.ellipse([x + 18, 2, x + 40, 20], fill=WHITE)
    cx, cy = x + 29, 11
    d.rectangle([cx - 1, cy - 3, cx + 1, cy + 3], fill=BLACK)
    for dx, dy in ((-3, -4), (3, -4), (-4, -1), (4, -1), (-4, 2), (4, 2), (-3, 5), (3, 5)):
        d.line([cx, cy, cx + dx, cy + dy], fill=BLACK)
    building(d, random.Random(6), x, 30, 12, CH, ROOF, .2)


ACTS = [
    ("I", "THE ORIGIN STORY", vignette_origin),
    ("II", "THE ARSENAL", vignette_arsenal),
    ("III", "THE DAILY BUGLE", vignette_bugle),
    ("IV", "NEIGHBORHOOD MISSIONS", vignette_missions),
    ("V", "THE WEB OF ACTIVITY", vignette_web),
    ("VI", "THE SPIDER SIGNAL", vignette_signal),
]


def act_card(n, num, title, vignette):
    img, d, rnd = night(CW, CH, 10 + n, horizon=1.1)
    skyline(d, random.Random(20 + n), CW, CH, 3, 12, 8, 18, NIGHT, .12, extras=False)
    d.rectangle([0, CH - 2, CW, CH], fill=ROOF)
    # thread linking the acts, with a node at the title
    d.line([5, 0, 5, CH], fill=STEEL)
    d.rectangle([4, 23, 6, 25], fill=RED)
    draw_text(img, f"ACT {num}", 12, 6, RED, 1, 2, outline=BLACK)
    draw_text(img, title, 12, 17, WHITE, 2, 2, shadow=(CRIMSON, 1, 1), outline=BLACK)
    vignette(img, d, CW - 48)
    d.line([0, CH - 1, CW, CH - 1], fill=RED)
    stars(img, 26, 30, 10 + n)
    return upscale(img, SCALE)


# ---- portrait + footer --------------------------------------------------------------

def portrait():
    img, d, rnd = night(40, 40, 31)
    moon(d, 30, 9, 5)
    skyline(d, random.Random(32), 40, 40, 8, 18, 6, 10, NIGHT, .15, extras=False)
    d.rectangle([4, 31, 36, 40], fill=ROOF)
    d.line([4, 31, 36, 31], fill=STEEL)
    p = sprite("perch")
    img.paste(p, ((40 - p.width) // 2, 31 - p.height), p)
    stars(img, 6, 20, 31)
    return upscale(img, 6)


def footer():
    w, h = 320, 64
    img, d, rnd = night(w, h, 41)
    moon(d, 18, 13, 7)
    skyline(d, random.Random(42), w, h, 16, 34, 12, 22, STEEL, .05)
    skyline(d, random.Random(43), w, h, 6, 22, 10, 20, NIGHT, .12)
    # hero hanging upside down from a line, keeping watch
    hang = sprite("swing").transpose(Image.FLIP_TOP_BOTTOM)
    hx, hy = 284, 16
    d.line([hx + 11, 0, hx + 11, hy], fill=WEB)  # line to his boots
    img.paste(hang, (hx, hy), hang)
    for i, line in enumerate(("SHIP WITH CARE. OWN WHAT YOU BUILD.", "COME BACK BETTER TOMORROW.")):
        draw_text(img, line, 44, 16 + i * 11, WHITE, 1, 1, outline=BLACK)
    draw_text(img, "- NAVINSKYY · BRAND NEW DAY", 44, 42, RED, 1, 1, outline=BLACK)
    d.rectangle([0, h - 2, w, h], fill=ROOF)
    stars(img, 30, 40, 41)
    return upscale(img, SCALE)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    header()
    for n, (num, title, vig) in enumerate(ACTS, 1):
        save(act_card(n, num, title, vig), f"act-{n}.png", optimize=True)
    save(portrait(), "portrait.png", optimize=True)
    save(footer(), "footer.png", optimize=True)


if __name__ == "__main__":
    main()
