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
