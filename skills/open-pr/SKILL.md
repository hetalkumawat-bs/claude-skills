---
name: open-pr
description: Open a GitHub pull request with a short, evidence-backed description built from the repo's own PR template, the branch's commit bodies, and real test/lint runs. Use when work on a branch is finished and needs a PR, when a PR exists with an empty or stale description, or when the user says "raise a PR" / "open a PR" / "fill the PR description". Classifies failing checks as pre-existing vs introduced so reviewers do not chase inherited red.
---

# Open PR

Turn a finished branch into a pull request whose description a reviewer can trust, without
re-typing what the commits already say.

## Core principle

**The commit bodies are the source material.** Summarise them; never invent a narrative the
commits do not support. If the commits are thin, say so and ask the user for the missing
"why" rather than filling the gap with plausible prose.

## Procedure

### 1. Preflight

```bash
git rev-parse --is-inside-work-tree
git branch --show-current
git status --short
```

Stop and explain if: not a git repo; the current branch is the default branch; or there are
zero commits ahead of base (nothing to open). If the working tree is dirty, warn that the
evidence gathered may not match what is pushed, then continue.

### 2. Resolve base branch and any existing PR

```bash
gh pr view --json number,baseRefName,url,body 2>/dev/null
```

- PR exists → note its number, take its `baseRefName` as the base *branch name*, and plan to
  **edit**.
- No PR → the base branch name is the user's argument, else the default branch:
  `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`), falling back to `main`.
- `gh` missing or unauthenticated → record that, keep going, and deliver via clipboard in
  step 8.
- **`no git remotes found`** → there is nowhere to open a PR. Do not abort: compose the body
  anyway, deliver it to the clipboard in step 8, and tell the user to add a remote and push
  first. Never report a PR as created.

**Then turn that branch NAME into the ref you will actually diff against — never use the bare
local branch.** A local `main` is frequently weeks behind `origin/main`, and diffing against it
silently pulls in every commit merged since, plus every project those files belong to:

```bash
git fetch --quiet origin                                  # skip when there is no remote
BASE_NAME=<baseRefName from above>                        # e.g. main
BASE=$(git rev-parse --verify --quiet "origin/$BASE_NAME" >/dev/null \
  && echo "origin/$BASE_NAME" || echo "$BASE_NAME")       # remote ref wins; local is the fallback
```

Use `$BASE` for every later step — the diff in step 4, `nx affected --base=` in step 6, and
the merge base in step 6's classification. **Report it in step 9** so the reviewer knows what
the numbers were measured against.

Why this matters: on a stale local `main`, `git diff main...HEAD` returned 93 files belonging
to another team's app, so `nx affected` ran that app's targets and failed on dependencies this
branch never touched — failures that are neither the branch's fault nor pre-existing in any
meaningful sense. If the two refs differ, say so in the report; a stale local `main` is worth
the user knowing about (`git fetch && git branch -f <name> origin/<name>`).

### 3. Push the branch if needed

```bash
git remote 2>/dev/null | head -1                       # empty → skip this step entirely
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null \
  || git push -u origin "$(git branch --show-current)"
```

Never force-push. **A failed push is not fatal to this skill** — if the push errors (no
remote, no permission, protected branch), report the exact error and carry on to compose the
body; the user still gets usable text. Only the delivery step changes, never the composition.

### 4. Gather change facts

`$BASE` is the ref resolved in step 2 (`origin/<name>` whenever that exists), not the bare
branch name.

```bash
git log "$BASE"..HEAD --format='%n===%n%H%n%s%n%n%b'   # full bodies — the source material
git diff "$BASE"...HEAD --stat
git diff "$BASE"...HEAD --name-only | sort
```

Sanity-check the file list before going further: every path should plausibly belong to this
branch's work. A diff spanning apps the branch never touched means `$BASE` is wrong — go back
to step 2 rather than reporting on someone else's changes.

### 5. Locate the PR template

Check in order, take the first that exists:

1. `.github/pull_request_template.md`
2. `.github/PULL_REQUEST_TEMPLATE.md`
3. `PULL_REQUEST_TEMPLATE.md`
4. `.github/PULL_REQUEST_TEMPLATE/*.md` (if several, ask which)

None found → use the generic body in step 7.

### 6. Detect the runner and verify

Detect:

