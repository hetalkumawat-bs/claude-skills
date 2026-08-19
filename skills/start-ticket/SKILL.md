---
name: start-ticket
description: Start work on a Jira ticket — pull the base branch, cut the ticket branch, then report a cited, per-AC gap between the ticket's acceptance criteria and the code that exists, before changing anything. Use when the user pastes a Jira URL or issue key, or says "start PROJ-142" / "pick up this ticket" / "what's left on this ticket". Confirms which parts of the repo are in scope and refuses to edit the rest. Pass --gap-only for read-only analysis.
argument-hint: "<jira-url | KEY | pasted ticket text> [--gap-only]"
---

# Start ticket

## Core principle

**The acceptance criteria are the source material.** Every verdict cites a `file:line`; no
citation, no verdict. Never infer an AC the ticket doesn't state, and never implement one the
user hasn't approved.

Detect, don't assume: base branch, branch naming, scope, runner and house style all come from
*this* repo, never from a hardcoded convention.

## 1. Resolve the ticket

Accept a Jira URL, a bare key, or pasted prose. Extract keys with `[A-Z][A-Z0-9]+-[0-9]+`.

**Fetch once, cache, then re-read the cache.** Never re-fetch to answer a follow-up.

```bash
TICKET=$(mktemp /tmp/ticket-XXXX.json)
```

Atlassian MCP `getJiraIssue`, `cloudId` = the URL's hostname, fields: `summary`, `description`,
`issuetype`, `status`, `priority`, `labels`, `comment`, `subtasks`, `issuelinks`;
`responseContentFormat: markdown`. Write the response to `$TICKET`.

Then fetch **every other key named in the description or comments** — one level deep, max 3.
They carry constraints the AC depends on ("existing validation from PROJ-125 stays unchanged"),
and they are invisible otherwise.

No tracker access → ask for the ticket body pasted, and proceed identically. Never claim the
tracker was consulted when it wasn't.

**Build a numbered AC list.** Sources in priority order: an explicit "Acceptance Criteria"
section; then bullets under "What"/"Requirements"; then comments that amend them (later wins).
Keep the ticket's own wording. Zero testable criteria → stop and ask; everything downstream
keys off this list.

## 2. Scope gate — before reading any code

First, because it is both the enforcement point and the largest context saving: excluded
surfaces are never grepped.

```bash
if [ -f nx.json ]; then npx nx show projects 2>/dev/null
elif grep -q '"workspaces"' package.json 2>/dev/null; then ls -d */*/ 2>/dev/null
else git ls-files | awk -F/ 'NF>1 {print $1}' | sort -u
fi
```

Read the repo's own rules — first that exists: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.cursorrules`. **A `## Scope` section naming permanent exclusions is authoritative** — honour
it and skip the question.

Otherwise default in-scope from the ticket itself: scope tags in the title (`[WEB & BACKEND]`),
plus any surface the AC text names. Everything else is excluded.

Confirm once, showing **both** lists — in scope, and excluded. An excluded surface returns only
if the ticket text or the user names it explicitly.

Then offer to persist it (ask before writing):

```markdown
## Scope
Default in-scope: <paths>
Never modify <path> unless the ticket or the request names it explicitly.
```

That file is what every agent reads, so the constraint then holds outside this skill too, and
travels to the team through git. Later runs read it and skip the question.

## 3. Branch

```bash
git branch --show-current && git status --short
```

Dirty tree → ask: stash, or work on the current branch. Never decide that alone.

**Three checks before creating anything** — duplicate branches per ticket are the most common
waste this skill exists to prevent:

```bash
git log --all --oneline --grep="$KEY"                                  # already done or merged?
git branch -a --list "*${KEY}*" --list "*$(echo "$KEY" | tr A-Z a-z)*" # branch exists?
gh pr list --search "$KEY" --state all --json number,title,headRefName,state 2>/dev/null
```

Any hit → report it and ask whether to resume that branch instead of cutting a second one.

```bash
git fetch --quiet origin
DEFAULT=$(git symbolic-ref --quiet refs/remotes/origin/HEAD | sed 's|.*/||')
git rev-list --count "HEAD..origin/$DEFAULT"
git branch -a --format='%(refname:short)' | sed 's|^origin/||' | grep / | cut -d/ -f1 \
  | sort | uniq -c | sort -rn                                          # naming convention
```

