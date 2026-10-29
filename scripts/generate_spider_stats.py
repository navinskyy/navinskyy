"""Generate spider-stats.svg: contributions, streaks, all-time total, repo
counts and top languages in a Spider-Man themed card.

Run by .github/workflows/update-game.yml every day at 12:00 AM Manila time.
Needs GITHUB_TOKEN. Pass --sample to render with made-up data.
"""

import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request
from html import escape

from generate_spider_card import BG, BLUE, BLUE_DARK, MANILA, MUTED, PANEL, RED, RED_DARK, TEXT, USER, web_bg

OUT = os.environ.get("STATS_PATH", "spider-stats.svg")

# language bar colours: spider palette instead of GitHub's rainbow
LANG_COLORS = [RED, BLUE, "#f1f1f5", RED_DARK, "#6f97ff", "#ff8a8a", "#1d3f9e", "#9aa3c7"]


def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


PROFILE_QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    original: repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    forks: repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: true) { totalCount }
  }
}
"""


def fetch():
    u = gql(PROFILE_QUERY, {"login": USER})
    created = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    now = dt.datetime.now(dt.timezone.utc)

    # contributionsCollection spans at most one year, so ask for each year in one request
    parts = []
    for year in range(created.year, now.year + 1):
        start = max(created, dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
        end = min(now, dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        parts.append(
            f'y{year}: contributionsCollection(from: "{start.isoformat()}", to: "{end.isoformat()}") '
            "{ contributionCalendar { weeks { contributionDays { date contributionCount } } } }"
        )
    years = gql(f'query($login: String!) {{ user(login: $login) {{ {" ".join(parts)} }} }}', {"login": USER})

    days = {}
    for coll in years.values():
        for w in coll["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]

    langs = {}
    for repo in u["original"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]

    return {
        "days": sorted(days.items()),
        "original": u["original"]["totalCount"],
        "forks": u["forks"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["original"]["nodes"]),
        "langs": langs,
    }


def sample():
    random.seed(3)
    today = dt.date.today()
    d, days = dt.date(2023, 5, 21), []
    while d <= today:
        recent = (today - d).days < 120
        n = random.choice([0, 1, 2, 4, 7]) if random.random() < (0.45 if recent else 0.03) else 0
        days.append((d.isoformat(), n))
        d += dt.timedelta(days=1)
    days[-1] = (days[-1][0], 3)
    days[-2] = (days[-2][0], 2)
    return {"days": days, "original": 14, "forks": 6, "stars": 0,
            "langs": {"Python": 520000, "TypeScript": 260000, "JavaScript": 140000, "C++": 40000,
                      "Jupyter Notebook": 30000, "CSS": 12000, "HTML": 3000}}


def summarize(s):
    days = s["days"]
    today = dt.datetime.now(MANILA).date()
    year_ago = (today - dt.timedelta(days=365)).isoformat()
    last_year = [(d, n) for d, n in days if d > year_ago]

    # longest streak, all-time
    best = (0, None, None)
    run_start, run = None, 0
    for d, n in days:
        if n:
            run_start = d if run == 0 else run_start
            run += 1
            if run > best[0]:
                best = (run, run_start, d)
        else:
            run = 0

    # current streak: today without a contribution yet doesn't break it
    cur = (0, None, None)
    i = len(days) - 1
    if i >= 0 and days[i][1] == 0:
        i -= 1
    end = days[i][0] if i >= 0 else None
    while i >= 0 and days[i][1]:
        cur = (cur[0] + 1, days[i][0], end)
        i -= 1

    first = next((d for d, n in days if n), None)
    return {
        "year_total": sum(n for _, n in last_year),
        "active_days": sum(1 for _, n in last_year if n),
        "all_time": sum(n for _, n in days),
        "first": first,
        "cur": cur,
        "best": best,
    }


def fmt_range(a, b):
    if not a:
        return "No streak yet"
    da, db = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    if a == b:
        return f"{da:%b} {da.day}, {da.year}"
    if da.year == db.year:
        return f"{da:%b} {da.day} – {db:%b} {db.day}, {db.year}"
    return f"{da:%b} {da.day}, {da.year} – {db:%b} {db.day}, {db.year}"


# small white glyphs drawn inside the red icon tiles (24x24 box)
ICONS = {
    "web": '<g stroke="#fff" stroke-width="1.4" fill="none"><path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6 5.6 18.4"/>'
           '<circle cx="12" cy="12" r="3.5"/><circle cx="12" cy="12" r="7"/></g>',
    "bolt": '<path d="M13.5 2 5 13.5h5.5L9.5 22 19 9.5h-5.5z" fill="#fff"/>',
    "mask": '<path d="M12 3C7 3 4 7 4 12c0 5 3.5 9 8 9s8-4 8-9c0-5-3-9-8-9z" fill="none" stroke="#fff" stroke-width="1.5"/>'
            '<path d="M6.5 10.5c2 0 4 1 4.5 3-2.2.6-4 0-4.5-3zM17.5 10.5c-2 0-4 1-4.5 3 2.2.6 4 0 4.5-3z" fill="#fff"/>',
    "spider": '<g fill="#fff"><ellipse cx="12" cy="13.5" rx="3" ry="4"/><circle cx="12" cy="8.3" r="2.2"/></g>'
              '<g stroke="#fff" stroke-width="1.3" fill="none" stroke-linecap="round">'
              '<path d="M9.5 11 5 7.5 4 4M14.5 11 19 7.5 20 4M9 13.5H4l-1.5-2M15 13.5h5l1.5-2'
              'M9.5 16 5.5 19l-1 2.5M14.5 16l4 3 1 2.5"/></g>',
}


def stat_col(x, icon, label, big, unit, sub):
    unit_svg = f'<tspan class="unit" dx="6">{unit}</tspan>' if unit else ""
    return f'''
<g transform="translate({x},0)">
  <g transform="translate({-78},38)">
    <rect width="30" height="30" rx="7" fill="{RED}"/>
    <rect width="30" height="30" rx="7" fill="url(#iconShine)"/>
    <g transform="translate(3,3)">{ICONS[icon]}</g>
    <text x="40" y="21" class="label">{escape(label)}</text>
  </g>
  <text x="0" y="122" text-anchor="middle" class="big">{big}{unit_svg}</text>
  <text x="0" y="150" text-anchor="middle" class="sub">{escape(sub)}</text>
</g>'''


def render(s):
    m = summarize(s)
    W, H = 800, 340
    now = dt.datetime.now(MANILA)

    cols = [
        ("web", "Contributions", m["year_total"], "", "in the last year"),
        ("bolt", "Current streak", m["cur"][0], "day" if m["cur"][0] == 1 else "days", fmt_range(m["cur"][1], m["cur"][2])),
        ("mask", "Longest streak", m["best"][0], "day" if m["best"][0] == 1 else "days", fmt_range(m["best"][1], m["best"][2])),
        ("spider", "All-time", m["all_time"], "",
         f"since {dt.date.fromisoformat(m['first']):%b} {dt.date.fromisoformat(m['first']).day}, "
         f"{m['first'][:4]}" if m["first"] else "no contributions yet"),
    ]
    col_w = W / 4

    total = sum(s["langs"].values()) or 1
    langs = sorted(s["langs"].items(), key=lambda kv: -kv[1])
    if len(langs) > 7:
        langs = langs[:7] + [("Other", sum(v for _, v in langs[7:]))]

    bar_x, bar_y, bar_w, bar_h = 24, 252, W - 48, 12
    segs, x = [], bar_x
    for i, (name, size) in enumerate(langs):
        w = bar_w * size / total
        segs.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{max(w, 0.5):.2f}" height="{bar_h}" fill="{LANG_COLORS[i]}">'
                    f'<title>{escape(name)} {100 * size / total:.1f}%</title></rect>')
        x += w
    legend = []
    for i, (name, size) in enumerate(langs):
        lx = 24 + (i % 4) * 190
        ly = 288 + (i // 4) * 22
        pct = 100 * size / total
        pct_s = f"{pct:.1f}%" if pct >= 0.1 else "&lt;0.1%"
        legend.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{LANG_COLORS[i]}"/>'
                      f'<text x="{lx + 16}" y="{ly}" class="lang">{escape(name)} <tspan class="pct">{pct_s}</tspan></text>')

    dividers = "".join(
        f'<line x1="{col_w * i:.0f}" y1="34" x2="{col_w * i:.0f}" y2="160" stroke="{RED}" stroke-opacity=".45" '
        f'stroke-dasharray="1 5" stroke-linecap="round" stroke-width="2"/>' for i in range(1, 4))

    # dangling spider on a thread, top right
    spider = f'''
<g class="swing">
  <line x1="784" y1="0" x2="784" y2="22" stroke="#fff" stroke-opacity=".7"/>
  <g transform="translate(784,30)">
    <ellipse rx="5" ry="6.5" fill="#111" stroke="{RED}" stroke-width=".8"/><circle cy="-8" r="3.5" fill="#111" stroke="{RED}" stroke-width=".8"/>
    <g stroke="#ddd" stroke-width="1.1" fill="none" stroke-linecap="round">
      <path d="M-4-3-10-8-11-13M4-3 10-8 11-13M-5 0h-7l-2-3M5 0h7l2-3M-4 3-9 8-10 12M4 3 9 8 10 12"/>
    </g>
  </g>
</g>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub stats for {USER}: {m["year_total"]} contributions in the last year, current streak {m["cur"][0]} days, longest streak {m["best"][0]} days">
<style>
  text {{ font-family: 'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif; fill: {TEXT}; }}
  .label {{ font-size: 16px; font-weight: 700; }}
  .big {{ font-size: 50px; font-weight: 900; fill: {RED}; letter-spacing: -1px; }}
  .unit {{ font-size: 17px; font-weight: 600; fill: {MUTED}; letter-spacing: 0; }}
  .sub {{ font-size: 13px; fill: {MUTED}; }}
  .mid {{ font-size: 14px; }}
  .h {{ font-size: 15px; font-weight: 800; }}
  .note {{ font-size: 12px; fill: {MUTED}; }}
  .lang {{ font-size: 13px; }}
  .pct {{ fill: {MUTED}; }}
  .foot {{ font-family: 'Fira Code', Consolas, monospace; font-size: 10.5px; fill: {MUTED}; }}
  .swing {{ transform-origin: 784px 0; animation: swing 3.5s ease-in-out infinite; }}
  @keyframes swing {{ 0%,100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(8deg); }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#1a0a10"/><stop offset=".5" stop-color="{BG}"/><stop offset="1" stop-color="#0a1230"/>
  </linearGradient>
  <linearGradient id="iconShine" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#000" stop-opacity=".15"/>
  </linearGradient>
  <linearGradient id="rule" x1="0" x2="1">
    <stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset=".2" stop-color="{RED}"/>
    <stop offset=".8" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
  <clipPath id="barclip"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="6"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{web_bg(0, 0, 170, 5, 10, RED, 0.18)}
{web_bg(W, H, 190, 5, 10, BLUE, 0.2)}
{spider}
{dividers}
{"".join(stat_col(col_w * i + col_w / 2, *c) for i, c in enumerate(cols))}
<rect x="24" y="180" width="{W - 48}" height="1.5" fill="url(#rule)"/>
<text x="{W / 2}" y="210" text-anchor="middle" class="mid">{m["active_days"]} active days in the last year  ·  {s["original"] + s["forks"]} public repositories ({s["original"]} original, {s["forks"]} forks)  ·  {s["stars"]} stars</text>
<text x="24" y="242" class="h">Top languages</text>
<text x="{W - 24}" y="242" text-anchor="end" class="note">by code size across original repositories</text>
<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="6" fill="{PANEL}"/>
<g clip-path="url(#barclip)">{"".join(segs)}</g>
{"".join(legend)}
<text x="{W - 24}" y="{H - 10}" text-anchor="end" class="foot">updated {now:%Y-%m-%d} · from github.com/{USER}</text>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="13.5" fill="none" stroke="{RED}" stroke-opacity=".45" stroke-width="1.5"/>
</svg>
'''


def main():
    s = sample() if "--sample" in sys.argv else fetch()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(s))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
