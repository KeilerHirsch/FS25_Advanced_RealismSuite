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
    cards = snapshot(issues, release, releases)
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="144" '
        'viewBox="0 0 1160 144" role="img" aria-labelledby="statusTitle statusDesc">',
        '<title id="statusTitle">ARS live development pulse</title>',
        '<desc id="statusDesc">Latest release and active roadmap epics, '
        'generated from GitHub Issues and Releases.</desc>',
        '<defs><linearGradient id="dark" x2="1" y2=".25">'
        '<stop stop-color="#06120e"/><stop offset=".6" stop-color="#091f19"/>'
        '<stop offset="1" stop-color="#06140f"/></linearGradient>'
        '<pattern id="scan" width="8" height="8" patternUnits="userSpaceOnUse">'
        '<path d="M0 7.5H8" stroke="#225a43" stroke-opacity=".15"/></pattern></defs>',
        '<rect width="1158" height="142" x="1" y="1" rx="10" '
        'fill="url(#dark)" stroke="#278c60" stroke-width="1.3"/>',
        '<rect width="1156" height="140" x="2" y="2" rx="9" fill="url(#scan)"/>',
        '<path d="M13 32V14H30 M1130 14h17v18 M13 113v17h17 '
        'M1130 130h17v-17" fill="none" stroke="#47d99a" stroke-width="2"/>',
        '<circle cx="37" cy="25" r="4" fill="#4dffac"/>',
        svg_text(52, 30, "ARS  //  LIVE SYSTEM PULSE", 16, "#7ae6af", 700, "1.3"),
        svg_text(890, 30, "GITHUB-SOURCED STATUS", 12, "#7cae98", 500, "0.7"),
    ]
    for i, (label, value, color) in enumerate(cards):
        x = (34, 620)[i]
        if i:
            out.append(f'<path d="M580 49V124" stroke="#337d58" opacity=".65"/>')
        out.append(svg_text(x, 69, label, 14, "#7db69e", 600, "1.1"))
        out.append(f'<circle cx="{x+6}" cy="98" r="6" fill="{color}"/>')
        out.append(svg_text(x+25, 106, value, 24, color, 700, "0.3"))
    out.append("</svg>\n")
    result = "\n".join(out)
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
