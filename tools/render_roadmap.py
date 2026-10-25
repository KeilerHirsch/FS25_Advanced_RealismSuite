#!/usr/bin/env python3
"""Build a visual and accessible ARS roadmap from public GitHub Issues only.

A commit or closed issue is not proof of in-game verification or release.
Python standard library only; no images, external packages or extra services.
"""
import json
import os
from pathlib import Path
import re
import textwrap
from urllib.request import Request, urlopen
from xml.etree import ElementTree
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
REPO = os.getenv("GITHUB_REPOSITORY", "KeilerHirsch/FS25_Advanced_RealmsSuite")
PHASES = (
    ("now", "NOW", "CURRENT ENGINEERING", "#4fdfb2"),
    ("next", "NEXT", "RELEASE FOUNDATIONS", "#81b8ff"),
    ("planned", "PLANNED", "CONNECTED SYSTEMS", "#c3adff"),
    ("future", "FUTURE", "LONG-TERM VISION", "#f1c47c"),
)
STATES = (
    ("status:released", "RELEASED", "#4fdfb2"),
    ("status:verified", "VERIFIED", "#4fdfb2"),
    ("status:testing", "TESTING", "#f1c47c"),
    ("status:building", "BUILDING", "#81b8ff"),
)


def label_names(issue):
    return {x.get("name", "") for x in issue.get("labels", []) if isinstance(x, dict)}


def phase(issue):
    names = label_names(issue)
    for key, _, _, _ in PHASES:
        if "phase:" + key in names:
            return key
    return "future"


REPORT_URL = re.compile(
    r"https://github\.com/KeilerHirsch/FS25_Advanced_RealmsSuite/"
    r"blob/[0-9a-f]{40}/docs/acceptance/"
    r"[A-Za-z0-9._/-]+\.md(?:#L[0-9]+(?:-L[0-9]+)?)?",
    re.I,
)


def evidence_reference(issue, field="Verification evidence"):
    """Return a complete evidence URL for a specifically named body field."""
    prefix = field.lower() + ":"
    for line in (issue.get("body") or "").splitlines():
        clean = line.strip().replace("**", "")
        if clean.lower().startswith(prefix):
            return clean[len(prefix):].strip()
    return ""


def has_verification_evidence(issue):
    """Accept only a commit-pinned, public ARS acceptance report reference.

    This is still a provenance pointer, NOT machine verification of gameplay.
    The report must be inspected and accepted by a human before labeling.
    """
    url = evidence_reference(issue)
    if not REPORT_URL.fullmatch(url):
        return False
    # Do not allow path traversal disguised as a report link.
    suffix = url.split("/docs/acceptance/", 1)[-1].split("#", 1)[0]
    return all(segment not in {".", "..", ""} for segment in suffix.split("/"))


def published_release_for_issue(issue, releases):
    """Match a stated release URL to a real public release with an FS25 ZIP."""
    claimed = evidence_reference(issue, "Release evidence")
    if not claimed:
        return False
    for release in releases:
        if release.get("draft") or not release.get("tag_name"):
            continue
        canonical = release.get("html_url", "").rstrip("/")
        if not canonical or claimed.rstrip("/") != canonical:
            continue
        assets = release.get("assets") or []
        if any(
            re.fullmatch(r"FS25_[A-Za-z0-9._-]+\.zip", asset.get("name", ""), re.I)
            for asset in assets if isinstance(asset, dict)
        ):
            return True
    return False


def status(issue, releases=()):
    """Conservative status shared by roadmap text, image, and pulse."""
    names = label_names(issue)
    selected = [(tag, state) for tag, state, _ in STATES if tag in names]
    if len(selected) > 1:
        return "STATUS CONFLICT"
    if selected:
        _, state = selected[0]
        if state in {"RELEASED", "VERIFIED"} and not has_verification_evidence(issue):
            return "EVIDENCE REQUIRED"
        if state == "RELEASED" and not published_release_for_issue(issue, releases):
            return "VERIFY RELEASE"
        return state
    return "CLOSED / UNVERIFIED" if issue.get("state") == "closed" else "PLANNED"


def fetch_releases():
    """Fetch published Release metadata; do not infer releases from tags/labels."""
    token = os.getenv("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "ARS-Live-Roadmap/1.1",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request("https://api.github.com/repos/" + REPO +
                  "/releases?per_page=100", headers=headers)
    with urlopen(req, timeout=30) as response:
        releases = json.load(response)
    if not isinstance(releases, list):
        raise ValueError("Unexpected GitHub releases response")
    return [x for x in releases if not x.get("draft")]



