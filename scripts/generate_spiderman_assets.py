from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = "#39d353"
LIGHT = "#b6fcb6"
RED = "#d9273f"
BLUE = "#172c63"
BG = "#020807"
INK = "#f7fff8"


def profile_card() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300" role="img" aria-labelledby="title desc">
<title id="title">Navin Llanes — cybersecurity intern and computer science student</title>
<desc id="desc">A Spider-Man-inspired profile card with animated web lines and a red and blue climber.</desc>
<defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="#092016"/><stop offset="1" stop-color="{BG}"/></linearGradient><pattern id="w" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M30 0v60M0 30h60M8 8l44 44M52 8L8 52" stroke="{GREEN}" stroke-opacity=".15"/><circle cx="30" cy="30" r="16" fill="none" stroke="{GREEN}" stroke-opacity=".14"/></pattern></defs>
<rect width="900" height="300" rx="18" fill="url(#g)"/><rect width="900" height="300" rx="18" fill="url(#w)" stroke="{GREEN}" stroke-opacity=".4"/>
<path d="M48 70q0-28 28-28h485q28 0 28 28v76q0 28-28 28H267l-44 32 10-32H76q-28 0-28-28z" fill="#f7f7f2" stroke="{RED}" stroke-width="5"/>
<text x="300" y="86" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="900" fill="#101820">WITH GREAT POWER</text><text x="300" y="119" text-anchor="middle" font-family="Arial,sans-serif" font-size="25" font-weight="900" fill="{RED}">COMES GREAT RESPONSIBILITY.</text><text x="300" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#52605b">Navin Llanes · Cybersecurity Intern at Rivan</text>
<g transform="translate(725 136)" stroke-linecap="round" stroke-linejoin="round"><animateTransform attributeName="transform" type="translate" values="725 136;725 118;725 136" dur="2.4s" repeatCount="indefinite"/><circle cx="0" cy="-38" r="18" fill="{RED}" stroke="white" stroke-width="2"/><path d="M-11-39l8-7m3 10 9-6m-7 15-8-6M-12-7l-35 25m47-25 35 25M-9 5l-17 40M9 5l17 40" fill="none" stroke="{RED}" stroke-width="15"/><path d="M-11-39l8-7m3 10 9-6M-9 5l18 0" fill="none" stroke="white" stroke-width="2"/></g>
<text x="48" y="248" font-family="Consolas,monospace" font-size="14" fill="{LIGHT}">BS COMPUTER SCIENCE · LPU MANILA · VS CODE</text><text x="48" y="272" font-family="Consolas,monospace" font-size="13" fill="{GREEN}">WEB DEVELOPMENT // CYBERSECURITY // SOFTWARE ENGINEERING</text>
</svg>'''


def daily_graph() -> str:
    values = [1, 2, 0, 4, 3, 1, 6, 8, 2, 0, 4, 5, 9, 3, 1, 2, 7, 5, 4, 10, 6, 2, 1, 5, 8, 4, 3, 6, 2, 1, 4]
    bars = []
    for i, value in enumerate(values, 1):
        height = 12 + value * 10
        color = ["#0e4429", "#006d32", "#26a641", GREEN, LIGHT][min(value // 3, 4)]
        bars.append(f'<g><title>Day {i}: {value} contributions</title><rect x="{35 + (i-1)*27}" y="205" width="18" height="{height}" rx="3" fill="{color}"/></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="260" viewBox="0 0 900 260" role="img" aria-labelledby="title desc"><title id="title">Daily GitHub contributions</title><desc id="desc">A green daily contribution bar chart with hover labels for each day.</desc><rect width="900" height="260" rx="18" fill="{BG}"/><path d="M35 205h830" stroke="{LIGHT}" stroke-opacity=".35"/>{''.join(bars)}<text x="35" y="32" font-family="Arial,sans-serif" font-size="19" font-weight="900" fill="{INK}">DAILY CONTRIBUTIONS // THE WEB</text><text x="35" y="54" font-family="Arial,sans-serif" font-size="12" fill="{LIGHT}">Hover a node for the exact daily count · GitHub green intensity</text><g transform="translate(430 142)" fill="none" stroke-linecap="round"><animateTransform attributeName="transform" type="translate" values="430 142;457 126;484 142;511 120;538 142" dur="6s" repeatCount="indefinite"/><circle cy="-20" r="12" fill="{RED}" stroke="white" stroke-width="2"/><path d="M-8-10l-28 18m36-18 28 18M-5 0l-12 28m17-28 12 28" stroke="{RED}" stroke-width="9"/><path d="M-7 0h14" stroke="white" stroke-width="2"/></g><text x="35" y="232" font-family="Consolas,monospace" font-size="11" fill="{GREEN}">LOW ACTIVITY</text><text x="790" y="232" font-family="Consolas,monospace" font-size="11" fill="{LIGHT}">HIGH ACTIVITY</text></svg>'''


