"""Generate banner.svg: the comic-style 3D title at the top of the README.

The banner never changes, so this runs by hand, not in the workflow. Lettering
is converted to outlines so it looks the same for every viewer.
Needs fontTools and the Impact and Bahnschrift fonts (both ship with Windows).
"""

import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from generate_spider_card import (BG, BLUE, BLUE_DARK, BLUE_LIGHT, RED, SPIDER_EMBLEM, YELLOW,
                                  web_bg)

FONTS = os.environ.get("FONT_DIR", "C:/Windows/Fonts")
OUT = os.environ.get("BANNER_PATH", "banner.svg")
W, H = 1200, 340


def text_path(font, text, size, tracking=0):
    """Outline `text` as one SVG path starting at x=0 on the baseline. Returns (d, width)."""
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    pen = SVGPathPen(glyphs)
    x = 0
    for ch in text:
        name = cmap[ord(ch)]
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        x += glyphs[name].width * scale + tracking
    return pen.getCommands(), x - tracking


def skyline():
    out, x, i = [], 0, 0
    heights = [40, 70, 52, 96, 60, 34, 82, 56, 110, 44, 74, 38, 90, 58, 78, 48]
    while x < W:
        h = heights[i % len(heights)]
        w = 46 + (i * 11) % 28
        out.append(f'<rect x="{x}" y="{H - h}" width="{w}" height="{h}"/>')
        x += w + 4
        i += 1
    return f'<g fill="{BLUE_DARK}" opacity=".55">{"".join(out)}</g>'


def main():
    impact = TTFont(f"{FONTS}/impact.ttf")
    bahn = instantiateVariableFont(TTFont(f"{FONTS}/bahnschrift.ttf"), {"wght": 700, "wdth": 100})

    title, tw = text_path(impact, "SPIDER-NAVIN", 150, tracking=4)
    sub, sw = text_path(bahn, "BRAND NEW COMMIT", 44, tracking=10)
    tag, gw = text_path(bahn, "FRIENDLY NEIGHBORHOOD DEVELOPER", 15, tracking=5)

    tx, ty = (W - tw) / 2 + 10, 212
    depth = 14
    # extrusion: copies of the lettering stepped down-right, dark navy at the back to bright blue up front
    extrude = "".join(
        f'<use href="#t" transform="translate({tx + i * 0.9:.1f},{ty + i * 0.9:.1f}) skewX(-8)" '
        f'fill="{BLUE_DARK if i > depth * 0.5 else BLUE}" stroke="#000" stroke-width="{1.4 if i == depth else 0}"/>'
        for i in range(depth, 0, -1)
    )
    face = f'transform="translate({tx:.1f},{ty}) skewX(-8)"'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Spider-Navin: Brand New Commit">
<defs>
  <path id="t" d="{title}"/>
  <path id="s" d="{sub}"/>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="#10235e"/>
  </linearGradient>
  <linearGradient id="faceShade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f01218"/><stop offset="1" stop-color="{RED}"/>
  </linearGradient>
  <pattern id="dots" width="9" height="9" patternUnits="userSpaceOnUse">
    <circle cx="4.5" cy="4.5" r="1.6" fill="{BLUE_LIGHT}"/>
  </pattern>
  <radialGradient id="dotFade" cx="1" cy="0" r="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/>
  </radialGradient>
  <mask id="dotMask"><rect width="{W}" height="{H}" fill="url(#dotFade)"/></mask>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<style>
  .swing {{ transform-origin: 1110px 0; animation: swing 4s ease-in-out infinite; }}
  @keyframes swing {{ 0%,100% {{ transform: rotate(-5deg); }} 50% {{ transform: rotate(5deg); }} }}
</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotMask)" opacity=".35"/>
{web_bg(0, 0, 260, 6, 12, BLUE_LIGHT, 0.22)}
{skyline()}
<g class="swing">
  <line x1="1110" y1="0" x2="1110" y2="62" stroke="#fff" stroke-width="1.5" opacity=".85"/>
  <g transform="translate(1110,26) scale(.95)" fill="{RED}" stroke="#000" stroke-width="1.2">{SPIDER_EMBLEM}</g>
</g>
<path d="{tag}" transform="translate({(W - gw) / 2:.1f},52)" fill="{BLUE_LIGHT}"/>
{extrude}
<use href="#t" {face} fill="none" stroke="{BLUE_LIGHT}" stroke-width="9" stroke-linejoin="round"/>
<use href="#t" {face} fill="none" stroke="#000" stroke-width="4.5" stroke-linejoin="round"/>
<use href="#t" {face} fill="url(#faceShade)"/>
<use href="#s" transform="translate({(W - sw) / 2 + 3:.1f},{ty + 82}) skewX(-8)" fill="#000" opacity=".55"/>
<use href="#s" transform="translate({(W - sw) / 2:.1f},{ty + 79}) skewX(-8)" fill="{YELLOW}"/>
</g>
</svg>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT} ({os.path.getsize(OUT) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