- `nx.json` present → `npx nx affected -t lint typecheck test --base="$BASE" --head=HEAD`
- else read `package.json` `scripts` and run whichever of `lint`, `typecheck`, `test` exist,
  with the package manager from the lockfile (`pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn,
  `package-lock.json` → npm). Confirm the binary exists (`command -v yarn`) before using it;
  fall back to `npx`.
- Neither → record "no runner detected" and go to step 7.

Run them. Capture real pass/fail counts — never estimate.

**For each FAILING target only**, establish whether it is inherited:

```bash
MB=$(git merge-base "$BASE" HEAD)
WT=$(mktemp -d)/mb
git worktree add -q --detach "$WT" "$MB"
ln -s "$(git rev-parse --show-toplevel)/node_modules" "$WT/node_modules"   # see note
# re-run ONLY the failing target inside $WT, adding --skip-nx-cache so a cached
# green result from the branch cannot be served here, e.g.:
#   (cd "$WT" && npx nx run <project>:<target> --skip-nx-cache)
rm -f "$WT/node_modules" && git worktree remove --force "$WT"
```

**A fresh worktree has no `node_modules`, so the runner will not start.** Symlink the main
checkout's `node_modules` in (as above) and remove the symlink before
`git worktree remove`, or the remove will try to delete the real directory. For
non-JS ecosystems, do the equivalent for that toolchain's dependency directory.

Fails at merge base too → **pre-existing**. Passes there → **introduced by this branch**.
Skip this entirely when everything is green. Never run it inside the user's working tree.

### 7. Compose the body

Fill the template if one was found; otherwise use:

```markdown
## Summary
- <3–4 bullets from the commit bodies; root cause first when stated>

## Changes
- `<app-or-package>` — <one line>

## Verification
- <runner> — <observed counts>

<!-- generated-by: open-pr -->
```

Rules that keep it short and honest:

- **Delete every non-applicable template section.** Do not print a section in order to mark
  it N/A. This is the single biggest length saving.
- **Budget: 45 lines.** Count them before delivering (`wc -l`). Over budget, compact in this
  order: merge per-app sections into one "Per-app checks" list when each has fewer than three
  items; fold the acceptance-criteria verdict into the last Summary bullet instead of giving
  it its own heading; combine the Verification lines. Never hit the budget by dropping a
  pre-existing-failure entry or an unticked-box reason — those are the load-bearing parts.
- Summary: 4 bullets maximum. Longer belongs in the commit message.
- Changes: one line per app or package. The diff already lists files.
- Verification: one line, real numbers.
- **Pre-existing failures**: include a short section ONLY if some exist, naming the target,
  the file, and the merge-base evidence.
- **Checkboxes**: tick only what was verified in this run. Anything else stays `- [ ]` with a
  trailing `— <reason>`. Ticking an unchecked box makes the whole checklist worthless.
- Scope checkboxes map from changed top-level paths (e.g. `apps/api/**` → the
  backend-api box).
- Acceptance criteria: include an AC table only if a ticket key appears in the branch name or
  commits AND the tracker is reachable. Otherwise omit silently — never invent verdicts.
- Always end with `<!-- generated-by: open-pr -->`.

Title: `type(scope): description`, under 72 characters, matching the convention visible in
`git log`.

### 8. Deliver

Write the body to a temp file outside the repo:

```bash
BODY=$(mktemp /tmp/pr-body-XXXX.md)
```

Then, in order of availability:

```bash
# no existing PR
# NOTE: --base takes the branch NAME ($BASE_NAME from step 2), never the ref ($BASE).
# `gh pr create --base origin/main` fails: there is no branch called "origin/main".
gh pr create --base "$BASE_NAME" --title "<title>" --body-file "$BODY"

# existing PR whose body is empty or carries the generated-by marker
gh pr edit <number> --body-file "$BODY"
```

**If an existing body is non-empty and has no `generated-by: open-pr` marker, it was written
by a human.** Show it to the user and ask before replacing it.

No `gh`, or not authenticated:

```bash
pbcopy < "$BODY"     # macOS; xclip -selection clipboard on Linux; clip.exe on Windows
```

then print the file path and
`https://github.com/<owner>/<repo>/pull/new/<branch>` so the user can paste it.

### 9. Report

State: the PR URL (or the paste-me URL), the title used, **which ref the evidence was measured
against** (`$BASE`), every checkbox left unticked and why, and any failure classified as
pre-existing. If the local branch of the same name was behind the remote, mention it — the user
is probably running stale `nx affected` commands too.

## Failure behaviour

| Condition | Behaviour |
| --- | --- |
| `gh` absent or unauthenticated | Clipboard + printed path and `pull/new/<branch>` URL |
| No git remote configured | Body to clipboard; tell the user to add a remote and push. Never claim a PR was created |
| Push rejected or fails | Report the exact error, still compose and deliver the body |
| PR already exists | Edit it, subject to the human-body rule in step 8 |
| No PR template | Compact generic body |
| No test/lint scripts | Body emitted; Verification says "no runner detected" |
| Verification errors or times out | Body emitted; Verification marked incomplete, cause named |
| Dirty working tree | Warn that evidence may not match the pushed commit |
| Local base branch behind the remote | Diff against `origin/<name>`; say so in the report |
| On default branch, or 0 commits ahead | Stop and explain; there is nothing to open |

## Never

- Tick a checkbox that was not verified in this run.
- State a test count that was not observed.
- Overwrite a human-written PR description without asking.
- Invent acceptance-criteria verdicts, or claim a tracker was consulted when it was not.
- Measure the diff or `nx affected` against a bare local branch when a remote-tracking ref for
  it exists. A stale local base attributes other people's failures to this branch.
- Force-push, amend commits, or write inside the target repo's tree.
