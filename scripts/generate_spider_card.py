"""Generate spider-card.svg: a Spider-Man themed profile card with live GitHub stats.

Run by .github/workflows/update-profile.yml every day at 12:00 AM Manila time.
Needs GITHUB_TOKEN (the Actions token is enough). Pass --sample to render with
made-up numbers for a local preview without a token.
"""

import datetime as dt
import json
import os
import random
import sys
import urllib.request
from html import escape

USER = os.environ.get("GH_USER", "navinskyy")
OUT = os.environ.get("CARD_PATH", "spider-card.svg")
MANILA = dt.timezone(dt.timedelta(hours=8))

# "Brand New Day" palette: red faces, blue extrusion, light-blue rim, yellow titles
RED = "#d7090d"
RED_DARK = "#7e0609"
BLUE = "#1f4bbf"
BLUE_LIGHT = "#3d86f0"
BLUE_DARK = "#132a7a"
YELLOW = "#fcd11a"
BG = "#060a1a"
PANEL = "#0d1533"
TEXT = "#f5f6ff"
MUTED = "#a8b6e6"
HEAT = ["#16204a", "#4a0a14", RED_DARK, "#b0080c", RED]

# Spider emblem, 75 x 123 units, centred on x=0 with the leg tips at y=0.
# Right-hand legs are drawn once and mirrored for the left.
_LEGS = (
    '<path d="M22 0.2C31 7 37.6 17 37.6 28.9L16.6 42.3L37.6 56.4C36.5 85 30 105 19.5 122.8'
    'C25 104 34 72 31.4 54.9L11.8 43.3L32.4 28.1C33.5 20 30 10 22 0.2Z"/>'
    '<path d="M16.2 14.2C20 17.5 21 27 21 33.4L9.2 43.3L23.8 52.8C25 72 19 92 15.2 102'
    'C18 85 19.5 65 18.8 52.2L5.5 44.1L18.5 32.1C19 27 18 20 16.2 14.2Z"/>'
)
SPIDER_EMBLEM = (
    f'<g>{_LEGS}</g><g transform="scale(-1,1)">{_LEGS}</g>'
    '<path d="M-3.2 36.2V37.6H3.2V36.2L7.2 39.6L3.4 42.9H-3.4L-7.2 39.6Z"/>'
    '<path d="M-3.4 44.2H3.4L8.5 48.6C8 58 3 66 0 68.7C-3 66-8 58-8.5 48.6Z"/>'
)


QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, first: 100, privacy: PUBLIC) {
      totalCount
      nodes { stargazerCount forkCount }
    }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]) { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_stats():
    token = os.environ["GITHUB_TOKEN"]
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    u = data["data"]["user"]
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return {
        "created": u["createdAt"][:10],
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "forks": sum(r["forkCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "contributed_to": u["repositoriesContributedTo"]["totalCount"],
        "prs": u["pullRequests"]["totalCount"],
        "issues": u["issues"]["totalCount"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "year_total": cc["contributionCalendar"]["totalContributions"],
        "days": days,
    }


def sample_stats():
    random.seed(7)
    today = dt.date.today()
    start = today - dt.timedelta(days=370)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # align to Sunday
    days = []
    d = start
    while d <= today:
        n = random.choice([0, 0, 0, 1, 2, 3, 5, 8, 12]) if random.random() > 0.2 else 0
        days.append({"date": d.isoformat(), "contributionCount": n})
        d += dt.timedelta(days=1)
    return {
        "created": "2023-05-21", "repos": 20, "stars": 3, "forks": 1, "followers": 2,
        "contributed_to": 4, "prs": 12, "issues": 5, "commits": 406,
        "year_total": sum(x["contributionCount"] for x in days), "days": days,
    }


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    # today may not have contributions yet; don't break the streak for it
    i = len(counts) - 1
    if counts and counts[i] == 0:
        i -= 1
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def elapsed(created):
    start = dt.date.fromisoformat(created)
    today = dt.datetime.now(MANILA).date()
    months = (today.year - start.year) * 12 + today.month - start.month
    if today.day < start.day:
        months -= 1
    return f"{months // 12}Y {months % 12}M"


def web_bg(cx, cy, r, rings, spokes, color, opacity):
    """Spider web centred at (cx, cy)."""
    import math
    parts = []
    pts = [(cx + r * math.cos(2 * math.pi * k / spokes), cy + r * math.sin(2 * math.pi * k / spokes))
           for k in range(spokes)]
    for x, y in pts:
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>')
    for ring in range(1, rings + 1):
        rr = r * ring / rings
        p = []
        for k in range(spokes + 1):
            a = 2 * math.pi * k / spokes
            p.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
        parts.append(f'<polyline points="{" ".join(p)}" fill="none"/>')
    return f'<g stroke="{color}" stroke-width="1" opacity="{opacity}">{"".join(parts)}</g>'


def heat_color(n, peak):
    if n == 0:
        return HEAT[0]
    return HEAT[min(4, 1 + int(4 * n / (peak + 1)))]


def heatmap(days, x0, y0):
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)][-53:]
    peak = max([d["contributionCount"] for d in days] + [1])
    cell, gap = 11, 2.6
    out = []
    for wi, week in enumerate(weeks):
        for di, d in enumerate(week):
            x = x0 + wi * (cell + gap)
            y = y0 + di * (cell + gap)
            n = d["contributionCount"]
            out.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.5" '
                f'fill="{heat_color(n, peak)}"><title>{d["date"]}: {n}</title></rect>'
            )
    return "".join(out)


def stat_tile(x, y, value, label, color):
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect width="118" height="64" rx="10" fill="{PANEL}" stroke="{color}" stroke-opacity="0.55"/>'
        f'<text x="59" y="32" text-anchor="middle" class="num" fill="{color}">{value}</text>'
        f'<text x="59" y="51" text-anchor="middle" class="lbl">{escape(label)}</text>'
        f"</g>"
    )


def row(x, y, key, val):
    return (f'<text x="{x}" y="{y}" class="key">{escape(key)}</text>'
            f'<text x="{x}" y="{y + 18}" class="val">{escape(val)}</text>')


def chips(x, y, items, color):
    out, cx = [], x
    for it in items:
        w = 14 + 7.4 * len(it)
        out.append(f'<rect x="{cx}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{color}" fill-opacity="0.18" '
                   f'stroke="{color}" stroke-opacity="0.7"/>'
                   f'<text x="{cx + w / 2:.0f}" y="{y + 16}" text-anchor="middle" class="chip">{escape(it)}</text>')
        cx += w + 8
    return "".join(out)


def section_title(y, title, tag):
    return (f'<g transform="translate(32,{y})">'
            f'<rect width="6" height="22" rx="2" fill="{RED}"/>'
            f'<text x="16" y="17" class="h2">{escape(title)}</text>'
            f'<text x="736" y="17" text-anchor="end" class="tag">{tag}</text>'
            f'<line x1="0" y1="32" x2="736" y2="32" stroke="{BLUE_LIGHT}" stroke-opacity="0.35"/></g>')


def render(s):
    cur, longest = streaks(s["days"])
    now = dt.datetime.now(MANILA)
    W, H = 800, 1010

    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Spider-Man themed profile card for {USER}">
