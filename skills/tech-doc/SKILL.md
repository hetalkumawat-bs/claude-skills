---
name: tech-doc
description: Write a technical documentation deliverable for a codebase in the BigStep house format — the evidence sweep, the standard section outline, the diagram set, and the markdown → branded DOCX → PDF build. Use when the user asks for technical documentation, an architecture / HLD / SDD / handover document, a client-facing "how the system works" deliverable, or wants an existing one refreshed, exported to Word or PDF, or brought into the company format. Every claim is traced to a file or a live command.
---

# Technical Documentation

## Core principle

**The codebase is the source material.** Not the README, not the ticket, not what the user
remembers building. Anything you cannot point at — a file path, the output of a command, a
console listing — does not go in the document. Where the truth isn't reachable, write what you
did check and record the gap in *Appendix D — Architectural Notes & Assumptions*. A confident
sentence about infrastructure nobody verified is the one thing that discredits the whole
document with a client's architect.

Two rules that are not negotiable:

- **Never paste a secret.** Environment sections list variable *names*, whether they are secret,
  what they are for, and where the value is stored. No values, no tokens, no connection strings
  with passwords, not even for local dev.
- **Say "not implemented" out loud.** Every integration, environment and feature carries a status.
  A planned integration described in the present tense is a lie the client finds in week three.

## 1. Scope it (one round of questions, then go)

Ask only what changes the document, in a single `AskUserQuestion` round:

- **Audience** — internal engineering only, or client-facing? Client-facing means an explicit
  Classification line, no internal nicknames, no unflattering TODOs quoted verbatim.
- **Client / product name** as it should appear on the cover and in the footer, and the
  internal codebase name if they differ (cover says the product, code references say the repo).
- **Scope** — which services/repos are in, and whether Phase-2 designs are in or out.
- **Live infrastructure** — is there a cloud project you may inspect (`gcloud`, `aws`, `kubectl`)?
  If not, the deployment section documents the IaC as written and says it was not verified live.

Default output path: `docs/<Product>-Technical-Documentation.md` next to a `docs/assets/`.

## 2. Preflight

```bash
command -v pandoc dot; ls /Applications/LibreOffice.app/Contents/MacOS/soffice 2>/dev/null
```

Missing → `brew install pandoc graphviz` and `brew install --cask libreoffice`. Markdown is
still worth writing without them; say which formats you can't produce and continue.

## 3. Evidence sweep

Fan out read-only `Explore` agents, one per area, and collect file-cited answers before writing
a word. Typical split — drop what doesn't apply, add what does:

| Agent | Comes back with |
| --- | --- |
| Repo shape | monorepo layout, package manifests, language/framework versions from lockfiles — not from memory |
| Backend / CMS | schemas, models, content types, relations, migrations |
| API surface | every route, its method, auth requirement, request/response shape |
| Frontend | routes, rendering strategy per route, data-fetch path, form handling |
| Other services | each additional deployable, its entrypoint, its API, its data store |
| Integrations | third-party SDK calls, which env var gates each, **implemented vs stubbed vs planned** |
| Config | every env var per service, from `.env.example` / config loaders / deploy manifests |
| CI/CD & IaC | workflows, branch→environment mapping, Terraform/Helm/Compose |
| Security | authn/authz, CORS, rate limits, validation, secret storage, any pen-test report in the repo |

Then verify what the repo cannot tell you. IaC describes intent; the console holds the truth:

```bash
gcloud run services list --project P; gcloud sql instances list --project P
gcloud secrets list --project P | wc -l   # count secrets, never print values
```

Stamp anything you got this way: *"Verified against live `gcloud` on <date>."* Reach for
`git log --since` to date things rather than guessing.

Cross-check the repo's own `docs/` against the code as you go. Where they disagree, **the code
wins** and the stale doc gets a note in Appendix D — that mismatch is usually the most useful
paragraph in the deliverable.

## 4. Structure

`references/outline.md` is the house section order, and what each section must contain to be
worth its page. Read it before drafting. Omit a section that genuinely doesn't apply — an
empty section with "N/A" reads worse than a shorter document.

## 5. Draft

Start from `templates/document.md` — cover block, Document Control table, manual TOC — and fill
it. `references/build-pipeline.md` has the markdown conventions the build depends on
(manual section numbers, `*Figure N — …*` captions, `{width=…in}` image sizing).

House voice: short declarative sentences, present tense for what exists, and **tables for
anything enumerable** — endpoints, env vars, content types, cloud resources, risks. Prose is for
the *why*: a design decision, a trade-off, a deviation. If a paragraph is a list of names, it's
a table.

Bold the load-bearing fact in a row, not the whole row. Never bold a whole bullet list.

## 6. Diagrams

One diagram per architectural idea, maximum seven or so for a full document. `.dot` sources are
checked in and PNGs are derived — never hand-edit a PNG. `references/diagrams.md` has the house
graphviz style and the starters in `templates/diagrams/`. A diagram that repeats a table earns
nothing; a diagram of the request path, the deployment topology, or the CI/CD flow earns its page.

## 7. Build

```bash
<skill>/scripts/build-doc.sh docs/Acme-Technical-Documentation.md \
  --client "Acme" --diagrams docs/assets
```

Renders any `.dot`, converts markdown → DOCX with the BigStep reference template, post-processes
(full-width tables, one page break per top-level section, centred figures kept with their
captions), then DOCX → PDF via LibreOffice. `--no-pdf` to stop early.

The client name lands in the footer's confidentiality line. Add `--reference` to style from a
different Word template; `scripts/make_reference_docx.py` converts any branded .docx into a
clean one (see `references/build-pipeline.md` — read the warning there before shipping a
template you didn't build).

## 8. Verify before handing over

```bash
python3 - <<'EOF'
import re
md = open("docs/Acme-Technical-Documentation.md").read()
print("headings:", len(re.findall(r"^# ", md, re.M)))
print("figures :", re.findall(r"^!\[.*?\]\((.*?)\)", md, re.M))
print("TODO    :", re.findall(r"TODO|TBD|XXX|FIXME", md))
EOF
```

Then check by hand, because these are the failures that actually happen:

- Every image path resolves and every `*Figure N*` number is unique and in order.
- No secret values, no internal-only URLs or IPs in a client-facing document.
- Every integration and environment row carries a status.
- Section numbers in the body match the TOC (both are manual — they drift on every edit).
- The PDF page count is sane and no table runs off the right edge.

Report what you built, what you verified live, and what you couldn't verify — the last list is
part of the deliverable, not an apology for it.

## Refreshing an existing document

Re-run the evidence sweep first, then diff findings against the current text and change only what
moved. Bump **Version** and **Last updated** in the Document Control table, and keep a one-line
changelog row. Don't rewrite prose that's still accurate — a refresh that touches every paragraph
is unreviewable.

## Companion skill

`bigstep-branding` carries the palette, the Poppins TTFs, logo variants, and ReportLab/Office
primitives. Load it when a deliverable needs brand mechanics beyond this pipeline — a PDF built
from scratch, a deck, a one-pager. This skill covers the document; that one covers the design
system.
