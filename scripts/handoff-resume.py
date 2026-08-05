#!/usr/bin/env python3
"""SessionStart hook: point a fresh session at an existing handoff document.

This is what makes switching accounts seamless -- open Claude in the repo and it
picks up from the handoff instead of starting cold.
"""
import json, os, subprocess, sys, time

def main() -> None:
    try:
        cwd = json.load(sys.stdin).get("cwd") or ""
    except Exception:
        return
    if not cwd:
        return

    try:
        root = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip() or cwd
    except Exception:
        root = cwd

    doc = os.path.join(root, "handoff", "HANDOFF-latest.md")
    if not os.path.isfile(doc):
        return

    try:
        age_days = int((time.time() - os.path.getmtime(doc)) // 86400)
    except Exception:
        age_days = 0

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": (
            f"A handoff document from a previous session exists at {doc} "
            f"(last written {age_days} day(s) ago). Read it before doing anything "
            "else and treat its \"Next steps\" as the starting point. If it looks "
            "stale or unrelated to what the user asks for, say so rather than "
            "following it blindly."
        )}}))

main()
