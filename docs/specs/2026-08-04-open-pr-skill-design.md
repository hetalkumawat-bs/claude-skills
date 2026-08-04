# Design — `open-pr` skill

*(Named `open-pr`, not `pr-description`: it opens the PR as well as writing its body.)*

**Date:** 2026-08-04
**Status:** approved, pending implementation plan

## Problem

Opening a PR means re-writing information that already exists. The commit bodies in this
team's repos are already essays — root cause, per-app fix, test notes — and the PR
description restates them by hand. On top of that, the repo's
`.github/pull_request_template.md` is 98 lines of checklist, so a filled-in body is mostly
padding: every non-applicable section printed with a "🚫 N/A" tick.

Two costs, observed on ACME-42:

1. The same prose was written three times — commit message, PR body, Jira comment.
2. Proving that a red lint check and a failing test were **pre-existing** (not introduced by
   the branch) took a manual hunt through `git show <parent>:<path>`.

## Goal

One skill that, from a branch with commits, opens a PR whose description is short, accurate,
and evidence-backed — and that works in repos neither the author nor the model has seen
before.

## Non-goals

- Posting the Jira "dev complete" comment. Same evidence pass would feed it, but that is a
  separate skill (`jira-handoff`) to be built only after this one earns its keep.
- Reviewing the code. This skill reports; it does not judge.
- Replacing project-local PR commands (e.g. a project's own PR command).

## Distribution

Public repo, installable by anyone:

```
claude-skills/
├── .claude-plugin/
│   ├── marketplace.json          # name, owner, plugins[] — makes the repo installable
│   └── plugin.json               # identity + version
├── docs/specs/                   # design docs (this file)
├── skills/
│   └── open-pr/SKILL.md
├── README.md
└── LICENSE                       # MIT
```

Consumers run:

```
/plugin marketplace add hetalkumawat-bs/claude-skills
/plugin install hetal-skills@hetal-skills
```

Marketplace name, plugin name and GitHub owner are all `hetal-skills` /
`hetalkumawat-bs` by default; renaming means editing the two manifest files and nothing
else. Local checkout lives at `~/claude-skills`.

Author's dev loop uses a symlink instead of an install, so edits take effect with no
reinstall:

```bash
ln -s ~/claude-skills/skills/open-pr ~/.claude/skills/open-pr
```

## Behaviour

### Inputs

Optional: target base branch (default: the repository's default branch). No other arguments.
Everything else is derived.

### Procedure

1. **Preflight.** Confirm a git repo, a current branch that is not the default branch, and
   at least one commit ahead of base. Push the branch if it has no upstream.
2. **Resolve base and existing PR.** `gh pr view --json number,baseRefName,url` for the
   current branch. If a PR exists, its `baseRefName` is authoritative and the skill will
   **edit** rather than create. If not, base is the argument or the default branch.
3. **Gather change facts.** `git log <base>..HEAD` with **full commit bodies** (the primary
   source material — the summary is a reformat of these, never freshly invented),
   `git diff <base>...HEAD --stat`, and `--name-only`.
4. **Locate the template.** In order: `.github/pull_request_template.md`,
   `PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/*.md`. None found → the
   compact generic body (Summary / Changes / Verification / Notes).
5. **Detect the runner.** `nx.json` → `nx affected -t lint typecheck test --base=<base>`.
   Otherwise `package.json` scripts, with the package manager inferred from the lockfile
   (`pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, else npm). Verify the binary exists before
   using it; fall back to `npx`.
6. **Verify.** Run the detected targets. For **failing targets only**, re-run that one
   target at `git merge-base <base> HEAD` inside a throwaway `git worktree`, then label each
   failure **pre-existing** or **introduced**. Green branches skip this step entirely.
7. **Compose the body** (see Output shape).
8. **Deliver.** Write the body to a temp file outside the repo tree. Then
   `gh pr create --base <base> --title <title> --body-file <file>`, or
   `gh pr edit <n> --body-file <file>` when a PR already exists. No `gh` on the machine →
   copy to the clipboard (`pbcopy` / `xclip` / `clip.exe`), print the file path and the
   `pull/new/<branch>` URL.
9. **Report.** PR URL, the title used, which checkboxes were left unticked and why, and any
   failure classified as pre-existing.

### Output shape

Target: about 30 lines for a normal change. Ordered as:

- **Summary** — 3–4 bullets, derived from commit bodies. States the root cause when the
  commits do.
- **Changes** — one line per app or package, not per file.
- **Verification** — one line with real observed counts.
- **Pre-existing failures** — only when some exist; names the target, the file, and the
  evidence that it predates the branch.
- **Template checklist** — ticks mapped from changed paths and verified runs.

Length control, in priority order:

1. **Delete non-applicable template sections entirely.** Do not print a section only to mark
   it N/A. This is the single biggest reduction (~60 lines on the reference repo).
2. Cap Summary at 4 bullets; move anything longer into the commit message where it belongs.
3. Group Changes by app; never list every file — the diff already does that.

Title format: `type(scope): description`, under 72 characters, matching the repo's commit
convention when one is evident from `git log`.

### Hard rules

- **Never tick a checkbox not verified in this run.** Leave it unticked with a short reason.
  A ticked box that was never checked makes the whole checklist worthless.
- **Never state a test count that was not observed.** No estimates, no "should pass".
- **Never overwrite a human-written description.** Every generated body carries
  `<!-- generated-by: open-pr -->`. On re-run, that marker means safe to replace; a
  body without it is shown to the user and confirmed before any edit.
- **Never invent acceptance-criteria verdicts.** Include an AC table only when a ticket key
  is present in the branch or commits AND the tracker is reachable. Otherwise omit silently.
- **Never** force-push, amend commits, or write inside the repo tree. Merge-base runs use a
  separate worktree, removed afterwards.

### Failure behaviour

Every dead end degrades rather than blocks:

| Condition | Behaviour |
| --- | --- |
| `gh` absent | Clipboard + printed path and `pull/new/<branch>` URL |
| Not authenticated to `gh` | Same as absent, plus a note to run `gh auth login` |
| PR already exists | Edit it (subject to the marker rule) |
| No PR template | Compact generic body |
| No test/lint scripts detected | Body emitted, Verification says "no runner detected" |
| Verification fails to run or times out | Body emitted, Verification marked incomplete, cause named |
| Dirty working tree | Warn that evidence may not match the pushed commit |
| Branch is the default branch, or 0 commits ahead | Stop with an explanation; nothing to open |

## Testing

Skills cannot be unit tested; verification is by execution against known references.

1. **Golden reference.** Run against the `feat/acme-42` PR in `example-monorepo`, whose
   description was written by hand. The generated body must capture the same substance —
   root cause, the three acceptance criteria, both pre-existing failures with their
   evidence — in materially fewer lines. Specifically, it must classify
   `src/lib/assets/large-asset.ts` lint and the `ReviewDetail` author-name test as
   pre-existing without being told.
2. **Fallback path.** Run in a non-Nx repo with no PR template and no `gh` installed:
   expect the compact generic body on the clipboard, no crash, no invented counts.
3. **Idempotence.** Re-run on the same PR: body replaced cleanly, no duplication. Then
   hand-edit the description, strip the marker, re-run: the skill must ask before
   overwriting.

Both passing runs are recorded in the README as worked examples.

## Open questions

None. Decisions settled during design: template-aware compact body (not a fixed body);
`gh` as the delivery mechanism with clipboard fallback; verification always runs, with
merge-base comparison only for failing targets; single instruction file, with `references/`
extracted later only if repetition proves it necessary.
