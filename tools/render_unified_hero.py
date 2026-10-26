#!/usr/bin/env python3
"""Public ARS single-image hero: immersive garage, development, and two-state Hall.

The GitHub roadmap is the source for public product focus, not the developer's
private Codex plans. The Hall records only INSPIRATION or HONORED. A fully honored
mod needs a matching pinned acceptance report, published ARS ZIP, and explicit
human-accepted, full-replacement proof. No external mod icons are used.
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from render_roadmap import (
    REPORT_URL, evidence_reference, fetch_issues, fetch_releases,
    label_names, phase, status, clean_title
)

ROOT = Path(__file__).resolve().parent.parent
CREDITS = ROOT / "docs/COMMUNITY_INSPIRATIONS.md"
REGISTRY = ROOT / "docs/data/assimilation-featured.json"
PROOFS = ROOT / "docs/data/assimilation-proofs.json"
SCENERY = ROOT / "docs/assets/ars-roadmap-hud-base.png"
OUT = ROOT / "docs/assets/ars-unified-live-hero.png"
INDEX = ROOT / "docs/ASSIMILATION_INDEX.md"

W, H = 1672, 1176
BG = "#07110e"
PANEL = "#0a1d15"
CREAM = "#f3eee1"
GREEN = "#67efb0"
GOLD = "#d9b778"
SOFT = "#b3cdbb"
BORDER = "#3b7256"
LINK = re.compile(r"\[([^\]]+)\]\((https://[^)\s]+)\)")
CREDIT = re.compile(r"^\s*-\s+\*\*([^*]+)\*\*\s+[\u2014-]\s+(.+)$")
ALLOWED_SOURCES = ("https://github.com/", "https://gitlab.com/",
                   "https://www.farming-simulator.com/mod.php?",
                   "https://farming-simulator.com/mod.php?")
SKIP = {"original project", "original", "source", "modhub", "readme", "license"}


def font(size: int, bold=False):
    for name in (
        "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
        if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def serif(size: int, bold=False):
    for name in (
        "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf",
        "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
        if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return font(size, bold)


def credited_mods(text: str) -> list[dict]:
    """Get original authors and source links from the one canonical public list."""
    results, seen = [], set()
    for raw in text.splitlines():
        row = CREDIT.match(raw)
        if not row:
            continue
        author, rest = row.groups()
        for name, url in LINK.findall(rest):
            if name.strip().lower() in SKIP or not url.startswith(ALLOWED_SOURCES):
                continue
            if url in seen:
                continue
            seen.add(url)
            results.append({"name": name.strip(), "author": author.strip(),
                            "source": url})
    return results


def validate_config(config, mods):
    if config.get("schema_version") != 1:
        raise ValueError("Unknown featured-source schema")
    by_source = {m["source"]: m for m in mods}
    selected, seen = [], set()
    for entry in config.get("featured", []):
        source = entry["source"]
        if source not in by_source or source in seen:
            raise ValueError("Featured source missing or duplicate: " + str(source))
        seen.add(source)
        issue_id = entry.get("issue")
        if not isinstance(issue_id, int) or issue_id <= 0:
            raise ValueError("Invalid related public Issue")
        selected.append({**by_source[source], "issue": issue_id})
    if not selected:
        raise ValueError("At least one highlighted credited source is needed")
    return selected


def read_proofs(sources):
    data = json.loads(PROOFS.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unknown replacement-proof schema")
    found = {}
    for item in data.get("replacements", []):
        source = item.get("source")
        if source not in sources or source in found:
            raise ValueError("Unknown or duplicated replacement proof: " + str(source))
        found[source] = item
    return found


def verified_replacement(mod, issues, releases, proofs) -> bool:
    """Public Issue + per-mod human review + pinned report + ZIP release required."""
    proof = proofs.get(mod.get("source"))
    if not proof or proof.get("human_accepted") is not True:
        return False
    if proof.get("complete_replacement") is not True:
        return False
    issue_num = proof.get("issue")
    if not isinstance(issue_num, int) or issue_num <= 0:
        return False
    issue = issues.get(issue_num)
    if not issue or "roadmap" not in label_names(issue):
        return False
    if status(issue, releases) != "RELEASED":
        return False
    report = proof.get("acceptance", "")
    if not isinstance(report, str) or not REPORT_URL.fullmatch(report):
        return False
    if evidence_reference(issue) != report:
        return False
    release = proof.get("release", "")
    if not isinstance(release, str) or evidence_reference(issue, "Release evidence") != release:
        return False
    return True


def stage_for(mod, issues, releases=(), proofs=None) -> str:
    return "HONORED" if verified_replacement(mod, issues, releases, proofs or {}) \
        else "INSPIRATION"


def md_escape(s):
    return str(s).replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def mk_index(mods, issues, releases, proofs):
    honored = [m for m in mods if stage_for(m, issues, releases, proofs) == "HONORED"]
    lines = [
        "<!-- Generated by tools/render_unified_hero.py. Do not edit manually. -->",
        "# ARS — Hall of Assimilation / full credits", "",
        "All names and original source links come from "
        "[Community Inspirations & Thanks](COMMUNITY_INSPIRATIONS.md). "
        "The approved README Hero artwork is static. This generated index carries "
        "the current status of every credited original.", "",
        "**Only two Hall states:** Inspiration (acknowledged reference) and "
        "Honored (complete independently implemented, tested and published replacement). "
        "No partial feature or roadmap-epic status means an entire mod is replaced.", "",
        f"**{len(mods)} documented inspirations · {len(honored)} honored**", "",
        "| Original mod | Original author / team | Hall status |",
        "|---|---|---|",
    ]
    for mod in mods:
        flag = stage_for(mod, issues, releases, proofs)
        lines.append(f"| [{md_escape(mod['name'])}]({mod['source']}) | "
                     f"{md_escape(mod['author'])} | {flag} |")
    lines += ["", "## How the Hall updates", "",
              "- Names, creators, and links are read from the original credits page.",
              "- The README links here; static artwork does not claim completed replacements.",
              "- Honored requires a dedicated [proof record](data/assimilation-proofs.json), "
              "human-approved complete parity, a pinned acceptance report "
              "and a published, downloadable ARS ZIP release.",
              "- Public development focus comes from the existing "
              "[GitHub roadmap](ROADMAP.md); internal working plans are never displayed.",
              "- No original third-party mod icons or artwork are added to this credit index.",
              "", "Explore the [Hall of Heroes](HALL_OF_HEROES.md), "
              "[live roadmap](ROADMAP.md) and [project home](../README.md).", ""]
    return "\n".join(lines)


def center(d, y, text, face, fill, left=0, right=W):
    width = d.textbbox((0, 0), text, font=face)[2]
    d.text(((left + right - width) // 2, y), text, font=face, fill=fill)


def truncate(d, label, face, width):
    original = str(label)
    if d.textbbox((0, 0), original, font=face)[2] <= width:
        return original
    val = original
    while val and d.textbbox((0, 0), val + "...", font=face)[2] > width:
        val = val[:-1]
    return val.rstrip() + "..."


def border(d, rect, color=BORDER, width=2, radius=7):
    d.rounded_rectangle(rect, radius=radius, outline=color, width=width)


def picture(canvas):
    """Reuse approved ARS concept tractor photograph; paint an immersive garage frame."""
    if not SCENERY.is_file():
        raise FileNotFoundError("Missing existing approved ARS artwork")
    with Image.open(SCENERY) as img:
        photo = img.convert("RGB")
    if photo.size != (1672, 941):
        raise ValueError(f"Unexpected photo master {photo.size}")
    # Only use scenic upper-right section, never the mocked roadmap cards.
    crop = photo.crop((710, 5, 1667, 450))
    crop = crop.resize((1010, 455), Image.Resampling.LANCZOS)
    canvas.paste(crop, (642, 22))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Workshop interior left: restrained steel framing and glow.
    od.rectangle((0, 0, 760, 487), fill=(4, 15, 12, 240))
    for x in (40, 122, 204, 286, 368, 450, 532, 614):
        od.line((x, 3, x, 480), fill=(45, 85, 65, 60), width=1)
    for y in (88, 177, 266, 355):
        od.line((0, y, 690, y), fill=(39, 79, 61, 43), width=1)
    # Tint the scene like the garage reference, preserve the tractor's visibility.
    od.rectangle((642, 22, 1652, 480), fill=(2, 16, 10, 34))
    # Gentle gradient where black workshop merges with the field scene.
    for xx in range(643, 885, 3):
        intensity = round(217 * (1 - (xx - 643) / 242))
        od.rectangle((xx, 0, xx + 3, 484), fill=(4, 15, 11, intensity))
    # Upper beam and machine shed architecture.
    od.rectangle((0, 0, W, 24), fill=(4, 13, 11, 250))
    od.rectangle((0, 471, W, 491), fill=(4, 14, 11, 250))
    od.rectangle((1532, 22, 1562, 471), fill=(4, 18, 14, 165))
    od.line((28, 39, 1634, 39), fill=(99, 231, 165, 110), width=2)
    od.line((638, 28, 638, 473), fill=(79, 166, 113, 160), width=3)
    od.line((1568, 29, 1568, 473), fill=(79, 166, 113, 160), width=2)
    canvas.paste(overlay, (0, 0), overlay)


PUBLIC_CATEGORIES = {
    3: ("Vehicle Systems & Maintenance", "Wear  ·  Breakdowns  ·  Workshop"),
    4: ("Unified ARS Interface", "One connected settings & navigation hub"),
    5: ("Mod Compatibility", "Interoperability between gameplay systems"),
    6: ("Farming Simulator 25 Integration", "Connected system integration"),
    7: ("Physics, Fuel & Machinery", "Driving  ·  Fuel  ·  Equipment"),
    8: ("Fields & Agronomy", "Soil  ·  Crop rotation  ·  Growth"),
    9: ("Farm Economics", "Finance  ·  Land  ·  Markets"),
    10: ("Production & Livestock", "Animals  ·  Storage  ·  Production"),
    11: ("Forestry & Logistics", "Cargo  ·  Forest  ·  Transport"),
    12: ("Field & Transport Automation", "Farming assistance  ·  Routing"),
}


def development_cards(issues, releases):
    """Issue-driven selection of useful public product topics, never private code names.

    A building/testing public roadmap epic takes priority, then 'now',
    then 'next'. Internal implementation nicknames are never rendered.
    """
    roadmap = [x for x in issues if "roadmap" in label_names(x)]
    def priority(item):
        state = status(item, releases)
        active = state in {"BUILDING", "TESTING"}
        ph = phase(item)
        return (0 if active else 1,
                {"now": 0, "next": 1, "planned": 2, "future": 3}.get(ph, 4),
                int(item["number"]))
    ordered = sorted(roadmap, key=priority)
    active = [x for x in ordered if status(x, releases) in {"BUILDING","TESTING"}]
    current = (active or ordered or [None])[0]
    future = [x for x in ordered if current is None or x["number"] != current["number"]]
    next_items = [x for x in future if phase(x) in {"now","next"}]
    if not next_items:
        next_items = future

    def friendly(item):
        if item is None:
            return ("Development roadmap", "Product details coming soon")
        num = int(item["number"])
        if num in PUBLIC_CATEGORIES:
            return PUBLIC_CATEGORIES[num]
        title = clean_title(item)
        title = re.sub(r"(?i)option\s+[a-z]\s*[:\-]?\s*", "", title).strip()
        return title[:100], "See public ARS roadmap"

    main_title, main_detail = friendly(current)
    next_title, _ = friendly(next_items[0] if next_items else None)
    next_detail, _ = friendly(next_items[1] if len(next_items) > 1 else None)
    if current is None:
        main_title, main_detail = "Roadmap in preparation", "Future connected systems"
    elif status(current, releases) not in {"BUILDING","TESTING"}:
        main_detail = "Next development focus"
    return (
        ("CURRENT DEVELOPMENT", main_title, main_detail),
        ("NEXT FOCUS", next_title,
         next_detail if len(next_items) > 1 else "Further modules on the roadmap"),
        ("EXPANDING INTO", "Physics  ·  Fuel  ·  Agronomy",
         "Economy  ·  Logistics  ·  Automation"),
    )


def sketch(canvas, issues, releases):
    d = ImageDraw.Draw(canvas)
    picture(canvas)
    d = ImageDraw.Draw(canvas)

    # 01 | Cinematic garage pitch
    d.text((62, 94), "ARS", font=font(163, True), fill=GREEN,
           stroke_width=2, stroke_fill="#17412b")
    d.line((64, 275, 572, 275), fill=GREEN, width=3)
    d.text((65, 298), "ADVANCED REALMS SUITE", font=font(30, True), fill=CREAM)
    d.text((66, 355), "MORE REALISM.", font=font(35, True), fill=CREAM)
    d.text((66, 405), "LESS MOD JUGGLING.", font=font(29, True), fill=GREEN)
    d.text((1133, 72), "CONNECTED SYSTEMS", font=font(18, True), fill=GREEN)

    # 02 | Technical command center; public-facing product features only.
    d.rounded_rectangle((27, 511, W-27, 717), radius=12,
                        fill=PANEL, outline=BORDER, width=2)
    center(d, 523, "ARS // LIVE DEVELOPMENT", font(29, True), GREEN)
    d.line((49, 566, W - 49, 566), fill="#275a42", width=2)
    divs = (563, 1113)
    for x in divs:
        d.line((x, 582, x, 698), fill="#2d6049", width=2)
    columns = [(39, 565, *development_cards(issues, releases)[0]),
               (569, 1115, *development_cards(issues, releases)[1]),
               (1122, 1630, *development_cards(issues, releases)[2])]
    for left, right, label, name, sub in columns:
        center(d, 584, label, font(18, True), GREEN, left, right)
        f = font(22, True)
        center(d, 626, truncate(d, name, f, right-left-20), f, CREAM, left, right)
        f = font(17)
        center(d, 668, truncate(d, sub, f, right-left-17), f, SOFT, left, right)

    # 03 | A worthy, completely centered Hall. No icons or individual mod cards.
    d.rounded_rectangle((27, 734, W-27, H-23), radius=11,
                        fill="#0b1410", outline="#8c774a", width=2)
    d.line((53, 756, 396, 756), fill=GOLD, width=2)
    d.line((W - 396, 756, W - 53, 756), fill=GOLD, width=2)
    center(d, 754, "HALL OF ASSIMILATION", serif(45, True), GOLD)
    center(d, 816, "Inspired by the modding pioneers. Honoring the legends.",
           serif(21), CREAM)
    d.line((230, 857, W-230, 857), fill="#75633e", width=2)


def name_lines(d, names, limit=1420, max_lines=3):
    """Greedy width-bound, center-ready text rows; cannot overflow the image."""
    f = font(23)
    lines, current = [], ""
    for name in names:
        candidate = (current + "   ·   " if current else "") + name
        if d.textbbox((0, 0), candidate, font=f)[2] > limit and current:
            lines.append(current)
            current = name
        else:
            current = candidate
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    consumed = sum(line.count("   ·   ") + 1 for line in lines)
    if consumed < len(names) and lines:
        suffix = f"  ·  +{len(names)-consumed} more"
        while lines[-1] and d.textbbox((0, 0), lines[-1]+suffix, font=f)[2] > limit:
            part = lines[-1].rsplit("   ·   ", 1)
            if len(part) == 1:
                break
            lines[-1] = part[0]
        lines[-1] += suffix
    return lines


def hall(canvas, mods, featured, issue_map, releases, proofs):
    d = ImageDraw.Draw(canvas)
    honored = [m for m in mods if stage_for(m, issue_map, releases, proofs) == "HONORED"]
    honors = {m["source"] for m in honored}
    # Prefer the curated order, then canonical credits; nothing hand-drawn per mod.
    picked = featured + [m for m in mods if m["source"] not in
                         {f["source"] for f in featured}]
    inspiration = [m["name"] for m in picked if m["source"] not in honors]
    featured_names = inspiration[:8]
    center(d, 876, f"INSPIRATION  /  {len(mods)-len(honored)}",
           font(22, True), GREEN)
    for i, line in enumerate(name_lines(d, featured_names, max_lines=2)):
        center(d, 922 + 43*i, line, font(26), CREAM)
    remaining = len(inspiration) - len(featured_names)
    if remaining:
        center(d, 1006, f"+{remaining} MORE IN THE FULL TRIBUTE ARCHIVE",
               font(18), SOFT)
    d.line((250, 1034, W-250, 1034), fill="#655538", width=1)
    center(d, 1047, f"HONORED  /  {len(honored)}", font(24, True), GOLD)
    if honored:
        names = [m["name"] for m in honored]
        for i, line in enumerate(name_lines(d, names, max_lines=1)):
            center(d, 1083 + i*30, line, serif(21), CREAM)
    else:
        center(d, 1087, "The legends are still working. No retirements yet.",
               serif(23), "#e5c994")
    center(d, 1130,
           f"FULL TRIBUTE ARCHIVE: {len(mods)} ORIGINAL SOURCES  //  FEWER ZIPs. MORE CREDITS.",
           font(17), SOFT)


def render(issues, releases):
    mods = credited_mods(CREDITS.read_text(encoding="utf-8"))
    if not mods:
        raise ValueError("Missing source attributions")
    featured = validate_config(json.loads(REGISTRY.read_text(encoding="utf-8")), mods)
    issue_map = {int(i["number"]): i for i in issues}
    proofs = read_proofs({m["source"] for m in mods})

    canvas = Image.new("RGB", (W, H), BG)
    sketch(canvas, issues, releases)
    hall(canvas, mods, featured, issue_map, releases, proofs)
    data = io.BytesIO()
    canvas.save(data, format="PNG", optimize=True)
    payload = data.getvalue()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUT.exists() or OUT.read_bytes() != payload:
        OUT.write_bytes(payload)
    index = mk_index(mods, issue_map, releases, proofs)
    if not INDEX.exists() or INDEX.read_text(encoding="utf-8") != index:
        INDEX.write_text(index, encoding="utf-8")
    print(f"Rendered cinematic garage Hero + public feature pulse + two-state Hall; "
          f"{len(mods)} credited sources, "
          f"{sum(stage_for(m, issue_map, releases, proofs)=='HONORED' for m in mods)} honored")


if __name__ == "__main__":
    render(fetch_issues(), fetch_releases())
