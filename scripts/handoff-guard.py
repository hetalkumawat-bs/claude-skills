#!/usr/bin/env python3
"""Stop hook: trigger the handoff skill *before* the usage limit is exhausted.

Reads the percentages recorded by scripts/usage-sensor.py (the status line) and,
once usage crosses the threshold, asks Claude to run the `handoff` skill while
budget still remains. Waiting for the limit to be hit would be useless: at that
point the model has no capacity left to write anything.

Fires at most once per rate-limit window so it does not nag every turn.

Env:
  HANDOFF_USAGE_THRESHOLD  percent, default 90
  HANDOFF_STATE_DIR        default ~/.claude/handoff
  HANDOFF_DISABLE=1        turn the nudge off
"""
import json, os, sys

def main() -> None:
    if os.environ.get("HANDOFF_DISABLE") == "1":
        return

    try:
        threshold = float(os.environ.get("HANDOFF_USAGE_THRESHOLD", "90"))
    except ValueError:
        threshold = 90.0

    state_dir = os.environ.get("HANDOFF_STATE_DIR") or os.path.expanduser("~/.claude/handoff")
    state_file = os.path.join(state_dir, "usage-state.json")

    try:
        session = json.load(sys.stdin).get("session_id") or "unknown"
    except Exception:
        session = "unknown"

    # No sensor data (status line not configured, or not a Pro/Max account) ->
    # stay silent rather than guess at usage.
    try:
        with open(state_file) as fh:
            state = json.load(fh)
    except Exception:
        return

    def as_pct(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    five, seven = as_pct(state.get("five_hour")), as_pct(state.get("seven_day"))
    candidates = [(p, name) for p, name in ((five, "5-hour"), (seven, "7-day")) if p is not None]
    if not candidates:
        return

    pct, window = max(candidates)
    if pct < threshold:
        return

    # Once per window per session. resets_at changes when the window rolls over,
    # so the nudge returns for the next window.
    marker = os.path.join(state_dir, f"nudged-{session}-{state.get('resets_at') or 0}")
    if os.path.exists(marker):
        return
    try:
        os.makedirs(state_dir, exist_ok=True)
        open(marker, "w").close()
    except Exception:
        return  # can't dedupe -> better silent than nagging every turn

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "Stop",
        "additionalContext": (
            f"USAGE ALERT: the {window} limit is at {pct:.0f}% (threshold {threshold:.0f}%). "
            "Before doing anything else, invoke the `handoff` skill to write "
            "handoff/HANDOFF-latest.md in the project root, so this work can be "
            "continued in a fresh session or under a different account. Keep it "
            "complete but economical -- little budget remains. Then end your turn "
            "and tell the user the file path and their usage percentage."
        )}}))

main()
