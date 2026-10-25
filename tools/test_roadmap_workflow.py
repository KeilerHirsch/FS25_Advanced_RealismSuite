#!/usr/bin/env python3
"""Regression guard for generated ARS roadmap files and PR permissions."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
GENERATED = (
    "docs/ROADMAP.md",
    "docs/assets/roadmap.svg",
    "docs/assets/roadmap-live.png",
    "docs/assets/status-live.svg",
)
DIFF_COMMAND = "git diff --exit-code -- " + " ".join(GENERATED)


def assert_pr_roadmap_contract(workflow):
    """Raise if a generated-file PR could skip parity checks."""
    pr = workflow.split("  pull_request:\n", 1)[1].split("  push:\n", 1)[0]
    push = workflow.split("  push:\n", 1)[1].split("  schedule:\n", 1)[0]
    verify = workflow.split("  verify:\n", 1)[1].split("  publish:\n", 1)[0]

    for path in GENERATED:
        assert "- " + path in pr, f"PR does not trigger on {path}"
        assert "- " + path in push, f"push does not trigger on {path}"
    assert "- tools/test_roadmap_workflow.py" in pr
    assert "permissions:\n  contents: read" in workflow
    assert "contents: write" not in verify, "PR validation has write access"
    assert "persist-credentials: false" in verify
    assert "git push" not in verify

    rendered = verify.find("python tools/render_status_hud.py")
    checked = verify.find(DIFF_COMMAND)
    assert rendered >= 0, "status rendering missing"
    assert checked > rendered, "generated files not checked after rendering"
    assert "continue-on-error: true" not in verify[rendered:checked]


def assert_pinned_actions(workflow):
    """Refuse mutable action tags in either the read-only or publishing job."""
    for action in ("actions/checkout", "actions/setup-python"):
        refs = re.findall(r"uses: " + re.escape(action) +
                          r"@([0-9a-f]{40})(?:\\s|$)", workflow)
        assert len(refs) == 2, f"{action} must have two full SHA references"


class RoadmapWorkflowContractTest(unittest.TestCase):
    def test_real_workflow_checks_generated_content(self):
        workflow = (ROOT / ".github/workflows/roadmap.yml").read_text(
            encoding="utf-8"
        )
        assert_pr_roadmap_contract(workflow)

    def test_actions_use_immutable_commit_refs(self):
        workflow = (ROOT / ".github/workflows/roadmap.yml").read_text(
            encoding="utf-8"
        )
        assert_pinned_actions(workflow)

    def test_mutable_action_tag_rejected(self):
        workflow = (ROOT / ".github/workflows/roadmap.yml").read_text(
            encoding="utf-8"
        )
        tampered = re.sub(r"actions/checkout@[0-9a-f]{40}",
                          "actions/checkout@v4", workflow, count=1)
        with self.assertRaisesRegex(AssertionError, "two full SHA"):
            assert_pinned_actions(tampered)

    def test_missing_generated_asset_trigger_is_rejected(self):
        workflow = (ROOT / ".github/workflows/roadmap.yml").read_text(
            encoding="utf-8"
        )
        tampered = workflow.replace(
            "      - docs/assets/roadmap-live.png\n", "", 1
        )
        with self.assertRaisesRegex(AssertionError, "PR does not trigger"):
            assert_pr_roadmap_contract(tampered)

    def test_missing_parity_check_is_rejected(self):
        workflow = (ROOT / ".github/workflows/roadmap.yml").read_text(
            encoding="utf-8"
        )
        tampered = workflow.replace(DIFF_COMMAND, "git status --short", 1)
        with self.assertRaisesRegex(AssertionError, "not checked"):
            assert_pr_roadmap_contract(tampered)


if __name__ == "__main__":
    unittest.main()
