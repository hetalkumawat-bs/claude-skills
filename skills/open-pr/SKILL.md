---
name: open-pr
description: Open or update a GitHub pull request with a short, evidence-backed description built from the repo's own PR template, the branch's commit bodies, and real test/lint runs. Use when a branch is finished and needs a PR, when a PR has an empty or stale description, or when the user says "raise a PR" / "open a PR" / "fill the PR description". Labels failing checks pre-existing vs introduced.
---

# Open PR

## Core principle

**The commit bodies are the source material.** Summarise them; never invent a narrative they
don't support. If the commits are thin, say so and ask for the missing "why".

## 1. Preflight

```bash
git branch --show-current && git status --short
```

Stop if: not a git repo, on the default branch, or 0 commits ahead of base. Dirty tree → warn
that evidence may not match what's pushed, then continue.

## 2. Resolve the PR and the base ref

```bash
gh pr view --json number,baseRefName,url,body 2>/dev/null
git fetch --quiet origin
BASE_NAME=<baseRefName, else the user's argument, else origin's default branch, else main>
BASE=$(git rev-parse --verify --quiet "origin/$BASE_NAME" >/dev/null \
  && echo "origin/$BASE_NAME" || echo "$BASE_NAME")
```

Use `$BASE` (the remote ref) for every diff and test comparison — a local branch is often
stale. `$BASE_NAME` is only for `gh pr create --base`. Report `$BASE` in step 9, and mention it
if the local ref differs.

PR exists → **edit** it. No `gh` / no remote → compose anyway, deliver via clipboard.

## 3. Push

```bash
git rev-parse --abbrev-ref @{u} 2>/dev/null || git push -u origin "$(git branch --show-current)"
```

Never force-push. A failed push isn't fatal — report the error, still compose the body.

## 4. Gather facts

```bash
git log "$BASE"..HEAD --format='%n===%n%H%n%s%n%n%b'    # full bodies
git diff "$BASE"...HEAD --stat
git diff "$BASE"...HEAD --name-only | sort
```

If the file list spans apps this branch never touched, `$BASE` is wrong — fix it, don't report.

## 5. Find the template

First that exists: `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`,
`PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/*.md`. None → generic body (step 7).

## 6. Verify

Runner: `nx.json` → `npx nx affected -t lint typecheck test --base="$BASE" --head=HEAD`.
Else `package.json` scripts with the lockfile's package manager (check `command -v` first, else
`npx`). Neither → record "no runner detected", skip to 7.

**Run each target once, tee to a file, then grep the file. Never re-run to answer a follow-up.**

```bash
OUT=$(mktemp); npx nx affected -t lint typecheck test --base="$BASE" --head=HEAD \
  --skip-nx-cache 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | tee "$OUT" | tail -40

grep -E "Test Files|Tests |Failed tasks" "$OUT"
grep -E "^ *❯ " "$OUT" | awk '{print $2}' | grep -E "\.test\.[jt]sx?$" | sort -u
```

Don't anchor that filename pattern with `$` — vitest appends `(8 tests | 1 failed) 927ms`.

**Only if something failed**, check whether it's inherited — one run at the merge base, tee'd:

```bash
MB=$(git merge-base "$BASE" HEAD); WT=$(mktemp -d)/mb
git worktree add -q --detach "$WT" "$MB"
ln -s "$(git rev-parse --show-toplevel)/node_modules" "$WT/node_modules"
BASE_OUT=$(mktemp)
(cd "$WT" && npx nx run <project>:<target> --skip-nx-cache 2>&1 \
  | sed 's/\x1b\[[0-9;]*m//g' | tee "$BASE_OUT" | tail -20)
rm -f "$WT/node_modules" && git worktree remove --force "$WT"

extract() { grep -E "^ *❯ " "$1" | awk '{print $2}' | grep -E "\.test\.[jt]sx?$" | sort -u; }
comm -13 <(extract "$BASE_OUT") <(extract "$OUT")   # empty = no regressions from this branch
```

Symlink `node_modules` in (a fresh worktree has none) and remove the symlink before
`git worktree remove`. Compare SETS, not totals. Two suite runs per invocation, max.

## 7. Compose

Fill the template, else:

```markdown
## Summary
- <3–4 bullets from the commit bodies; root cause first>

## Changes
- `<app>` — <one line>

## Verification
- <runner> — <observed counts>

<!-- generated-by: open-pr -->
```

- **Delete non-applicable template sections** — never print one to mark it N/A.
- **45-line budget.** Over it: merge thin per-app sections into one list, fold the AC verdict
  into the last Summary bullet, combine Verification lines. Never drop a pre-existing-failure
  entry or an unticked-box reason.
- Summary ≤4 bullets. Changes: one line per app. Verification: real numbers only.
- Pre-existing failures: a short section only if some exist — target, file, merge-base evidence.
- Tick only what was verified this run; otherwise `- [ ]` with `— <reason>`.
- Scope checkboxes from changed top-level paths.
- AC table only if a ticket key is in the branch/commits AND the tracker is reachable.
- End with `<!-- generated-by: open-pr -->`.

Title: `type(scope): description`, <72 chars, matching `git log`'s convention.

## 8. Deliver

```bash
BODY=$(mktemp /tmp/pr-body-XXXX.md)
gh pr create --base "$BASE_NAME" --title "<title>" --body-file "$BODY"   # NAME, not $BASE
gh pr edit <number> --body-file "$BODY"                                  # existing PR
pbcopy < "$BODY"        # no gh: also print the path + pull/new/<branch> URL
```

A non-empty existing body **without** the marker is human-written — show it and ask first.

## 9. Report

PR URL, title, `$BASE` used, every unticked box and why, any pre-existing failure.

## Failure behaviour

| Condition | Behaviour |
| --- | --- |
| No `gh` / unauthenticated / no remote | Clipboard + path + `pull/new/<branch>`; never claim a PR was created |
| Push fails | Report the error, still compose |
| PR exists | Edit it (marker rule above) |
| No template | Generic body |
| No runner | "no runner detected" |
| Verification errors/times out | Body emitted, verification marked incomplete + cause |
| Dirty tree | Warn evidence may not match |
| Local base behind remote | Use `origin/<name>`, say so |
| Default branch / 0 commits ahead | Stop and explain |

## Never

- Tick an unverified checkbox, or state an unobserved test count.
- Overwrite a human-written description without asking.
- Invent AC verdicts or claim a tracker was consulted.
- Diff or run `nx affected` against a bare local branch when a remote ref exists.
- Re-run a suite for an answer the saved output already has.
- Force-push, amend commits, or write inside the repo tree.
