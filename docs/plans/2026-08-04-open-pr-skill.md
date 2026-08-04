# `open-pr` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a publicly installable Claude Code skill that opens a GitHub PR whose description is short, accurate, and backed by real test runs — filled from the repo's own PR template and the branch's commit bodies.

**Architecture:** A single instruction file (`skills/open-pr/SKILL.md`) read by the model at invocation time; no executable code. The repo doubles as a plugin marketplace via two small JSON manifests, so anyone can install it with `/plugin marketplace add`. Verification is by execution against two reference repos, not unit tests.

**Tech Stack:** Markdown + JSON manifests. Runtime dependencies at *use* time: `git`, `gh` (optional — clipboard fallback), and whatever test runner the target repo has.

## Global Constraints

- Skill directory name and frontmatter `name` are both `open-pr`.
- Marketplace name and plugin name are both `hetal-skills`; GitHub owner `hetalkumawat-bs`; repo `claude-skills`. Renaming touches only the two manifest files.
- Local checkout: `~/claude-skills`. Never commit any of this into `example-monorepo`.
- Generated PR bodies target **~30 lines**; non-applicable template sections are **deleted**, never printed as "N/A".
- Generated bodies always carry `<!-- generated-by: open-pr -->`.
- The skill must never tick an unverified checkbox, never state an unobserved test count, never force-push, never amend commits, and never write inside the target repo's tree.
- Commits in this repo use `hetalkumawat-bs` / `<your-git-email>` and carry **no** `Co-Authored-By: Claude` trailer.
- License: MIT.

---

### Task 1: Repo skeleton and plugin manifests

**Files:**
- Create: `~/claude-skills/.claude-plugin/marketplace.json`
- Create: `~/claude-skills/.claude-plugin/plugin.json`
- Create: `~/claude-skills/LICENSE`
- Create: `~/claude-skills/.gitignore`

**Interfaces:**
- Consumes: nothing (first task; the git repo and `docs/specs/` already exist from the design step).
- Produces: an installable marketplace whose single plugin `hetal-skills` exposes every directory under `skills/`. Task 2 places a skill there; Task 6 publishes it.

- [ ] **Step 1: Write the marketplace manifest**

```bash
cat > ~/claude-skills/.claude-plugin/marketplace.json <<'JSON'
{
  "name": "hetal-skills",
  "description": "Personal Claude Code skills: PR authoring, Jira handoff, review flow",
  "owner": {
    "name": "Hetal Kumawat"
  },
  "plugins": [
    {
      "name": "hetal-skills",
      "description": "Skills for shipping work: open a PR with an evidence-backed description, and related workflow helpers",
      "source": "."
    }
  ]
}
JSON
```

- [ ] **Step 2: Write the plugin manifest**

```bash
cat > ~/claude-skills/.claude-plugin/plugin.json <<'JSON'
{
  "name": "hetal-skills",
  "description": "Skills for shipping work: open a PR with an evidence-backed description, and related workflow helpers",
  "version": "0.1.0",
  "author": {
    "name": "Hetal Kumawat"
  },
  "repository": "https://github.com/hetalkumawat-bs/claude-skills",
  "license": "MIT",
  "keywords": ["pull-request", "github", "workflow", "gh-cli"]
}
JSON
```

- [ ] **Step 3: Add MIT LICENSE and .gitignore**

```bash
cat > ~/claude-skills/.gitignore <<'EOF'
.DS_Store
node_modules/
EOF

cat > ~/claude-skills/LICENSE <<'EOF'
MIT License

Copyright (c) 2026 Hetal Kumawat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

Verify:

```bash
head -3 ~/claude-skills/LICENSE
```

Expected: `MIT License`, a blank line, then `Copyright (c) 2026 Hetal Kumawat`.

- [ ] **Step 4: Verify both manifests are valid JSON with the expected keys**

```bash
cd ~/claude-skills
python3 -c "
import json
m = json.load(open('.claude-plugin/marketplace.json'))
p = json.load(open('.claude-plugin/plugin.json'))
assert m['name'] == 'hetal-skills', m['name']
assert m['plugins'][0]['source'] == '.', m['plugins'][0]
assert p['version'] == '0.1.0', p['version']
print('manifests OK')
"
```

Expected: `manifests OK`

- [ ] **Step 5: Commit**

```bash
cd ~/claude-skills
git add .claude-plugin LICENSE .gitignore
git -c user.name="hetalkumawat-bs" -c user.email="<your-git-email>" \
  commit -m "chore: plugin manifests, MIT license, gitignore"
