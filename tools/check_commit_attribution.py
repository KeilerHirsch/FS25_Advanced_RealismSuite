#!/usr/bin/env python3
"""Reject ambiguous co-author identities in newly introduced Git commits.

Only checks newly introduced commits, never rewrites history.
"""
import json
import os
import re
import subprocess
import sys

TRAILER = re.compile(r"(?im)^\s*co-authored-by\s*:\s*.+?<([^<>\s]+)>\s*$")
INVALID = {"noreply@users.noreply.github.com", "noreply@github.com"}


def ambiguous_coauthors(message):
    return sorted({email.casefold() for email in TRAILER.findall(message)
                   if email.casefold() in INVALID})


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True,
                          text=True, encoding="utf-8").stdout.strip()


def audit(event, payload):
    if event == "pull_request":
        old, new = payload["pull_request"]["base"]["sha"], "HEAD"
    elif event == "push":
        old, new = payload["before"], payload["after"]
        if old == "0" * 40:
            raise ValueError("Cannot verify a push without a previous commit")
    else:
        raise ValueError(f"Unsupported event {event}")
    commits = git("rev-list", "--no-merges", f"{old}..{new}").splitlines()
    violations = []
    for sha in commits:
        bad = ambiguous_coauthors(git("log", "-1", "--format=%B", sha))
        if bad:
            violations.append((sha[:12], bad))
    return violations, len(commits)


def main():
    event = os.environ["GITHUB_EVENT_NAME"]
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as f:
        payload = json.load(f)
    violations, checked = audit(event, payload)
    if violations:
        for sha, emails in violations:
            print(f"ERROR {sha}: ambiguous Co-authored-by: " + ", ".join(emails),
                  file=sys.stderr)
        print("Use a verified email address or the contributor's exact GitHub "
              "privacy email with numeric user ID.", file=sys.stderr)
        return 1
    print(f"PASS: {checked} introduced commit(s), no ambiguous co-authors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
