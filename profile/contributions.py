
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

    # Flower drawing helper
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

    # Background and lighting
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

    # Moon
    moon_x = width - 175

    moon = f'''
    <circle cx="{moon_x}" cy="57" r="62"
      fill="url(#moonGlow)"/>

    <circle cx="{moon_x}" cy="57" r="29"
      fill="#F0E3FF" filter="url(#glow)"/>

    <circle cx="{moon_x-8}" cy="49" r="4"
      fill="#D8C2F4" opacity="0.5"/>

    <circle cx="{moon_x+8}" cy="65" r="5"
      fill="#D8C2F4" opacity="0.4"/>
    '''

    # Floral branches
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

    branches.append('''
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
        (22, 25, 10),
        (58, 13, 9),
        (92, 35, 8),
        (120, 10, 7),
        (8, 83, 8),
        (43, 52, 7)
    ]:
        branches.append(
            flower(x, y, s, "#DDA6FF", "#FFF0D8")
        )

    # Upper-right flower branch
    branches.append(f'''
    <g fill="none" stroke="#9270B7"
      stroke-width="2.5" stroke-linecap="round">

      <path d="M{width-390} 105
      Q{width-345} 75 {width-315} 18"/>

      <path d="M{width-350} 73
      Q{width-320} 83 {width-285} 48"/>

      <path d="M{width-330} 47
      Q{width-300} 20 {width-270} 16"/>

    </g>
    ''')

    for x, y, s in [
        (width-315, 27, 10),
        (width-285, 48, 8),
        (width-270, 15, 9),
        (width-350, 75, 7)
    ]:
        branches.append(
            flower(x, y, s, "#DDA6FF", "#FFF0D8")
        )

    # Glass contribution panel
    panel = f'''
    <rect x="18" y="112" width="{width-36}"
      height="235" rx="16"
      fill="url(#panel)"
      stroke="url(#borderGlow)"
      stroke-width="1.5"/>

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

    # Contribution legend
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

    # Layered meadow
    meadow = f'''
    <path d="M0 405 Q130 365 270 405
    T540 395 T820 400 T{width} 385
    L{width} 490 L0 490 Z"
    fill="#211832"/>

    <path d="M0 435 Q160 390 330 430
    T680 420 T{width} 415
    L{width} 490 L0 490 Z"
    fill="#302044"/>

    <path d="M0 463 Q180 425 390 458
    T790 450 T{width} 445
    L{width} 490 L0 490 Z"
    fill="#46305E"/>

    <path d="M0 480 Q250 450 480 480
    T790 468 T{width} 470
    L{width} 490 L0 490 Z"
    fill="#594071"/>
    '''

    # Decorative rocks
    rocks = []

    for x, y, rx, ry in [
        (22, 465, 25, 12),
        (95, 477, 15, 8),
        (width-145, 474, 22, 11),
        (width-28, 465, 30, 15),
        (width-105, 483, 18, 8)
    ]:
        rocks.append(
            f'<ellipse cx="{x}" cy="{y}" '
            f'rx="{rx}" ry="{ry}" fill="#75618D" '
            f'stroke="#A68BBC" stroke-width="1" '
            f'opacity="0.85"/>'
        )

    # Meadow plants
    plants = []

    for i in range(55):
        x = (i * 47 + 15) % width
        y = 468 - (i % 4) * 7
        size = 5 + (i % 4)

        # Keep the lantern area clear
        if width - 120 < x < width - 35:
            continue

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

    # Tall lavender flowers
    for x, y in [
        (35, 430), (110, 445), (width//3, 430),
        (width//2, 438), (width-230, 432),
        (width-170, 440)
    ]:
        plants.append(
            f'<path d="M{x} 475 Q{x-8} 450 {x} {y}" '
            f'fill="none" stroke="#A58AC5" '
            f'stroke-width="2"/>'
        )

        for j in range(5):
            plants.append(
                f'<ellipse cx="{x + (j%2)*5}" '
                f'cy="{y+j*7}" rx="3" ry="6" '
                f'fill="#C38BEA" opacity="0.9"/>'
            )

    # Fireflies
    fireflies = []

    for i in range(18):
        x = (i * 67 + 35) % width
        y = 375 + (i % 3) * 17

        fireflies.append(
            f'<circle cx="{x}" cy="{y}" r="7" '
            f'fill="#FFD58D" opacity="0.18" '
            f'filter="url(#softGlow)"/>'
        )

        fireflies.append(
            f'<circle cx="{x}" cy="{y}" r="2.2" '
            f'fill="#FFE4A6" filter="url(#glow)"/>'
        )

    # Golden lantern
    lx = width - 75

    lantern = f'''
    <circle cx="{lx}" cy="425" r="55"
      fill="url(#lanternGlow)"
      filter="url(#softGlow)"/>

    <g transform="translate({lx},424)" filter="url(#glow)">

      <path d="M-7 -42 Q0 -61 7 -42"
        fill="none" stroke="#E8C18B" stroke-width="2.5"/>

      <path d="M-13 -38 L13 -38 L19 -29
        L-19 -29 Z"
        fill="#59405D" stroke="#F2C88E"
        stroke-width="2"/>

      <path d="M-13 -28 L13 -28 L16 12
        L-16 12 Z"
        fill="#5A3B4D" stroke="#F4CE93"
        stroke-width="2"/>

      <path d="M-8 -23 L8 -23 L10 7
        L-10 7 Z"
        fill="#FFD98F"/>

      <path d="M0 -18 Q-10 -5 0 4
        Q10 -5 0 -18 Z"
        fill="#FFF2C6"/>

      <path d="M-18 13 L18 13 L22 20
        L-22 20 Z"
        fill="#72513F" stroke="#EBC18D"
        stroke-width="2"/>

      <path d="M-10 20 L10 20 L7 25
        L-7 25 Z"
        fill="#A77A57"/>
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
      {''.join(rocks)}
      {''.join(plants)}
      {''.join(fireflies)}
      {lantern}

    </svg>'''
