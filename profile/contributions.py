
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

    # Start the calendar on Sunday.
    first_day = start.fromordinal(
        start.toordinal() - (start.weekday() + 1) % 7
    )

    # End the calendar on Saturday.
   last_day = end

    cell = 13
    gap = 4
    step = cell + gap
    left = 38
    top = 35

    weeks = []
    current = first_day

    while current <= last_day:
        week = []
        for _ in range(7):
            date_string = current.isoformat()
            week.append((date_string, days.get(date_string, 0)))
            current = current.fromordinal(current.toordinal() + 1)
        weeks.append(week)

    width = left + len(weeks) * step + 10
    height = top + 7 * step + 15

    month_labels = []
    for x, week in enumerate(weeks):
        for date_string, count in week:
            if date_string[8:10] == "01" and date_string[:4] == str(year):
                month = datetime.strptime(
                    date_string, "%Y-%m-%d"
                ).strftime("%b")

                month_labels.append(
                    f'<text x="{left + x * step}" y="20" '
                    f'font-size="12" fill="#E4E9FF">{month}</text>'
                )
                break

    day_labels = []
    for index, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        day_labels.append(
            f'<text x="0" y="{top + index * step + 11}" '
            f'font-size="11" fill="#C9B6FF">{name}</text>'
        )

    rectangles = []
    for x, week in enumerate(weeks):
        for y, (date_string, count) in enumerate(week):
            rectangles.append(
                f'<rect x="{left + x * step}" '
                f'y="{top + y * step}" '
                f'width="{cell}" height="{cell}" '
                f'rx="3" ry="3" fill="{get_color(count)}">'
                f'<title>{date_string}: {count} contributions</title>'
                f'</rect>'
            )

    return f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="100%" height="{height}" viewBox="0 0 {width} {height}">
    <g font-family="Arial, sans-serif">
    {''.join(month_labels)}
    {''.join(day_labels)}
    {''.join(rectangles)}
    </g>
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
