#!/usr/bin/env python3
"""Compact, truthful README HUD derived from public GitHub Issues and Releases.

This is an engineering activity indicator, NOT an FS25 playability assertion.
No invented percentages, guessed dates or manually maintained status mirrors.
"""
from pathlib import Path
import re
from xml.etree import ElementTree
from xml.sax.saxutils import escape

from render_roadmap import fetch_issues, fetch_releases, label_names, status

OUTPUT = Path(__file__).resolve().parent.parent / "docs/assets/status-live.svg"


def latest_downloadable_release(releases):
    """Only present a real public FS25 ZIP release as a downloadable build."""
    return next((release for release in releases if any(
        re.fullmatch(r"FS25_[A-Za-z0-9._-]+\.zip", asset.get("name", ""), re.I)
        for asset in release.get("assets", []) if isinstance(asset, dict)
    )), None)



def snapshot(issues, release=None, releases=None):
    """Only explicit status labels or an actual published Release count as evidence."""
    if releases is None:
        releases = [release] if release else []
    documented = [x for x in issues if "roadmap" in label_names(x)]
    by_number = {int(x["number"]): x for x in documented}
    focus = by_number.get(3)
    activity = sum(bool(label_names(x) & {"status:building", "status:testing"})
                   for x in documented)

    if release:
        tag = re.sub(r"[\x00-\x1f\x7f]+", "", str(release["tag_name"])).strip()
        public = ("PRE-RELEASE" if release.get("prerelease") else "RELEASE",
                  tag[:25] or "UNKNOWN", "#4df1ad")
    elif focus is None:
        public = ("DEVELOPMENT", "UNTRACKED", "#f1bb74")
    else:
        stage = status(focus, releases)
        # The shared status() function already checks release evidence and ZIP assets.
        public = ("DEVELOPMENT", f"#3  /  {stage}",
                  "#4df1ad" if stage == "BUILDING" else "#e5cf8b")

    roadmap = ("ROADMAP EPICS",
               f"{activity:02d} ACTIVE  /  {len(documented):02d} TOTAL", "#a3f8d2")
    return (public, roadmap)


def svg_text(x, y, content, size, color, weight=600, tracking="0.4"):
    return ('<text x="%d" y="%d" fill="%s" font-size="%d" '
            'font-family="Consolas,DejaVu Sans Mono,monospace" '
            'font-weight="%d" letter-spacing="%s">%s</text>' %
            (x, y, color, size, weight, tracking, escape(str(content))))


def render_svg(issues, release=None, releases=None):
    """Minimal terminal badges: one release, one roadmap count."""
    release_card, roadmap_card = snapshot(issues, release, releases)
    release_label, release_value, release_color = release_card
    roadmap_label, roadmap_value, _ = roadmap_card

    # Keep the roadmap information in two compact, readable chips.
    active, total = roadmap_value.split("  /  ", 1)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="120" '
        'viewBox="0 0 1160 120" role="img" '
        'aria-labelledby="statusTitle statusDesc">',
        '<title id="statusTitle">ARS live development</title>',
        '<desc id="statusDesc">Latest release and active roadmap epics, '
        'updated from GitHub Issues and Releases.</desc>',
        '<rect x="1" y="1" width="1158" height="118" rx="8" '
        'fill="#06110e" stroke="#22865d" stroke-width="1.4"/>',
        '<path d="M18 43H1142" stroke="#174f3b" stroke-width="1"/>',
        '<rect x="26" y="18" width="11" height="11" fill="#37efaa"/>',
        svg_text(51, 29, "ARS // LIVE DEVELOPMENT", 17, "#42efaa", 700, "1"),
        svg_text(861, 29, "GITHUB-SOURCED  /  AUTO-UPDATED",
                 11, "#7db5a0", 500, "0.6"),
        # Small terminal hatch detail, intentionally subordinate to the data.
        '<path d="M365 21l8 -8m1 8l8 -8m1 8l8 -8m1 8l8 -8" '
        'stroke="#235b4a" stroke-width="2" opacity=".6"/>',
    ]

    def frame(x, width, color="#397e68", fill="#071711"):
        parts.append(f'<rect x="{x}" y="61" width="{width}" height="42" '
                     f'rx="4" fill="{fill}" stroke="{color}" stroke-width="1"/>')

    frame(30, 151)
    # The release value has a reserved 390px region, including long beta tags.
    frame(190, 398, release_color, "#081b13")
    frame(626, 177)
    frame(813, 163, "#b89542", "#191807")
    frame(987, 143)
    parts.extend([
        svg_text(48, 88, release_label, 16, "#99cbbb", 600, "0.5"),
        svg_text(205, 89, release_value, 19, release_color, 700, "0.1"),
        svg_text(644, 88, roadmap_label, 16, "#99cbbb", 600, "0.3"),
        svg_text(829, 89, active, 18, "#efc86f", 700, "0.2"),
        svg_text(999, 89, "/ " + total, 16, "#e0f0e9", 600, "0.1"),
        "</svg>\n",
    ])
    result = "\n".join(parts)
    ElementTree.fromstring(result)
    return result

def main():
    issues = fetch_issues()
    releases = fetch_releases()
    release = latest_downloadable_release(releases)
    svg = render_svg(issues, release, releases)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != svg:
        OUTPUT.write_text(svg, encoding="utf-8")
    print("Rendered ARS system pulse from public Issues and Releases")


if __name__ == "__main__":
    main()
