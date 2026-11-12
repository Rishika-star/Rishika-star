
import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from collections import defaultdict

TOKEN = os.environ["GH_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]

today = datetime.now(timezone.utc).date()
start_date = today - timedelta(days=364)

query = """
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

payload = {
    "query": query,
    "variables": {
        "username": USERNAME,
        "from": start_date.isoformat() + "T00:00:00Z",
        "to": today.isoformat() + "T23:59:59Z"
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

calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]

days = {}
for week in calendar["weeks"]:
    for day in week["contributionDays"]:
        days[day["date"]] = day["contributionCount"]

colors = ["#151B35", "#30275A", "#59449A", "#927DCC", "#B69AFF"]

def get_color(count):
    if count == 0:
        return colors[0]
    if count <= 2:
        return colors[1]
    if count <= 5:
        return colors[2]
    if count <= 9:
        return colors[3]
    return colors[4]

# Arrange days into GitHub-style columns (Sunday to Saturday)
first_day = start_date - timedelta(days=(start_date.weekday() + 1) % 7)
last_day = today + timedelta(days=(5 - today.weekday()) % 7)

weeks = []
current = first_day

while current <= last_day:
    week = []
    for _ in range(7):
        date_string = current.isoformat()
        count = days.get(date_string, 0)
        week.append((date_string, count))
        current += timedelta(days=1)
    weeks.append(week)

cell = 11
gap = 4
step = cell + gap
left = 35
top = 20

width = left + len(weeks) * step + 10
height = top + 7 * step + 25

rectangles = []

for x, week in enumerate(weeks):
    for y, (date_string, count) in enumerate(week):
        color = get_color(count)
        rectangles.append(
            f'<rect x="{left + x * step}" y="{top + y * step}" '
            f'width="{cell}" height="{cell}" rx="3" ry="3" '
            f'fill="{color}">'
            f'<title>{date_string}: {count} contributions</title>'
            f'</rect>'
        )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<g font-family="Arial, sans-serif" font-size="10" fill="#C9B6FF">
<text x="0" y="31">Sun</text>
<text x="0" y="46">Mon</text>
<text x="0" y="61">Tue</text>
<text x="0" y="76">Wed</text>
<text x="0" y="91">Thu</text>
<text x="0" y="106">Fri</text>
<text x="0" y="121">Sat</text>
</g>
{''.join(rectangles)}
</svg>'''

os.makedirs("profile", exist_ok=True)

with open("profile/contributions.svg", "w", encoding="utf-8") as file:
    file.write(svg)

print("Contribution heatmap generated successfully!")
print("Total contributions:", calendar["totalContributions"])

