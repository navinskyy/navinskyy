"""Generate the live assets from GitHub data:
  assets/bugle-report.svg    Daily Bugle front page: headline numbers
  assets/bugle-activity.svg  Field report: contribution calendar, streaks, languages
  assets/web-of-activity.gif Pixel hero webbing every contribution day (+ .png still)

Run nightly by .github/workflows/update-profile.yml (12:00 AM Manila time).
    GITHUB_TOKEN=... python scripts/generate_reports.py
    python scripts/generate_reports.py --sample      # offline preview
"""

import datetime as dt
import os

import generate_web
from github_data import USER, load, summarize
from theme import (BLACK, BLUE, BLUE_GLOW, CRIMSON, HAIRLINE, MIDNIGHT, PANEL, RED, RED_GLOW, SILVER, WHITE, emblem,
                   grain_defs, label, measure, text, web)

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")

# contribution intensity: empty, then four steps from crimson to bright red
LEVELS = ["#121C2C", "#4A0D16", CRIMSON, RED, RED_GLOW]
LANG_COLORS = [RED, BLUE_GLOW, WHITE, SILVER, CRIMSON, BLUE, "#5C6676"]


def write(name, svg):
    path = os.path.join(ASSETS, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote assets/{name} ({os.path.getsize(path) / 1024:.0f} KB)")


def fmt_day(d):
    d = dt.date.fromisoformat(d)
    return f"{d:%b} {d.day}, {d.year}"


def fmt_range(a, b):
    if not a:
        return "none yet"
    da, db = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    if a == b:
        return f"{da:%b} {da.day}"
    if da.year == db.year:
        return f"{da:%b} {da.day} – {db:%b} {db.day}" if da.month != db.month else f"{da:%b} {da.day}–{db.day}"
    return f"{fmt_day(a)} – {fmt_day(b)}"


def plural(n, word):
    s = "S" if word.isupper() else "s"
    return f"{n} {word}" if n == 1 else f"{n} {word}{s}"


def level(n, peak):
    return 0 if n == 0 else min(4, 1 + int(4 * n / (peak + 1)))


def weeks_of(last_year):
    """Group the last 365 days into Sunday-first weeks, padding the first week."""
    first = dt.date.fromisoformat(last_year[0][0])
    pad = (first.weekday() + 1) % 7
    cells = [None] * pad + last_year
    return [cells[i:i + 7] for i in range(0, len(cells), 7)]


def frame(W, H, body, extra_defs="", style=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
{body[0]}
<defs>
  <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BLACK}"/><stop offset="1" stop-color="{MIDNIGHT}"/>
  </linearGradient>
  {grain_defs(opacity=.05)}
  <clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  {extra_defs}
</defs>
{f"<style>{style}</style>" if style else ""}
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="url(#paper)"/>
{body[1]}
<rect width="{W}" height="{H}" filter="url(#grain)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="{HAIRLINE}"/>
</svg>
'''


def fit(s, face, size, max_w, tracking=0):
    while measure(s, face, size, tracking) > max_w and size > 10:
        size -= 1
    return size


def bugle_report(s, m):
    W, H = 600, 500
    today = m["today"]
    cx = W / 2
    head1 = f"LOCAL DEVELOPER LOGS {m_fmt(s['year_total'])} CONTRIBUTIONS"
    head2 = "ACROSS THE PAST TWELVE MONTHS"
    hs = min(fit(head1, "serif", 26, W - 64), fit(head2, "serif", 26, W - 64))
    best = m["best"]
    dek = (f"{m['active_days']} active days  ·  current streak {plural(m['cur'][0], 'day')}  ·  "
           f"longest streak {plural(best[0], 'day')} ({fmt_range(best[1], best[2])})")

    first = fmt_day(m["first"]) if m["first"] else "—"
    stats = [
        (s["year_total"], "CONTRIBUTIONS", "last 12 months", RED),
        (m["all_time"], "ALL-TIME", f"since {first}", WHITE),
        (s["public_commits"], "PUBLIC COMMITS", "last 12 months", WHITE),
        (s["private"], "PRIVATE CONTRIBUTIONS", "last 12 months · counts only", WHITE),
        (s["prs"], "PULL REQUESTS", "all time", WHITE),
        (s["original"] + s["forks"], "PUBLIC REPOS", f"{s['original']} original · {s['forks']} forks", WHITE),
    ]
    grid = []
    col_w, row_h, gx, gy = (W - 64) / 3, 92, 32, 262
    for i, (val, lab, sub, color) in enumerate(stats):
        x = gx + (i % 3) * col_w + col_w / 2
        y = gy + (i // 3) * row_h
        grid.append(text(m_fmt(val), "display", 46, x, y + 46, "middle", 1, f'fill="{color}"'))
        grid.append(label(lab, x, y + 66, 10.5, WHITE, "middle", 600, 1.6))
        grid.append(label(sub, x, y + 81, 10.5, SILVER, "middle"))
    rules = "".join(f'<path d="M{gx + col_w * k:.0f} {gy} V{gy + row_h * 2 - 8}" stroke="{HAIRLINE}"/>'
                    for k in (1, 2))
    rules += f'<path d="M{gx} {gy + row_h - 6}H{W - gx}" stroke="{HAIRLINE}"/>'

    title = (f'<title id="t">Daily Bugle report: {s["year_total"]} contributions in the last 12 months, '
             f'{m["all_time"]} all-time, current streak {plural(m["cur"][0], "day")}, longest {plural(best[0], "day")}.</title>')
    body = f'''
{web(W, 0, 170, 90, 180, spokes=6, rings=5, opacity=.09)}
{label(f"VOL. {today.year}  ·  NO. {today.timetuple().tm_yday:03d}", 32, 36, 10, SILVER, spacing=1.5)}
{label(f"MANILA EDITION  ·  {today:%A}, {today:%B} {today.day}, {today.year}".upper(), W - 32, 36, 10, SILVER, "end", spacing=1.5)}
<path d="M32 46H{W - 32}M32 49H{W - 32}" stroke="{SILVER}" stroke-opacity=".5"/>
{text("THE DAILY BUGLE", "serif", 46, cx, 104, "middle", 2, f'fill="{WHITE}"')}
{text("DEVELOPER INTELLIGENCE REPORT", "display", 14, cx, 129, "middle", 6, f'fill="{RED_GLOW}"')}
<path d="M32 142H{W - 32}" stroke="{SILVER}" stroke-opacity=".5"/>
{text(head1, "serif", hs, cx, 182, "middle", 0.5, f'fill="{WHITE}"')}
{text(head2, "serif", hs, cx, 214, "middle", 0.5, f'fill="{WHITE}"')}
{label(dek, cx, 240, 11.5, SILVER, "middle")}
{rules}
{"".join(grid)}
<path d="M32 {H - 40}H{W - 32}" stroke="{HAIRLINE}"/>
{label("Source: GitHub GraphQL API  ·  refreshed nightly at 00:00 Manila time", 32, H - 18, 10, SILVER)}
{emblem(W - 40, H - 22, .16, RED)}
'''
    return frame(W, H, (title, body))


def m_fmt(n):
    return f"{n:,}"


def bugle_activity(s, m):
    W, H = 600, 470
    weeks = weeks_of(m["last_year"])[-53:]
    peak = max([n for _, n in m["last_year"]] + [1])
    gx, gy = 52, 92
    step = (W - 32 - gx) / len(weeks)
    cell = step * 0.82
    cells, months, last_month = [], [], None
    for c, week in enumerate(weeks):
        for r, day in enumerate(week):
            if day is None:
                continue
            d, n = day
            x, y = gx + c * step, gy + r * step
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2" '
                         f'fill="{LEVELS[level(n, peak)]}"><title>{fmt_day(d)}: {n}</title></rect>')
            mo = d[5:7]
            if r == 0 and mo != last_month:
                last_month = mo
                if c < len(weeks) - 2:
                    months.append(label(dt.date.fromisoformat(d).strftime("%b"), x, gy - 8, 9.5, SILVER))
    days_lbl = "".join(label(t, gx - 8, gy + i * step + 7.5, 9, SILVER, "end") for i, t in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    legend_x = W - 32 - 5 * (cell + 3) - 30
    legend = label("Less", legend_x - 6, gy + 7 * step + 18, 9, SILVER, "end")
    legend += "".join(f'<rect x="{legend_x + i * (cell + 3):.1f}" y="{gy + 7 * step + 10:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2" fill="{c}"/>'
                      for i, c in enumerate(LEVELS))
    legend += label("More", legend_x + 5 * (cell + 3) + 4, gy + 7 * step + 18, 9, SILVER)

    # streak strip
    sy = 208
    cur, best = m["cur"], m["best"]
    streaks = f'''
<rect x="32" y="{sy}" width="{(W - 72) / 2}" height="62" rx="10" fill="{PANEL}" stroke="{HAIRLINE}"/>
<rect x="{32 + (W - 72) / 2 + 8}" y="{sy}" width="{(W - 72) / 2}" height="62" rx="10" fill="{PANEL}" stroke="{HAIRLINE}"/>
{label("CURRENT STREAK", 48, sy + 22, 10, SILVER, spacing=1.6, weight=600)}
{text(plural(cur[0], "DAY"), "display", 26, 48, sy + 50, attrs=f'fill="{RED}"')}
{label(fmt_range(cur[1], cur[2]) if cur[0] else "start one today", 48 + measure(plural(cur[0], "DAY"), "display", 26) + 10, sy + 49, 11, SILVER)}
{label("LONGEST STREAK", 48 + (W - 72) / 2 + 8, sy + 22, 10, SILVER, spacing=1.6, weight=600)}
{text(plural(best[0], "DAY"), "display", 26, 48 + (W - 72) / 2 + 8, sy + 50, attrs=f'fill="{WHITE}"')}
{label(fmt_range(best[1], best[2]), 48 + (W - 72) / 2 + 8 + measure(plural(best[0], "DAY"), "display", 26) + 10, sy + 49, 11, SILVER)}
'''

    # languages
    total = sum(s["langs"].values()) or 1
    langs = sorted(s["langs"].items(), key=lambda kv: -kv[1])
    if len(langs) > 6:
        langs = langs[:6] + [("Other", sum(v for _, v in langs[6:]))]
    ly = 318
    bar, x = [], 32.0
    bw = W - 64
    for i, (name, size) in enumerate(langs):
        w = bw * size / total
        bar.append(f'<rect x="{x:.2f}" y="{ly}" width="{max(w, .6):.2f}" height="8" fill="{LANG_COLORS[i]}"/>')
        x += w
    legend_l = []
    for i, (name, size) in enumerate(langs):
        lx = 32 + (i % 3) * (bw / 3)
        lyy = ly + 34 + (i // 3) * 22
        pct = 100 * size / total
        legend_l.append(f'<circle cx="{lx + 4}" cy="{lyy - 4}" r="4" fill="{LANG_COLORS[i]}"/>')
        legend_l.append(label(f"{name}", lx + 14, lyy, 12, WHITE))
        legend_l.append(label(f"{pct:.1f}%" if pct >= .1 else "<0.1%", lx + bw / 3 - 22, lyy, 12, SILVER, "end"))

    title = (f'<title id="t">Field report: contribution calendar for the last 12 months, current streak '
             f'{plural(cur[0], "day")}, longest streak {plural(best[0], "day")}, and top languages by code size.</title>')
    body = f'''
{text("FIELD REPORT", "serif", 22, 32, 46, tracking=1, attrs=f'fill="{WHITE}"')}
{label("LAST 12 MONTHS", W - 32, 44, 10.5, RED_GLOW, "end", 700, 2)}
<path d="M32 58H{W - 32}" stroke="{SILVER}" stroke-opacity=".4"/>
{"".join(months)}{days_lbl}{"".join(cells)}{legend}
{streaks}
{text("LANGUAGE INTEL", "serif", 16, 32, ly - 14, tracking=1, attrs=f'fill="{WHITE}"')}
{label(f"by code size across {s['original']} original public repos", W - 32, ly - 15, 10.5, SILVER, "end")}
<clipPath id="bar"><rect x="32" y="{ly}" width="{bw}" height="8" rx="4"/></clipPath>
<g clip-path="url(#bar)"><rect x="32" y="{ly}" width="{bw}" height="8" fill="{HAIRLINE}"/>{"".join(bar)}</g>
{"".join(legend_l)}
<path d="M32 {H - 40}H{W - 32}" stroke="{HAIRLINE}"/>
{label(f"Filed {m['today']:%Y-%m-%d}  ·  github.com/{USER}", 32, H - 18, 10, SILVER)}
{emblem(W - 40, H - 22, .16, RED)}
'''
    return frame(W, H, (title, body))


def main():
    s = load()
    m = summarize(s)
    os.makedirs(ASSETS, exist_ok=True)
    write("bugle-report.svg", bugle_report(s, m))
    write("bugle-activity.svg", bugle_activity(s, m))
    generate_web.build(s, m, ASSETS)


if __name__ == "__main__":
    main()
