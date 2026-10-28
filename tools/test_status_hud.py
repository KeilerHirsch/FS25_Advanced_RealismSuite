#!/usr/bin/env python3
"""Offline regressions for the ARS release-aware compact status pulse."""
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

    def test_building_and_gate_open(self):
        cards = snapshot(self.issues)
        self.assertEqual(cards[0][1], "#3  /  BUILDING")
        self.assertEqual(cards[1][1], "ISSUE #6 OPEN")
        self.assertEqual(cards[2][1], "01 ACTIVE  /  03 TOTAL")

    def test_closed_is_not_verified(self):
        self.issues[1]["state"] = "closed"
        self.assertEqual(snapshot(self.issues)[1][1], "ISSUE #6 OPEN")

    def test_selflink_does_not_satisfy_acceptance(self):
        self.issues[1] = issue(6, "phase:next", "status:verified",
                               evidence=ROOT + "/issues/6")
        self.assertEqual(snapshot(self.issues)[1][1], "#6 NEEDS EVIDENCE")

    def test_pinned_acceptance_report_satisfies_pointer(self):
        self.issues[1] = issue(6, "phase:next", "status:verified",
                               evidence=REPORT)
        self.assertEqual(snapshot(self.issues)[1][1], "ISSUE #6 VERIFIED")

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

    def test_conflicting_gate_labels_not_green(self):
        self.issues[1] = issue(6, "status:verified", "status:building",
                               evidence=REPORT)
        self.assertEqual(snapshot(self.issues)[1][1],
                         "#6 STATUS CONFLICT")

    def test_published_release_precedes_development_label(self):
        self.assertEqual(snapshot(self.issues, RELEASE)[0][:2],
                         ("PRE-RELEASE", "v0.2.0"))

    def test_fail_closed_missing_epic(self):
        first, second, third = snapshot([issue(9, "phase:planned")])
        self.assertEqual(first[1], "UNTRACKED")
        self.assertEqual(second[1], "UNTRACKED")
        self.assertEqual(third[1], "00 ACTIVE  /  01 TOTAL")

    def test_svg_is_valid_and_escapes_release_tag(self):
        fake = dict(RELEASE, tag_name="v1.0<x&y>")
        svg = render_svg(self.issues, fake)
        self.assertTrue(ElementTree.fromstring(svg).tag.endswith("svg"))
        self.assertIn("v1.0&lt;x&amp;y&gt;", svg)

    def test_deterministic(self):
        self.assertEqual(render_svg(self.issues), render_svg(self.issues))


if __name__ == "__main__":
    unittest.main()
