"""Fetch the numbers the Daily Bugle reports and the Web of Activity need.

Uses GITHUB_TOKEN (the Actions token is enough). Private contributions are only
counted when "Private contributions" is enabled in the profile's contribution
settings, and then only as counts.
"""

import datetime as dt
import json
import os
import random
import sys
import urllib.request

USER = os.environ.get("GH_USER", "navinskyy")
MANILA = dt.timezone(dt.timedelta(hours=8))


def gql(query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


PROFILE = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    original: repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    forks: repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: true) { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions }
    }
  }
}
"""


def fetch():
    u = gql(PROFILE, {"login": USER})
    created = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    now = dt.datetime.now(dt.timezone.utc)

    # contributionsCollection spans at most a year, so request every calendar year at once
    parts = []
    for year in range(created.year, now.year + 1):
        start = max(created, dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
        end = min(now, dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        parts.append(f'y{year}: contributionsCollection(from: "{start.isoformat()}", to: "{end.isoformat()}") '
                     "{ contributionCalendar { weeks { contributionDays { date contributionCount } } } }")
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

    cc = u["contributionsCollection"]
    return {
        "days": sorted(days.items()),
        "year_total": cc["contributionCalendar"]["totalContributions"],
        "public_commits": cc["totalCommitContributions"],
        "private": cc["restrictedContributionsCount"],
        "prs": u["pullRequests"]["totalCount"],
        "followers": u["followers"]["totalCount"],
        "original": u["original"]["totalCount"],
        "forks": u["forks"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["original"]["nodes"]),
        "langs": langs,
    }


def sample():
    rnd = random.Random(5)
    today = dt.datetime.now(MANILA).date()
    d, days = dt.date(2023, 5, 21), []
    while d <= today:
        recent = (today - d).days < 120
        n = rnd.choice([1, 1, 2, 3, 5, 8]) if rnd.random() < (0.45 if recent else 0.02) else 0
        days.append((d.isoformat(), n))
        d += dt.timedelta(days=1)
    days[-1] = (days[-1][0], 2)
    year = [n for ds, n in days if ds > (today - dt.timedelta(days=365)).isoformat()]
    return {"days": days, "year_total": sum(year), "public_commits": 128, "private": 41, "prs": 1,
            "followers": 2, "original": 11, "forks": 9, "stars": 0,
            "langs": {"JavaScript": 2160000, "CSS": 330000, "Python": 250000, "HTML": 120000,
                      "Astro": 47000, "TypeScript": 31000, "Shell": 25000, "Batchfile": 25000}}


def summarize(s):
    """Derived numbers: 12-month window, streaks with dates, all-time total."""
    days = s["days"]
    today = dt.datetime.now(MANILA).date()
    cutoff = (today - dt.timedelta(days=365)).isoformat()
    last_year = [(d, n) for d, n in days if d > cutoff]

    best, run, start = (0, None, None), 0, None
    for d, n in days:
        if n:
            start = d if run == 0 else start
            run += 1
            if run > best[0]:
                best = (run, start, d)
        else:
            run = 0

    cur = (0, None, None)
    i = len(days) - 1
    if i >= 0 and days[i][1] == 0:  # no contribution yet today doesn't break the streak
        i -= 1
    end = days[i][0] if i >= 0 else None
    while i >= 0 and days[i][1]:
        cur = (cur[0] + 1, days[i][0], end)
        i -= 1

    return {
        "last_year": last_year,
        "active_days": sum(1 for _, n in last_year if n),
        "all_time": sum(n for _, n in days),
        "first": next((d for d, n in days if n), None),
        "cur": cur,
        "best": best,
        "today": today,
    }


def load():
    return sample() if "--sample" in sys.argv else fetch()
