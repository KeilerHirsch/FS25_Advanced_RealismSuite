#!/usr/bin/env python3
"""Offline checks for evidence-integrity and the eight cinematic roadmap cards."""
import unittest

from render_roadmap import has_verification_evidence, status
from render_roadmap_hud import THEMES, card_metrics

ROOT = "https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite"
REPORT = ROOT + "/blob/" + "a" * 40 + "/docs/acceptance/ars-first-test.md"
RELEASE_URL = ROOT + "/releases/tag/v0.2.0"
PUBLISHED = {"html_url": RELEASE_URL, "tag_name": "v0.2.0", "draft": False,
             "assets": [{"name": "FS25_Advanced_RealmsSuite_v0.2.0.zip"}]}


def issue(number, labels, state="open", evidence="", release=""):
    body = []
    if evidence:
        body.append("Verification evidence: " + evidence)
    if release:
        body.append("Release evidence: " + release)
    return {"number": number, "state": state, "body": "\n".join(body),
            "labels": [{"name": tag} for tag in ["roadmap", *labels]]}


class LiveHudMetricsTest(unittest.TestCase):
    def test_eight_approved_themes(self):
        self.assertEqual(len(THEMES), 8)
        self.assertEqual([name for name, _ in THEMES],
                         ["Vehicle Systems & Workshop", "Fleet & Maintenance",
                          "Physics, Fuel & Wear", "Fields & Agronomy",
                          "Soil, Climate & Crop Health",
                          "Animals, Storage & Production",
                          "Economics, Logistics & Markets",
                          "Compatibility, Automation & Diagnostics"])

    def test_building_is_not_verified(self):
        self.assertEqual(card_metrics({3: issue(3, ["status:building"])}, (3,)),
                         ("ACTIVE", 0, 1, 0))

    def test_closed_issue_is_not_verified(self):
        self.assertEqual(card_metrics({3: issue(3, [], state="closed")}, (3,)),
                         ("PLANNED", 0, 1, 0))

    def test_commit_pinned_report_makes_claim_traceable(self):
        verified = issue(3, ["status:verified"], evidence=REPORT)
        self.assertTrue(has_verification_evidence(verified))
        self.assertEqual(card_metrics({3: verified}, (3,)),
                         ("VERIFIED", 1, 1, 100))

    def test_self_link_is_not_an_acceptance_report(self):
        verified = issue(6, ["status:verified"], evidence=ROOT + "/issues/6")
        self.assertFalse(has_verification_evidence(verified))
        self.assertEqual(status(verified), "EVIDENCE REQUIRED")

    def test_unpinned_and_external_report_rejected(self):
        for evidence in [ROOT + "/blob/main/docs/acceptance/test.md",
                         "https://github.com/another/project/blob/" +
                         "a" * 40 + "/docs/acceptance/test.md",
                         ROOT + "/actions/runs/123",
                         ROOT + "/blob/" + "a" * 40 +
                         "/docs/acceptance/../fake.md"]:
            with self.subTest(evidence=evidence):
                self.assertFalse(has_verification_evidence(
                    issue(3, ["status:verified"], evidence=evidence)))

    def test_conflicting_labels_dont_count(self):
        found = {3: issue(3, ["status:building", "status:verified"],
                          evidence=REPORT)}
        self.assertEqual(card_metrics(found, (3,)),
                         ("PLANNED", 0, 1, 0))

    def test_released_requires_matching_published_archive(self):
        released = issue(3, ["status:released"], evidence=REPORT,
                         release=RELEASE_URL)
        self.assertEqual(status(released), "VERIFY RELEASE")
        self.assertEqual(card_metrics({3: released}, (3,)),
                         ("PLANNED", 0, 1, 0))
        self.assertEqual(status(released, [PUBLISHED]), "RELEASED")
        self.assertEqual(card_metrics({3: released}, (3,), [PUBLISHED]),
                         ("VERIFIED", 1, 1, 100))

    def test_release_without_zip_does_not_count(self):
        released = issue(3, ["status:released"], evidence=REPORT,
                         release=RELEASE_URL)
        no_zip = dict(PUBLISHED, assets=[{"name": "changelog.txt"}])
        self.assertEqual(status(released, [no_zip]), "VERIFY RELEASE")
        wrong_tag = dict(PUBLISHED, html_url=ROOT + "/releases/tag/v9")
        self.assertEqual(status(released, [wrong_tag]), "VERIFY RELEASE")
        draft = dict(PUBLISHED, draft=True)
        self.assertEqual(status(released, [draft]), "VERIFY RELEASE")

    def test_missing_issue_fails_closed(self):
        found = {3: issue(3, ["status:verified"], evidence=REPORT)}
        self.assertEqual(card_metrics(found, (3, 4)),
                         ("UNTRACKED", 0, 0, 0))
        found[3]["labels"] = [{"name": "status:verified"}]
        self.assertEqual(card_metrics(found, (3,)),
                         ("UNTRACKED", 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
