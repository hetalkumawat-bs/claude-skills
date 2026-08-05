# handoff

Writes a handoff document so a fresh session — or a **different account** — can
continue your work instead of starting from scratch. Runs on demand, and
automatically when session usage crosses a threshold.

## Why it triggers at 90%, not at the limit

Once you hit the usage limit the model has no capacity left, so it cannot write
a handoff at that point. The document has to be produced *before* the ceiling.
This plugin fires at 90% by default, leaving ~10% to write it.

## How it reads your usage

Claude Code hooks receive `session_id`, `transcript_path`, `cwd` … but **no**
usage data. The **status line** does receive it — `rate_limits.five_hour.
used_percentage` is the same figure `/usage` reports.

So the plugin splits the job:

| Piece | Role |
|---|---|
| `scripts/usage-sensor.py` | status line; also records usage to `~/.claude/handoff/usage-state.json` |
| `scripts/handoff-guard.py` | `Stop` hook; reads that file, and past the threshold asks Claude to run `handoff` |
| `scripts/handoff-resume.py` | `SessionStart` hook; points a new session at an existing handoff |
| `scripts/handoff-gitignore.py` | `PostToolUse` hook; adds `handoff/` to `.gitignore` the first time a handoff file is written |

## Setup

The hooks install with the plugin. The sensor must be wired up as your status
line, otherwise there is no usage signal and the automatic trigger stays silent:

```json
{
  "statusLine": {
    "type": "command",
    "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/usage-sensor.py"
  }
}
```

Already have a status line? Call this one from yours, or copy its ~15 lines of
sensing into your script — the only thing that matters is that it writes
`usage-state.json`.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `HANDOFF_USAGE_THRESHOLD` | `90` | percent at which the handoff is requested |
| `HANDOFF_STATE_DIR` | `~/.claude/handoff` | where usage state and dedupe markers live |
| `HANDOFF_DISABLE` | unset | `1` disables the automatic nudge (`/handoff` still works) |

## Behaviour

- Fires **once per rate-limit window** per session — no nagging every turn.
  `resets_at` changing rolls the dedupe marker over, so the next window nudges
  again.
- Uses the **higher** of the 5-hour and 7-day windows.
- Writes to `<repo root>/handoff/`: `HANDOFF-<timestamp>.md` plus a stable
  `HANDOFF-latest.md`. Project root, never a temp dir — it has to survive the
  session and be readable by the other account.
- Degrades quietly: no status line, a free account (`rate_limits` absent), or
  malformed input all mean "no nudge" rather than a wrong nudge.

## Resuming on another account

Open Claude Code in the same repo. The `SessionStart` hook spots
`handoff/HANDOFF-latest.md` and tells the session to read it first, so you can
just carry on. Nothing to type.

## .gitignore

`handoff/` is added to the repo's `.gitignore` automatically — but only when a
handoff file is actually written there, so repos where you never use the skill
are left alone. The check is idempotent and recognises existing patterns
(`handoff/`, `handoff/*`, `/handoff`), so it never appends a duplicate. Non-git
directories are skipped entirely.

That keeps the document local to the machine. If you want it to travel between
*machines* rather than just between accounts, commit the folder instead — remove
the entry and `git add handoff/`.

## Requirements

`python3` (no `jq` dependency — it is commonly absent).
