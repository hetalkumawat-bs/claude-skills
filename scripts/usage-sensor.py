#!/usr/bin/env python3
"""Status line AND usage sensor.

Hooks receive no usage data, but the status line does: `rate_limits` here is the
same data `/usage` reports. So this script does double duty -- it prints a status
line, and records the usage percentages to a state file that the Stop hook
(handoff-guard.py) reads to decide when to trigger a handoff.

Configure in settings.json:
  "statusLine": {"type": "command",
                 "command": "\\"${CLAUDE_PLUGIN_ROOT}\\"/scripts/usage-sensor.py"}

Deliberately never raises: a crashing status line would break the display, and a
missing sensor value must degrade to "no nudge" rather than a wrong nudge.
"""
import json, os, sys, time, tempfile

def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("")
        return

    def dig(*path, default=None):
        cur = data
        for key in path:
            if not isinstance(cur, dict):
                return default
            cur = cur.get(key)
        return cur if cur is not None else default

    # rate_limits exists only for Pro/Max accounts, and only after the first API
    # response of the session. Absent -> record empty, never fabricate a number.
    five = dig("rate_limits", "five_hour", "used_percentage", default="")
    seven = dig("rate_limits", "seven_day", "used_percentage", default="")
    resets = dig("rate_limits", "five_hour", "resets_at", default="")
    ctx = dig("context_window", "used_percentage", default="")
    model = dig("model", "display_name", default="claude")
    cwd = dig("workspace", "current_dir", default=None) or dig("cwd", default="") or ""

    state_dir = os.environ.get("HANDOFF_STATE_DIR") or os.path.expanduser("~/.claude/handoff")
    try:
        os.makedirs(state_dir, exist_ok=True)
        payload = {
            "five_hour": five, "seven_day": seven, "resets_at": resets,
            "context": ctx, "recorded_at": int(time.time()),
        }
        # Atomic write so a concurrent hook read never sees a partial file.
        fd, tmp = tempfile.mkstemp(dir=state_dir)
        with os.fdopen(fd, "w") as fh:
            json.dump(payload, fh)
        os.replace(tmp, os.path.join(state_dir, "usage-state.json"))
    except Exception:
        pass  # sensing is best-effort; the status line must still render

    def pct(v):
        try:
            return f"{float(v):.0f}"
        except (TypeError, ValueError):
            return None

    parts = [f"[{model}]"]
    if cwd:
        parts.append(os.path.basename(cwd.rstrip("/")) or cwd)
    if pct(ctx):
        parts.append(f"{pct(ctx)}% ctx")
    if pct(five):
        parts.append(f"5h {pct(five)}%")
    if pct(seven):
        parts.append(f"7d {pct(seven)}%")
    print(" | ".join(parts))

main()
