#!/usr/bin/env python3
"""Single ARS README hero: live roadmap + public engineering pulse + mod tribute.

This renderer is intentionally conservative. Being inspired by a mod, having an
active epic, or closing an issue is NEVER proof that its mod was replaced.
Community credits are the source of authorship; featured JSON only adds layout
and maps a mod to its related public roadmap epic.
"""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from render_roadmap import (
    REPORT_URL, evidence_reference, fetch_issues, fetch_releases,
    label_names, status,
)
from render_status_hud import latest_downloadable_release, snapshot

ROOT = Path(__file__).resolve().parent.parent
CREDITS = ROOT / "docs/COMMUNITY_INSPIRATIONS.md"
REGISTRY = ROOT / "docs/data/assimilation-featured.json"
PROOFS = ROOT / "docs/data/assimilation-proofs.json"
ART = ROOT / "docs/assets/roadmap-live.png"
OUT = ROOT / "docs/assets/ars-unified-live-hero.png"
INDEX = ROOT / "docs/ASSIMILATION_INDEX.md"

W, H = 1672, 1782
BG = "#060f0c"
PANEL = "#091b15"
BORDER = "#316c4b"
GREEN = "#5df2a7"
CREAM = "#f0e8d5"
MUTED = "#afc8ba"
GOLD = "#cfaa6b"
COLORS = {
    "UNDER DISSECTION": "#ffbe76",
    "FIELD TEST": "#eebf67",
    "IN QUEUE": "#98c5f2",
    "RESEARCH": "#95c0a7",
    "HONORED": "#6ef5a4",
}
LINK = re.compile(r"\[([^\]]+)\]\((https://[^)\s]+)\)")
CREDIT = re.compile(r"^\s*-\s+\*\*([^*]+)\*\*\s+[\u2014-]\s+(.+)$")
SKIP = {"original project", "original", "source", "modhub", "readme", "license"}
ALLOWED_SOURCES = ("https://github.com/", "https://gitlab.com/",
                   "https://www.farming-simulator.com/mod.php?",
                   "https://farming-simulator.com/mod.php?")
ALLOWED_GLYPHS = {"engine", "field", "route", "soil", "year", "weather",
                  "calendar", "tractor", "wrench"}


def font(size: int, bold=False) -> ImageFont.FreeTypeFont:
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


def credited_mods(text: str) -> list[dict]:
    """Read original authors and source links from the canonical credits doc."""
    found, seen = [], set()
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
            found.append({"name": name.strip(), "author": author.strip(),
                          "source": url})
    return found


def validate_config(config: dict, mods: list[dict]) -> list[dict]:
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported assimilation-featured schema")
    sources = {m["source"]: m for m in mods}
    featured, used = [], set()
    for row in config.get("featured", []):
        source = row["source"]
        if source not in sources:
            raise ValueError(f"Featured source missing from credits: {source}")
        if source in used:
            raise ValueError(f"Duplicate featured source: {source}")
        used.add(source)
        glyph = row.get("glyph", "tractor")
        if glyph not in ALLOWED_GLYPHS:
            raise ValueError(f"Unknown original glyph type: {glyph}")
        issue = row.get("issue")
        if not isinstance(issue, int) or issue < 1:
            raise ValueError(f"Invalid roadmap issue for {source}")
        featured.append({**sources[source], "glyph": glyph, "issue": issue})
    if len(featured) != 8:
        raise ValueError(f"Hero uses exactly 8 framed exhibits; got {len(featured)}")
    return featured


def verified_replacement(mod: dict, issues: dict, releases, proofs: dict) -> bool:
    """Require *per-mod* human approval AND exact issue evidence + public ZIP release."""
    proof = proofs.get(mod.get("source"))
    if not proof or proof.get("human_accepted") is not True:
        return False
    if proof.get("complete_replacement") is not True:
        return False
    issue_number = proof.get("issue")
    if not isinstance(issue_number, int) or issue_number < 1:
        return False
    issue = issues.get(issue_number)
    if not issue or "roadmap" not in label_names(issue):
        return False
    if status(issue, releases) != "RELEASED":
        return False
    acceptance = proof.get("acceptance", "")
    if not isinstance(acceptance, str) or not REPORT_URL.fullmatch(acceptance):
        return False
    if acceptance != evidence_reference(issue):
        return False
    link = proof.get("release", "")
    if not isinstance(link, str) or link != evidence_reference(issue, "Release evidence"):
        return False
    return True


