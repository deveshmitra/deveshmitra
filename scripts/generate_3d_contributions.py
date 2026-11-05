#!/usr/bin/env python3
"""Generate a GitHub README-compatible isometric contribution chart."""
import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = os.environ.get("GITHUB_USERNAME", "deveshmitra")
TOKEN = os.environ["GITHUB_TOKEN"]
OUTPUT = Path(os.environ.get("OUTPUT_FILE", "3d-contributions.svg"))

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

def fetch_contributions():
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=363)
    variables = {
        "login": USERNAME,
        "from": start.isoformat() + "T00:00:00Z",
        "to": today.isoformat() + "T23:59:59Z",
    }
    body = json.dumps({"query": QUERY, "variables": variables}).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "github-readme-3d-contributions",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read())
    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL error: " + str(result["errors"]))
    user = result.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found or inaccessible: {USERNAME}")
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [
        day
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    return days, calendar["totalContributions"]

def faces(count, maximum):
    if count == 0:
        return "#10243A", "#173653", "#0A1828"
    level = count / max(maximum, 1)
    if level <= 0.25:
        return "#063B63", "#075A8C", "#042B49"
    if level <= 0.50:
        return "#0066A8", "#008BCB", "#004D80"
    if level <= 0.75:
        return "#008FCB", "#00B7E8", "#006D9E"
    return "#00D9FF", "#75E9FF", "#0096C7"

def make_svg(days, total):
    if not days:
        raise RuntimeError("GitHub returned no contribution days.")

    max_count = max((int(day["contributionCount"]) for day in days), default=1)
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()

    cell_w, cell_d = 13, 8
    cube_w, cube_d = 10, 6
    origin_x, origin_y = 55, 92
    max_height = 38
    width, height = 900, 310

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(USERNAME)} — 3D GitHub contributions</title>',
        f'<desc id="desc">{total} contributions in the last year, shown as an isometric cube chart.</desc>',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111827"/><stop offset="1" stop-color="#080D16"/></linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="18" fill="url(#bg)"/>',
        '<text x="28" y="34" fill="#E6EDF3" font-family="Arial,sans-serif" font-size="17" font-weight="700">GitHub Activity · 3D</text>',
        f'<text x="28" y="55" fill="#9AA7B4" font-family="Arial,sans-serif" font-size="11">{escape(USERNAME)} · {total:,} contributions in the last year</text>',
    ]

    for item in days:
        date = datetime.strptime(item["date"], "%Y-%m-%d").date()
        week = (date - first).days // 7
        weekday = (date.weekday() + 1) % 7  # Sunday = 0
        x = origin_x + week * cell_w - weekday * cell_d
        y = origin_y + week * 2 + weekday * 6
        count = int(item["contributionCount"])
        top, left, right = faces(count, max_count)
        title = escape(f'{item["date"]}: {count} contributions')

        if count == 0:
            points = f"{x},{y} {x+cube_w},{y-3} {x+cube_w+cube_d},{y} {x+cube_d},{y+3}"
            parts.append(
                f'<polygon points="{points}" fill="{left}" opacity="0.9"><title>{title}</title></polygon>'
            )
            continue

        cube_h = min(max_height, 5 + round(27 * count / max(max_count, 1)))
        top_face = f"{x},{y-cube_h} {x+cube_w},{y-cube_h-3} {x+cube_w+cube_d},{y-cube_h} {x+cube_d},{y-cube_h+3}"
        left_face = f"{x},{y-cube_h} {x+cube_d},{y-cube_h+3} {x+cube_d},{y+3} {x},{y}"
        right_face = f"{x+cube_d},{y-cube_h+3} {x+cube_w+cube_d},{y-cube_h} {x+cube_w+cube_d},{y} {x+cube_d},{y+3}"
        parts.append(
            f'<g><title>{title}</title><polygon points="{left_face}" fill="{left}"/>'
            f'<polygon points="{right_face}" fill="{right}"/>'
            f'<polygon points="{top_face}" fill="{top}"/></g>'
        )

    parts.append('<text x="28" y="280" fill="#9AA7B4" font-family="Arial,sans-serif" font-size="10">Less</text>')
    legend = ["#10243A", "#063B63", "#0066A8", "#008FCB", "#00D9FF"]
    for index, color in enumerate(legend):
        parts.append(
            f'<rect x="{61 + index * 17}" y="270" width="12" height="9" rx="2" fill="{color}"/>'
        )
    parts.extend([
        '<text x="155" y="280" fill="#9AA7B4" font-family="Arial,sans-serif" font-size="10">More</text>',
        '<text x="872" y="298" text-anchor="end" fill="#64748B" font-family="Arial,sans-serif" font-size="9">Updated automatically · GitHub Contributions</text>',
        '</svg>',
    ])
    return "\n".join(parts)

def main():
    days, total = fetch_contributions()
    OUTPUT.write_text(make_svg(days, total), encoding="utf-8")
    print(f"Generated {OUTPUT} for {USERNAME}: {total} contributions")

if __name__ == "__main__":
    main()
