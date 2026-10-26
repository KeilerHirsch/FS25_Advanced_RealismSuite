#!/usr/bin/env python3
"""Offline contract tests for the single dynamically generated README hero."""
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import render_unified_hero as h


def issue(num, labels, body="", state="open"):
    return {"number": num, "labels": [{"name": v} for v in labels],
            "body": body, "state": state}


def fixtures():
    return [
        issue(3, ["roadmap", "phase:now", "status:building"]),
        issue(6, ["roadmap", "phase:next"]),
        issue(7, ["roadmap", "phase:planned"]),
        issue(8, ["roadmap", "phase:planned"]),
        issue(12, ["roadmap", "phase:future"]),
    ]


def run():
    text = h.CREDITS.read_text(encoding="utf-8")
    mods = h.credited_mods(text)
    assert len(mods) >= 40, len(mods)
    config = json.loads(h.REGISTRY.read_text(encoding="utf-8"))
    featured = h.validate_config(config, mods)
    assert len(featured) == 8
    assert featured[0]["author"] == "id577"
    assert featured[1]["author"] == "Courseplay team"
    assert featured[2]["author"] == "Stephan-S and AutoDrive contributors"

    sample = {int(i["number"]): i for i in fixtures()}
    assert h.stage_for(featured[0], sample) == "UNDER DISSECTION"
    assert h.stage_for(featured[1], sample) == "IN QUEUE"
    assert h.stage_for(featured[3], sample) == "IN QUEUE"
    assert h.stage_for({"name": "No epic"}, sample) == "RESEARCH"
    missing = dict(sample)
    del missing[3]
    assert h.stage_for(featured[0], missing) == "RESEARCH"

    # Even a 'verified' or 'released' roadmap epic does NOT retire a whole mod.
    completed = issue(3, ["roadmap", "status:verified"],
                      "Verification evidence: "
                      "https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/"
                      "blob/" + "a" * 40 + "/docs/acceptance/example.md")
    sample[3] = completed
    assert h.stage_for(featured[0], sample) != "HONORED"
    sample[3] = issue(3, ["roadmap", "status:released"])
    assert h.stage_for(featured[0], sample) != "HONORED"

    duplicated = json.loads(json.dumps(config))
    duplicated["featured"][1]["source"] = duplicated["featured"][0]["source"]
    try:
        h.validate_config(duplicated, mods)
        raise AssertionError("Duplicate icon source not rejected")
    except ValueError:
        pass

    orphan = json.loads(json.dumps(config))
    orphan["featured"][0]["source"] = "https://github.com/not-in-credits/nope"
    try:
        h.validate_config(orphan, mods)
        raise AssertionError("Ghost original credit not rejected")
    except ValueError:
        pass

    with tempfile.TemporaryDirectory() as d:
        target = Path(d)
        base = target / "roadmap.png"
        outfile = target / "hero.png"
        index = target / "index.md"
        Image.new("RGB", (h.W, 941), "#081914").save(base, "PNG")
        with patch.object(h, "ART", base), patch.object(h, "OUT", outfile), \
             patch.object(h, "INDEX", index):
            h.render(fixtures(), [])
            first = outfile.read_bytes()
            first_index = index.read_text("utf-8")
            h.render(fixtures(), [])
            assert first == outfile.read_bytes(), "Non-deterministic hero PNG"
            assert first_index == index.read_text("utf-8"), "Non-deterministic index"
            with Image.open(outfile) as im:
                assert im.size == (1672, 1782)
            assert len(first) > 12000
            assert "Advanced Damage System" in first_index
            assert "Fully replaced: 0" in first_index
            assert "UNDER DISSECTION" in first_index
            assert len([x for x in first_index.splitlines() if x.startswith("| [")]) == len(mods)
            print("Unified hero tests: PASSED",
                  len(mods), "mod credits,",
                  len(featured), "framed icons,",
                  hashlib.sha256(first).hexdigest()[:16], "PNG SHA256 prefix")


if __name__ == "__main__":
    run()
