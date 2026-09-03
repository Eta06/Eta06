#!/usr/bin/env python3
"""Generate ETA06's contribution-to-identity SVG.

The SVG uses one square for every visible day in GitHub's 53 × 7 contribution
calendar. The squares begin in the familiar calendar grid, then reassemble into
the ETA06 wordmark while preserving each day's contribution intensity.

No third-party runtime service is required. A scheduled GitHub Action regenerates
and commits the SVG from public contribution data.
"""

from __future__ import annotations

import argparse
import html
import random
import re
import urllib.request
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path

USERNAME = "Eta06"
DISPLAY_NAME = "EMIR TUNAHAN ALIM"
UNIVERSITY = "SOFTWARE ENGINEERING · BAHÇEŞEHİR UNIVERSITY"
CELL_SIZE = 10.4
PITCH = 12.4
DURATION = 10.5

# Target point assigned to each cell of a 53 × 7 GitHub calendar.
# The assignment was solved once with minimum-cost bipartite matching so paths
# cross as little as possible. Runtime generation therefore needs no packages.
TARGETS = [
    (45.000, 38.875),
    (45.000, 72.625),
    (45.000, 89.500),
    (45.000, 123.250),
    (45.000, 140.125),
    (45.000, 190.750),
    (45.000, 207.625),
    (45.000, 22.000),
    (45.000, 55.750),
    (61.875, 106.375),
    (45.000, 106.375),
    (45.000, 157.000),
    (45.000, 173.875),
    (61.875, 190.750),
    (61.875, 38.875),
    (61.875, 55.750),
    (61.875, 89.500),
    (61.875, 123.250),
    (61.875, 157.000),
    (61.875, 173.875),
    (61.875, 207.625),
    (61.875, 22.000),
    (61.875, 72.625),
    (78.750, 89.500),
    (78.750, 123.250),
    (61.875, 140.125),
    (78.750, 173.875),
    (78.750, 190.750),
    (78.750, 38.875),
    (78.750, 55.750),
    (78.750, 72.625),
    (78.750, 106.375),
    (78.750, 140.125),
    (78.750, 157.000),
    (78.750, 207.625),
    (78.750, 22.000),
    (95.625, 55.750),
    (95.625, 72.625),
    (95.625, 106.375),
    (95.625, 140.125),
    (95.625, 173.875),
    (95.625, 207.625),
    (95.625, 22.000),
    (95.625, 38.875),
    (95.625, 89.500),
    (95.625, 123.250),
    (95.625, 157.000),
    (95.625, 190.750),
    (112.500, 207.625),
    (112.500, 22.000),
    (112.500, 38.875),
    (112.500, 55.750),
    (112.500, 106.375),
    (112.500, 123.250),
    (112.500, 173.875),
    (112.500, 190.750),
    (129.375, 22.000),
    (129.375, 38.875),
    (129.375, 55.750),
    (129.375, 106.375),
    (129.375, 123.250),
    (129.375, 173.875),
    (129.375, 190.750),
    (146.250, 22.000),
    (146.250, 38.875),
    (146.250, 55.750),
    (146.250, 106.375),
    (146.250, 173.875),
    (146.250, 190.750),
    (129.375, 207.625),
    (163.125, 22.000),
    (163.125, 38.875),
    (163.125, 55.750),
    (146.250, 123.250),
    (163.125, 123.250),
    (163.125, 190.750),
    (146.250, 207.625),
    (180.000, 22.000),
    (180.000, 38.875),
    (180.000, 55.750),
    (163.125, 106.375),
    (180.000, 123.250),
    (163.125, 173.875),
    (163.125, 207.625),
    (213.750, 22.000),
    (213.750, 38.875),
    (213.750, 55.750),
    (180.000, 106.375),
    (180.000, 173.875),
    (180.000, 190.750),
    (180.000, 207.625),
    (230.625, 22.000),
    (230.625, 38.875),
    (230.625, 55.750),
    (264.375, 106.375),
    (264.375, 140.125),
    (264.375, 157.000),
    (264.375, 190.750),
    (247.500, 22.000),
    (247.500, 38.875),
    (247.500, 55.750),
    (264.375, 89.500),
    (264.375, 123.250),
    (264.375, 173.875),
    (264.375, 207.625),
    (264.375, 22.000),
    (264.375, 38.875),
    (264.375, 55.750),
    (264.375, 72.625),
    (281.250, 140.125),
    (281.250, 173.875),
    (281.250, 207.625),
    (281.250, 22.000),
    (281.250, 38.875),
    (281.250, 72.625),
    (281.250, 106.375),
    (281.250, 123.250),
    (281.250, 157.000),
    (281.250, 190.750),
    (298.125, 22.000),
    (281.250, 55.750),
    (298.125, 55.750),
    (281.250, 89.500),
    (298.125, 123.250),
    (298.125, 173.875),
    (298.125, 190.750),
    (315.000, 22.000),
    (298.125, 38.875),
    (298.125, 72.625),
    (298.125, 106.375),
    (298.125, 140.125),
    (298.125, 157.000),
    (298.125, 207.625),
    (331.875, 22.000),
    (315.000, 38.875),
    (315.000, 55.750),
    (298.125, 89.500),
    (365.625, 157.000),
    (348.750, 190.750),
    (348.750, 207.625),
    (331.875, 38.875),
    (331.875, 55.750),
    (348.750, 55.750),
    (382.500, 123.250),
    (365.625, 140.125),
    (365.625, 173.875),
    (365.625, 207.625),
    (348.750, 22.000),
    (348.750, 38.875),
    (382.500, 89.500),
    (382.500, 106.375),
    (382.500, 140.125),
    (382.500, 173.875),
    (365.625, 190.750),
    (399.375, 38.875),
    (399.375, 72.625),
    (399.375, 89.500),
    (399.375, 123.250),
    (382.500, 157.000),
    (399.375, 173.875),
    (382.500, 190.750),
    (416.250, 38.875),
    (399.375, 55.750),
    (416.250, 89.500),
    (399.375, 106.375),
    (399.375, 140.125),
    (399.375, 157.000),
    (382.500, 207.625),
    (416.250, 22.000),
    (416.250, 55.750),
    (416.250, 72.625),
    (416.250, 106.375),
    (416.250, 140.125),
    (416.250, 157.000),
    (399.375, 190.750),
    (433.125, 22.000),
    (433.125, 55.750),
    (433.125, 72.625),
    (416.250, 123.250),
    (433.125, 140.125),
    (416.250, 173.875),
    (433.125, 173.875),
    (433.125, 38.875),
    (450.000, 72.625),
    (433.125, 89.500),
    (450.000, 140.125),
    (450.000, 157.000),
    (433.125, 157.000),
    (450.000, 173.875),
    (450.000, 22.000),
    (450.000, 55.750),
    (450.000, 89.500),
    (466.875, 106.375),
    (466.875, 140.125),
    (466.875, 173.875),
    (483.750, 190.750),
    (450.000, 38.875),
    (466.875, 72.625),
    (466.875, 89.500),
    (466.875, 123.250),
    (483.750, 140.125),
    (466.875, 157.000),
    (483.750, 207.625),
    (466.875, 38.875),
    (466.875, 55.750),
    (483.750, 106.375),
    (483.750, 123.250),
    (483.750, 157.000),
    (483.750, 173.875),
    (500.625, 190.750),
    (466.875, 22.000),
    (483.750, 72.625),
    (483.750, 89.500),
    (500.625, 123.250),
    (500.625, 157.000),
    (500.625, 173.875),
    (500.625, 207.625),
    (483.750, 55.750),
    (551.250, 72.625),
    (500.625, 106.375),
    (500.625, 140.125),
    (517.500, 157.000),
    (517.500, 173.875),
    (517.500, 207.625),
    (551.250, 55.750),
    (551.250, 89.500),
    (551.250, 106.375),
    (551.250, 123.250),
    (551.250, 157.000),
    (517.500, 190.750),
    (534.375, 207.625),
    (568.125, 38.875),
    (568.125, 72.625),
    (568.125, 89.500),
    (568.125, 123.250),
    (551.250, 140.125),
    (551.250, 173.875),
    (568.125, 190.750),
    (585.000, 38.875),
    (568.125, 55.750),
    (568.125, 106.375),
    (568.125, 140.125),
    (568.125, 157.000),
    (568.125, 173.875),
    (585.000, 190.750),
    (601.875, 38.875),
    (585.000, 55.750),
    (585.000, 89.500),
    (585.000, 106.375),
    (585.000, 140.125),
    (585.000, 173.875),
    (601.875, 207.625),
    (601.875, 22.000),
    (601.875, 55.750),
    (585.000, 72.625),
    (585.000, 123.250),
    (585.000, 157.000),
    (601.875, 173.875),
    (601.875, 190.750),
    (618.750, 22.000),
    (618.750, 38.875),
    (618.750, 55.750),
    (652.500, 140.125),
    (618.750, 173.875),
    (618.750, 190.750),
    (618.750, 207.625),
    (635.625, 38.875),
    (635.625, 55.750),
    (652.500, 72.625),
    (652.500, 89.500),
    (635.625, 173.875),
    (635.625, 190.750),
    (635.625, 207.625),
    (635.625, 22.000),
    (652.500, 55.750),
    (669.375, 89.500),
    (669.375, 123.250),
    (652.500, 157.000),
    (652.500, 173.875),
    (652.500, 190.750),
    (652.500, 38.875),
    (669.375, 55.750),
    (669.375, 72.625),
    (669.375, 106.375),
    (669.375, 140.125),
    (669.375, 157.000),
    (669.375, 190.750),
    (669.375, 38.875),
    (686.250, 72.625),
    (686.250, 106.375),
    (686.250, 123.250),
    (686.250, 140.125),
    (686.250, 157.000),
    (669.375, 173.875),
    (686.250, 55.750),
    (720.000, 72.625),
    (686.250, 89.500),
    (720.000, 106.375),
    (720.000, 140.125),
    (720.000, 157.000),
    (686.250, 173.875),
    (736.875, 55.750),
    (736.875, 72.625),
    (720.000, 89.500),
    (736.875, 123.250),
    (720.000, 123.250),
    (736.875, 157.000),
    (736.875, 173.875),
    (753.750, 38.875),
    (753.750, 72.625),
    (736.875, 89.500),
    (736.875, 106.375),
    (736.875, 140.125),
    (753.750, 173.875),
    (753.750, 190.750),
    (770.625, 22.000),
    (753.750, 55.750),
    (753.750, 89.500),
    (753.750, 106.375),
    (753.750, 123.250),
    (753.750, 157.000),
    (770.625, 207.625),
    (770.625, 38.875),
    (770.625, 55.750),
    (770.625, 106.375),
    (770.625, 123.250),
    (753.750, 140.125),
    (770.625, 173.875),
    (770.625, 190.750),
    (787.500, 22.000),
    (787.500, 38.875),
    (787.500, 89.500),
    (787.500, 106.375),
    (787.500, 173.875),
    (787.500, 190.750),
    (787.500, 207.625),
    (804.375, 22.000),
    (804.375, 55.750),
    (804.375, 89.500),
    (804.375, 106.375),
    (821.250, 123.250),
    (804.375, 173.875),
    (804.375, 207.625),
    (821.250, 22.000),
    (804.375, 38.875),
    (821.250, 72.625),
    (821.250, 106.375),
    (821.250, 140.125),
    (821.250, 173.875),
    (804.375, 190.750),
    (821.250, 38.875),
    (821.250, 55.750),
    (821.250, 89.500),
    (838.125, 106.375),
    (838.125, 140.125),
    (821.250, 157.000),
    (821.250, 190.750),
    (838.125, 38.875),
    (838.125, 55.750),
    (838.125, 72.625),
    (838.125, 123.250),
    (838.125, 157.000),
    (838.125, 173.875),
    (838.125, 190.750),
    (855.000, 55.750),
    (855.000, 72.625),
    (855.000, 106.375),
    (855.000, 123.250),
    (855.000, 140.125),
    (855.000, 157.000),
    (855.000, 173.875)
]


class ContributionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.days: list[dict[str, object]] = []
        self.counts: dict[str, int] = {}
        self._tooltip_for: str | None = None
        self._tooltip_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        day = values.get("data-date")
        if tag in {"td", "rect"} and day:
            try:
                level = int(values.get("data-level") or 0)
            except ValueError:
                level = 0
            self.days.append(
                {
                    "date": day,
                    "level": max(0, min(4, level)),
                    "id": values.get("id") or "",
                }
            )
        elif tag == "tool-tip":
            self._tooltip_for = values.get("for")
            self._tooltip_text = ""

    def handle_data(self, data: str) -> None:
        if self._tooltip_for:
            self._tooltip_text += data

    def handle_endtag(self, tag: str) -> None:
        if tag != "tool-tip" or not self._tooltip_for:
            return
        match = re.search(r"(No|[\d,]+) contributions?", self._tooltip_text)
        if match:
            token = match.group(1)
            self.counts[self._tooltip_for] = 0 if token == "No" else int(token.replace(",", ""))
        self._tooltip_for = None
        self._tooltip_text = ""


def fetch_days(username: str) -> list[dict[str, object]]:
    request = urllib.request.Request(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "eta06-profile-art/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        parser = ContributionParser()
        parser.feed(response.read().decode("utf-8", errors="replace"))

    # Keep one record per date, then restore chronological order.
    unique: dict[str, dict[str, object]] = {}
    for day in parser.days:
        unique[str(day["date"])] = day
    days = [unique[key] for key in sorted(unique)]

    if len(days) < 350:
        raise RuntimeError(
            f"GitHub returned only {len(days)} contribution days; refusing to overwrite existing art."
        )

    days = days[-371:]
    for item in days:
        identity = str(item.pop("id", ""))
        item["count"] = parser.counts.get(identity, 0)
    return days


def demo_days() -> list[dict[str, object]]:
    rng = random.Random(606)
    end = date.today()
    start = end - timedelta(days=370)
    days: list[dict[str, object]] = []
    for offset in range(371):
        current = start + timedelta(days=offset)
        # A deterministic, natural-looking preview—not claimed as real activity.
        weekday = current.weekday()
        pulse = 0.11 if weekday < 5 else -0.08
        seasonal = 0.10 * (1 + __import__("math").sin(offset / 19.0))
        probability = max(0.12, min(0.78, 0.42 + pulse + seasonal))
        if rng.random() > probability:
            level = 0
            count = 0
        else:
            roll = rng.random()
            level = 1 if roll < 0.52 else 2 if roll < 0.79 else 3 if roll < 0.94 else 4
            count = {1: 1, 2: 3, 3: 7, 4: 14}[level] + rng.randrange(0, 4)
        days.append({"date": current.isoformat(), "level": level, "count": count})
    return days


def clamp_calendar(days: list[dict[str, object]]) -> list[dict[str, object]]:
    if not days:
        raise RuntimeError("No contribution data.")
    days = days[-371:]
    while len(days) < 371:
        first = date.fromisoformat(str(days[0]["date"])) - timedelta(days=1)
        days.insert(0, {"date": first.isoformat(), "level": 0, "count": 0})
    return days


def month_year(value: str) -> str:
    parsed = date.fromisoformat(value)
    return parsed.strftime("%b %Y").upper()


def path_values(index: int, gx: float, gy: float, tx: float, ty: float) -> tuple[str, str]:
    dx, dy = gx - tx, gy - ty
    distance = (dx * dx + dy * dy) ** 0.5 or 1.0
    ux, uy = -dy / distance, dx / distance
    rng = random.Random(index * 7919 + 606)

    bend = rng.uniform(-24.0, 24.0)
    mx1 = dx * 0.56 + ux * bend
    my1 = dy * 0.56 + uy * bend
    mx2 = dx * 0.48 - ux * bend * 0.74
    my2 = dy * 0.48 - uy * bend * 0.74

    # Small springy overshoot near the assembled wordmark and again on exit.
    overshoot_scale_in = 0.075 + rng.uniform(-0.012, 0.012)
    overshoot_scale_out = 0.055 + rng.uniform(-0.010, 0.010)
    ox1 = -dx * overshoot_scale_in + ux * bend * 0.12
    oy1 = -dy * overshoot_scale_in + uy * bend * 0.12
    ox2 = -dx * overshoot_scale_out - ux * bend * 0.10
    oy2 = -dy * overshoot_scale_out - uy * bend * 0.10

    cx, cy = 450.0, 118.0
    radial = min(1.0, (((tx - cx) ** 2 + (ty - cy) ** 2) ** 0.5) / 430.0)
    delay = max(0.0, min(0.048, 0.040 * radial + rng.uniform(-0.005, 0.005)))

    assemble_start = 0.080 + delay
    assemble_curve_1 = assemble_start + 0.105
    assemble_curve_2 = assemble_curve_1 + 0.085
    assemble_settle = 0.345

    hold_end = 0.620

    disassemble_start = hold_end + (0.048 - delay) * 0.55
    disassemble_curve_1 = disassemble_start + 0.080
    disassemble_curve_2 = disassemble_curve_1 + 0.100
    disassemble_end = 0.900

    times = (
        f"0;{assemble_start:.4f};{assemble_curve_1:.4f};{assemble_curve_2:.4f};{assemble_settle:.4f};"
        f"{hold_end:.4f};{disassemble_start:.4f};{disassemble_curve_1:.4f};{disassemble_curve_2:.4f};{disassemble_end:.4f};1"
    )
    values = (
        f"{dx:.3f} {dy:.3f};{dx:.3f} {dy:.3f};"
        f"{mx1:.3f} {my1:.3f};{ox1:.3f} {oy1:.3f};0 0;0 0;"
        f"{ox2:.3f} {oy2:.3f};{mx2:.3f} {my2:.3f};{dx:.3f} {dy:.3f};{dx:.3f} {dy:.3f};{dx:.3f} {dy:.3f}"
    )
    return times, values


def render(days: list[dict[str, object]], output: Path, username: str) -> None:
    days = clamp_calendar(days)
    start_label = month_year(str(days[0]["date"]))
    end_label = month_year(str(days[-1]["date"]))
    total = sum(int(day.get("count", 0)) for day in days)

    cells: list[str] = []
    for index, (day, (tx, ty)) in enumerate(zip(days, TARGETS)):
        column, row = divmod(index, 7)
        gx = 128.0 + column * PITCH
        gy = 80.0 + row * PITCH
        x, y = tx - CELL_SIZE / 2, ty - CELL_SIZE / 2
        level = max(0, min(4, int(day.get("level", 0))))
        key_times, values = path_values(index, gx, gy, tx, ty)

        rotation = ""
        if index % 3 == 0:
            angle = ((index * 37) % 25) - 12
            rotation = f"""
      <animateTransform attributeName="transform" type="rotate"
        values="0 {tx:.3f} {ty:.3f};0 {tx:.3f} {ty:.3f};{angle * 0.85:.2f} {tx:.3f} {ty:.3f};{-angle * 0.18:.2f} {tx:.3f} {ty:.3f};0 {tx:.3f} {ty:.3f};0 {tx:.3f} {ty:.3f};{-angle * 0.65:.2f} {tx:.3f} {ty:.3f};{angle * 0.12:.2f} {tx:.3f} {ty:.3f};0 {tx:.3f} {ty:.3f};0 {tx:.3f} {ty:.3f};0 {tx:.3f} {ty:.3f}"
        keyTimes="{key_times}" dur="{DURATION}s" repeatCount="indefinite" calcMode="spline"
        keySplines="0 0 1 1;0.24 0.86 0.32 1;0.28 0.18 0.38 1;0.22 0 0.16 1;0 0 1 1;0.22 0.86 0.32 1;0.28 0.18 0.38 1;0.22 0 0.16 1;0.2 0.2 0.2 1;0 0 1 1"/>"""

        boost_animation = """
        <animate attributeName="opacity"
          values="0;0;0;.78;.78;0;0"
          keyTimes="0;.18;.27;.36;.62;.76;1"
          dur="10.5s" repeatCount="indefinite" calcMode="spline"
          keySplines="0 0 1 1;0.22 0.84 0.28 1;0.22 0.84 0.28 1;0 0 1 1;0.22 0.16 0.28 1;0 0 1 1"/>"""

        tooltip = html.escape(
            f"{day['date']} · {int(day.get('count', 0))} contribution"
            f"{'' if int(day.get('count', 0)) == 1 else 's'}"
        )
        cells.append(
            f"""  <g class="cell" aria-label="{tooltip}">
    <title>{tooltip}</title>
    <animateTransform attributeName="transform" type="translate"
      values="{values}" keyTimes="{key_times}"
      dur="{DURATION}s" repeatCount="indefinite" calcMode="spline"
      keySplines="0 0 1 1;0.25 0.85 0.34 1;0.22 0 0.18 1;0.18 0.82 0.28 1;0 0 1 1;0.18 0.82 0.28 1;0.24 0 0.18 1;0.22 0.86 0.32 1;0 0 1 1;0 0 1 1"/>
    <g>{rotation}
      <rect class="level-{level}" x="{x:.3f}" y="{y:.3f}"
        width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2.1"/>
      <rect class="boost-{level}" x="{x:.3f}" y="{y:.3f}"
        width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2.1">{boost_animation}
      </rect>
    </g>
  </g>"""
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300"
  viewBox="0 0 900 300" role="img"
  aria-labelledby="title description">
  <title id="title">ETA06 contribution identity</title>
  <desc id="description">
    GitHub contribution cells leave their calendar and assemble into ETA06,
    followed by Emir Tunahan Alim and Bahçeşehir University.
  </desc>

  <style>
    :root {{
      --level-0: #ebedf0;
      --level-1: #9be9a8;
      --level-2: #40c463;
      --level-3: #30a14e;
      --level-4: #216e39;
      --boost-0: #40c463;
      --boost-1: #30a14e;
      --text: #24292f;
      --muted: #57606a;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --level-0: #161b22;
        --level-1: #0e4429;
        --level-2: #006d32;
        --level-3: #26a641;
        --level-4: #39d353;
        --boost-0: #26a641;
        --boost-1: #39d353;
        --text: #f0f6fc;
        --muted: #8b949e;
      }}
    }}
    .level-0 {{ fill: var(--level-0); }}
    .level-1 {{ fill: var(--level-1); }}
    .level-2 {{ fill: var(--level-2); }}
    .level-3 {{ fill: var(--level-3); }}
    .level-4 {{ fill: var(--level-4); }}
    .boost-0 {{ fill: var(--boost-0); opacity: 0; }}
    .boost-1 {{ fill: var(--boost-1); opacity: 0; }}
    .boost-2, .boost-3, .boost-4 {{ opacity: 0; }}
    .label {{
      fill: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      text-anchor: middle;
    }}
    .muted {{
      fill: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      text-anchor: middle;
    }}
    .cell {{ shape-rendering: geometricPrecision; }}
  </style>

