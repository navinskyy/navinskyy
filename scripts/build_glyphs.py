"""Extract glyph outlines into glyphs.json so display text renders identically
for every visitor, and on the Actions runner, which has none of these fonts.

Run by hand on Windows only when the type system changes:
    python scripts/build_glyphs.py
"""

import json
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = os.environ.get("FONT_DIR", "C:/Windows/Fonts")
OUT = os.path.join(os.path.dirname(__file__), "glyphs.json")
CHARS = "".join(chr(c) for c in range(32, 127)) + "—–·’‘“”•×"
EM = 1000

FACES = {
    # condensed, heavy: titles and big numbers
    "display": lambda: instantiateVariableFont(TTFont(f"{FONTS}/bahnschrift.ttf"), {"wght": 700, "wdth": 75}),
    # light, wide: kickers and tracked-out captions
    "light": lambda: instantiateVariableFont(TTFont(f"{FONTS}/bahnschrift.ttf"), {"wght": 300, "wdth": 100}),
    # editorial serif: Daily Bugle masthead and headlines
    "serif": lambda: TTFont(f"{FONTS}/georgiab.ttf"),
    "italic": lambda: TTFont(f"{FONTS}/georgiai.ttf"),
}


def extract(font):
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = EM / font["head"].unitsPerEm
    out = {}
    for ch in CHARS:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.0f}")
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, 0, 0)))
        out[ch] = [round(glyphs[name].width * scale), pen.getCommands()]
    return out


def main():
    data = {"em": EM, "faces": {name: extract(load()) for name, load in FACES.items()}}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT} ({os.path.getsize(OUT) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
