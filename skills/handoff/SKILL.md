---
name: handoff
description: Write a handoff document so a fresh session (or a different account) can continue this work without starting from scratch. Saves to handoff/ in the project root. Also invoked automatically when session usage crosses the configured threshold.
argument-hint: "[what the next session should focus on]"
---

# Handoff

Write a handoff document that lets a **fresh agent with no memory of this
conversation** continue the work. Assume the next session may run under a
different account, on a different machine, with no access to this transcript.

## Where to save it

Write to the **project root** of the current workspace:

- `handoff/HANDOFF-<YYYY-MM-DD-HHmm>.md` — the document
- `handoff/HANDOFF-latest.md` — a copy of the same content, always overwritten

Create the `handoff/` directory if it does not exist. Use the repository root
(the directory containing `.git`) rather than the current subdirectory. Never
write to a system temp directory — the doc must survive the session ending and
be readable by another account.

If the repo has a `.gitignore` and `handoff/` is not listed, mention to the user
that they can either commit the folder (so it travels between machines) or
ignore it (keep it local). Do not change `.gitignore` without asking.

## What to include

1. **Task** — what the user is trying to achieve, in their own framing.
2. **State** — what is done, what is in progress, what is untouched. Be specific
   about which parts are *verified* versus *assumed*.
3. **Key decisions and the reasons** — especially ones a fresh agent would
   otherwise re-litigate or accidentally reverse.
4. **Next steps** — concrete and ordered. First item should be immediately
   actionable.
5. **Do not redo** — things already tried that failed or were rejected, so the
   next session does not waste the budget repeating them.
6. **Environment** — branch, uncommitted work, running services (ports), how to
   start them, credentials the user must supply themselves.
7. **Suggested skills** — skills the next agent should invoke.

## What to leave out

- Anything already captured in commits, diffs, specs, plans, ADRs or issues —
  reference those by path, SHA or URL instead of restating them.
- Secrets. Redact API keys, passwords, tokens, connection strings and personal
  data. Name the variable, never the value.
- Narration of the conversation. Write the current state, not a chat log.

## Arguments

If the user passed arguments, treat them as the focus of the next session and
tailor the document to that. Otherwise cover the work in progress broadly.

## When invoked automatically

A `Stop` hook injects a request to run this skill once session usage crosses the
threshold (default 90%). In that case:

- Write the document immediately, before doing anything else.
- Keep it complete but economical — the remaining budget is small.
- End your turn by telling the user the path, their usage percentage, and that
  they can resume in a fresh session (or on another account) from that file.
