# Gap analysis

Loaded at step 4 of `start-ticket`. The goal is one defensible verdict per acceptance criterion,
at the lowest read cost that still supports it.

## Prior art first

Before reading implementation files, check whether the repo already documents this problem —
a solutions index, ADR directory, `docs/` index, or a plans folder naming the same feature:

```bash
ls docs 2>/dev/null
git log --oneline -15 --grep="$KEY" --all
git log --oneline -15 -- <the surface the AC names>
```

A recent commit touching the same file is the cheapest possible evidence that an AC is already
Implemented or Partial. Read the diff before you read the file.

## Location ladder

Stop at the first rung that finds the owning code. Search only in-scope surfaces.

1. **Ticket nouns.** Take the domain nouns from the AC verbatim (`client`, `email`, `geofence`)
   and grep for them as file and directory names first, contents second. File names beat
   contents — they find the module, not its 200 call sites.
2. **The layer word.** ACs describe a layer: "form", "field", "endpoint", "column", "screen",
   "report". Combine noun + layer to reach the owning file in one hop.
3. **The identifier.** Once one file is found, grep its distinctive symbol names to find the rest
   of the chain — schema, service, repository, migration, test.
4. **Nothing found.** That is itself the answer: verdict Missing, evidence = the searches that
   came back empty. Say which patterns you tried.

## Read budget

**Cap at roughly 10 files, and declare it.** Read only files that *own* an AC — the schema, the
validator, the service, the form, the migration. Skip call sites, snapshots, generated files and
lockfiles.

Prefer a targeted read to a whole-file read: `grep -n` the symbol, then read the surrounding
20-40 lines. A whole file is justified when the AC concerns its structure rather than one value.

If the budget runs out with ACs unresolved, stop and report which ones are unanalysed. An honest
"not analysed" beats a guessed verdict.

## The multi-layer trap

**The single most common false verdict.** An AC about one field or rule almost always has more
than one enforcement point, and partial implementation across those layers is the norm rather
than the exception. Before calling anything Implemented, enumerate every layer that could
enforce it and check each:

| Layer | Typical question |
| --- | --- |
| Client form / UI | Is the field required in the form schema, and is the inline error shown? |
| API request schema | Is it optional, and does an empty string read as absent? |
| Service / business rule | Is the rule enforced when the request bypasses the form? |
| Database | Is the column nullable? Is there a constraint or a partial index? |
| Existing rows | Would a required field break records that predate the change? |

Two consequences worth stating explicitly in the report: a rule enforced only in the UI is
**Partial**, not Implemented, because any other client bypasses it — and tightening a field that
existing rows violate is a migration question the ticket probably doesn't mention. Raise it.

## Verdicts and their evidence bar

| Verdict | Means | Evidence required |
| --- | --- | --- |
| **Implemented** | Satisfied at every layer that can enforce it | A citation per layer, plus the test that covers it |
| **Partial** | Satisfied at some layers, bypassable at others | The citation that satisfies, **and** the one that doesn't |
| **Missing** | No enforcement anywhere in scope | The file that should own it, or the searches that found nothing |
| **Ambiguous** | The code is clear; the AC is not | The citation, plus the two readings it could mean → becomes a blocking question |
| **Out of scope (implicated)** | Enforced or duplicated on an excluded surface | The path, and what would change there |

Never soften Partial to Implemented because the missing layer feels unlikely to be hit. Never
harden Ambiguous into a verdict by picking a reading silently — that is what step 5 is for.

## Ripple detection into excluded surfaces

Cheap and mandatory. For each AC's key identifier, one grep across the **whole** repo including
excluded surfaces:

```bash
git grep -ln "<identifier>" -- . | sed 's|/.*||' | sort -u
```

A hit outside the in-scope set means the surface duplicates the rule. Report it as
`Out of scope (implicated)` with the path — do not read further into it and do not edit it.
Silently skipping it is how a rule ends up enforced on web and not on mobile.

## Report shape

One row per AC in the ticket's order, ticket wording preserved so the user can diff it against
Jira by eye. Then, below the table:

- **Read budget** — how many files, and what you deliberately did not read.
- **Unresolved constraints** — referenced tickets you couldn't reach.
- **Beyond the ticket** — anything the AC implies but doesn't state (a migration for existing
  rows, an API contract or docs update the repo's rules require). Name it; don't fold it in
  silently and don't act on it unasked.
