
import os
import json
import urllib.request
from datetime import date, datetime, timezone

TOKEN = os.environ["GH_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]

START_YEAR = 2026
CURRENT_YEAR = datetime.now(timezone.utc).year
TODAY = datetime.now(timezone.utc).date()

QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
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

COLORS = ["#151B35", "#30275A", "#59449A", "#927DCC", "#B69AFF"]

def get_color(count):
    if count == 0:
        return COLORS[0]
    if count <= 2:
        return COLORS[1]
    if count <= 5:
        return COLORS[2]
    if count <= 9:
        return COLORS[3]
    return COLORS[4]


def fetch_year(year):
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    if year == CURRENT_YEAR:
        end = TODAY

    payload = {
        "query": QUERY,
        "variables": {
            "username": USERNAME,
            "from": start.isoformat() + "T00:00:00Z",
            "to": end.isoformat() + "T23:59:59Z"
        }
    }

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "errors" in result:
        raise Exception(result["errors"])

    user = result.get("data", {}).get("user")
    if user is None:
        raise Exception("GitHub user not found: " + USERNAME)

    calendar = user["contributionsCollection"]["contributionCalendar"]

    days = {}
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days[day["date"]] = day["contributionCount"]

    return days, calendar["totalContributions"]



def create_year_svg(year, days):
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    first_day = start.fromordinal(
        start.toordinal() - (start.weekday() + 1) % 7
    )

    cell = 16
    gap = 5
    step = cell + gap
    left = 42
    top = 65

    weeks = []
    current = first_day

    while current <= end:
        week = []

        for _ in range(7):
            if start <= current <= end:
                date_string = current.isoformat()
                week.append((date_string, days.get(date_string, 0)))

            current = current.fromordinal(current.toordinal() + 1)

        if week:
            weeks.append(week)

    width = left + len(weeks) * step + 20
    height = top + 7 * step + 135

    # SVG definitions and background
    background = f'''
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#10152D"/>
        <stop offset="100%" stop-color="#21183D"/>
      </linearGradient>

      <radialGradient id="moonGlow">
        <stop offset="0%" stop-color="#E6D8FF" stop-opacity="0.7"/>
        <stop offset="100%" stop-color="#B69AFF" stop-opacity="0"/>
      </radialGradient>

      <filter id="glow">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>

    <rect width="100%" height="100%" rx="18" fill="url(#sky)"/>
    '''

    # Moon and stars
    moon = '''
    <circle cx="90%" cy="55" r="42" fill="url(#moonGlow)"/>
    <circle cx="90%" cy="55" r="17" fill="#E9DCFF"/>
    '''

    stars = []
    for i in range(24):
        x = (i * 79 + 31) % width
        y = (i * 37 + 13) % 55
        stars.append(
            f'<circle cx="{x}" cy="{y}" r="1.5" '
            f'fill="#D9C8FF" opacity="0.7"/>'
        )

    # Month labels
    month_labels = []
    for x, week in enumerate(weeks):
        for date_string, count in week:
            if date_string[8:10] == "01":
                month = datetime.strptime(
                    date_string, "%Y-%m-%d"
                ).strftime("%b")

                month_labels.append(
                    f'<text x="{left + x * step}" y="48" '
                    f'font-size="12" fill="#D9C8FF">{month}</text>'
                )
                break

    # Weekday labels
    day_labels = []
    for index, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        day_labels.append(
            f'<text x="4" y="{top + index * step + 11}" '
            f'font-size="10" fill="#C9B6FF">{name}</text>'
        )

    # Flower contribution cells
    flowers = []

    for x, week in enumerate(weeks):
        for date_string, count in week:
            weekday = datetime.strptime(
                date_string, "%Y-%m-%d"
            ).weekday()

            y = (weekday + 1) % 7
            cx = left + x * step + cell / 2
            cy = top + y * step + cell / 2

            if count == 0:
                petal = "#493B67"
                center = "#79659B"
                opacity = 0.55
            elif count <= 2:
                petal = "#9C7ACB"
                center = "#D8B7FF"
                opacity = 0.85
            elif count <= 5:
                petal = "#D58CCF"
                center = "#FFE0F4"
                opacity = 1
            else:
                petal = "#E9B1E5"
                center = "#FFF0C9"
                opacity = 1

            petals = []
            for angle in range(0, 360, 60):
                petals.append(
                    f'<ellipse cx="{cx}" cy="{cy - 4}" '
                    f'rx="2.5" ry="4" fill="{petal}" '
                    f'transform="rotate({angle} {cx} {cy})"/>'
                )

            flowers.append(
                f'<g opacity="{opacity}" filter="url(#glow)">'
                + ''.join(petals)
                + f'<circle cx="{cx}" cy="{cy}" r="2.1" '
                f'fill="{center}"/>'
                + f'<title>{date_string}: {count} contributions</title>'
                + '</g>'
            )

    # Decorative meadow
    meadow = f'''
    <path d="M0 {height-75} Q{width/3} {height-115}
    {width/2} {height-72} T{width} {height-90}
    L{width} {height} L0 {height} Z"
    fill="#24203F"/>

    <path d="M0 {height-40} Q{width/2} {height-85}
    {width} {height-45} L{width} {height}
    L0 {height} Z" fill="#30244A"/>
    '''

    grass = []
    for i in range(38):
        x = (i * 53 + 19) % width
        y = height - 18 - (i % 5) * 5

        grass.append(
            f'<path d="M{x} {y} q-7 -18 -4 -25 '
            f'M{x} {y} q7 -15 11 -21" '
            f'fill="none" stroke="#8B76A9" '
            f'stroke-width="1.5" opacity="0.8"/>'
        )

    # Decorative lantern
    lantern = f'''
    <g transform="translate({width-55},{height-62})" filter="url(#glow)">
      <path d="M-7 -20 L7 -20 L10 7 L-10 7 Z"
      fill="#C99A72" stroke="#E9C6A1" stroke-width="1.5"/>
      <path d="M-5 -16 L5 -16 L6 3 L-6 3 Z"
      fill="#FFD99A"/>
      <path d="M-5 -22 Q0 -34 5 -22"
      fill="none" stroke="#E9C6A1" stroke-width="2"/>
      <path d="M-13 8 L13 8" stroke="#E9C6A1" stroke-width="2"/>
    </g>
    '''

    return f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="100%" height="{height}" viewBox="0 0 {width} {height}">
    {background}
    {moon}
    {''.join(stars)}
    <g font-family="Arial, sans-serif">
      {''.join(month_labels)}
      {''.join(day_labels)}
      {''.join(flowers)}
    </g>
    {meadow}
    {''.join(grass)}
    {lantern}
    </svg>'''



os.makedirs("profile", exist_ok=True)

year_links = []

for year in range(START_YEAR, CURRENT_YEAR + 1):
    days, total = fetch_year(year)

    svg = create_year_svg(year, days)
    filename = f"profile/contributions-{year}.svg"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(svg)

    year_links.append(
        f'<a href="profile/contributions-{year}.svg">'
        f'{year}</a>'
    )

    print(f"{year}: {total} contributions generated")

# Current year's graph is shown by default.
current_file = f"profile/contributions-{CURRENT_YEAR}.svg"

with open(current_file, "r", encoding="utf-8") as file:
    current_svg = file.read()

with open("profile/contributions.svg", "w", encoding="utf-8") as file:
    file.write(current_svg)

# Update the year selector in README.
readme_path = "README.md"
start_marker = "<!-- CONTRIBUTION_YEARS_START -->"
end_marker = "<!-- CONTRIBUTION_YEARS_END -->"

with open(readme_path, "r", encoding="utf-8") as file:
    readme = file.read()

if start_marker in readme and end_marker in readme:
    links = " &nbsp; | &nbsp; ".join(year_links)

    section = (
        start_marker + "\n"
        + '<p align="center">' + links + '</p>\n'
        + '<p align="center">'
        + f'<img src="profile/contributions.svg" '
        + 'width="100%" alt="Yearly Contribution Graph"/>'
        + '</p>\n'
        + end_marker
    )

    before, remainder = readme.split(start_marker, 1)
    _, after = remainder.split(end_marker, 1)

    with open(readme_path, "w", encoding="utf-8") as file:
        file.write(before + section + after)
else:
    print("README year-selector markers not added yet.")

print("Yearly contribution graphs generated successfully!")