def clean_title(issue):
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", str(issue.get("title", "")))
    return re.sub(r"^\[Roadmap\]\s*", "", text, flags=re.I).strip()[:160]

def markdown_link_label(value):
    """Escape untrusted issue titles before inserting them into Markdown links.

    Backslash first, then the GFM metacharacters that can change link,
    image, entity or inline formatting in the label.
    """
    return re.sub(r"([\\`*_{}\[\]()<>#+.!|~&-])", r"\\\1", value)


def fetch_issues():
    token = os.getenv("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "ARS-Live-Roadmap/1.0",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    found = []
    for page in range(1, 11):
        req = Request("https://api.github.com/repos/" + REPO +
                      "/issues?state=all&per_page=100&page=" + str(page),
                      headers=headers)
        with urlopen(req, timeout=30) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("Unexpected GitHub issues response")
        found += [x for x in batch if "pull_request" not in x and
                  "roadmap" in label_names(x)]
        if len(batch) < 100:
            break
    else:
        raise RuntimeError("Pagination exceeded limit; extend safely")
    return sorted(found, key=lambda issue: int(issue["number"]))


def text_el(x, y, value, size=17, color="#eaf6f4", weight=500, attrs=""):
    return ('<text x="%d" y="%d" font-family="Segoe UI,Arial,sans-serif" '
            'font-size="%d" fill="%s" font-weight="%d" %s>%s</text>' %
            (x, y, size, color, weight, attrs, escape(value)))


def rectangle(x, y, w, h, fill, corner=18, stroke="none"):
    return ('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" '
            'fill="%s" stroke="%s"/>' % (x, y, w, h, corner, fill, stroke))


def render_svg(issues, releases=()):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="744" '
        'viewBox="0 0 1160 744" role="img" aria-labelledby="roadmapTitle roadmapDesc">',
        '<title id="roadmapTitle">ARS live development roadmap</title>',
        '<desc id="roadmapDesc">Four grouped roadmap stages generated from public GitHub Issues. '
        'Closed issues are not automatically marked as tested or released.</desc>',
        '<defs><linearGradient id="background" x1="0" y1="0" x2="1" y2="1">'
        '<stop stop-color="#0c1828"/><stop offset=".55" stop-color="#102b32"/>'
        '<stop offset="1" stop-color="#122139"/></linearGradient>'
        '<linearGradient id="accent"><stop stop-color="#52e0b6"/>'
        '<stop offset="1" stop-color="#8ac1ff"/></linearGradient></defs>',
        rectangle(0, 0, 1160, 744, "url(#background)", 28),
        '<path d="M720 -20Q915 170 1160 45 M780 -30Q1050 180 1210 95" '
        'stroke="#3b837d" stroke-opacity=".24" stroke-width="2" fill="none"/>',
        rectangle(35, 32, 7, 29, "url(#accent)", 3),
        text_el(55, 52, "ADVANCED REALMS SUITE  /  LIVE ROADMAP", 15, "#91e5c8", 700,
                'letter-spacing="1.8"'),
        text_el(35, 109, "ONE SUITE. CONNECTED SYSTEMS.", 37, "#f6fbfc", 800),
        text_el(36, 145, "GitHub Issues are the source of truth. No invented progress percentages.",
                17, "#a9c1c6", 400),
        rectangle(906, 38, 217, 38, "#1c4245", 19, "#427d72"),
        text_el(921, 62, str(len(issues)) + " TRACKED ROADMAP EPICS",
                13, "#a5f0d7", 700),
    ]
    for i, (key, name, description, accent) in enumerate(PHASES):
        x, y = 34 + (i % 2) * 563, 176 + (i // 2) * 274
        w, h = 529, 254
        chosen = [issue for issue in issues if phase(issue) == key]
        parts += [
            rectangle(x, y, w, h, "#142e38", 21, "#34525c"),
            rectangle(x + 1, y + 1, 5, h - 2, accent, 2),
            text_el(x + 25, y + 41, "%02d  %s" % (i + 1, name),
                    25, "#f3fbfb", 800),
            text_el(x + 26, y + 63, description, 12, accent, 700,
                    'letter-spacing="1.3"'),
            rectangle(x + w - 77, y + 21, 44, 29, "#294953", 14),
            text_el(x + w - 65, y + 42, "%02d" % len(chosen), 16, "#f0faf9", 700),
        ]
        if not chosen:
            parts.append(text_el(x + 27, y + 124, "No roadmap issues in this phase yet.",
                                 16, "#aec6c8", 400))
        for j, issue in enumerate(chosen[:3]):
            top = y + 91 + j * 54
            parts.append(rectangle(x + 25, top + 5, 6, 6, accent, 3))
            wrapped = textwrap.wrap(clean_title(issue), width=37,
                                    break_long_words=False, break_on_hyphens=False)
            wrapped = wrapped or ["Untitled"]
            if len(wrapped) > 2:
                wrapped = [wrapped[0], wrapped[1][:32].rstrip() + "..."]
            parts.append(text_el(x + 43, top + 14, wrapped[0], 16, "#f0f9f9", 600))
            if len(wrapped) == 2:
                parts.append(text_el(x + 43, top + 33, wrapped[1], 15, "#cbe2e4", 500))
            parts.append(text_el(x + w - 65, top + 14, "#" + str(issue["number"]),
                                 13, "#a4bbc2", 600))
            value = status(issue, releases)
            if value != "PLANNED":
                color = next((c for _, state, c in STATES if state == value), "#ddbd9b")
                parts.append(text_el(x + w - 25, top + 35, value, 10, color, 700,
                                     'text-anchor="end" letter-spacing=".3"'))
        if len(chosen) > 3:
            parts.append(text_el(x + 26, y + h - 15, "+" + str(len(chosen)-3) +
                                 " additional epics in full roadmap", 12, "#b8cdd1", 400))
    parts += [
        '<line x1="38" y1="730" x2="1122" y2="730" stroke="#3b5a63"/>',
        text_el(39, 741, "PLANNED  !=  VERIFIED  !=  RELEASED", 11, "#91b4bb", 700),
        text_el(1120, 741, "AUTO-REFRESHED FROM ISSUE CHANGES", 11, "#91b4bb", 700,
                'text-anchor="end"'),
        "</svg>\n",
    ]
    rendered = "\n".join(parts)
    ElementTree.fromstring(rendered)
    return rendered


def render_md(issues, releases=()):
    lines = [
        "<!-- Generated from GitHub Issues by tools/render_roadmap.py. Do not edit manually. -->",
        "# ARS public roadmap", "",
        "This page and the [visual dashboard](assets/roadmap.svg) are generated from "
        "[roadmap-labeled GitHub issues](https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/issues?q=is%3Aissue+label%3Aroadmap). "
        "Internal research and planning topics are not shipped features.",
        "",
        "**Status contract:** Commits, PR merges and closed issues do not automatically "
        "mean verified or released. The verified status needs in-game acceptance evidence; "
        "released means a publicly shipped build. No release dates are promised.", "",
    ]
    for key, title, subtitle, _ in PHASES:
        lines.extend(["## " + title.title() + " — " + subtitle.title(), "",
                      "| Public feature epic | Status |", "|---|---|"])
        chosen = [i for i in issues if phase(i) == key]
        if not chosen:
            lines.append("| No epics currently tracked | — |")
        for issue in chosen:
            label = markdown_link_label(clean_title(issue))
            lines.append("| [#" + str(issue["number"]) + " — " + label + "](" +
                         issue["html_url"] + ") | " + status(issue, releases) + " |")
        lines.append("")
    lines += [
        "## How this stays current", "",
        "- A public GitHub Issue becomes visible with the roadmap label and one phase label: "
        "phase:now, phase:next, phase:planned or phase:future.",
        "- Add status:building or status:testing only when supported by work. "
        "For status:verified or status:released, the epic must also contain a "
        "Verification evidence: must link to a commit-pinned ARS "
        "docs/acceptance/*.md report. For status:released, Release evidence: "
        "must additionally link to the exact published GitHub Release containing "
        "an FS25 ZIP. Conflicting status labels are rejected. Humans must review "
        "the actual gameplay evidence; URLs alone are not gameplay proof.",
        "- Roadmap Issue changes, GitHub Release events and periodic checks refresh the SVG "
        "phase dashboard, cinematic roadmap image, compact live-status HUD and "
        "this text page via GitHub Actions. PR runs verify only and never publish.",
        "- Detailed internal research remains separate; the public board tracks outcome-focused epics.",
        "", "[Public discussion](https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/discussions/2) · [Project home](../README.md)", "",
    ]
    return "\n".join(lines)


def main():
    issues = fetch_issues()
    releases = fetch_releases()
    img_path = ROOT / "docs" / "assets" / "roadmap.svg"
    text_path = ROOT / "docs" / "ROADMAP.md"
    img_path.parent.mkdir(parents=True, exist_ok=True)
    img_path.write_text(render_svg(issues, releases), encoding="utf-8")
    text_path.write_text(render_md(issues, releases), encoding="utf-8")
    print("Rendered %d public roadmap issues" % len(issues))


if __name__ == "__main__":
    main()