def read_proofs(sources: set[str]) -> dict:
    """No magic inference: an explicit evidence record is mandatory for every full replacement."""
    config = json.loads(PROOFS.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("Unknown assimilation proof schema")
    found = {}
    for entry in config.get("replacements", []):
        key = entry["source"]
        if key not in sources or key in found:
            raise ValueError(f"Unknown or duplicate source in assimilation proofs: {key}")
        found[key] = entry
    return found


def stage_for(mod: dict, issues: dict, releases=(), proofs=None) -> str:
    """Never infer full replacement from an epic-level status or merge."""
    if verified_replacement(mod, issues, releases, proofs or {}):
        return "HONORED"
    number = mod.get("issue")
    if number is None:
        return "RESEARCH"
    issue = issues.get(number)
    if not issue or "roadmap" not in label_names(issue):
        return "RESEARCH"
    current = status(issue, releases)
    if current == "BUILDING":
        return "UNDER DISSECTION"
    if current == "TESTING":
        return "FIELD TEST"
    if current in {"PLANNED", "VERIFIED", "RELEASED"}:
        # Epic verification says nothing about FULL replacement of this mod.
        return "IN QUEUE" if current == "PLANNED" else "RESEARCH"
    return "RESEARCH"


def text_fit(d, value, max_width, face):
    t = str(value)
    while t and d.textbbox((0, 0), t, font=face)[2] > max_width:
        t = t[:-1]
    if t != str(value):
        t = t.rstrip()[:-1] + "\u2026" if len(t) > 2 else "\u2026"
    return t


def symbol(d, x, y, kind, tint):
    """Project-owned schematic pictograms; no redistributed third-party icons."""
    box = (x, y, x + 93, y + 93)
    d.rounded_rectangle(box, radius=11, fill="#142b20", outline=GOLD, width=3)
    cx, cy = x + 46, y + 46
    if kind in {"engine", "wrench", "year", "tractor"}:
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), outline=tint, width=5)
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), outline=GOLD, width=4)
        for dx, dy in [(0, -31), (0, 31), (-31, 0), (31, 0)]:
            d.line((cx + dx // 2, cy + dy // 2, cx + dx, cy + dy), fill=tint, width=5)
        if kind == "year":
            d.text((x + 11, y + 64), "20XX", font=font(13, True), fill=GOLD)
    elif kind == "field":
        for s in range(-2, 3):
            d.line((cx + s * 13, cy - 29, cx + s * 17, cy + 27), fill=GOLD, width=3)
        d.arc((cx - 31, cy - 32, cx + 31, cy + 32), 45, 270, fill=tint, width=4)
    elif kind == "route":
        d.line((cx - 27, cy + 23, cx - 7, cy - 22, cx + 13, cy + 3, cx + 30, cy - 23),
               fill=tint, width=5, joint="curve")
        for px, py in [(-27, 23), (-7, -22), (30, -23)]:
            d.ellipse((cx + px - 5, cy + py - 5, cx + px + 5, cy + py + 5),
                      fill=GOLD)
    elif kind == "soil":
        for k in range(3):
            d.arc((cx - 28, cy + k * 13 - 11, cx + 29, cy + k * 13 + 11),
                  0, 180, fill=GOLD, width=3)
        d.line((cx, cy - 31, cx, cy - 2), fill=tint, width=4)
        d.line((cx, cy - 17, cx - 13, cy - 29), fill=tint, width=3)
        d.line((cx, cy - 20, cx + 13, cy - 31), fill=tint, width=3)
    elif kind == "weather":
        d.ellipse((cx - 18, cy - 20, cx + 9, cy + 5), outline=GOLD, width=4)
        d.ellipse((cx - 3, cy - 9, cx + 25, cy + 15), outline=GOLD, width=4)
        for dx in (-14, 5, 23):
            d.line((cx + dx, cy + 20, cx + dx - 7, cy + 34), fill=tint, width=4)
    elif kind == "calendar":
        d.rectangle((cx - 31, cy - 28, cx + 31, cy + 31), outline=tint, width=4)
        d.line((cx - 28, cy - 10, cx + 29, cy - 10), fill=GOLD, width=4)
        d.text((cx - 21, cy - 3), "12", fill=GOLD, font=font(22, True))


def background(canvas):
    d = ImageDraw.Draw(canvas)
    for y in range(941, H):
        blend = (y - 941) / (H - 941)
        d.line((0, y, W, y),
               fill=(int(6 + 3 * blend), int(15 + 9 * blend), int(12 + 4 * blend)))
    for x in range(28, W, 64):
        d.line((x, 947, x, H), fill="#10251b", width=1)


def fill_header(d, cards):
    d.rounded_rectangle((34, 959, W - 34, 1117), radius=13,
                        fill=PANEL, outline=BORDER, width=3)
    d.text((56, 977), "ARS // LIVE ENGINEERING PULSE", font=font(27, True), fill=GREEN)
    d.text((56, 1019), "GITHUB ISSUES + RELEASES  |  EVIDENCE-GATED",
           font=font(15), fill=MUTED)
    for idx, (label, value, color) in enumerate(cards):
        x = (63, 586, 1091)[idx]
        if idx:
            d.line((x - 30, 1000, x - 30, 1098), fill=BORDER, width=2)
        d.text((x, 1053), text_fit(d, label, 390, font(17)),
               font=font(17), fill=MUTED)
        d.ellipse((x, 1081, x + 13, 1094), fill=color)
        d.text((x + 22, 1070), text_fit(d, value, 405, font(27, True)),
               font=font(27, True), fill=color)


def card(d, mod, idx, stage):
    col, row = idx % 4, idx // 4
    x, y = 40 + 401 * col, 1235 + 230 * row
    w, h = 383, 213
    d.rounded_rectangle((x, y, x + w, y + h), radius=11,
                        fill="#0b1914", outline=GOLD, width=3)
    d.rounded_rectangle((x + 8, y + 8, x + w - 8, y + h - 8),
                        radius=8, outline="#4b6c50", width=1)
    d.line((x + 14, y + 157, x + w - 14, y + 157), fill="#506247", width=1)
    kind = mod.get("glyph", "tractor")
    symbol(d, x + 21, y + 32, kind, GREEN)
    nfont = font(19, True)
    raw_name = mod["name"].replace("\n", " ").strip()
    lines = textwrap.wrap(raw_name, width=21, break_long_words=True)
    if len(lines) > 2:
        lines = [lines[0], lines[1][:20] + "\u2026"]
    for z, line in enumerate(lines[:2]):
        d.text((x + 130, y + 38 + z * 28), text_fit(d, line, 240, nfont),
               font=nfont, fill=CREAM)
    d.text((x + 130, y + 107), text_fit(d, "by " + mod["author"], 228, font(15)),
           font=font(15), fill=MUTED)
    d.text((x + 20, y + 167), stage, font=font(20, True), fill=COLORS[stage])
    d.text((x + w - 155, y + 174), ("FULLY REPLACED" if stage == "HONORED" else "NOT REPLACED"),
           font=font(13), fill="#a9bcb0")


def mk_index(mods, featured, issues, releases, proofs):
    feat = {m["source"]: m for m in featured}
    honored_count = sum(verified_replacement(m, issues, releases, proofs) for m in mods)
    rows = [f"<!-- AUTO-GENERATED by tools/render_unified_hero.py. Do not edit. -->",
            "# ARS assimilation research index", "",
            "Every entry comes from the public [Community Inspirations & Thanks]"
            "(COMMUNITY_INSPIRATIONS.md); its author and source are credited there. "
            "The hero's **featured** entries are selected in "
            "[assimilation-featured.json](data/assimilation-featured.json).",
            "",
            "**Status is a research or public roadmap activity indicator, not a "
            "claim of copying, verified gameplay parity or complete replacement.** "
            "Only a human-accepted, mod-specific pinned acceptance report paired with an actual public ZIP release can earn HONORED status.",
            "",
            f"**Source entries: {len(mods)} | Featured: {len(featured)} | "
            f"Fully replaced: {honored_count} (evidence-gated)**", "",
            "| Original mod | Original author | ARS research status | Related public issue |",
            "|---|---|---|---|"]
    for mod in mods:
        linked = feat.get(mod["source"])
        stage = stage_for(linked or mod, issues, releases, proofs)
        issue = f"[#{linked['issue']}](https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/issues/{linked['issue']})" if linked else "\u2014"
        def esc(s):
            return str(s).replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
        rows.append(f"| [{esc(mod['name'])}]({mod['source']}) | "
                    f"{esc(mod['author'])} | {stage} | {issue} |")
    rows.extend(["", "### Status discipline", "",
                 "- **RESEARCH:** credited source; no active assimilation work is claimed.",
                 "- **IN QUEUE:** related public feature epic is planned.",
                 "- **UNDER DISSECTION:** related public epic is building; "
                 "does not prove this particular external mod was replaced.",
                 "- **FIELD TEST:** related public epic is in testing; "
                 "gameplay parity is not yet proven.",
                 "- **HONORED:** reserved for future **separately evidenced, human-accepted, "
                 "published full functional replacement**; not inferred from issue closure.",
                 "", "The public [live roadmap](ROADMAP.md) has the exact epic statuses. "
                 "The [Hall of Heroes](HALL_OF_HEROES.md) explains the tribute and "
                 "original creators' rights. Icons on the unified hero are **original "
                 "ARS schematic pictograms**; third-party mod icons will only be used "
                 "where redistribution rights have been confirmed.", ""])
    return "\n".join(rows)


def render(issues, releases):
    mods = credited_mods(CREDITS.read_text(encoding="utf-8"))
    if not mods:
        raise ValueError("No mod sources found in community credits")
    proofs = read_proofs({m["source"] for m in mods})
    config = json.loads(REGISTRY.read_text(encoding="utf-8"))
    featured = validate_config(config, mods)
    issue_map = {int(x["number"]): x for x in issues}
    if not ART.is_file():
        raise FileNotFoundError("Render roadmap-live.png before unified hero")
    base = Image.open(ART).convert("RGB")
    if base.size != (W, 941):
        raise ValueError(f"Expected 1672x941 live roadmap image, got {base.size}")
    canvas = Image.new("RGB", (W, H), BG)
    canvas.paste(base, (0, 0))
    background(canvas)
    d = ImageDraw.Draw(canvas)
    cards = snapshot(issues, latest_downloadable_release(releases), releases)
    fill_header(d, cards)
    d.line((42, 1151, W - 42, 1151), fill=BORDER, width=2)
    d.text((43, 1130), "ARS // HALL OF ASSIMILATED HEROES", font=font(29, True), fill=GOLD)
    d.text((43, 1173), "FRAMED TRIBUTES  /  LIVE RESEARCH & ROADMAP STATUS",
           font=font(16), fill=GREEN)
    d.text((1110, 1173), "FEWER ZIPs. MORE CREDITS.", font=font(15, True), fill=CREAM)
    for i, mod in enumerate(featured):
        card(d, mod, i, stage_for(mod, issue_map, releases, proofs))
    d.line((38, 1697, W - 38, 1697), fill=BORDER, width=2)
    d.text((42, 1714), "THE EXHIBITION IS OPEN. THE LEGENDS ARE STILL WORKING.",
           font=font(23, True), fill=CREAM)
    d.text((42, 1750),
           f"ALL {len(mods)} CREDITED MOD REFERENCES: docs/ASSIMILATION_INDEX.md"
           "   /   FULL REPLACEMENTS REQUIRE REVIEWED IN-GAME EVIDENCE",
           font=font(17), fill=GREEN)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    import io
    output = io.BytesIO()
    canvas.save(output, format="PNG", optimize=True)
    payload = output.getvalue()
    if not OUT.is_file() or OUT.read_bytes() != payload:
        OUT.write_bytes(payload)
    index = mk_index(mods, featured, issue_map, releases, proofs)
    if not INDEX.is_file() or INDEX.read_text(encoding="utf-8") != index:
        INDEX.write_text(index, encoding="utf-8")
    print(f"Rendered one live hero; {len(featured)} framed displays, "
          f"{len(mods)} credited sources; no fake assimilation")


if __name__ == "__main__":
    render(fetch_issues(), fetch_releases())