{chr(10).join(cells)}

  <g opacity="1">
    <text class="label" x="450" y="255" font-size="18" font-weight="650"
      letter-spacing="2.8">{html.escape(DISPLAY_NAME)}</text>
    <text class="muted" x="450" y="281" font-size="12.5"
      letter-spacing="1.05">{html.escape(UNIVERSITY)}</text>
    <animate attributeName="opacity" values="0;0;1;1;0;0"
      keyTimes="0;.28;.36;.64;.75;1" dur="{DURATION}s"
      repeatCount="indefinite" calcMode="spline"
      keySplines="0 0 1 1;0.22 0.84 0.28 1;0 0 1 1;0.22 0.16 0.28 1;0 0 1 1"/>
  </g>

  <g opacity="0">
    <text class="muted" x="450" y="190" font-size="11.5"
      letter-spacing="1.6">{start_label} — {end_label}</text>
    <animate attributeName="opacity" values="1;1;0;0;1;1"
      keyTimes="0;.08;.20;.80;.92;1" dur="{DURATION}s"
      repeatCount="indefinite" calcMode="spline"
      keySplines="0 0 1 1;0.22 0.16 0.28 1;0 0 1 1;0.22 0.84 0.28 1;0 0 1 1"/>
  </g>

  <!-- Public count fetched at build time: {total}. Username: {html.escape(username)}. -->
</svg>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default=USERNAME)
    parser.add_argument("--output", type=Path, default=Path("assets/eta06-assembly.svg"))
    parser.add_argument("--demo", action="store_true", help="Use deterministic preview data.")
    args = parser.parse_args()

    days = demo_days() if args.demo else fetch_days(args.username)
    render(days, args.output, args.username)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