<style>
  text {{ font-family: 'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif; fill: {TEXT}; }}
  .h1 {{ font-size: 34px; font-family: Impact, 'Arial Black', sans-serif; letter-spacing: 1.5px; }}
  .h2 {{ font-size: 15px; font-weight: 800; letter-spacing: 2.5px; }}
  .tag {{ font-size: 11px; fill: {MUTED}; letter-spacing: 2px; font-family: 'Fira Code', Consolas, monospace; }}
  .sub {{ font-size: 14px; fill: {MUTED}; }}
  .key {{ font-size: 10.5px; fill: {YELLOW}; letter-spacing: 1.8px; font-weight: 700; }}
  .val {{ font-size: 14px; }}
  .num {{ font-size: 24px; font-weight: 800; }}
  .lbl {{ font-size: 10px; fill: {MUTED}; letter-spacing: 1.5px; }}
  .chip {{ font-size: 12px; font-weight: 600; }}
  .mono {{ font-family: 'Fira Code', Consolas, monospace; }}
  .pulse {{ animation: pulse 1.6s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
  .swing {{ transform-origin: 700px 0px; animation: swing 4s ease-in-out infinite; }}
  @keyframes swing {{ 0%,100% {{ transform: rotate(-6deg); }} 50% {{ transform: rotate(6deg); }} }}
</style>
<defs>
  <linearGradient id="hdr" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{BLUE_DARK}"/><stop offset=".6" stop-color="{BLUE}"/><stop offset="1" stop-color="{RED_DARK}"/>
  </linearGradient>
  <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{RED}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{BG}"/>
{web_bg(0, 0, 330, 6, 12, BLUE, 0.16)}
{web_bg(W, H, 300, 6, 12, RED, 0.12)}

<!-- header -->
<rect width="{W}" height="150" fill="url(#hdr)"/>
{web_bg(W - 60, -20, 210, 5, 14, BLUE_LIGHT, 0.35)}
<g class="swing">
  <line x1="700" y1="0" x2="700" y2="50" stroke="#fff" stroke-width="1.5" opacity=".8"/>
  <g transform="translate(700,14)" fill="{RED}" stroke="#000" stroke-width="1.2">{SPIDER_EMBLEM}</g>
</g>
<g transform="translate(32,34)">
  <circle cx="40" cy="40" r="40" fill="{BG}" stroke="#fff" stroke-width="3"/>
  {web_bg(40, 40, 38, 3, 8, RED, 0.6)}
  <text x="40" y="51" text-anchor="middle" font-size="30" font-weight="900" fill="#fff">NL</text>
</g>
<text x="132" y="62" class="tag" style="fill:{YELLOW}">FRIENDLY NEIGHBORHOOD DEVELOPER</text>
<g class="h1" transform="translate(132,98) skewX(-8)" stroke-linejoin="round">
  <text x="4" y="4" style="fill:{BLUE_DARK}" stroke="#000" stroke-width="1.5">{escape(USER)}</text>
  <text x="2" y="2" style="fill:{BLUE}">{escape(USER)}</text>
  <text style="fill:{RED}" stroke="{BLUE_LIGHT}" stroke-width="1.2">{escape(USER)}</text>
</g>
<text x="132" y="122" class="sub" style="fill:{TEXT}">AI Security Intern @ RivanAI  ·  BSCS '27 · LPU – Manila</text>

<!-- spider-sense bar -->
<g transform="translate(32,168)">
  <rect width="736" height="40" rx="10" fill="{PANEL}" stroke="{RED}" stroke-opacity=".5"/>
  <circle cx="22" cy="20" r="6" fill="{RED}" class="pulse"/>
  <text x="38" y="25" class="tag" style="fill:{TEXT}">SPIDER-SENSE: TINGLING</text>
  <text x="380" y="25" text-anchor="middle" class="tag">SWINGING FOR {elapsed(s["created"])}</text>
  <text x="714" y="25" text-anchor="end" class="tag">UPDATED {now:%b %d, %Y}</text>
</g>
''']

    # Secret identity
    svg.append(section_title(232, "SECRET IDENTITY", "FILE // 01"))
    y = 290
    svg.append(row(40, y, "ALIAS", USER))
    svg.append(row(410, y, "ACADEMY", "LPU – Manila"))
    svg.append(row(40, y + 46, "TRAINING", "BS Computer Science, Class of 2027"))
    svg.append(row(410, y + 46, "DAY JOB", "AI Security Intern @ RivanAI"))
    svg.append(row(40, y + 92, "THE AVENGERS (ORGS)", "LPE VP Committee · LPU Esports"))
    svg.append(row(410, y + 92, "HONORS", "Dean's Lister"))
    svg.append(row(40, y + 138, "GADGETS", "VS Code, Jupyter, Colab, Claude Code"))
    svg.append(row(410, y + 138, "BASES", "Windows 11, Ubuntu (Azure) · EN / FIL"))

    # Web-shooter arsenal
    svg.append(section_title(478, "WEB-SHOOTER ARSENAL", "FILE // 02"))
    svg.append('<text x="40" y="540" class="key">LANGUAGES</text>')
    svg.append(chips(40, 550, ["Python", "TypeScript", "C++", "SQL"], RED))
    svg.append('<text x="410" y="540" class="key">AI / ML</text>')
    svg.append(chips(410, 550, ["TensorFlow", "scikit-learn", "YOLOv8"], BLUE))
    svg.append(chips(410, 582, ["LangChain", "HuggingFace", "ChromaDB"], BLUE))

    # Live stats
    svg.append(section_title(628, "DAILY BUGLE  //  GITHUB STATS", '<tspan fill="#e23636" class="pulse">●</tspan> LIVE'))
    tiles = [
        (s["year_total"], "CONTRIB · 1Y", RED), (s["commits"], "COMMITS · 1Y", RED),
        (s["repos"], "REPOS", BLUE), (s["stars"], "STARS", BLUE),
        (s["prs"], "PULL REQS", RED), (s["followers"], "FOLLOWERS", BLUE),
    ]
    for i, (v, label, c) in enumerate(tiles):
        svg.append(stat_tile(32 + i * 123.6, 676, v, label, c))

    # Streak + heatmap
    svg.append(f'''
<g transform="translate(32,760)">
  <rect width="736" height="40" rx="10" fill="{PANEL}"/>
  <text x="20" y="25" class="tag" style="fill:{TEXT}">CURRENT STREAK <tspan fill="{RED}" font-weight="800">{cur}d</tspan></text>
  <text x="368" y="25" text-anchor="middle" class="tag" style="fill:{TEXT}">LONGEST STREAK <tspan fill="{BLUE}" font-weight="800" style="fill:{BLUE_LIGHT}">{longest}d</tspan></text>
  <text x="716" y="25" text-anchor="end" class="tag" style="fill:{TEXT}">REPOS HELPED <tspan fill="{RED}" font-weight="800">{s["contributed_to"]}</tspan></text>
</g>
<text x="40" y="828" class="key">CONTRIBUTION WEB  ·  LAST 12 MONTHS</text>
''')
    svg.append(heatmap(s["days"], 40, 838))
    svg.append(f'''
<g transform="translate(40,945)" class="tag">
  <text x="0" y="10">LESS</text>
  <rect x="38" y="0" width="11" height="11" rx="2.5" fill="{HEAT[0]}"/>
  <rect x="53" y="0" width="11" height="11" rx="2.5" fill="{HEAT[1]}"/>
  <rect x="68" y="0" width="11" height="11" rx="2.5" fill="{RED_DARK}"/>
  <rect x="83" y="0" width="11" height="11" rx="2.5" fill="{HEAT[3]}"/>
  <rect x="98" y="0" width="11" height="11" rx="2.5" fill="{RED}"/>
  <text x="116" y="10">MORE</text>
</g>
<rect x="0" y="{H - 34}" width="{W}" height="34" fill="url(#bar)" opacity=".9"/>
<text x="{W / 2}" y="{H - 12}" text-anchor="middle" class="tag" style="fill:#fff">// WITH GREAT POWER COMES GREAT RESPONSIBILITY TO GIT PUSH //</text>
</g>
</svg>
''')
    return "".join(svg)


def main():
    stats = sample_stats() if "--sample" in sys.argv else fetch_stats()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(stats))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
