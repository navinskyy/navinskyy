"""Shared design system for the Daily Bugle reports: palette, outlined type,
and the recurring motifs (webs, emblem, grain)."""

import json
import math
import os
from html import escape

# ---- palette: Spider-Man: Brand New Day inspired ------------------------------
RED = "#C1121F"        # Spider Red: restrained highlights
CRIMSON = "#7F101A"    # Deep Crimson: shadows inside red
BLUE = "#145DA0"       # Spider Blue: rim light accents
MIDNIGHT = "#08182D"   # Midnight Blue: sky, panels
BLACK = "#080A0F"      # Near Black: base
WHITE = "#F1F3F5"      # Off White: primary text
SILVER = "#A9B0BB"     # Subtle Silver: secondary text, hairlines

# derived tints, kept close to the palette
RED_GLOW = "#E5383B"
BLUE_GLOW = "#3A86D1"
PANEL = "#0C1524"
HAIRLINE = "#1C2A40"

SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

_GLYPHS = None


def _glyphs():
    global _GLYPHS
    if _GLYPHS is None:
        with open(os.path.join(os.path.dirname(__file__), "glyphs.json"), encoding="utf-8") as f:
            _GLYPHS = json.load(f)
    return _GLYPHS


def measure(text, face, size, tracking=0):
    g = _glyphs()
    k = size / g["em"]
    glyphs = g["faces"][face]
    adv = sum(glyphs.get(ch, glyphs["?"])[0] for ch in text) * k
    return adv + tracking * max(len(text) - 1, 0)


def text(s, face, size, x, y, anchor="start", tracking=0, attrs=""):
    """Outlined text. tracking is extra space in px between letters."""
    g = _glyphs()
    k = size / g["em"]
    glyphs = g["faces"][face]
    w = measure(s, face, size, tracking)
    x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    parts, cx = [], 0.0
    for ch in s:
        adv, d = glyphs.get(ch, glyphs["?"])
        if d:
            parts.append(f'<path transform="translate({cx:.0f})" d="{d}"/>')
        cx += adv + tracking / k
    return (f'<g {attrs} transform="translate({x0:.1f},{y:.1f}) scale({k:.5f})">'
            f'{"".join(parts)}</g>')


def label(s, x, y, size=12, fill=SILVER, anchor="start", weight=400, spacing=0, extra=""):
    """Small system-font text for body copy (keeps files light)."""
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{spacing}" {extra}>{escape(str(s))}</text>')


# ---- motifs --------------------------------------------------------------------

def web(cx, cy, r, a0, a1, spokes=7, rings=5, color=SILVER, opacity=0.25, width=1, sag=0.18, cls=""):
    """Spider web fanning from (cx, cy) between angles a0..a1 (degrees), with sagging rings."""
    angles = [math.radians(a0 + (a1 - a0) * i / (spokes - 1)) for i in range(spokes)]
    out = [f'<g class="{cls}" stroke="{color}" stroke-opacity="{opacity}" stroke-width="{width}" fill="none" '
           f'stroke-linecap="round">']
    for a in angles:
        out.append(f'<path d="M{cx:.1f} {cy:.1f}L{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}"/>')
    for ring in range(1, rings + 1):
        rr = r * (ring / rings) ** 1.1
        d = []
        for i, a in enumerate(angles):
            px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
            if i == 0:
                d.append(f"M{px:.1f} {py:.1f}")
                continue
            am = (angles[i - 1] + a) / 2
            mr = rr * (1 - sag) * math.cos((a - angles[i - 1]) / 2)
            d.append(f"Q{cx + mr * math.cos(am):.1f} {cy + mr * math.sin(am):.1f} {px:.1f} {py:.1f}")
        out.append(f'<path d="{"".join(d)}"/>')
    out.append("</g>")
    return "".join(out)


# Spider emblem, 75 x 123 units, centred on x=0 with the leg tips at y=0.
_LEGS = (
    '<path d="M22 0.2C31 7 37.6 17 37.6 28.9L16.6 42.3L37.6 56.4C36.5 85 30 105 19.5 122.8'
    'C25 104 34 72 31.4 54.9L11.8 43.3L32.4 28.1C33.5 20 30 10 22 0.2Z"/>'
    '<path d="M16.2 14.2C20 17.5 21 27 21 33.4L9.2 43.3L23.8 52.8C25 72 19 92 15.2 102'
    'C18 85 19.5 65 18.8 52.2L5.5 44.1L18.5 32.1C19 27 18 20 16.2 14.2Z"/>'
)
EMBLEM = (
    f'<g>{_LEGS}</g><g transform="scale(-1,1)">{_LEGS}</g>'
    '<path d="M-3.2 36.2V37.6H3.2V36.2L7.2 39.6L3.4 42.9H-3.4L-7.2 39.6Z"/>'
    '<path d="M-3.4 44.2H3.4L8.5 48.6C8 58 3 66 0 68.7C-3 66-8 58-8.5 48.6Z"/>'
)


def emblem(x, y, scale, fill=RED, extra=""):
    """Emblem with its visual centre (the body) at (x, y)."""
    return f'<g transform="translate({x},{y}) scale({scale}) translate(0,-50)" fill="{fill}" {extra}>{EMBLEM}</g>'


def grain_defs(fid="grain", opacity=0.07):
    return (f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 {opacity} 0"/></filter>')