Ask which base, defaulting to `$DEFAULT` and reporting how far behind it you are — an informed
yes, not a blank prompt. Never assume a release branch exists. Map issuetype onto the prefix
this repo actually uses (Bug → its fix-shaped prefix, Story/Task → its feature-shaped one),
match the observed casing of the key, and confirm the name before creating it.

```bash
git checkout "$DEFAULT" && git pull --ff-only origin "$DEFAULT" && git checkout -b "$BRANCH"
```

A non-fast-forward pull, a name collision, or a failed checkout stops the flow — report and ask.
If `git branch --merged "origin/$DEFAULT"` lists several stale locals, mention it in one line
and move on; cleanup is not this skill's job.

## 4. Gap analysis

**Read `references/gap-analysis.md` before this step.** It holds the location ladder, the read
budget, the per-verdict evidence bar, and the multi-layer trap.

Report one row per AC, in the ticket's order:

| # | AC | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | <ticket's wording, trimmed> | Missing | `path/to/file.ts:42` — field is `.optional()` |

Verdicts: **Implemented · Partial · Missing · Ambiguous · Out of scope (implicated)**. State the
read budget you used and what you did not read.

## 5. Questions and assumptions

Split what you don't know:

- **Blocking** — a different answer changes the code. Ask these, all in **one** batch, max 4.
- **Assumable** — state the assumption in the plan and carry on.

Never drip-feed questions one per message, and never ask what the ticket already answers.

`--gap-only` (or "just analyse this") exits here, after the report and before any edit.

## 6. Plan, then one approval gate

Per AC: the files to touch, and the test that proves it. Write to the repo's plan directory if
one exists (`docs/plans/`, else `docs/`), otherwise keep it in chat and say so.

**STOP. Nothing is edited before an explicit yes.**

## 7. Fix

The repo's own `CLAUDE.md`/`AGENTS.md` is the authority on style, layering, migrations, docs and
test requirements — follow it over any habit of your own.

Work AC by AC. **Each AC becomes a test name, written first**, so "done" is observable rather
than a judgement call. Do not re-ask permission per AC; stop only when a stated assumption turns
out to be false — then say which one, and re-ask.

Never write to a path outside the confirmed in-scope set, even when an AC would be easier to
satisfy there.

## 8. Verify

Runner: `nx.json` → `npx nx affected -t lint typecheck test --base="origin/$DEFAULT" --head=HEAD`.
Else `package.json` scripts with the lockfile's package manager. Neither → say "no runner
detected". **Run each target once, tee to a file, grep the file.**

Anything red → one run at the merge base in a detached worktree to classify it pre-existing vs
introduced. Compare sets of failing files, not totals.

## 9. Report

AC table with final verdicts, branch and base used, files changed, test counts observed, every
assumption you carried, and each implicated out-of-scope surface. Then hand off to `open-pr`.

## Failure behaviour

| Condition | Behaviour |
| --- | --- |
| No tracker access | Ask for pasted body; never claim the tracker was consulted |
| Ticket has no testable criteria | Stop and ask; do not invent an AC |
| Referenced key unreachable | Note it as an unresolved constraint in the gap report |
| Branch/PR already exists for the key | Report it, offer to resume, never cut a second |
| Ticket already merged | Report the SHAs and stop |
| Dirty tree | Ask: stash or continue on the current branch |
| No `origin/HEAD` | Ask for the base ref outright |
| Non-fast-forward pull | Stop and report; never force or rebase to resolve it |
| No repo rules file | Ask the scope question every run |
| AC needs an excluded surface | Verdict `Out of scope (implicated)` + path; do not edit it |
| No runner | "no runner detected"; report the gap closed but unverified |
| `--gap-only` | Exit after step 5, with no git writes |

## Never

- Edit a path outside the confirmed in-scope set.
- Comment on, transition, assign or otherwise write to the tracker — read-only unless the user
  explicitly asks for a write.
- State a verdict without a `file:line`, or an assumption you didn't surface.
- Invent an acceptance criterion, or implement one the ticket doesn't state.
- Cut a second branch for a ticket that already has one.
- Re-fetch the ticket, or re-run a suite, for something the cache already answers.
- Force-push, amend, or commit unless asked.
- Silently drop an implicated out-of-scope surface — report it or it becomes a field bug.