```

---

### Task 2: Write `skills/open-pr/SKILL.md`

**Files:**
- Create: `~/claude-skills/skills/open-pr/SKILL.md`

**Interfaces:**
- Consumes: the marketplace from Task 1 (this directory is what the plugin exposes).
- Produces: the skill itself. Tasks 3–5 exercise and correct it; Task 6 publishes it. Frontmatter `name: open-pr` is the invocation name (`/open-pr`).

- [ ] **Step 1: Write the file**

Write `~/claude-skills/skills/open-pr/SKILL.md` with exactly this content:

````markdown
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
evidence gathered may not match what is pushed, and continue.

### 2. Resolve base branch and any existing PR

```bash
gh pr view --json number,baseRefName,url,body 2>/dev/null
```

- PR exists → note its number, use its `baseRefName` as base, and plan to **edit**.
- No PR → base is the user's argument, else the default branch:
  `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`), falling back to `main`.
- `gh` missing or unauthenticated → record that, keep going, and deliver via clipboard in
  step 8.

### 3. Push the branch if needed

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null \
  || git push -u origin "$(git branch --show-current)"
```

Never force-push.

### 4. Gather change facts

```bash
BASE=<resolved base>
git log "$BASE"..HEAD --format='%n===%n%H%n%s%n%n%b'   # full bodies — the source material
git diff "$BASE"...HEAD --stat
git diff "$BASE"...HEAD --name-only | sort
```

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
- Neither → record "no runner detected" and skip to step 7.

Run them. Capture real pass/fail counts — never estimate.

**For each FAILING target only**, establish whether it is inherited:

```bash
MB=$(git merge-base "$BASE" HEAD)
WT=$(mktemp -d)
git worktree add -q --detach "$WT" "$MB"
# re-run ONLY the failing target inside $WT, e.g.:
#   (cd "$WT" && npx nx run <project>:<target>)
git worktree remove --force "$WT"
```

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
gh pr create --base "$BASE" --title "<title>" --body-file "$BODY"

# existing PR, and its body is empty or carries the generated-by marker
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

State: the PR URL (or the paste-me URL), the title used, every checkbox left unticked and
why, and any failure classified as pre-existing.

## Failure behaviour

| Condition | Behaviour |
| --- | --- |
| `gh` absent or unauthenticated | Clipboard + printed path and `pull/new/<branch>` URL |
| PR already exists | Edit it, subject to the human-body rule in step 8 |
| No PR template | Compact generic body |
| No test/lint scripts | Body emitted; Verification says "no runner detected" |
| Verification errors or times out | Body emitted; Verification marked incomplete, cause named |
| Dirty working tree | Warn that evidence may not match the pushed commit |
| On default branch, or 0 commits ahead | Stop and explain; there is nothing to open |

## Never

- Tick a checkbox that was not verified in this run.
- State a test count that was not observed.
- Overwrite a human-written PR description without asking.
- Invent acceptance-criteria verdicts, or claim a tracker was consulted when it was not.
- Force-push, amend commits, or write inside the target repo's tree.
````

- [ ] **Step 2: Verify the frontmatter parses and the name matches the directory**

```bash
cd ~/claude-skills
python3 - <<'PY'
import re, pathlib
p = pathlib.Path('skills/open-pr/SKILL.md')
text = p.read_text()
m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
assert m, 'no frontmatter'
fm = m.group(1)
assert re.search(r'^name: open-pr$', fm, re.M), fm
assert 'description:' in fm
assert '<!-- generated-by: open-pr -->' in text
print('SKILL.md OK, frontmatter fields:', [l.split(':')[0] for l in fm.splitlines() if l.strip()])
PY
```

Expected: `SKILL.md OK, frontmatter fields: ['name', 'description']`

- [ ] **Step 3: Symlink into the personal skills dir so it is invocable**

```bash
mkdir -p ~/.claude/skills
ln -sfn ~/claude-skills/skills/open-pr ~/.claude/skills/open-pr
ls -l ~/.claude/skills/open-pr
```

Expected: a symlink pointing at `~/claude-skills/skills/open-pr`. The skill appears
in the available-skills list on the next session start.

- [ ] **Step 4: Commit**

```bash
cd ~/claude-skills
git add skills/open-pr/SKILL.md
git -c user.name="hetalkumawat-bs" -c user.email="<your-git-email>" \
  commit -m "feat: open-pr skill — PR with evidence-backed description"
```

---

### Task 3: Golden-reference run against the ACME-42 branch

