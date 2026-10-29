#!/usr/bin/env python3
"""Offline regressions for the ARS release and roadmap live status pulse."""
import unittest
from xml.etree import ElementTree

from render_status_hud import (render_svg, snapshot,
                               latest_downloadable_release)

ROOT = "https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite"
REPORT = ROOT + "/blob/" + "a" * 40 + "/docs/acceptance/ars-fs25-gameplay.md"
RELEASE_URL = ROOT + "/releases/tag/v0.2.0"
RELEASE = {"html_url": RELEASE_URL, "tag_name": "v0.2.0", "draft": False,
           "prerelease": True,
           "assets": [{"name": "FS25_Advanced_RealismSuite_v0.2.0.zip"}]}


def issue(number, *tags, state="open", evidence="", release=""):
    body = []
    if evidence:
        body.append("Verification evidence: " + evidence)
    if release:
        body.append("Release evidence: " + release)
    return {"number": number, "state": state, "body": "\n".join(body),
            "labels": [{"name": x} for x in ("roadmap", *tags)]}


class LiveStatusTest(unittest.TestCase):
    def setUp(self):
        self.issues = [issue(3, "phase:now", "status:building"),
                       issue(6, "phase:next"), issue(9, "phase:planned")]

    def test_two_cards_building_and_roadmap(self):
        cards = snapshot(self.issues)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0][:2], ("DEVELOPMENT", "#3  /  BUILDING"))
        self.assertEqual(cards[1][:2],
                         ("ROADMAP EPICS", "01 ACTIVE  /  03 TOTAL"))

    def test_gate_issue_does_not_affect_live_status(self):
        cards = snapshot(self.issues)
        self.issues[1] = issue(6, "phase:next", "status:verified",
                               evidence=REPORT)
        self.assertEqual(snapshot(self.issues), cards)

    def test_released_without_proven_zip_not_shipped(self):
        self.issues[0] = issue(3, "phase:now", "status:released",
                               evidence=REPORT, release=RELEASE_URL)
        self.assertEqual(snapshot(self.issues)[0][1],
                         "#3  /  VERIFY RELEASE")
        self.assertEqual(snapshot(self.issues, releases=[RELEASE])[0][1],
                         "#3  /  RELEASED")

    def test_release_visibility_needs_fs25_archive(self):
        self.assertIsNone(latest_downloadable_release(
            [dict(RELEASE, assets=[{"name": "notes.txt"}])]))
        self.assertEqual(latest_downloadable_release([RELEASE]), RELEASE)

    def test_published_release_precedes_development_label(self):
        self.assertEqual(snapshot(self.issues, RELEASE)[0][:2],
                         ("PRE-RELEASE", "v0.2.0"))
        stable = dict(RELEASE, prerelease=False)
        self.assertEqual(snapshot(self.issues, stable)[0][:2],
                         ("RELEASE", "v0.2.0"))

    def test_missing_focus_does_not_hide_roadmap(self):
        first, second = snapshot([issue(9, "phase:planned")])
        self.assertEqual(first[1], "UNTRACKED")
        self.assertEqual(second[1], "00 ACTIVE  /  01 TOTAL")

    def test_svg_is_valid_and_escapes_release_tag(self):
        fake = dict(RELEASE, tag_name="v1.0<x&y>")
        svg = render_svg(self.issues, fake)
        self.assertTrue(ElementTree.fromstring(svg).tag.endswith("svg"))
        self.assertIn("v1.0&lt;x&amp;y&gt;", svg)
        self.assertNotIn("IN-GAME GATE", svg)
        self.assertIn("ARS // LIVE DEVELOPMENT", svg)
        self.assertIn("ROADMAP EPICS", svg)
        self.assertIn("PRE-RELEASE", svg)
        self.assertIn("01 ACTIVE", svg)
        self.assertIn("/ 03 TOTAL", svg)
        self.assertEqual(svg.count('y="61"'), 5)
        self.assertIn("GITHUB-SOURCED", svg)

    def test_deterministic(self):
        self.assertEqual(render_svg(self.issues), render_svg(self.issues))


if __name__ == "__main__":
    unittest.main()
