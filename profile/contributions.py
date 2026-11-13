
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

    cell = 13
    gap = 5
    step = cell + gap
    left = 76
    top = 166

    weeks = []
    current = first_day

    while current <= end:
        week = []

        for _ in range(7):
            if start <= current <= end:
                ds = current.isoformat()
                week.append((ds, days.get(ds, 0)))

            current = current.fromordinal(current.toordinal() + 1)

        if week:
            weeks.append(week)

    width = left + len(weeks) * step + 35
    height = 490
    total = sum(days.values())

    # Reusable flower drawing
    def flower(cx, cy, scale, petal, center, opacity=1):
        petals = []

        for angle in range(0, 360, 72):
            petals.append(
                f'<ellipse cx="{cx}" cy="{cy - scale * 0.65}" '
                f'rx="{scale * 0.34}" ry="{scale * 0.65}" '
                f'fill="{petal}" '
                f'transform="rotate({angle} {cx} {cy})"/>'
            )

        return (
            f'<g opacity="{opacity}">'
            + ''.join(petals)
            + f'<circle cx="{cx}" cy="{cy}" '
            f'r="{scale * 0.27}" fill="{center}"/>'
            + '</g>'
        )

    # Background and glow effects
    background = f'''
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#090D20"/>
        <stop offset="55%" stop-color="#17132F"/>
        <stop offset="100%" stop-color="#302047"/>
      </linearGradient>

      <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#111329" stop-opacity="0.97"/>
        <stop offset="100%" stop-color="#201735" stop-opacity="0.97"/>
      </linearGradient>

      <linearGradient id="borderGlow">
        <stop offset="0%" stop-color="#A76BFF"/>
        <stop offset="50%" stop-color="#F0B5FF"/>
        <stop offset="100%" stop-color="#8E64DB"/>
      </linearGradient>

      <radialGradient id="moonGlow">
        <stop offset="0%" stop-color="#F5DFFF" stop-opacity="0.8"/>
        <stop offset="100%" stop-color="#B68AFF" stop-opacity="0"/>
      </radialGradient>

      <radialGradient id="lanternGlow">
        <stop offset="0%" stop-color="#FFE7A8" stop-opacity="0.9"/>
        <stop offset="100%" stop-color="#FFBD69" stop-opacity="0"/>
      </radialGradient>

      <filter id="glow">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>

      <filter id="softGlow">
        <feGaussianBlur stdDeviation="7"/>
      </filter>
    </defs>

    <rect width="{width}" height="{height}"
      fill="url(#sky)"/>
    '''

    # Stars
    stars = []

    for i in range(65):
        x = (i * 83 + 27) % width
        y = (i * 47 + 17) % 115
        r = 1.1 if i % 4 else 1.8

        stars.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" '
            f'fill="#E8D6FF" opacity="0.8"/>'
        )

    # Moon and clouds
    moon_x = width - 88

    moon = f'''
    <circle cx="{moon_x}" cy="57" r="55"
      fill="url(#moonGlow)"/>
    <circle cx="{moon_x}" cy="57" r="23"
      fill="#F0E3FF" filter="url(#glow)"/>
    <circle cx="{moon_x-8}" cy="49" r="4"
      fill="#D8C2F4" opacity="0.5"/>
    <circle cx="{moon_x+8}" cy="65" r="5"
      fill="#D8C2F4" opacity="0.4"/>

    <path d="M{moon_x-70} 76 Q{moon_x-45} 53
    {moon_x-20} 73 Q{moon_x+5} 60
    {moon_x+32} 77 L{moon_x+40} 86
    L{moon_x-65} 86 Z"
    fill="#554078" opacity="0.8"/>
    '''

    # Decorative blossom branches
    branches = []

    branches.append(f'''
    <g fill="none" stroke="#70528F"
       stroke-width="3" stroke-linecap="round">
      <path d="M-15 115 Q25 82 45 30 Q65 5 110 -8"/>
      <path d="M15 72 Q58 68 92 34"/>
      <path d="M36 46 Q20 22 18 5"/>
      <path d="M53 29 Q80 10 125 14"/>
    </g>
    ''')

    branches.append(f'''
    <g fill="#A78BC5" opacity="0.9">
      <ellipse cx="40" cy="63" rx="5" ry="12"
        transform="rotate(-45 40 63)"/>
      <ellipse cx="72" cy="48" rx="5" ry="12"
        transform="rotate(45 72 48)"/>
      <ellipse cx="91" cy="20" rx="5" ry="12"
        transform="rotate(65 91 20)"/>
      <ellipse cx="18" cy="31" rx="5" ry="12"
        transform="rotate(-35 18 31)"/>
    </g>
    ''')

    for x, y, s in [
        (22, 25, 10), (58, 13, 9),
        (92, 35, 8), (120, 10, 7),
        (8, 83, 8), (43, 52, 7)
    ]:
        branches.append(
            flower(x, y, s, "#DDA6FF", "#FFF0D8")
        )

    # Small decorative branch on upper-right
    branches.append(f'''
    <g fill="none" stroke="#9270B7"
      stroke-width="2">
      <path d="M{width-190} 100 Q{width-145} 65
      {width-120} 15"/>
      <path d="M{width-150} 65 Q{width-110} 70
      {width-85} 35"/>
    </g>
    ''')

    branches.append(
        flower(width-120, 29, 9, "#DCA4FF", "#FFF0D8")
    )

    # Contribution panel
    panel = f'''
    <rect x="18" y="112" width="{width-36}"
      height="235" rx="16"
      fill="url(#panel)"
      stroke="url(#borderGlow)" stroke-width="1.5"
      filter="url(#glow)"/>

    <rect x="20" y="114" width="{width-40}"
      height="231" rx="15"
      fill="none" stroke="#B88BFF"
      stroke-opacity="0.3"/>
    '''

    # Header
    header = f'''
    <text x="65" y="73" font-size="30"
      font-family="Georgia, serif"
      fill="#F0D8FF">{total} contributions in {year}</text>

    <text x="{width-310}" y="68"
      font-size="15" fill="#E6D2FF"
      font-family="Georgia, serif">
      Flower Meadow
    </text>

    <rect x="{width-115}" y="36" width="88"
      height="35" rx="9"
      fill="#51356F" stroke="#BD8BFF"/>
    <text x="{width-71}" y="59"
      text-anchor="middle" font-size="16"
      fill="#F5E5FF">{year}</text>
    '''

    # Month labels
    month_labels = []

    for x, week in enumerate(weeks):
        for ds, count in week:
            if ds[8:10] == "01":
                month = datetime.strptime(
                    ds, "%Y-%m-%d"
                ).strftime("%b")

                month_labels.append(
                    f'<text x="{left+x*step}" y="151" '
                    f'font-size="13" fill="#E8D4FF" '
                    f'font-family="Georgia, serif">'
                    f'{month}</text>'
                )
                break

    # Weekday labels
    day_labels = []

    for index, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        day_labels.append(
            f'<text x="25" y="{top+index*step+10}" '
            f'font-size="11" fill="#D8B8FF">{name}</text>'
        )

    # Contribution flowers
    flowers = []

    for x, week in enumerate(weeks):
        for ds, count in week:
            weekday = datetime.strptime(
                ds, "%Y-%m-%d"
            ).weekday()

            y = (weekday + 1) % 7

            cx = left + x * step + cell / 2
            cy = top + y * step + cell / 2

            if count == 0:
                petal, center, scale = "#49345F", "#8C6BAA", 4
                opacity = 0.65
            elif count <= 2:
                petal, center, scale = "#A77AD7", "#E5C7FF", 4.5
                opacity = 0.9
            elif count <= 5:
                petal, center, scale = "#D78BE0", "#FFE1F7", 5
                opacity = 1
            else:
                petal, center, scale = "#F0B1F0", "#FFF0C5", 5.5
                opacity = 1

            if count >= 3:
                flowers.append(
                    f'<circle cx="{cx}" cy="{cy}" r="8" '
                    f'fill="#D58CFF" opacity="0.22" '
                    f'filter="url(#softGlow)"/>'
                )

            flowers.append(
                f'<g filter="url(#glow)">'
                + flower(cx, cy, scale, petal, center, opacity)
                + f'<title>{ds}: {count} contributions</title>'
                + '</g>'
            )

    # Legend
    legend = '''
    <text x="35" y="328" font-size="12"
      fill="#E4CFFF">✧ Contribution activity</text>
    <text x="700" y="328" font-size="12"
      fill="#E4CFFF">Less</text>
    '''

    for i, (petal, center, scale) in enumerate([
        ("#49345F", "#8C6BAA", 4),
        ("#A77AD7", "#E5C7FF", 4.5),
        ("#D78BE0", "#FFE1F7", 5),
        ("#F0B1F0", "#FFF0C5", 6)
    ]):
        legend += flower(
            748 + i * 27, 324, scale, petal, center
        )

    legend += '''
    <text x="865" y="328" font-size="12"
      fill="#E4CFFF">More</text>
    '''

    # Layered meadow hills
    meadow = f'''
    <path d="M0 410 Q150 350 300 405
    T600 393 T900 400 T{width} 385
    L{width} 490 L0 490 Z"
    fill="#211A3C"/>

    <path d="M0 438 Q180 375 340 430
    T680 423 T{width} 420
    L{width} 490 L0 490 Z"
    fill="#302249"/>

    <path d="M0 465 Q200 420 420 458
    T800 451 T{width} 455
    L{width} 490 L0 490 Z"
    fill="#44305E"/>
    '''

    # Meadow plants and fireflies
    plants = []

    for i in range(55):
        x = (i * 47 + 15) % width
        y = 468 - (i % 4) * 7
        size = 5 + (i % 4)

        plants.append(
            f'<path d="M{x} {y} q-9 -20 -4 -30 '
            f'M{x} {y} q8 -17 13 -24" '
            f'fill="none" stroke="#9C83B8" '
            f'stroke-width="1.5" opacity="0.8"/>'
        )

        if i % 3 == 0:
            plants.append(
                flower(
                    x, y-23, size,
                    "#D79BEF", "#FFF0D5", 0.9
                )
            )

    fireflies = []

    for i in range(18):
        x = (i * 67 + 35) % width
        y = 375 + (i % 3) * 17

        fireflies.append(
            f'<circle cx="{x}" cy="{y}" r="2.2" '
            f'fill="#FFD58D" filter="url(#glow)"/>'
        )

    # Detailed lantern
    lx = width - 75

    lantern = f'''
    <circle cx="{lx}" cy="425" r="45"
      fill="url(#lanternGlow)" filter="url(#softGlow)"/>

    <g transform="translate({lx},424)" filter="url(#glow)">
      <path d="M-10 -30 L10 -30 L15 8
      L-15 8 Z" fill="#3B294A"
      stroke="#D5A76E" stroke-width="2"/>

      <path d="M-7 -25 L7 -25 L9 4
      L-9 4 Z" fill="#FFD88F"/>

      <path d="M-5 -30 Q0 -48 5 -30"
      fill="none" stroke="#E9C18D" stroke-width="2"/>

      <path d="M-14 9 L14 9 L18 15
      L-18 15 Z" fill="#76513F"
      stroke="#E8BF8B" stroke-width="1.5"/>

      <path d="M-10 -33 L-7 -39 L7 -39
      L10 -33 Z" fill="#61435C"
      stroke="#E8BF8B" stroke-width="1.5"/>

      <path d="M-4 -42 Q0 -52 4 -42"
      fill="none" stroke="#E8BF8B" stroke-width="2"/>
    </g>
    '''

    # Final SVG
    return f'''<svg xmlns="http://www.w3.org/2000/svg"
      width="{width}" height="{height}"
      viewBox="0 0 {width} {height}">

      {background}
      {''.join(stars)}
      {moon}
      {''.join(branches)}
      {header}
      {panel}

      <g font-family="Arial, sans-serif">
        {''.join(month_labels)}
        {''.join(day_labels)}
        {''.join(flowers)}
      </g>

      {legend}
      {meadow}
      {''.join(fireflies)}
      {''.join(plants)}
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
