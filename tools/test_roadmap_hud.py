#!/usr/bin/env python3
"""Offline regression checks for evidence-based cinematic GitHub roadmap HUD."""
import unittest

from render_roadmap_hud import THEMES, card_metrics


def issue(number, labels, state="open", evidence=False):
    body = ("Verification evidence: "
            "https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/actions/runs/123"
            if evidence else "")
    return {"number": number, "state": state, "body": body,
            "labels": [{"name": tag} for tag in ["roadmap", *labels]]}


class LiveHudMetricsTest(unittest.TestCase):
    def test_eight_user_approved_themes(self):
        self.assertEqual(len(THEMES), 8)
        self.assertEqual([name for name, _ in THEMES],
                         ["Vehicle Systems & Workshop", "Fleet & Maintenance",
                          "Physics, Fuel & Wear", "Fields & Agronomy",
                          "Soil, Climate & Crop Health",
                          "Animals, Storage & Production",
                          "Economics, Logistics & Markets",
                          "Compatibility, Automation & Diagnostics"])

    def test_open_building_not_claimed_verified(self):
        self.assertEqual(card_metrics({3: issue(3, ["status:building"])}, (3,)),
                         ("ACTIVE", 0, 1, 0))

    def test_closed_not_automatically_verified(self):
        self.assertEqual(card_metrics({3: issue(3, [], state="closed")}, (3,)),
                         ("PLANNED", 0, 1, 0))

    def test_explicit_verified_progress(self):
        found = {3: issue(3, ["status:verified"], evidence=True),
                 4: issue(4, ["status:building"])}
        self.assertEqual(card_metrics(found, (3, 4)),
                         ("ACTIVE", 1, 2, 50))

    def test_all_released_or_verified(self):
        found = {3: issue(3, ["status:released"], evidence=True),
                 4: issue(4, ["status:verified"], evidence=True)}
        self.assertEqual(card_metrics(found, (3, 4)),
                         ("VERIFIED", 2, 2, 100))

    def test_verified_label_without_evidence_does_not_count(self):
        found = {3: issue(3, ["status:verified"])}
        self.assertEqual(card_metrics(found, (3,)), ("PLANNED", 0, 1, 0))

    def test_conflicting_labels_dont_count(self):
        found = {3: issue(3, ["status:building", "status:verified"],
                          evidence=True)}
        self.assertEqual(card_metrics(found, (3,)), ("PLANNED", 0, 1, 0))

    def test_deleted_issue_must_not_inflate_progress(self):
        self.assertEqual(card_metrics({3: issue(3, ["status:verified"])}, (3, 4)),
                         ("UNTRACKED", 0, 0, 0))

    def test_missing_roadmap_label_invalidates_source(self):
        found = {3: issue(3, ["status:verified"])}
        found[3]["labels"] = [{"name": "status:verified"}]
        self.assertEqual(card_metrics(found, (3,)),
                         ("UNTRACKED", 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
