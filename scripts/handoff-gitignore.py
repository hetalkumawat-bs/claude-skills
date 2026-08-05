#!/usr/bin/env python3
"""PostToolUse hook: keep handoff/ out of git, automatically.

Fires after every Write/Edit but does nothing unless the file just written lives
under <repo root>/handoff/. That way the entry appears the first time a handoff
document is actually created, and repos where you never use the skill are left
completely untouched.

Idempotent: recognises handoff/, handoff/*, /handoff and bare handoff as already
covering it, so it never appends a duplicate.
"""
import json, os, subprocess, sys

# Patterns that already ignore the folder — don't add another line if any exist.
EQUIVALENT = {"handoff", "handoff/", "handoff/*", "/handoff", "/handoff/", "/handoff/*"}
BLOCK = "\n# Session handoff documents (written by the `handoff` skill)\nhandoff/\n"

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    path = (payload.get("tool_input") or {}).get("file_path") or ""
    cwd = payload.get("cwd") or ""
    if not path:
        return

    try:
        root = subprocess.run(
            ["git", "-C", cwd or os.path.dirname(path) or ".", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        return
    if not root:
        return  # not a git repo -> nothing to ignore

    # Only act on files inside <root>/handoff/
    handoff_dir = os.path.join(os.path.realpath(root), "handoff") + os.sep
    if not os.path.realpath(path).startswith(handoff_dir):
        return

    gitignore = os.path.join(root, ".gitignore")
    try:
        existing = ""
        if os.path.exists(gitignore):
            with open(gitignore) as fh:
                existing = fh.read()
            for line in existing.splitlines():
                if line.strip().split("#")[0].strip() in EQUIVALENT:
                    return  # already ignored
        with open(gitignore, "a") as fh:
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            fh.write(BLOCK)
    except Exception:
        return

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            "Added `handoff/` to .gitignore so handoff documents stay local. "
            "Mention this to the user, and note that if they want the document to "
            "travel between machines (not just between accounts on this one) they "
            "should commit the folder instead."
        )}}))

main()
