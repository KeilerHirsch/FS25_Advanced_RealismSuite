#!/usr/bin/env python3
"""Offline checks: public development topics, two-state Hall, honest evidence gate."""
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import render_unified_hero as h


def issue(number, labels, body="", state="open"):
    return {"number": number, "labels": [{"name": l} for l in labels],
            "body": body, "state": state}


def sample():
    return [
        issue(3, ["roadmap", "phase:now", "status:building"]),
        issue(4, ["roadmap", "phase:now"]),
        issue(5, ["roadmap", "phase:next"]),
        issue(7, ["roadmap", "phase:planned"]),
        issue(8, ["roadmap", "phase:planned"]),
        issue(12, ["roadmap", "phase:future"]),
    ]


def run():
    mods = h.credited_mods(h.CREDITS.read_text(encoding="utf-8"))
    assert len(mods) >= 40, len(mods)
    config = json.loads(h.REGISTRY.read_text(encoding="utf-8"))
    featured = h.validate_config(config, mods)
    assert len(featured) >= 4
    assert featured[0]["author"] == "id577"
    assert featured[1]["author"] == "Courseplay team"
    assert featured[2]["author"] == "Stephan-S and AutoDrive contributors"

    roadmap = sample()
    cards = h.development_cards(roadmap, [])
    assert cards[0][1] == "Vehicle Systems & Maintenance", cards
    assert cards[1][1] == "Unified ARS Interface"
    assert "Option C" not in repr(cards)
    assert "IN-GAME GATE" not in repr(cards)
    new = [issue(3, ["roadmap", "phase:now"]),
           issue(4, ["roadmap", "phase:now", "status:building"]),
           issue(5, ["roadmap", "phase:next"])]
    cards = h.development_cards(new, [])
    assert cards[0][1] == "Unified ARS Interface", cards
    assert cards[1][1] == "Vehicle Systems & Maintenance", cards
    assert h.development_cards([],[])[0][1] == "Roadmap in preparation"

    index = {int(x["number"]):x for x in roadmap}
    assert h.stage_for(featured[0], index) == "INSPIRATION"
    assert h.stage_for(featured[1], index) == "INSPIRATION"
    assert h.verified_replacement(featured[0], index, [], {}) is False
    assert h.read_proofs({m["source"] for m in mods}) == {}

    # A roadmap 'VERIFIED' label alone cannot retire any whole external mod.
    report = ("https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/"
              "blob/" + "a"*40 + "/docs/acceptance/full-ads.md")
    release_url = ("https://github.com/KeilerHirsch/FS25_Advanced_RealmsSuite/"
                   "releases/tag/v1.0.0")
    full_issue = issue(3, ["roadmap","status:released"],
                       "Verification evidence: " + report + "\n" +
                       "Release evidence: " + release_url)
    public = [{
        "html_url":release_url, "tag_name":"v1.0.0", "draft":False,
        "assets":[{"name":"FS25_Advanced_Realms_Suite.zip"}]
    }]
    numbered = {3:full_issue}
    assert h.stage_for(featured[0], numbered, public) == "INSPIRATION"
    proof = {"source":featured[0]["source"],"issue":3,"acceptance":report,
             "release":release_url,"human_accepted":True,
             "complete_replacement":True}
    assert h.stage_for(featured[0], numbered, public,
                       {featured[0]["source"]:proof}) == "HONORED"
    assert h.stage_for(featured[0], numbered, [],
                       {featured[0]["source"]:proof}) == "INSPIRATION"
    proof["complete_replacement"]=False
    assert h.stage_for(featured[0], numbered, public,
                       {featured[0]["source"]:proof}) == "INSPIRATION"

    doubled = json.loads(json.dumps(config))
    doubled["featured"][1]["source"]=doubled["featured"][0]["source"]
    try:
        h.validate_config(doubled,mods)
        raise AssertionError("Duplicate featured entry not rejected")
    except ValueError:
        pass
    unknown = json.loads(json.dumps(config))
    unknown["featured"][0]["source"]="https://github.com/unknown/unknown"
    try:
        h.validate_config(unknown,mods)
        raise AssertionError("Uncredited original source not rejected")
    except ValueError:
        pass

    with tempfile.TemporaryDirectory() as folder:
        folder=Path(folder)
        photo=folder/"photo.png"
        outfile=folder/"hero.png"
        target=folder/"index.md"
        Image.new("RGB",(1672,941),"#07170e").save(photo)
        with patch.object(h,"SCENERY",photo),patch.object(h,"OUT",outfile), \
             patch.object(h,"INDEX",target):
            h.render(roadmap, [])
            content=outfile.read_bytes()
            index=target.read_text("utf-8")
            h.render(roadmap, [])
            assert outfile.read_bytes() == content, "Image changes without input changes"
            assert target.read_text("utf-8") == index, "Index changes without input changes"
            with Image.open(outfile) as img:
                assert img.size == (1672,1176)
            assert len(content) > 12000
            assert "| INSPIRATION |" in index
            assert "Honored" in index
            assert "UNDER DISSECTION" not in index
            assert "IN QUEUE" not in index
            assert "FIELD TEST" not in index
            assert "Option C" not in index
            assert len([line for line in index.splitlines()
                        if line.startswith("| [")]) == len(mods)
            print("PASS: garage hero, two-state Hall, dynamic public focus,"
                  " evidence, 53+ authors, stable preview",
                  hashlib.sha256(content).hexdigest()[:16])


if __name__ == "__main__":
    run()
