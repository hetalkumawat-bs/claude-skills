> Redacted output from a real run in a private monorepo. Identifiers (ticket key, project
> name, function and file names, account email, commit SHA) are replaced with neutral
> equivalents; structure, counts and length are unchanged.

**Summary**

ACME-42 — Org-wide admin roles could only *view* review comments in the web app, not post them.

- Root cause: the route's `reviews.comment` capability gate passes for those roles, but the service asserted project *membership*, and org-wide roles sit on no project team.
- Backend: the comment handler now calls `assertOrgWideAccess(userId, userRole, projectId)`; scoped roles (manager / lead / field user) still require membership. Swagger 403 text corrected.
- Web: the add-comment box is gated on `reviews.comment`, so read-only roles no longer see a box that 403s on submit.
- Mobile needs no change — comments ride in the detail payload, which already refetches on mount.
- All three ACs met: org-wide and scoped roles can comment from web; web comments reflect on mobile; the read-only role stays view-only.

**Changes**

- `apps/api` — guard swap in the service, `userRole` threaded through the controller, service + route tests.
- `apps/web` — add-comment box gated on capability, two component tests.

**Verification**

- `api:test` 4972 pass · `ReviewDetail.test.tsx` 9 pass / 1 pre-existing fail · `nx affected -t typecheck` clean.
- Live check as `admin@example.com` (zero project assignments): comment POST returned 403 before the fix, 201 after.

**Pre-existing failures** — both reproduce at merge base `abc1234`, so neither comes from this branch:

- `api:lint` — `src/lib/assets/large-asset.ts`, "Parsing error: Maximum call stack size exceeded".
- `ReviewDetail.test.tsx` — "renders the embedded author name", a text-split matcher issue.

**Scope**

- [x] api
- [x] web

**Always**

- [x] Self-reviewed and self-tested; all AC met
- [x] Branch + commits + PR title follow the naming convention
- [x] No PII / tokens / secrets in logs or analytics
- [ ] `nx affected -t lint typecheck test` clean — lint is red from the pre-existing parser error above
- [x] New / changed types live in `libs/shared-types/` — no type changes in this PR

**Per-app checks**

- [x] backend — role + project assignment checked on the project-scoped endpoint (this is the change); no migration, no new endpoints, validation unchanged
- [x] web — role-aware rendering via `reviews.comment`; a11y unchanged (existing labelled `Input` + `Button`)

<!-- generated-by: open-pr -->