def activity() -> str:
    nodes = [(170, 610, "NEW REPOSITORIES", "3 launched", "last 6 months"), (170, 470, "PROJECT Y", "150 commits", "top repository"), (170, 330, "PROJECT X", "300 commits", "top repository"), (170, 190, "CONTRIBUTIONS", "1,200 total", "last 12 months")]
    body = []
    for x, y, label, value, period in nodes:
        body.append(f'<g><circle cx="{x}" cy="{y}" r="14" fill="#0d4429" stroke="{GREEN}" stroke-width="4"><title>{label}: {value} ({period})</title></circle><circle cx="{x}" cy="{y}" r="4" fill="{LIGHT}"/><path d="M{ x+16} {y}H650" stroke="{GREEN}" stroke-width="2" stroke-dasharray="5 7"/><text x="675" y="{y-18}" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="{LIGHT}">{label}</text><text x="675" y="{y+10}" font-family="Arial,sans-serif" font-size="25" font-weight="900" fill="{INK}">{value}</text><text x="675" y="{y+31}" font-family="Arial,sans-serif" font-size="12" fill="#9be9a8">{period}</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="720" viewBox="0 0 900 720" role="img" aria-labelledby="title desc"><title id="title">Contribution activity timeline with Spider-Man climbing upward</title><desc id="desc">An animated Spider-Man-inspired climber moves up a green vertical timeline past contribution milestones. Hover nodes for exact values.</desc><defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="#092016"/><stop offset="1" stop-color="{BG}"/></linearGradient><pattern id="w" width="70" height="70" patternUnits="userSpaceOnUse"><path d="M35 0v70M0 35h70M10 10l50 50M60 10L10 60" stroke="{GREEN}" stroke-opacity=".12"/></pattern></defs><rect width="900" height="720" rx="18" fill="url(#g)"/><rect width="900" height="720" rx="18" fill="url(#w)"/><text x="48" y="55" font-family="Arial,sans-serif" font-size="22" font-weight="900" fill="{INK}">CONTRIBUTION ACTIVITY // CLIMBING THE TIMELINE</text><text x="48" y="80" font-family="Arial,sans-serif" font-size="13" fill="{LIGHT}">Green web nodes carry exact values in hover tooltips.</text><path d="M170 610V190" stroke="{GREEN}" stroke-width="5"/><path d="M170 610V190" stroke="{LIGHT}" stroke-opacity=".18" stroke-width="14"/>{''.join(body)}<g><animateMotion dur="8s" repeatCount="indefinite" path="M170 650 V610 V470 V330 V190"/><g transform="translate(-20 -20)" stroke-linecap="round" stroke-linejoin="round"><circle cy="-17" r="13" fill="{RED}" stroke="white" stroke-width="2"/><path d="M-8-8l-25 18m33-18 25 18M-6 2l-12 26m12-26 14 26" stroke="{RED}" stroke-width="10"/><path d="M-8 2h16" stroke="white" stroke-width="2"/><path d="M-27 10l-8 8m52-8 8 8" stroke="{LIGHT}" stroke-width="2" stroke-dasharray="3 4"><animate attributeName="stroke-dashoffset" values="0;-14" dur=".7s" repeatCount="indefinite"/></path></g></g><text x="48" y="680" font-family="Consolas,monospace" font-size="12" fill="{GREEN}">KEEP CLIMBING · KEEP CONTRIBUTING · KEEP THE WEB STRONG</text></svg>'''


def main() -> None:
    (ROOT / "profile_card.svg").write_text(profile_card(), encoding="utf-8")
    (ROOT / "daily_graph.svg").write_text(daily_graph(), encoding="utf-8")
    (ROOT / "activity.svg").write_text(activity(), encoding="utf-8")
    print("generated profile_card.svg, daily_graph.svg, activity.svg")


if __name__ == "__main__":
    main()