**Files:**
- Modify: `~/claude-skills/skills/open-pr/SKILL.md` (only where the run exposes a gap)
- Create: `~/claude-skills/docs/examples/example-pr-body.md` (the generated output, kept as a reference)

**Interfaces:**
- Consumes: `SKILL.md` from Task 2.
- Produces: a corrected `SKILL.md` plus a recorded example that Task 5's README links to.

The reference target is `~/example-monorepo`, branch `feat/acme-42`
(base `main`). `gh` is not installed on this machine, so this run exercises the **clipboard
fallback**, not `gh pr create`.

A hand-written body for that branch exists in the originating session's scratchpad
(`acme-42-pr-body.md`), but **this task does not depend on it** — scratchpads are
session-scoped and may be gone. The four assertions in Step 2 are the complete pass criteria;
if the file happens to still be there, use it as a side-by-side sanity check only.

- [ ] **Step 1: Follow the skill's procedure manually against that branch, steps 1–7 only**

Do not deliver. Produce the body text and write it to
`~/claude-skills/docs/examples/example-pr-body.md`.

- [ ] **Step 2: Check it against the four things the hand-written body got right**

The generated body MUST contain, without being told:

1. The root cause — the route's `reviews.comment` capability passes but the service's
   project-**membership** check fails for Super Admin / Admin.
2. All three acceptance criteria, each marked met.
3. `src/lib/assets/large-asset.ts` lint error labelled **pre-existing**, with merge-base evidence.
4. The `ReviewDetail` author-name test failure labelled **pre-existing**.

```bash
cd ~/claude-skills
for needle in "assertOrgWideAccess" "large-asset.ts" "pre-existing" "submitter"; do
  grep -q "$needle" docs/examples/example-pr-body.md && echo "OK   $needle" || echo "MISS $needle"
done
wc -l docs/examples/example-pr-body.md
```

Expected: four `OK` lines, and a line count **under 45** (the hand-written body was ~120).

- [ ] **Step 3: Fix whichever instruction failed to produce those**

If a needle is missing, the fault is in `SKILL.md`, not the run. Typical fixes: step 4 does
not ask for full commit bodies; step 6's merge-base rule is not explicit enough about
re-running only the failing target; step 7 does not require a pre-existing-failures section.
Edit the instruction, then redo Steps 1–2.

- [ ] **Step 4: Confirm the length rule actually fired**

```bash
grep -c "N/A" ~/claude-skills/docs/examples/example-pr-body.md
```

Expected: `0`. Any "N/A" means non-applicable sections were printed instead of deleted.

- [ ] **Step 5: Commit**

```bash
cd ~/claude-skills
git add docs/examples/example-pr-body.md skills/open-pr/SKILL.md
git -c user.name="hetalkumawat-bs" -c user.email="<your-git-email>" \
  commit -m "test: golden-reference body for ACME-42, with instruction fixes"
```

---

### Task 4: Fallback and idempotence runs

**Files:**
- Modify: `~/claude-skills/skills/open-pr/SKILL.md` (only where a run exposes a gap)

**Interfaces:**
- Consumes: `SKILL.md` as corrected by Task 3.
- Produces: a `SKILL.md` proven to degrade gracefully. Task 5 documents the results.

- [ ] **Step 1: Build a throwaway repo with no template and no runner**

```bash
TMP=$(mktemp -d)
cd "$TMP" && git init -q -b main
printf 'hello\n' > README.md
git add -A && git -c user.name=t -c user.email=t@t commit -q -m "chore: init"
git checkout -q -b feat/thing
printf 'world\n' >> README.md
git add -A && git -c user.name=t -c user.email=t@t commit -q -m "feat: add world

Adds a second line so the diff is non-empty."
echo "$TMP"
```

- [ ] **Step 2: Run the skill's steps 1–7 there and assert graceful degradation**

The body must: use the generic shape (no checkboxes), say **"no runner detected"** under
Verification, invent no counts, and still carry the marker. There is no remote, so step 3's
push will fail — the skill must report that and continue to produce a body rather than
aborting.

If it aborts or fabricates a count, fix `SKILL.md` step 6 / step 8 and redo.

- [ ] **Step 3: Verify the no-`gh` path names the fallback correctly**

`gh` is genuinely absent on this machine, so this is the natural path. Confirm the report
prints a `pull/new/<branch>`-style URL and the temp file path, and does not claim a PR was
created.

- [ ] **Step 4: Idempotence — marker present**

Take the body from Task 3, confirm it ends with `<!-- generated-by: open-pr -->`, and confirm
the instruction in step 8 treats that as safe to replace. Re-generating must produce one body,
not an appended duplicate.

