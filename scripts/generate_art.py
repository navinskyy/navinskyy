"""Generate the static art: hero banner, act title cards and footer.

These never change with your GitHub data, so they are built by hand, not by the
nightly workflow:
    python scripts/generate_art.py
"""

import os

from theme import (BLACK, BLUE, BLUE_GLOW, CRIMSON, HAIRLINE, MIDNIGHT, REDUCED_MOTION, RED, RED_GLOW, SILVER, WHITE,
                   emblem, grain_defs, hero_silhouette, measure, rain, skyline, text, water_tower, web)

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")


def write(name, svg):
    path = os.path.join(ASSETS, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote assets/{name} ({os.path.getsize(path) / 1024:.0f} KB)")


def banner():
    W, H = 1200, 540
    title_size, title_track = 172, 16
    tw = measure("NAVINSKYY", "display", title_size, title_track)
    title = text("NAVINSKYY", "display", title_size, W / 2, 292, "middle", title_track)
    title_red = text("NAVINSKYY", "display", title_size, W / 2 - 3, 292, "middle", title_track)
    title_blue = text("NAVINSKYY", "display", title_size, W / 2 + 3, 292, "middle", title_track)
    bnd = text("BRAND NEW DAY", "display", 40, W / 2, 384, "middle", 22, f'fill="{RED}"')
    kicker = text("A NEW BEGINNING  ·  THE SAME RESPONSIBILITY", "light", 15, W / 2, 112, "middle", 6,
                  f'fill="{SILVER}"')
    rule_w = 250

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">NAVINSKYY — Brand New Day</title>
<desc id="d">Cinematic title card: the name NAVINSKYY over a rainy New York skyline at night, with a lone masked figure crouched on a rooftop beside a water tower.</desc>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BLACK}"/><stop offset=".55" stop-color="{MIDNIGHT}"/><stop offset="1" stop-color="#0E1F38"/>
  </linearGradient>
  <radialGradient id="glow" cx=".5" cy=".95" r=".65">
    <stop offset="0" stop-color="{CRIMSON}" stop-opacity=".75"/><stop offset=".5" stop-color="{CRIMSON}" stop-opacity=".18"/>
    <stop offset="1" stop-color="{CRIMSON}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="vignette" cx=".5" cy=".45" r=".75">
    <stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".7"/>
  </radialGradient>
  <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="{BLUE_GLOW}" stop-opacity=".22"/><stop offset="1" stop-color="{BLUE_GLOW}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="titleFill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset=".7" stop-color="{WHITE}"/><stop offset="1" stop-color="{SILVER}"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="rule" x1="0" x2="1">
    <stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset="1" stop-color="{RED}"/>
  </linearGradient>
  <mask id="titleMask">{title.replace("<g ", '<g fill="#fff" ', 1)}</mask>
  {grain_defs()}
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>
</defs>
<style>
  .rain {{ animation: fall 1.1s linear infinite; }}
  @keyframes fall {{ from {{ transform: translateY(0); }} to {{ transform: translateY({H}px); }} }}
  .sheen {{ animation: sweep 9s ease-in-out 1.2s infinite; }}
  @keyframes sweep {{ 0% {{ transform: translateX(-420px); }} 38%, 100% {{ transform: translateX({W + 200}px); }} }}
  .pulse {{ animation: pulse 4.5s ease-in-out infinite; }}
  @keyframes pulse {{ 0%, 100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
  .beam {{ transform-origin: 330px 540px; animation: beam 14s ease-in-out infinite; }}
  .beam2 {{ transform-origin: 900px 540px; animation: beam 17s ease-in-out infinite reverse; }}
  @keyframes beam {{ 0%, 100% {{ transform: rotate(-9deg); }} 50% {{ transform: rotate(7deg); }} }}
  {REDUCED_MOTION}
</style>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
<path class="beam" d="M330 470L280 0H380Z" fill="url(#beam)"/>
<path class="beam2" d="M900 470L860 0H940Z" fill="url(#beam)" opacity=".7"/>
{web(0, 0, 330, 0, 90, spokes=8, rings=6, color=SILVER, opacity=.13)}
{skyline(W, 500, 7, "#0B1B31", 90, 190, landmarks=[(250, "spire"), (835, "crown")])}
{skyline(W, H, 11, "#081325", 90, 170, 36, 80, windows=(SILVER, .045))}
<!-- title -->
{kicker}
<g opacity=".55">
  <g fill="{RED}">{title_red}</g>
  <g fill="{BLUE}">{title_blue}</g>
</g>
<g fill="url(#titleFill)">{title}</g>
<g mask="url(#titleMask)"><rect class="sheen" x="0" y="150" width="260" height="160" fill="url(#sheen)" transform="skewX(-18)" opacity=".55"/></g>
<rect x="{W / 2 - rule_w - 34}" y="326" width="{rule_w}" height="1.5" fill="url(#rule)"/>
<rect x="{W / 2 + 34}" y="326" width="{rule_w}" height="1.5" fill="url(#rule)" transform="rotate(180 {W / 2 + 34 + rule_w / 2} 326.75)"/>
<g class="pulse">{emblem(W / 2, 327, .34, RED)}</g>
{bnd}
<!-- rooftop -->
<path d="M845 470H1200V540H845Z" fill="{BLACK}"/>
<path d="M845 470H1200" stroke="{HAIRLINE}" stroke-width="2"/>
<path d="M845 470H1200V476H845Z" fill="{CRIMSON}" opacity=".35"/>
{water_tower(1128, 470, 1.25, BLACK)}
<path d="M1128 345L1066 0" stroke="{SILVER}" stroke-opacity=".35" stroke-width="1"/>
{hero_silhouette(972, 471, 1.2)}
{rain(W, H, 190, seed=4)}
<rect width="{W}" height="{H}" fill="url(#vignette)"/>
<rect width="{W}" height="{H}" filter="url(#grain)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="none" stroke="{HAIRLINE}"/>
</svg>
'''


ACTS = [
    ("I", "THE ORIGIN STORY", "WHO IS BEHIND THE MASK"),
    ("II", "THE ARSENAL", "TOOLS OF THE TRADE"),
    ("III", "THE DAILY BUGLE", "INTELLIGENCE REPORTS · FILED NIGHTLY"),
    ("IV", "FRIENDLY NEIGHBORHOOD MISSIONS", "VERIFIED CASE FILES"),
    ("V", "THE WEB OF ACTIVITY", "EVERY CONTRIBUTION, CONNECTED"),
    ("VI", "THE SPIDER SIGNAL", "OPEN CHANNEL"),
]


def act_card(num, title, sub):
    W, H = 1200, 132
    tsize = 46 if len(title) < 22 else 40
    tw = measure(title, "display", tsize, 5)
    thread_x0 = 78 + tw + 28
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Act {num}: {title.title()}">
<defs>
  <linearGradient id="bg" x1="0" x2="1">
    <stop offset="0" stop-color="{BLACK}"/><stop offset="1" stop-color="{MIDNIGHT}"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" x2="1">
    <stop offset="0" stop-color="{RED}"/><stop offset=".55" stop-color="{RED}" stop-opacity=".25"/>
    <stop offset="1" stop-color="{BLUE}" stop-opacity=".9"/>
  </linearGradient>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{skyline(W, H, 30 + len(title), "#0B1A2E", 14, 46, 20, 46, 2)}
{web(W, 0, 150, 90, 180, spokes=6, rings=4, color=SILVER, opacity=.12)}
<path d="M40 0V{H}" stroke="{SILVER}" stroke-opacity=".35"/>
<circle cx="40" cy="68" r="4.5" fill="{RED}"/>
<circle cx="40" cy="68" r="9" fill="none" stroke="{RED}" stroke-opacity=".4"/>
{text(f"ACT {num}", "display", 17, 78, 47, tracking=6, attrs=f'fill="{RED_GLOW}"')}
{text(title, "display", tsize, 78, 98, tracking=5, attrs=f'fill="{WHITE}"')}
<path d="M{thread_x0:.0f} 80H{W - 64}" stroke="{SILVER}" stroke-opacity=".28" stroke-dasharray="2 6"/>
{text(sub, "light", 12, W - 64, 62, "end", 4, f'fill="{SILVER}"')}
{emblem(W - 46, 81, .2, RED)}
<rect y="{H - 2}" width="{W}" height="2" fill="url(#edge)"/>
</g>
</svg>
'''


def footer():
    W, H = 1200, 300
    line = "Ship with care. Own what you build. Come back better tomorrow."
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{line}">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BLACK}"/><stop offset="1" stop-color="{MIDNIGHT}"/>
  </linearGradient>
  <radialGradient id="glow" cx=".5" cy="1" r=".6">
    <stop offset="0" stop-color="{CRIMSON}" stop-opacity=".55"/><stop offset="1" stop-color="{CRIMSON}" stop-opacity="0"/>
  </radialGradient>
  {grain_defs()}
  <clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath>
</defs>
<style>
  .rain {{ animation: fall 1.3s linear infinite; }}
  @keyframes fall {{ from {{ transform: translateY(0); }} to {{ transform: translateY({H}px); }} }}
  {REDUCED_MOTION}
</style>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
{skyline(W, H, 21, "#0B1B31", 40, 110, landmarks=[(980, "spire")])}
{skyline(W, H, 22, BLACK, 16, 60, 34, 80, windows=(SILVER, .04))}
{emblem(W / 2, 62, .42, RED)}
{text(line, "italic", 30, W / 2, 150, "middle", 0.5, f'fill="{WHITE}"')}
{text("— NAVINSKYY  ·  BRAND NEW DAY", "light", 13, W / 2, 190, "middle", 6, f'fill="{SILVER}"')}
{rain(W, H, 90, seed=9, opacity=.14)}
<rect width="{W}" height="{H}" filter="url(#grain)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="none" stroke="{HAIRLINE}"/>
</svg>
'''


def main():
    os.makedirs(ASSETS, exist_ok=True)
    write("banner.svg", banner())
    for i, (num, title, sub) in enumerate(ACTS, 1):
        write(f"act-{i}.svg", act_card(num, title, sub))
    write("footer.svg", footer())


if __name__ == "__main__":
    main()
