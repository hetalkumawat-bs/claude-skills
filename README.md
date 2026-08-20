# claude-skills

Personal [Claude Code](https://claude.com/claude-code) skills. A skill is a markdown file of
instructions the agent loads when your request matches it — no code to run, no dependencies to
install. This repo holds the ones I use across projects and is installable by anyone.

## Install

```
/plugin marketplace add hetalkumawat-bs/claude-skills
/plugin install hetal-skills@hetal-skills
```

## Skills

| Skill | What it does |
| --- | --- |
| `open-pr` | Opens a GitHub PR with a short, evidence-backed description built from the repo's own PR template, the branch's commit bodies, and real test/lint runs. Labels failing checks pre-existing vs introduced. |
| `start-ticket` | Paste a Jira ticket: pulls the base branch, cuts the ticket branch, then reports a cited, per-AC gap between the acceptance criteria and the code before changing anything. Confirms which parts of the repo are in scope and refuses to edit the rest. `--gap-only` for read-only analysis. |
| `handoff` | Writes a handoff doc to `handoff/` in the project root so a fresh session — or a different account — can continue the work. Fires automatically at 90% session usage, and a `SessionStart` hook points the next session at it. See [`docs/handoff.md`](docs/handoff.md). |
| `tech-doc` | Writes a technical documentation deliverable for a codebase: an evidence sweep that cites files and live cloud listings, the house section outline, graphviz diagrams, and a markdown → branded DOCX → PDF build. Never prints a secret value; every integration carries an honest status. |
| `bigstep-branding` | The BigStep design system — palette, Poppins, logo variants, and ReportLab/Office primitives for covers, stat cards, callouts and branded tables. Applies to any deliverable: PDF, Word, PowerPoint, Excel, HTML. |

### handoff needs one extra step

The hooks install with the plugin, but the usage sensor has to be your status line —
that is the only place Claude Code exposes the `/usage` percentages:

```json
{
  "statusLine": {
    "type": "command",
    "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/usage-sensor.py"
  }
}
```

### start-ticket asks about scope once

The first run in a repo asks which surfaces are in scope, defaulting to what the ticket's own
title tags declare, and offers to record the answer in the repo's `CLAUDE.md` / `AGENTS.md`:

```markdown
## Scope
Default in-scope: apps/backend-api, apps/frontend-web, libs/*
Never modify apps/mobile unless the ticket or the request names it explicitly.
```

Later runs read that and skip the question. Recording it there rather than in the skill's own
config means the constraint also holds in plain sessions, and travels to the team through git.

### tech-doc needs a toolchain

Markdown is written without anything installed. The Word and PDF build needs:

```bash
brew install pandoc graphviz
brew install --cask libreoffice   # PDF step only
```

The Word template it ships (`skills/tech-doc/assets/bigstep-reference.docx`) is styles, headers
and footers only — 25KB, no body. It was produced by `scripts/make_reference_docx.py`, which
exists because the branded .docx it was derived from still had a previous client's entire Scope
of Work inside it, invisible in every export. Run any template you're handed through that script
before committing it.

## Worked example

[`docs/examples/example-pr-body.md`](docs/examples/example-pr-body.md) is real output from a real
branch — a backend + web permissions fix in a private Nx monorepo — with identifiers redacted.
Two things worth noting:

- **44 lines of body, against a 102-line hand-written original** for the same change (the file
  itself is 48 lines because of the redaction note at the top). The saving comes from deleting
  non-applicable template sections instead of printing them with an "N/A" tick.
- **Two red checks classified as pre-existing without being told** — an ESLint parser crash and
  a failing component test. Both were re-run at the merge base to prove they predate the
  branch, so reviewers don't chase inherited red. One checkbox is deliberately left unticked
  with the reason attached, because the lint target genuinely isn't green.

## Local development

Symlink rather than installing your own plugin — edits then take effect immediately, with no
reinstall step:

```bash
git clone git@github.com:hetalkumawat-bs/claude-skills.git ~/claude-skills
mkdir -p ~/.claude/skills
ln -sfn ~/claude-skills/skills/open-pr ~/.claude/skills/open-pr
```

Anything under `~/.claude/skills/` is available in every project on the machine.

## Requirements

- `git`.
- `gh` (GitHub CLI), optional — without it the body goes to your clipboard along with the
  `pull/new/<branch>` URL, so nothing dead-ends.
- Works with or without a PR template, and detects Nx or plain npm / pnpm / yarn scripts. No
  runner detected means the Verification section says so rather than inventing numbers.

## Design notes

`docs/specs/` holds the design, `docs/plans/` the implementation plan. Both record why the
skill behaves the way it does — most of the rules exist because a specific manual PR was
tedious or a reviewer was misled.

## License

MIT — see [LICENSE](LICENSE).
