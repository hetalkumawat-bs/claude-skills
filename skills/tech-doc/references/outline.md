# The section outline

Front matter, then twenty numbered sections, then appendices. This order is the house format —
keep it. **Omit any section that doesn't apply** and renumber; an "N/A" section wastes a page and
tells the reader you filled a template.

Sections 1–12 describe *what the system is*. Sections 13–19 answer the questions a client's
architect or a new team asks *about* it. A short document that stops at 12 is legitimate; skipping
13–19 in a client handover deliverable is not.

---

## Front matter (unnumbered)

**Cover** — client/product logo, `Technical Documentation` as Title, the product line as
Subtitle, *Prepared for* / *Prepared by* with the BigStep entity line and URL, the BigStep logo,
and a **Classification** line (`Confidential` for anything client-facing).

**Table of Contents** — hand-written, bold, one line per top-level section, marked
`{.unlisted .unnumbered}`. Not a live Word field; it drifts, so re-check it against the body
before every build.

**Document Control** — a table, and the first thing a reviewer reads:

| Field | Value |
| --- | --- |
| Document title | |
| Version | `1.0`, bumped on every re-issue |
| Last updated | absolute date |
| Author | BigStep Technologies — Engineering |
| Owner / Reviewer | a named person |
| Platform / codebase | product name + repo name if they differ |
| Environments | each environment and its host |
| Scope | one line on what this document covers |

---

## 1. Introduction

**1.1 Purpose & Scope** — what the document is, who it's for, and an explicit *in scope* list
and *out of scope* list. The out-of-scope list prevents the "where's the UX spec?" email.
**1.2 Platform Overview** — what the product does, in the client's vocabulary, in a paragraph
or two. **1.3 Intended Audience.** **1.4 Definitions & Acronyms** — a table; every acronym used
later must appear here, including the ones you think are obvious.

## 2. System Architecture

**2.1 High-Level Architecture** — the layered diagram (Figure 1) plus what each layer is for.
**2.2 Service Responsibilities** — a table: service, responsibility, tech, port/host.
**2.3 Data Flow** — how a piece of content or a record travels end to end, per major flow.
**2.4 Request / Response Flow** — the numbered path from user to data store and back (a diagram).
**2.5 Key Architectural Patterns** — the deliberate choices: rendering strategy, caching,
where validation lives, what is deliberately *not* used (no state library, no ORM, no queue) —
absences are design decisions and reviewers ask about them.

## 3. Technology Stack

One table: layer, technology, version, why it's there. Versions come from lockfiles and
manifests, never from memory. If a version is pinned for a reason, say the reason.

## 4. Backend / CMS

Overview and run model · the schema or content-type catalogue (a table per model: field, type,
notes) · reusable components · the API surface and its permission model, with query examples in
fenced code blocks · seed/fixture data · admin roles and plugins.

## 5. Frontend Application

Routes and rendering strategy (a table: route, rendering, data source) · the API client and its
error handling · forms and validation · the design system in one paragraph plus a token table ·
any major sub-application.

## 6. Additional Services

One section per additional deployable — overview and run model, module map, endpoints,
orchestration/state, schema and migrations, and any file handling. Formulas or business rules
that live in code belong here with their source file cited as the single source of truth.

## 7. Consolidated API Reference

Every endpoint of every service, grouped by service: method, path, auth, purpose. Redundant with
sections 4–6 by design — it's the page people actually bookmark.

## 8. Integrations

A table: integration, purpose, env vars that gate it, **status**. Then a short paragraph per
integration for the detail that doesn't fit a cell. Status is mandatory and honest —
*implemented*, *stubbed*, *configured but unused*, *planned*.

## 9. Deployment & Infrastructure

Live topology (diagram) · a live inventory table per environment: VPC/subnet, each service and
where it runs, load balancers and IPs, database, registries · shared project-wide services ·
CI/CD and branch→environment mapping (diagram) · local infrastructure · cost snapshot if known ·
an environments matrix. State the date and the command you verified against. If the running
topology differs from the IaC or an earlier plan, say so plainly and point to Appendix D — that
paragraph saves the next engineer a day.

## 10. Environment Configuration

One table per service: variable, secret yes/no, purpose. **Names and purposes only — never
values.** Footnote the interesting cases (public by design, server-side only by design). Close
with where production values actually live.

## 11. Security

Authentication · authorisation · CORS · rate limiting · input validation and injection defence ·
secrets management · transport security · and the outcome of any security assessment, with its
date and what was remediated. An unremediated finding stays in the document; hiding it is worse
than the finding.

## 12. Local Development Setup

The commands, in order, that take a new machine from clone to running — copied from a run you
actually did, not reconstructed. Prerequisites with versions. What to expect when it works.

## 13. Business Architecture

Purpose and goals · stakeholders and personas (table) · business capabilities · core business
processes. Written in business language: this is the section a non-engineer reads.

## 14. Functional Architecture

Functional modules (table: module, what it does, where it lives) · routes and rendering ·
key user journeys, one diagram for the flagship journey.

## 15. Software Architecture Requirements (Non-Functional)

A table of NFRs — performance, scalability, availability, security, maintainability,
accessibility, browser support — each with its **current state**, not an aspiration. "Not yet
measured" is a valid, useful entry.

## 16. Development Strategy

Coding standards and the enforcement (linter, type checker, CI gate) · branching model ·
testing: what exists, what's covered, what isn't · data seeding or migration approach.

## 17. Deployment Strategy

How a change reaches production: trigger, build, deploy, rollback. Environment promotion path.
Who can deploy. What is manual, if anything.

## 18. Configuration & Version Management

Where configuration lives per environment · infrastructure as code and its state backend ·
version control conventions and image/artefact versioning.

## 19. Risks

A table: risk, impact, likelihood, mitigation, owner. Include the ones that are awkward —
single points of failure, unmanaged dependencies, a service with no test coverage, an
expiring credential. A risk register with no uncomfortable rows wasn't written honestly.

## 20. Appendices

**A — Core Data Model:** the entity list and relations, or an ER diagram.
**B — Glossary:** domain terms, beyond the acronyms in 1.4.
**C — Repository & Documentation Index:** what lives where in the repo, and which in-repo doc
covers what. This is how the document stays useful after it goes stale.
**D — Architectural Notes & Assumptions:** every assumption made, every superseded design still
described elsewhere, every gap you couldn't verify, each with its reason. Write this section as
you go — it is impossible to reconstruct at the end.