- [ ] **Step 5: Idempotence — marker absent (the dangerous case)**

Simulate a human-written description: take the Task 3 body, strip the marker line, and treat
it as an existing PR body. The skill MUST show it and ask before replacing. If the
instruction lets it overwrite silently, that is a defect — fix step 8's wording so the
human-body check precedes the edit.

- [ ] **Step 6: Clean up and commit any instruction fixes**

```bash
rm -rf "$TMP"
cd ~/claude-skills
git add skills/open-pr/SKILL.md
git -c user.name="hetalkumawat-bs" -c user.email="<your-git-email>" \
  commit -m "fix: harden open-pr fallbacks — no runner, no gh, human-written body" || echo "no fixes needed"
```

---

### Task 5: README with worked examples

**Files:**
- Create: `~/claude-skills/README.md`

**Interfaces:**
- Consumes: the example body from Task 3 and the findings from Task 4.
- Produces: the install instructions a stranger needs. Task 6 publishes it.

- [ ] **Step 1: Write the README**

It must contain, in this order:

1. One-paragraph what-and-why.
2. Install for others:
   ```
   /plugin marketplace add hetalkumawat-bs/claude-skills
   /plugin install hetal-skills@hetal-skills
   ```
3. Local development via symlink (`ln -sfn .../skills/open-pr ~/.claude/skills/open-pr`),
   and why a symlink beats installing your own plugin.
4. Skill index: `open-pr` with its one-line description.
5. **Worked example** — link `docs/examples/example-pr-body.md`, stating that it was generated
   from a real branch, is under 45 lines against a 120-line hand-written original, and
   classified two inherited failures unprompted.
6. Requirements: `git`; `gh` optional (clipboard fallback); works with or without a PR
   template; Nx and plain npm/pnpm/yarn runners detected.
7. MIT license line.

- [ ] **Step 2: Verify every claim in the README is true**

```bash
cd ~/claude-skills
test -f docs/examples/example-pr-body.md && echo "example exists"
wc -l < docs/examples/example-pr-body.md          # must match the number the README states
grep -o "hetal-skills@hetal-skills" README.md   # must match marketplace.json + plugin.json
```

Fix the README rather than the facts.

- [ ] **Step 3: Commit**

```bash
cd ~/claude-skills
git add README.md
git -c user.name="hetalkumawat-bs" -c user.email="<your-git-email>" \
  commit -m "docs: README with install instructions and worked example"
```

---

### Task 6: Publish and verify installability

**Files:**
- No new files; remote configuration only.

**Interfaces:**
- Consumes: everything from Tasks 1–5.
- Produces: a public repo that `/plugin marketplace add` resolves.

- [ ] **Step 1: User action — create the empty GitHub repo**

`gh` is not installed, so this step is manual. Ask the user to create
`https://github.com/new` → name `claude-skills`, **public**, no README/license/gitignore
(the repo already has them). Alternatively they may install `gh` first
(`! brew install gh` then `! gh auth login`), which also unlocks the skill's primary
delivery path — recommend it.

- [ ] **Step 2: Add the remote and push**

```bash
cd ~/claude-skills
git remote add origin git@github.com:hetalkumawat-bs/claude-skills.git
git push -u origin main
```

- [ ] **Step 3: Verify the marketplace resolves**

In a Claude Code session:

```
/plugin marketplace add hetalkumawat-bs/claude-skills
/plugin install hetal-skills@hetal-skills
```

Expected: the marketplace registers and `open-pr` appears in the skills list. If it does not,
inspect `~/.claude/plugins/known_marketplaces.json` and re-check `marketplace.json` against a
working example at `~/.claude/plugins/marketplaces/claude-plugins-official/.claude-plugin/marketplace.json`.

- [ ] **Step 4: End-to-end run with `gh` present (only if the user installed it)**

Run `/open-pr` on `example-monorepo`'s `feat/acme-42` branch. Expected: a real PR against
`main`, description under 45 lines, both inherited failures labelled pre-existing. This is the
first time the `gh pr create` path executes; until now only the clipboard path has been
exercised.

- [ ] **Step 5: Tag the release**

```bash
cd ~/claude-skills
git tag -a v0.1.0 -m "open-pr skill"
git push origin v0.1.0
```

---

## Deferred

`jira-handoff` — the same evidence pass would also produce the tracker's "dev complete"
comment, which was ~90% duplicate prose on ACME-42. Out of scope here by decision in the
spec; build it once `open-pr` has earned its keep.
