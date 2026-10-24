#!/usr/bin/env python3
import unittest
from check_commit_attribution import ambiguous_coauthors


class AttributionTests(unittest.TestCase):
    def test_personal_noreply_is_valid(self):
        self.assertEqual(ambiguous_coauthors(
            "Co-authored-by: KeilerHirsch "
            "<259172531+KeilerHirsch@users.noreply.github.com>"), [])

    def test_generic_identity_rejected(self):
        self.assertEqual(ambiguous_coauthors(
            "Co-authored-by: KeilerHirsch <noreply@users.noreply.github.com>"),
            ["noreply@users.noreply.github.com"])

    def test_github_system_identity_rejected_as_coauthor(self):
        self.assertEqual(ambiguous_coauthors(
            "Co-authored-by: GitHub <noreply@github.com>"),
            ["noreply@github.com"])

    def test_system_committer_not_coauthor(self):
        self.assertEqual(ambiguous_coauthors(
            "committer GitHub <noreply@github.com>"), [])

    def test_casefold(self):
        self.assertEqual(ambiguous_coauthors(
            " CO-AUTHORED-BY: Person <NoReply@Users.NoReply.GitHub.Com> "),
            ["noreply@users.noreply.github.com"])

    def test_legitimate_person(self):
        self.assertEqual(ambiguous_coauthors(
            "Co-authored-by: Pat <pat@example.net>"), [])

    def test_plain_prose_does_not_trigger(self):
        self.assertEqual(ambiguous_coauthors(
            "An older commit said Co-authored-by: "
            "KeilerHirsch <noreply@users.noreply.github.com>."), [])


if __name__ == "__main__":
    unittest.main()
