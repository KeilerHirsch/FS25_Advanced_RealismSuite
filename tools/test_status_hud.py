#!/usr/bin/env python3
"""Offline regressions for the small ARS README pulse graphic."""
import unittest
from xml.etree import ElementTree
from render_status_hud import render_svg, snapshot


def issue(number, *tags, state="open", evidence=False):
    body = ("Verification evidence: "
            "https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/issues/6"
            if evidence else "")
    return {"number": number, "state": state, "body": body,
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

    def test_explicit_testing_and_verified(self):
        self.issues[1]["labels"].append({"name": "status:testing"})
        self.assertEqual(snapshot(self.issues)[1][1], "ISSUE #6 IN TEST")
        self.issues[1]["labels"][-1]["name"] = "status:verified"
        self.assertEqual(snapshot(self.issues)[1][1], "#6 NEEDS EVIDENCE")
        self.issues[1]["body"] = (
            "Verification evidence: https://github.com/KeilerHirsch/"
            "FS25_Advanced_RealmsSuite/issues/6")
        self.assertEqual(snapshot(self.issues)[1][1], "ISSUE #6 VERIFIED")

    def test_ticket_released_without_release_is_not_shipped(self):
        self.issues[0]["labels"][-1]["name"] = "status:released"
        self.assertEqual(snapshot(self.issues)[0][1], "#3  /  EVIDENCE REQUIRED")
        self.issues[0]["body"] = ("Verification evidence: "
            "https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/releases/tag/v1")
        self.assertEqual(snapshot(self.issues)[0][1], "#3  /  VERIFY RELEASE")

    def test_conflicting_gate_labels_not_green(self):
        self.issues[1]["labels"].append({"name": "status:verified"})
        self.issues[1]["labels"].append({"name": "status:building"})
        self.issues[1]["body"] = (
            "Verification evidence: https://github.com/KeilerHirsch/"
            "FS25_Advanced_RealmsSuite/issues/6")
        self.assertEqual(snapshot(self.issues)[1][1], "#6 STATUS CONFLICT")

    def test_published_release_precedes_development_label(self):
        release = {"tag_name": "v0.2.0-beta", "prerelease": True, "draft": False}
        self.assertEqual(snapshot(self.issues, release)[0][:2],
                         ("PRE-RELEASE", "v0.2.0-beta"))

    def test_fail_closed_missing_epic(self):
        first, second, third = snapshot([issue(9, "phase:planned")])
        self.assertEqual(first[1], "UNTRACKED")
        self.assertEqual(second[1], "UNTRACKED")
        self.assertEqual(third[1], "00 ACTIVE  /  01 TOTAL")

    def test_svg_is_valid_and_escapes_release_tag(self):
        svg = render_svg(self.issues, {"tag_name": "v1.0<x&y>", "prerelease": False})
        self.assertTrue(ElementTree.fromstring(svg).tag.endswith("svg"))
        self.assertIn("v1.0&lt;x&amp;y&gt;", svg)

    def test_deterministic(self):
        self.assertEqual(render_svg(self.issues), render_svg(self.issues))


if __name__ == "__main__":
    unittest.main()
