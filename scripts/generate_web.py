"""Pixel Web of Activity: the hero zip-lines across the last 12 months of
contributions and webs up every day you contributed.

Writes assets/web-of-activity.gif and a finished still, assets/web-of-activity.png,
for visitors who prefer reduced motion. Called by generate_reports.py.
"""

import os
import random

from PIL import Image, ImageDraw

from pixel import (BLACK, CRIMSON, MIDNIGHT, NIGHT, RED, ROOF, SILVER, STEEL, SWING_HAND, WEB, WHITE, draw_text,
                   moon, new, rgb, sky, skyline, sprite, stars, text_width, upscale)

W, H, SCALE = 256, 84, 5
CELL, STEP = 3, 4
GX, GY = 22, 28
LINE_Y = 3
EMPTY = rgb("#13203A")
LEVELS = [EMPTY, rgb("#5A0E18"), CRIMSON, RED, rgb("#FF4B4F")]


def _weeks(last_year):
    import datetime as dt
    first = dt.date.fromisoformat(last_year[0][0])
    pad = (first.weekday() + 1) % 7
    cells = [None] * pad + last_year
    return [cells[i:i + 7] for i in range(0, len(cells), 7)][-53:]


def build(s, m, assets):
    weeks = _weeks(m["last_year"])
    peak = max([n for _, n in m["last_year"]] + [1])

    def level(n):
        return 0 if n == 0 else min(4, 1 + int(4 * n / (peak + 1)))

    # static backdrop
    bg, d = new(W, H)
    sky(bg, [(0, BLACK), (.6, MIDNIGHT), (1, rgb("#2A0E1A"))])
    moon(d, 240, 12, 5)
    skyline(d, random.Random(11), W, H, 6, 18, 8, 16, NIGHT, .1, extras=False)
    d.rectangle([0, H - 4, W, H], fill=ROOF)
    d.line([0, LINE_Y, W, LINE_Y], fill=STEEL)  # the zip line
    left = "LAST 12 MONTHS"
    right = f"{s['year_total']} CONTRIBUTIONS"
    draw_text(bg, left, GX, GY + 7 * STEP + 6, RED, outline=BLACK)
    draw_text(bg, right, W - GX - text_width(right), GY + 7 * STEP + 6, SILVER, outline=BLACK)
    for c, week in enumerate(weeks):
        for r, day in enumerate(week):
            if day is not None:
                x, y = GX + c * STEP, GY + r * STEP
                d.rectangle([x, y, x + CELL - 1, y + CELL - 1], fill=EMPTY)
    stars(bg, 22, GY - 4, 7)

    def webbed(dd, x, y, lv, fresh):
        dd.rectangle([x, y, x + CELL - 1, y + CELL - 1], fill=LEVELS[lv])
        dd.point((x + 1, y + 1), fill=WHITE if fresh else WEB)

    hero = sprite("swing")
    frames, durations = [], []
    done = Image.new("RGB", (W, H))
    state = bg.copy()
    sd = ImageDraw.Draw(state)
    for c, week in enumerate(weeks):
        hx = GX + c * STEP + 1
        targets = [(r, day) for r, day in enumerate(week) if day and day[1]]
        im = state.copy()
        dd = ImageDraw.Draw(im)
        hand = (hx, LINE_Y)
        body = (hand[0] - SWING_HAND[0] + 6, hand[1] + 12)
        for r, (date, n) in targets:  # web shots to every contribution this week
            x, y = GX + c * STEP, GY + r * STEP
            dd.line([body, (x + 1, y + 1)], fill=WEB)
            webbed(sd, x, y, level(n), False)
            webbed(dd, x, y, level(n), True)
        im.paste(hero, (hand[0] - SWING_HAND[0], hand[1] - SWING_HAND[1]), hero)
        frames.append(im)
        durations.append(140 if targets else 50)
    # hold the finished web, hero gone
    frames.append(state.copy())
    durations.append(2600)

    pal = frames[-1].quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = [upscale(f.quantize(palette=pal, dither=Image.Dither.NONE), SCALE) for f in frames]
    gif = os.path.join(assets, "web-of-activity.gif")
    out[0].save(gif, save_all=True, append_images=out[1:], duration=durations, loop=0, optimize=True, disposal=1)
    png = os.path.join(assets, "web-of-activity.png")
    upscale(frames[-1], SCALE).save(png, optimize=True)
    for p in (gif, png):
        print(f"wrote assets/{os.path.basename(p)} ({os.path.getsize(p) / 1024:.0f} KB)")
