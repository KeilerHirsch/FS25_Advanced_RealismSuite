#!/usr/bin/env python3
"""Render the approved cinematic ARS roadmap with evidence-based live status.

Progress means the share of assigned epics with verified/released status AND
an explicit public evidence link. It is NOT an estimate of code completion or
a machine-verification of gameplay evidence.
No artwork percentages, unverified PR merges or closed issues are used as evidence.
"""
from pathlib import Path
import io

from PIL import Image, ImageDraw, ImageFont
from render_roadmap import fetch_issues, label_names, status

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/assets/ars-roadmap-hud-base.png"
OUTPUT = ROOT / "docs/assets/roadmap-live.png"

# Values refer to existing public GitHub roadmap epic numbers, not internal research.
# An epic can contribute to two themes when its documented scope spans both.
THEMES = (
    ("Vehicle Systems & Workshop", (3,)),
    ("Fleet & Maintenance", (3, 4)),
    ("Physics, Fuel & Wear", (7,)),
    ("Fields & Agronomy", (8,)),
    ("Soil, Climate & Crop Health", (8,)),
    ("Animals, Storage & Production", (10,)),
    ("Economics, Logistics & Markets", (9, 11)),
    ("Compatibility, Automation & Diagnostics", (5, 6, 12)),
)

# Coordinates are for the approved 1672x941 photo-HUD master.
COLUMNS = (43, 451, 862, 1272)
ROWS = (580, 806)
GREEN = (57, 236, 167)
CYAN = (91, 239, 218)
YELLOW = (244, 202, 99)
SOFT = (190, 246, 224)
DARK = (5, 22, 18)
BAR = (8, 45, 33)


def font(size, bold=False):
    candidate = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono" + ("-Bold" if bold else "") + ".ttf"
    if Path(candidate).exists():
        return ImageFont.truetype(candidate, size)
    # Windows local tests (via uv) and GitHub Actions both have fallback fonts.
    for name in ("DejaVuSansMono.ttf", "C:/Windows/Fonts/consola.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def card_metrics(numbered_issues, expected):
    relevant = [numbered_issues[num] for num in expected if num in numbered_issues
                and "roadmap" in label_names(numbered_issues[num])]
    if len(relevant) != len(expected):
        # An issue has been deleted or lost its roadmap label; don't fake completion.
        return "UNTRACKED", 0, 0, 0
    # Conflicting or evidence-free labels never increase the verified share.
    states = [status(issue) for issue in relevant]
    finished = sum(value in {"VERIFIED", "RELEASED"} for value in states)
    if finished == len(relevant):
        state = "VERIFIED"
    elif "TESTING" in states:
        state = "IN TEST"
    elif "BUILDING" in states:
        state = "ACTIVE"
    else:
        state = "PLANNED"
    return state, finished, len(relevant), round(100 * finished / len(relevant))


def draw_footer(canvas, x, y, state, done, total, percentage, fonts):
    d = ImageDraw.Draw(canvas)
    # Source artwork has ALL mocked statuses/percentages masked in the base PNG.
    # We also redraw the entire footer area to make the output deterministic.
    d.rectangle((x - 1, y - 4, x + 311, y + 45), fill=DARK)
    d.line((x, y - 5, x + 306, y - 5), fill=GREEN, width=1)
    color = GREEN if state in {"VERIFIED", "ACTIVE"} else (
        YELLOW if state == "IN TEST" else SOFT
    )
    d.ellipse((x + 2, y + 3, x + 14, y + 15), fill=color)
    d.text((x + 24, y + 0), state, font=fonts["state"], fill=color)
    verdict = f"{percentage}% VERIFIED  ({done}/{total})" if total else "NO SOURCE"
    box = d.textbbox((0, 0), verdict, font=fonts["small"])
    d.text((x + 304 - (box[2] - box[0]), y + 1), verdict,
           font=fonts["small"], fill=SOFT)
    bx, by = x + 3, y + 26
    d.rounded_rectangle((bx, by, bx + 305, by + 13), radius=5,
                        fill=BAR, outline=(36, 156, 119), width=1)
    if percentage:
        width = max(3, round(302 * percentage / 100))
        d.rounded_rectangle((bx + 2, by + 2, bx + min(width, 301),
                             by + 11), radius=3, fill=GREEN)
    # Percent and denominator are printed above the segmented bar.


def redraw_theme_titles(image):
    # The original concept card captions partially overlap the live footer.
    # Re-render legible captions above it, without changing the photo/HUD.
    lines = (
        ("Vehicle Systems", "& Workshop"),
        ("Fleet &", "Maintenance"),
        ("Physics, Fuel", "& Wear"),
        ("Fields &", "Agronomy"),
        ("Soil, Climate", "& Crop Health"),
        ("Animals, Storage", "& Production"),
        ("Economics, Logistics", "& Markets"),
        ("Compatibility,", "Automation & Diagnostics"),
    )
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pane = ImageDraw.Draw(overlay)
    for n, (first, second) in enumerate(lines):
        x = COLUMNS[n % 4]
        top = 537 if n < 4 else 761
        pane.rectangle((x - 2, top - 5, x + 306, top + 38),
                       fill=(0, 13, 11, 255))
        pane.text((x + 3, top - 1), first, font=font(18, True),
                  fill=(226, 251, 241, 255))
        pane.text((x + 3, top + 18), second, font=font(18, True),
                  fill=(226, 251, 241, 255))
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def render(issues):
    indexed = {int(i["number"]): i for i in issues}
    image = Image.open(BASE).convert("RGB")
    if image.size != (1672, 941):
        raise ValueError(f"Unexpected HUD base dimensions {image.size}")
    fonts = {"state": font(16, True), "small": font(11, False)}
    for n, (_, epic_numbers) in enumerate(THEMES):
        state, done, total, percent = card_metrics(indexed, epic_numbers)
        x = COLUMNS[n % 4]
        y = ROWS[n // 4]
        draw_footer(image, x, y, state, done, total, percent, fonts)
    image = redraw_theme_titles(image)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    result = buffer.getvalue()
    if not OUTPUT.exists() or OUTPUT.read_bytes() != result:
        OUTPUT.write_bytes(result)
    print("Rendered live 8-theme cinematic HUD; verified-share metric only")


if __name__ == "__main__":
    render(fetch_issues())
