> **Note on CLAUDE.md's `.md` merge cross-reference**: this file corresponds to
> what CLAUDE.md's "Documentation control" section calls "Controlled local
> documentation" — the intent of that section is preserved by treating this
> file as the entry point; the individual source documents listed in
> `docs/DOCUMENTATION_INDEX.md` remain the maintained originals. This file is
> re-generated from them (see the changelog below) rather than replacing them.

# ServiceOps master reference (for any AI or engineer touching this codebase)

This single document merges every controlled ServiceOps planning/governance
document, the BP-001 blueprint traceability, and a fresh whole-app audit into
one place, so an AI agent or new engineer can get complete, precise context
without opening a dozen files. Individual source documents remain the
maintained originals — this file is regenerated from them; see
`docs/DOCUMENTATION_INDEX.md` for the authoritative source list and the
"Keeping this synchronized" rule that still applies to each of them.

**Read `CLAUDE.md` at the repository root first.** It is the top-level,
override-everything instruction set for this project (product direction,
production-only policy, authentication rules, ITIL record model, change
governance, security requirements, migration rules, engineering workflow, and
report format). Everything below is detail underneath those rules, not a
replacement for them.

---

## Part 0 — Quick-start for an AI agent picking up this repo

**What this product is**: an independent, production-oriented ITSM platform
(Flask + PostgreSQL + SQLAlchemy + Alembic), inspired by ITIL/ServiceNow
patterns but explicitly not claiming ServiceNow parity or compatibility (see
Part 1, Product boundary). Single monolithic `app.py` (~8,100 lines: every
route, every SQLAlchemy model, most business logic) plus a small
`serviceops_core/` package (`security.py`, `priority.py`, `workflow.py`,
`projections.py`, `business_time.py` — ~400 lines total) that the project is
slowly extracting bounded logic into. Templates are server-rendered Jinja2 in
`templates/`. Alembic migrations live in `migrations/versions/`, one file per
schema change, always additive/reversible — see CLAUDE.md's migration rules.

**Architecture map**:

| Layer | Where |
|---|---|
| Routes + business logic + all ORM models | `app.py` (single file, being decomposed incrementally — see Part 4 finding #1) |
| Extracted bounded services | `serviceops_core/{security,priority,workflow,projections,business_time}.py` |
| Schema history | `migrations/versions/*.py` (Alembic; head as of this document: `20260729_0023`) |
| Views | `templates/*.html` (Jinja2, server-rendered, light-mode only per ADR-012) |
| Static assets | `static/*.css`, `static/*.js` |
| CLI / lifecycle | `./serviceops` (install, status, health, backup, restore, rehearsals, retire-bootstrap-secret) |
| Deployment | `compose.yaml` / `compose.external-db.yaml` (Docker), `charts/serviceops` (Helm/Kubernetes), `packaging/` (RPM) |
| Ops tooling | `tools/*.py`/`*.sh` (migration rehearsal, recovery verify, release evidence, supply-chain verify, outbox worker, CMDB sync agent, demo/test data loaders) |
| Tests | `tests/test_app.py` (bulk of coverage), `tests/test_installer.py`, `tests/test_recovery_verify.py` |
| Config-as-code | `config/*.json` (authorization vocabulary, field projections, priority matrix, workflows) — Git-backed per CLAUDE.md rule 7 |

**Non-negotiable rules an agent must not violate** (full detail in
`CLAUDE.md`, restated here because it's the single most common way an AI
agent gets this codebase wrong):

- Never add a demo mode, shared demo accounts, sample records seeded into a
  *production* path, or a weak default password. `tools/load_test_fixture.py`
  and `tools/load_demo_dataset.py` are the only sanctioned non-production data
  loaders, both explicitly excluded from the production Docker image (see
  `Dockerfile`'s `rm -f` line) and both requiring an explicit
  `--confirm-non-production` flag.
- Tenant resolution fails closed (`tenant_context_id()` in `app.py`) — never
  make an authenticated user with no `tenant_id` silently fall back to tenant
  1. Every new tenant-owned table needs its own `tenant_id` column with
  `default=tenant_context_id, index=True`, following the existing ~30 tables
  that already do this (Part 4, finding #4 lists which dependent child tables
  still don't and why that's currently safe-by-construction, not safe-by-design).
- Don't collapse INC/PRB/PTASK/CHG/CTASK/REQ/RITM/SCTASK/KB/CI into one
  generic ticket table. See Part 3 (ITIL hierarchy) for the exact mapping
  ServiceOps uses instead of ServiceNow's literal table names.
- A change cannot reach implementation states without its full approval chain
  satisfied; material post-approval edits must supersede the prior approval
  and start a fresh cycle (see Part 3 §7, Part 2 B-036/B-231/B-251).
- Every migration is additive and reversible; never rewrite a deployed
  migration or reset a database without explicit user authorization. See
  `CLAUDE.md`'s "Migrations and releases" section.
- Keep new business logic out of the ever-growing `app.py` where practical —
  prefer `serviceops_core/`. See Part 4 finding #1: this rule is currently
  being under-observed and is worth actively pushing back toward.

**Current schema head**: `20260729_0023` (this session's CMDB enrichment —
see Part 5). Verify with:
```sql
SELECT version_num FROM alembic_version;
```

**Current deployed local dev image**: `serviceops-app:1.27.18`, rebuilt this
session with the changes in Part 5; running via `compose.yaml`
(`serviceops-app-1`, `serviceops-db-1`, `serviceops-worker-1`), verified
healthy and end-to-end smoke-tested (login, `/cmdb`, `/tickets/incident`,
`/tickets/change`, `/work/open`, `/knowledge`) against a freshly flushed and
reseeded database — see Part 5 for exact verification steps and output.

---

## Part 1 — Product governance and non-deviation policy

(Full text of `docs/GOVERNANCE.md`)

### Product boundary

ServiceOps is an independently implemented service-management platform. It
must not be described as ServiceNow, ServiceNow-compatible, certified, or as
containing "all ServiceNow features." Reference material may inform workflows
and usability; implementation status is proven only by repository evidence and
tests in the traceability matrix.

### Non-negotiable controls

1. Production-only runtime: no demo mode, shared personas, sample records, or
   default credentials.
2. No requirement is "done" without acceptance criteria, implementation
   evidence, tests, documentation, and an accountable reviewer.
3. Existing audit and approval history is preserved. Referenced removed users
   are tombstoned, never silently deleted.
4. Security-sensitive defaults fail closed. Secrets are supplied externally,
   encrypted where persisted, and never printed in validation results.
5. Schema changes require versioned, reversible migrations and backup/restore
   evidence before production rollout.
6. Production releases use immutable image tags or digests, two or more
   replicas on Kubernetes, external highly available PostgreSQL, TLS, and
   tested recovery.
7. LDAP/Keycloak, Kubernetes, restore, load, and security claims require tests
   against representative external systems. Static configuration is not proof.
8. Product changes update `BACKLOG.md`, `TRACEABILITY_MATRIX.md`, the decision
   log below when applicable, and the relevant manual in the same change.

### Change gate

Every release must pass unit/integration tests, dependency and image scans,
lint/type checks, migration rehearsal, backup/restore rehearsal, authorization
tests, and a production-like smoke test. Exceptions require a documented
owner, expiry date, impact, mitigation, and CCB approval.

### Architecture decision log

| ID | Date | Decision | Consequence |
|---|---|---|---|
| ADR-001 | 2026-07-25 | Product name is ServiceOps and is independent of ServiceNow. | No inherited branding, runtime, data, or parity claims. |
| ADR-002 | 2026-07-25 | Runtime is production-only. | Demo mode, sample seeding, shared personas, and login hints are prohibited. |
| ADR-003 | 2026-07-25 | Local admin is bootstrap/break-glass; AD/LDAP and Keycloak are enterprise identity sources. | Local auth can be disabled after enterprise identity verification. |
| ADR-004 | 2026-07-25 | Team managers and CCB approvers are explicitly appointed named users. | Change submission fails closed when governance configuration is incomplete. |
| ADR-005 | 2026-07-25 | Kubernetes production uses external HA PostgreSQL and shared attachment storage. | Bundled chart databases are not approved for production. |
| ADR-006 | 2026-07-25 | Removed referenced identities are tombstoned. | Audit and approval foreign keys remain valid while login is impossible. |
| ADR-007 | 2026-07-25 | The supplied 2026 ServiceNow UI PDF is a controlled UX reference. | Features remain gaps until implemented and verified. |
| ADR-008 | 2026-07-25 | AD team membership synchronizes at login; manager and CCB authority remain explicit grants. | Automated membership can reconcile without overwriting governance decisions. |
| ADR-009 | 2026-07-26 | BP-001 is a controlled multi-release product specification. | Every requirement requires traceability and evidence; blueprint wording alone never implies implementation or parity. |
| ADR-010 | 2026-07-26 | Each installation initially serves one organisation, while tenant identifiers and tenant-aware authorization conventions are introduced now. | Existing data is assigned to the installation's default tenant through reversible migrations; new tenant-owned models must never omit tenant scope. |
| ADR-011 | 2026-07-26 | Evolve the Flask product into bounded modules behind stable interfaces without a rewrite. | Refactors must preserve behavior, data and deployability; module extraction is independently tested. |
| ADR-012 | 2026-07-26 | ServiceOps is light-only. Dark mode is a governed non-requirement. | No dark theme controls, tokens or compatibility burden will be introduced unless this ADR is explicitly superseded. |
| ADR-013 | 2026-07-26 | Standard deployment requires PostgreSQL only; search, cache, object storage, event transport and workers are optional enterprise adapters. | Standard and enterprise profiles share domain behavior and APIs and must not become architectural forks. |
| ADR-014 | 2026-07-26 | Integration priority is SMTP/email, signed webhooks, monitoring ingestion, then Microsoft Teams. | Each adapter is separately configurable, observable, retryable and fail-safe. |
| ADR-015 | 2026-07-26 | Build a versioned REST API first; GraphQL is deferred until a demonstrated consumer requirement. | REST resources use OAuth/OIDC authorization, pagination, idempotency, rate limits and audit conventions. |
| ADR-016 | 2026-07-26 | Deliver a responsive installable PWA before native mobile applications. | API and authentication contracts must remain suitable for future native clients. |
| ADR-017 | 2026-07-26 | Configuration is Git-backed and declarative; the database contains deployed runtime configuration. | Packages require diff, validation, promotion, dependency and rollback evidence. |
| ADR-018 | 2026-07-26 | Security and platform foundations precede visible feature expansion. | Migrations, CSRF, authorization, audit, workflow durability, APIs and configuration versioning are release prerequisites. |
| ADR-019 | 2026-07-26 | Preserve existing data using reversible versioned migrations with tested upgrade, verification and rollback. | Destructive reset is not an accepted upgrade strategy. |

### Governed non-requirements

The following BP-001 suggestions are explicitly excluded from the current
programme unless an ADR supersedes this section:

- dark mode;
- GraphQL without an identified consumer;
- a frontend/backend rewrite disguised as modularisation;
- mandatory Redis, OpenSearch, object storage, event transport or workflow
  infrastructure in the standard PostgreSQL deployment;
- native mobile applications before the responsive PWA and REST contracts are
  proven.

### Current production-readiness verdict

**Not approved for enterprise production yet.** P0 backlog items include
versioned migrations, comprehensive CSRF and authorization assurance,
append-only audit controls, proven disaster recovery/failover, supply-chain
attestation, and independent penetration testing.

Approval requires clean-checkout quality gates, representative AD/Keycloak
tests, a real HA Kubernetes deployment, restore and failure-injection evidence,
load/soak results, security and accessibility assessments, and accountable
operations, security, privacy, and CCB sign-off.

The only exception is the explicit `tools/load_test_fixture.py` (and now
`tools/load_demo_dataset.py`) workflow on an intentionally reset, isolated
test database. Neither is ever automatic, both are excluded from the
production image, and both must be destroyed before any production assessment.

---

## Part 2 — Governed backlog (authoritative work register)

### 1.38.2 remediation checkpoint (2026-08-05)

The live backlog now includes B-277 and `docs/REMEDIATION_PLAN_1.38.2.md` as the
controlled scope for the next patch. That release synchronizes every governed
version-bearing runtime, installer, and Helm location; adds CI correctness,
compilation, migration-head, test, shell, JavaScript, and Compose-mode gates;
closes a scheme-relative improvement return-path redirect; and improves shared
keyboard/navigation/dialog semantics. The deployment pass also disables
Gunicorn 26's unused control socket, which could not be created beneath the
non-login user's home in the read-only container. It makes no schema change and does not
claim that the external penetration test, independent tenant review, real
registry/cluster validation, production recovery/rollback rehearsals,
observability, load testing, object storage, organization-enforced MFA/SCIM,
independent accessibility audit, or privacy controls are complete. Read the
live backlog and remediation plan for current acceptance evidence.

(Full text of `docs/BACKLOG.md` as last fully merged here; the live file has
since grown well past the entries reproduced below — as of this note it runs
through B-261 (whole-application audit follow-through: tenant_id on the three
approval/change-governance tables, attachment malware scanning and
cryptographic hashing, dashboard query batching, nine new regression tests
for the B-258 security fixes, and two already-deployed migrations'
`downgrade()` paths made to actually work). Re-merging the full text on every
backlog change isn't done every session (see the identical, deliberate
choice in Part 9) — read `docs/BACKLOG.md` directly for the current register.
"Done" requires code, tests, documentation, and evidence. Priority: P0
release blocker, P1 required for enterprise production, P2 planned
enhancement.)

| ID | Priority | State | Work and acceptance criteria |
|---|---|---|---|
| B-001 | P0 | Implemented | Remove demo mode/personas/sample seeding/default passwords; fresh-install and cleanup tests pass. |
| B-002 | P0 | Verified | Production uses an Alembic migration gate with safe fresh-schema creation, existing-schema adoption, version verification, dedicated Kubernetes migration Job and tenant backfill. Re-verified 2026-07-28 at full scale: 100,717 records across 63 tables, fingerprints preserved. Independent tenant-isolation review remains open under B-231. |
| B-003 | P0 | Verified | Central CSRF enforcement protects every unsafe browser request; rendered forms and JavaScript actions carry session-bound tokens, authentication rotates tokens, and tests prove missing-token rejection and authenticated acceptance. |
| B-004 | P0 | In progress | Tenant-specific chained HMAC evidence, correlation, database mutation denial, verification-gated signed export and adversarial tests are implemented. Per-event key identifiers, non-destructive governed key rotation, file-mounted key support, minimum seven-year retention/legal-hold policy, and signed durable SIEM-only outbox delivery are in place. Representative external WORM/SIEM validation and independent security review remain. |
| B-005 | P0 | In progress | Central object policies and adversarial coverage protect ticket, request, approval-chain, attachment, enterprise/problem, analytics and search surfaces, plus a validated fail-closed Git-backed field-projection registry. Independent authorization review remains. |
| B-006 | P0 | Implemented | File-mounted bootstrap secrets, bootstrap-password exclusion from workers, split Kubernetes bootstrap/runtime Secrets, retirement tooling, credential rotation. External vault rotation ceremony remains. |
| B-007 | P0 | In progress | Digest-pinned images, full-SHA-pinned CI actions, Trivy blocking, CycloneDX SBOM, keyless Cosign signing, SLSA/SBOM attestations, Sigstore admission enforcement. A real tagged GHCR run and cluster admission rejection test remain. |
| B-008 | P0 | Open | Run penetration test and remediate critical/high findings. |
| B-009 | P0 | In progress | SHA-256 recovery-set manifests, archive traversal protection, isolated logical restore, non-destructive `pg_basebackup` + continuous-WAL rehearsal. Off-site immutable recovery storage and organisation-approved RPO/RTO targets remain. |
| B-010 | P0 | In progress | Guarded candidate-image rehearsal, pre-upgrade recovery set, migration gate, Kubernetes retains five revisions with `maxUnavailable: 0`. A real two-version cluster rollout and forced-failure rollback test remain. |
| B-021 | P1 | Verified | Unified navigation, search, history, favorites and light-only preferences. |
| B-022 | P1 | Implemented | Ticket lists/forms/activity/attachments/checklists; pagination/saved-filter/malware-scanning gaps remain. |
| B-023 | P1 | Verified | Visual task board and state movement. |
| B-024 | P1 | Implemented | Post-install branding/settings/logo. |
| B-030 | P1 | Implemented | Named team managers, explicit CCB approver authority and approval chains. |
| B-031 | P1 | Implemented | Core INC/PRB/PTASK/CHG/CTASK/REQ/RITM/SCTASK lifecycle and relationship network, known errors, major-incident extension. |
| B-032 | P1 | Implemented | Primary/affected CI and impacted-service task relationships, CI-aware conflict detection, `/cmdb` manual CI+relationship CRUD, `PUT /api/v1/cmdb/configuration-items` (`cmdb:write`), `tools/cmdb_sync_agent.sh`. **This session extended the CI schema itself** — see Part 5. Discovery ingestion beyond self-reported facts remains open. |
| B-033 | P1 | Implemented | Multi-RITM requests, multiple independently assigned SCTASKs, sequential/parallel task control, closure roll-up, approvals and SLAs. |
| B-034 | P0 | Verified | Central server-side lifecycle guards prevent approval bypass through any surface. |
| B-035 | P0 | Verified | Explicit owning teams for incidents/requests/changes; only active owning-team members/managers/admins mutate operational fields. |
| B-036 | P0 | Verified | Append-only in-record task history; material CHG plan changes supersede prior approvals and notify. |
| B-037 | P1 | Verified | Governed related-record network (parent/child INC, INC↔PRB/CHG links, PRB knowledge, RITM↔CHG, PTASK/CTASK). |
| B-038 | P1 | Verified | Administrator-managed catalog-item fulfillment routing; Laptop/Software default to Windows. **Note:** as of this session, `Laptop Request`/`Software Request` catalog items themselves are now auto-created on fresh install (see Part 4 finding, "Part 5" fix) — previously a fresh install had zero catalog items despite this routing default existing in code. |
| B-039 | P0 | Verified | Scope REQ/RITM visibility to requested-by/for, fulfillment teams, SCTASK teams, named approvers, admins. |
| B-040 | P0 | Verified | Object-level authorization across ticket/enterprise lists, direct IDs, dashboards, boards, analytics, searches, attachments, approvals, CI links, REQ/SCTASK creation. |
| B-041 | P1 | Verified | Catalog item admin CRUD with governed fields; inactive items fail closed. |
| B-042 | P0 | Verified | All active IT fulfillment-team members/managers read every INC/CHG; mutation stays owning-team/admin only. |
| B-050 | P1 | Implemented | Docker bundled/external PostgreSQL deployment; restore/rolling-upgrade proof pending completion. |
| B-051 | P1 | Implemented | Helm HA scaffolding; real multi-zone cluster validation pending. |
| B-052 | P1 | Open | Add supported object storage for attachments, antivirus scanning, encryption and retention. |
| B-061 | P1 | Implemented | LDAP/Keycloak/local admin plus AD-group-to-team login sync; representative external validation pending. |
| B-062 | P1 | In progress | Local TOTP MFA is implemented; organization-enforced IdP MFA, SCIM lifecycle, session inventory/revocation and emergency access controls remain. |
| B-070 | P1 | Open | Metrics, structured logs, traces, alerting, SLO dashboards, capacity model and runbooks. |
| B-071 | P1 | Open | Load/soak/failover tests with published targets. |
| B-080 | P1 | In progress | Shared preferences and 1.38.2 landmark/navigation/dialog improvements are implemented; independent WCAG 2.2 AA audit evidence remains. |
| B-090 | P1 | Open | Data classification, retention, legal hold, privacy export/deletion and regional controls. |
| B-100 | P2 | Implemented | Administrator post-deployment settings; extend to workflows/numbering/states/notifications/policy versioning. |
| B-101 | P2 | Verified | Consolidate lifecycle operations behind `./serviceops`. |
| B-102 | P2 | Verified | Explicit isolated test-fixture loader (`tools/load_test_fixture.py`). **This session added a second, richer loader**, `tools/load_demo_dataset.py` (full CMDB, INC/PRB/CHG/REQ/RITM/SCTASK/KB spread) — see Part 5. |
| B-120 | P2 | Open | Guided tours and contextual help with versioned content and role targeting. |
| B-121 | P2 | Open | Configurable workspace/page builder. |
| B-130 | P1 | In progress | Durable outbox, worker coordination, bounded retry, SMTP/webhooks/Teams, encrypted secrets, delivery evidence, monitoring ingestion. External validation and DNS-rebinding egress enforcement remain. |
| B-200 | P0 | In progress | Decompose BP-001 into atomic requirements and governed release epics (ADR-010–019). |
| B-201 | P0 | Verified | Foundation CSRF/session/cookie/deployment release. |
| B-202 | P0 | In progress | Default tenant creation, 15 tenant-owned roots backfilled, tenant-aware query conventions. Independent tenant-isolation review remains. |
| B-203 | P0 | In progress | First stable bounded interface `serviceops_core.security`. Further extraction remains (see Part 4 finding #1 — this is the area most in need of continued work). |
| B-204 | P0 | In progress | REST v1 tenant/user-bound clients, scopes, cursor pagination, idempotent writes, OpenAPI, live docs at `/api/v1/docs`. Broader resources/OAuth2/rate limits remain. |
| B-205 | P1 | Implemented | Installable PWA manifest, privacy-safe shell-only service worker. |
| B-206 | P0 | Implemented | Git-backed impact/urgency matrix, documented priority overrides, business schedules, SLA lifecycle evidence, breach escalation. |
| B-207 | P0 | Implemented | Git-backed workflow packages, immutable versions, state-entry jobs, retries/dead-letter. |
| B-208 | P0 | Implemented | Durable wait cursors, per-workflow rate limits, manual/API/SLA triggers, idempotency, dead-job replay. |
| B-209 | P0 | Implemented | Reusable subflows, tenant-aware recurring schedules, SKIP LOCKED scheduler claims. |
| B-210 | P0 | Implemented | Credential auth-version invalidation, mounted bootstrap-secret loading, split Kubernetes Secrets. |
| B-211 | P0 | Implemented | Local-auth login lockout with audited events. |
| B-220 | P1 | Implemented | `/work/tasks` unified CTASK/PTASK/EVTASK/SCTASK queue; `/manager/portal`. |
| B-221 | P1 | Implemented | Dashboard "Assigned to me"/SLA breach/Incidents tiles, admin-toggleable. **Note:** this session added pagination/caps to `/work/open` — see Part 4/5. |
| B-222 | P1 | Implemented | Notifications carry target links. |
| B-223 | P1 | Implemented | Team-to-team reassignment for incidents/changes, restarting change approval. |
| B-224 | P1 | Implemented | Type-ahead lookups for CIs and cross-record references. |
| B-225 | P2 | Open | Git history predates 2026-07-27; not recoverable further back. |
| B-230 | P0 | Implemented | Migration rehearsal script derives head/prior revision dynamically instead of hardcoding. |
| B-231 | P0 | Implemented | `tenant_context_id()` fails closed instead of defaulting to tenant 1. Tenant-scoping remaining dependent tables (approvals/gates/votes, comments, catalog routing, group membership, directory mappings, requested items, catalog tasks, task history, record links, attachments) remains open — the larger follow-up. **This session added `tenant_id` to `CIRelationship`** as one instance of this follow-up (Part 5) and fixed a related cross-tenant lookup gap in `find_record_by_number()` (Part 4/5). |
| B-232 | P1 | Implemented | Reapproval notification deduplication. |
| B-233 | P1 | Implemented | Secure session cookie defaults with explicit insecure-cookie escape hatch. |
| B-234 | P1 | Implemented | Open-redirect guard on `UserPreference.start_page`. |
| B-235 | P1 | Implemented | Content-Security-Policy header. `style-src 'unsafe-inline'` noted as a residual weakening in Part 4 finding — worth tightening with nonces if inline styles can be removed. |
| B-236 | P1 | Implemented | Webhook DNS-rebinding/redirect-SSRF re-validation per hop. True DNS pinning remains open. |
| B-237 | P1 | Implemented | Gunicorn timeout/worker-recycling configuration. Root-cause (timeout vs. OOM) memory-profiling evidence still not gathered. |
| B-238 | P1 | Implemented | Version-string alignment across installer/Compose/Helm/env examples. |
| B-239 | P0 | Implemented | `.dockerignore` now excludes `backups/`, `.installer-state/`, etc. from the build context. |
| B-240 | P2 | Implemented | Removed dead dark-mode CSS (ADR-012 light-only). |
| B-241 | P1 | Implemented | `tools/load_test_fixture.py` excluded from the production image. **This session applied the identical exclusion to the new `tools/load_demo_dataset.py`** in the same `Dockerfile` line. |
| B-242 | P0 | Implemented | Authlib CVE-2026-27962 fix. |
| B-244 | P0 | Implemented | Dependency audit sweep (Flask/Authlib/requests/Werkzeug/pytest), secure-cookie default fix for `compose.external-db.yaml`/`.env.example`, digest-pinning support in `build-dist.sh`. |
| B-243 | P2 | Implemented | RPM packaging alternative to `git clone`. |
| B-245 | P1 | Verified | ServiceNow-inspired incident record workspace (dense two-column form, Event history). |
| B-246 | P0 | Verified | PWA service-worker cache-versioning fix (visual delivery bug). |
| B-247 | P1 | Verified | Governed record/list interaction model extended to Change/Problem/enterprise/REQ. |
| B-248 | P1 | Verified | Identity and administration workspace (searchable user list, admin-only role/active/department control, preferences). |
| B-249 | P1 | In progress | Notification read-state, profile AD-sync display, required-field-asterisk consistency, change-plan-edit state guard. |
| B-250 | P0 | Verified | `conflict_status` column widened (`VARCHAR(40)`→`VARCHAR(500)`) after a real truncation-triggered 500; ticket-create validation now redisplays the form instead of a generic error page. |
| B-251 | P1 | Verified | CTASK backfill migration for pre-existing changes; Change Tasks tab redesigned as a table with per-row inline update. |
| B-252 | P1 | Verified | Dedicated `operational_task_detail` page/route for CTASK/PTASK, replacing the inline-table interface. |

### This session's additions to the backlog (not yet assigned formal IDs — see Part 8 for the sync-required follow-up)

- **CMDB schema enrichment** (extends B-032): `ConfigurationItem` gained
  `description`, `lifecycle_state`, `business_criticality`, `serial_number`,
  `vendor`, `model`, `location`, `cost_center`, `discovery_source`,
  `install_date`, `warranty_expiry_date`, `attributes` (JSON),
  `support_group_id`, `created_at`/`updated_at`. `CIRelationship` gained
  `tenant_id`, `created_at`, and a `(parent_id, child_id, relationship_type)`
  unique constraint (previously only `(parent_id, child_id)`, allowing
  duplicate relationship types between the same pair). Migration
  `20260729_0023_cmdb_enrichment.py`. Routes (`/cmdb`, `/cmdb/new`,
  `/cmdb/<id>/edit`, `/cmdb/relationships`) and templates (`ci_form.html`,
  `cmdb.html`) updated to expose and edit the new fields.
- **Default catalog items**: `seed_itil()` in `app.py` now creates "Laptop
  Request" and "Software Request" catalog items on first bootstrap if none
  exist, closing a real gap where a fresh install had the Windows-routing
  default (B-038) wired up but zero catalog items to route.
- **Tenant-isolation fix**: `find_record_by_number()` (used for cross-record
  linking by number) previously had zero tenant filtering on any of its six
  branches — a cross-tenant existence oracle. Every branch now filters by the
  caller's tenant (joining through the owning parent for RITM/SCTASK/CTASK/
  PTASK, which don't carry their own `tenant_id`).
- **Performance fixes**: `/tickets/<kind>` now eager-loads
  `requester`/`assignee` and batch-fetches owning groups for the current page
  instead of issuing one query per row (was up to ~150 extra queries per
  50-row page). `/work/open` is now capped at 200 rows per section instead of
  loading a tenant's entire open-ticket/open-request backlog unbounded.
- **Stability fix**: the admin-triggered `/admin/integrations/process` route
  now caps synchronous outbox processing at 5 events (was up to 50, each
  potentially making a network call with its own timeout, risking exceeding
  the gunicorn worker timeout).
- **New tooling**: `tools/load_demo_dataset.py` — a second non-production
  data loader (see B-102), building a realistic, deep CMDB (business
  services → applications → databases → servers/network/storage with
  dependency relationships) plus per-team users and a representative spread
  of INC/PRB/CHG/REQ/RITM/SCTASK/KB records. Excluded from the production
  image identically to `load_test_fixture.py`.

---

## Part 3 — ITIL / ServiceNow-pattern ticket hierarchy reference

(Full text of `docs/ITIL_TICKET_HIERARCHY.md` — reference material, preserved
verbatim; ServiceOps is inspired by these patterns but does not claim full
ServiceNow compatibility, per Part 1. Where ServiceOps's model differs, that
divergence is deliberate and documented in Part 6, the traceability matrix.)

### Governing principle implemented in ServiceOps (2026-07-29)

Planning and assessment tasks may proceed before approval. Implementation and
testing tasks must remain in Pending state until the Change Request has
received all approvals required for the current authorization gate. Review
tasks must remain pending until implementation and testing are complete.

Implemented as `change_task_gate_block()` in `app.py`, enforced both at
change-task creation (initial state) and at every state-transition attempt
(`transition_operational_task()` / `POST /operational-task/<id>`). See
`tests/test_app.py::test_change_task_unlocking_model_gates_implementation_and_review`.

### 1. The ServiceNow ITSM ticket hierarchy

ServiceNow does not store every record as an independent, unrelated "ticket."
Most operational records extend the base Task `[task]` table:

```
Task [task]
│
├── Universal Request [universal_request]
│   └── Primary ticket
│       ├── Incident
│       ├── Requested Item
│       ├── HR Case
│       └── Other supported task
│
├── Incident [incident]
│   ├── Incident Tasks [incident_task]
│   ├── Child Incidents [incident]
│   ├── Major Incident classification
│   ├── Related Problem
│   ├── Related Change Requests
│   └── Related Knowledge Articles
│
├── Problem [problem]
│   ├── Problem Tasks [problem_task]
│   ├── Related Incidents
│   ├── Related Change Requests
│   ├── Known Error information
│   └── Knowledge Articles
│
├── Change Request [change_request]
│   ├── Change Tasks [change_task]
│   ├── Approval records [sysapproval_approver]
│   ├── Affected CIs and services
│   ├── Conflicts and schedules
│   ├── Related Incidents
│   ├── Related Problems
│   └── Related Requested Items
│
└── Service Catalog Request
    └── Request [sc_request]
        └── Requested Item [sc_req_item]
            ├── Catalog Tasks [sc_task]
            ├── Approval records
            ├── Variables
            ├── Related Incident
            └── Related Change Request
```

Formal Service Catalog hierarchy: `REQ → RITM → SCTASK`.

**ServiceOps mapping**: `Ticket` (`kind`=incident/change) plays the role of
the base Task table for INC/CHG; `CatalogRequest`/`RequestedItem`/
`CatalogTask` implement REQ/RITM/SCTASK; `EnterpriseRecord`
(`domain`=problem/event/etc.) implements PRB; `OperationalTask` implements
CTASK/PTASK. This is a documented, deliberate partial compromise (generic
containers for PRB/PTASK/CTASK rather than fully distinct tables per type) —
see Part 4 finding on schema shape for the current audit's assessment of
whether this still satisfies CLAUDE.md's "do not collapse" rule (verdict:
yes, because the record *types* are still genuinely distinct models/tables,
not one polymorphic ticket).

### 2. What counts as a sub-ticket

- **2.1 Execution task**: a defined work package (Incident/Problem/Change/
  Catalog/Release Task) owned by one group/person under a parent that owns
  the overall outcome.
- **2.2 Child ticket**: a full process record of the same or another class
  with its own lifecycle/assignment/priority/SLA/closure (parent/child
  incidents, Problem→Change, Incident→Change).
- **2.3 Approval record**: a decision record, not an execution task
  (`sysapproval_approver` in ServiceNow; `ApprovalChain`/`ApprovalGate`/
  `ApprovalVote` in ServiceOps).
- **2.4 Linked object**: context, not a ticket (CI, business service,
  outage, knowledge article, attachment, SLA record, conflict, CAB meeting).

### 3. Incident Management

Lifecycle: New → In Progress → On Hold → Resolved → Closed → Canceled. On
Hold reasons: Awaiting Caller/Change/Problem/Vendor. Process: Intake →
Classification → Prioritization (Impact + Urgency = Priority; P1 Critical …
P5 Planning) → Assignment → Investigation → Resolution → Closure.

**Incident Task**: work delegated without transferring ownership; must not
close the parent directly; parent shouldn't resolve while mandatory tasks are
active.

**Parent/Child Incidents**: separate reported impacts sharing an underlying
cause, each with its own SLA/caller communication — distinct from an
Incident Task (technical, invisible to end users).

### 4. Major Incident Management

Still fundamentally an Incident record with additional roles/workbench/
communications/review. Lifecycle: Potential → Candidate → Review →
Accepted/Rejected → Promoted → Response → Restoration → Resolution → PIR →
Problem creation. Ownership split: Major Incident Manager (coordination),
technical resolver groups (diagnosis/restoration), Problem Manager (later
root-cause process).

### 5. Problem Management

Incident Management asks "how do we restore service now?" Problem Management
asks "why did this happen, and how do we prevent it recurring?"

Typical lifecycle: New → Assess → Root Cause Analysis → Fix
planning/in progress → Resolved → Closed. Process: Identification →
Assessment → Root-cause investigation (Five Whys, fishbone, fault-tree,
timeline, Kepner-Tregoe, log correlation, config comparison, recent-change
analysis) → Workaround → Known Error (a state/knowledge record, not another
operational child ticket) → Permanent correction via a Change (`PRB → CHG →
CTASKS`) → Verification and closure.

**Problem Task**: divides investigation among subject-matter experts (Root
Cause Analysis, General types). A Problem should not resolve while mandatory
Problem Tasks remain active.

### 6. Change Management

A Change Request must answer what is changing, why, affected services/CIs,
business impact, technical risk, implementation/test/backout plans, required
approvers, schedule, post-implementation outcome.

- **6.1 Standard Change**: low risk, repeatable, pre-authorized via approved
  template/model; each instance still validates against the approved
  conditions.
- **6.2 Normal Change**: full assessment and authorization (technical,
  change-management, CAB as applicable).
- **6.3 Emergency Change**: expedited but never "no approval" — still
  requires Emergency CAB or designated emergency approver.
- **6.4 Typical Change states**: New → Assess → Authorize → Scheduled →
  Implement → Review → Closed (or Canceled at any point).

### 7. Change Tasks

Official task types: **Planning, Implementation, Testing, Review**.

**Change Task unlocking model** (implemented as `change_task_gate_block()`):

| Change stage | Planning | Implementation | Testing | Review |
|---|---|---|---|---|
| New | Open | Pending | Pending | Pending |
| Assess | Open | Pending | Pending | Pending |
| Authorize | Usually complete | Pending | Pending | Pending |
| Scheduled before start | Closed | Pending | Pending | Pending |
| Implement | Closed | Open by sequence | Open when predecessor completes | Pending |
| Review | Closed | Closed | Closed | Open |
| Closed | Closed | Closed | Closed | Closed |

Rules:

- Implementation may leave Pending only once the change's approval chain is
  fully Approved (or no chain applies).
- Testing opens once at least one required Implementation task is Closed
  Complete.
- Review opens only once all required Implementation/Testing tasks are
  terminal.
- Planning is never gated by approval.
- **Rejection behavior** (`app.py::supersede_change_approval`): returns the
  change to Awaiting Approval and starts a fresh approval cycle when material
  fields change after approval; cancels the approval chain when a change is
  soft-deleted/cancelled.
- **Parent-child closure**: a Change cannot enter Review while mandatory
  Implementation/Testing tasks are active; cannot close while any mandatory
  task is active; cancelling cascades to Pending/Open tasks; closed tasks
  retain audit history; backout must be its own task or explicit outcome;
  manually added tasks count toward closure validation.

### 8. Request Management

```
Request [sc_request]
└── Requested Item [sc_req_item]
    └── Catalog Task [sc_task]
```

REQ is the order-level container; RITM is one catalog item in the order (own
approval rules, fulfillment group, delivery target, variables, tasks,
outcome); SCTASK is fulfillment work under a RITM.

Process: Catalog selection → variables → REQ/RITM created → approval where
required → fulfillment flow starts → SCTASKs (sequential/parallel/
conditional) → RITM fulfilled → REQ closes when all RITMs finish.

**Closure aggregation** (`catalog_task_update()`): all Closed Complete → RITM
Closed Complete; any Closed Incomplete → RITM Closed Incomplete; all Closed
Skipped → RITM Closed Skipped. Same aggregation RITM→REQ.

**SCTASK is not a child of CHG** — implemented 2026-07-29. SCTASKs belong to
RITMs only; a Change relates to a RITM only through `RecordLink`
(`link_type="requested_item_change"`). When a RITM's SCTASK is linked to a
Change, coordination may proceed freely, but production/implementation work
on that SCTASK is blocked while the linked Change is still New/Awaiting
Approval (`ritm_linked_change()` / `transition_catalog_task()` — returns 409).
This is a task-level check, not a task-type distinction — `CatalogTask` has
no Planning/Implementation/Testing/Review split; a `purpose` field
(Coordination vs. Production) is a flagged, not-yet-implemented candidate
follow-up.

### 9. Request versus Incident

| Situation | Correct record |
|---|---|
| Existing service is broken | Incident |
| User needs a standard service | Catalog Request |
| User needs access | Catalog Request |
| Access that previously worked has stopped | Incident |
| New laptop required | Catalog Request |
| Existing laptop has failed | Incident |
| Standard software installation | Catalog Request |
| Installed software crashes | Incident |
| Password forgotten | Usually Catalog Request or automated service |
| Authentication system outage | Incident |
| Permanent fix required for repeated failures | Problem plus Change |

### 10. Universal Request

A common front-door ticket when the requester doesn't know which department
should handle the matter. **Not currently implemented in ServiceOps**;
tracked as a candidate backlog item if a genuine multi-department front door
becomes a requirement.

### 11. Release Management

Groups multiple Changes/deployment activities into a coordinated delivery. A
Release doesn't replace Change authorization. **Not currently implemented in
ServiceOps**.

### 12. Relationships between the main tickets

- Incident → Problem: many Incidents → one Problem.
- Problem → Change: one Problem → one or more Changes.
- Incident → Change: service restoration requires controlled modification.
- Request → Change: RITM → Change Request when fulfillment requires one.
- Major Incident → Problem: root-cause analysis and prevention.
- Change → Incident: a failed Change may create/link an Incident.
- Change → Problem: a failed/repeatedly-unsuccessful Change may lead to a
  Problem investigation.
- Release → Change: coordinated deployment governance.

### 13. The complete operational chain

```
Monitoring alert or user report → Incident → Service restored using
workaround → Multiple/major incidents identified → Problem → Root cause and
permanent fix identified → Change Request → Planning/assessment tasks →
Technical/business approvals → Implementation/testing tasks →
Post-implementation review → Change closed → Problem verifies permanent
correction → Problem closed → Knowledge/Known Error records updated
```

For a requested service:

```
User submits catalog item → REQ and RITM created → Approval → SCTASK
fulfillment → Change created when production modification is required →
Change approved and implemented → RITM fulfilled → REQ closed
```

### 14. Mandatory governance rules for ServiceOps

**Parent ticket controls**:
- Parent cannot close while mandatory child tasks are active. *(Implemented.)*
- Canceling a parent cascades to eligible child tasks. *(Partial —
  full task cascade is a candidate follow-up.)*
- Closed child tasks remain immutable except via controlled reopening.
  *(Implemented.)*
- Every task must have an assignment group. *(Implemented — non-nullable.)*
- Every closed task must have close code and close notes. *(Not yet
  enforced — candidate follow-up.)*
- Parent resolution must aggregate child outcomes. *(Implemented for RITM/
  REQ; partial for Change via required-task gating.)*
- Failed/incomplete/skipped outcomes must remain distinguishable.
  *(Implemented.)*
- Work notes internal; customer comments externally visible.
  *(Implemented via `TaskNote.visibility`.)*
- All state/assignment/approval/field changes audited. *(Implemented via
  `log_history`/`log_field_changes`/`audit`.)*
- Cross-ticket relationships visible from both records. *(Implemented via
  `RecordLink`/`related_records()`.)*

**Approval controls**:
- Requester must not approve their own high-risk Change. *(Not yet
  enforced.)*
- Approval delegation recorded. *(Implemented:
  `ApprovalVote.delegated_from_id`.)*
- Approval requirements recalculated on material field changes.
  *(Implemented: `supersede_change_approval`.)*
- Rejected approval stops downstream execution. *(Implemented via task
  gating.)*
- Approval comments mandatory for rejection. *(Not yet enforced.)*
- No approval record deleted to bypass a decision. *(Implemented — no
  delete path exists.)*
- All approvals retain timestamp/identity. *(Implemented.)*

**Change Task controls**: as in §7 above, implemented via
`change_task_gate_block()`. Remaining not-yet-enforced candidates: task
dates fitting strictly within a live schedule exception window; automatic
Change-outcome review trigger on task failure; backout task
auto-provisioning on rollback declaration.

---

## Part 4 — Whole-application audit (this session)

Fresh audit performed against `CLAUDE.md`'s rules (not generic best practice),
reading `app.py` (8,015 lines pre-session), `serviceops_core/*` (395 lines
total), 49 template files, all 22 pre-session migrations, and `tools/*`.
Findings are grouped by category; items marked **[fixed this session]** were
addressed and are detailed further in Part 5.

### 1. Code quality / structure

- **High**: The monolith imbalance is severe and getting worse, contrary to
  CLAUDE.md's "avoid expanding the monolithic application file
  unnecessarily"/"continue decomposing" guidance. `app.py` (8,015 lines)
  holds ~112 routes, every model (60+ `db.Model` classes), and almost all
  business logic (workflow execution, change-conflict detection, priority/
  SLA math, webhook signing/SSRF guards), while `serviceops_core/` totals
  only 395 lines across five files. The extraction this module was created
  for has stalled. Best candidates to move: `find_change_conflicts`/
  `precreate_change_conflicts`, `deliver_webhook`/`process_outbox` delivery
  logic, `visible_ticket_query`/`user_can_manage_ticket` authorization
  predicates, workflow action execution.
- **Medium**: `ticket_owning_group` and `user_can_manage_ticket` duplicate
  "resolve owning group" logic that also appears inline in
  `visible_ticket_query` — three paths to one concept. `find_record_by_number`
  is a cross-record-type dispatcher — **[fixed this session: tenant
  filtering added]**, but still a candidate for consolidation into one
  tenant-safe lookup service.
- **Low**: `serviceops_core/__init__.py` is 1 line — the package boundary
  exists in name more than in practice so far.

### 2. Performance

- **High**: Systemic N+1 pattern — zero eager loading anywhere in the
  codebase prior to this session (`grep -c "joinedload|selectinload"` = 0).
  `/tickets/<kind>` rendered `requester`/`assignee` per row (up to ~100 extra
  queries per 50-row page) and called `ticket_owning_group()` per row (each
  issuing its own query) — **[fixed this session: eager loading +
  batch-fetch added, see Part 5]**. `open_work()` had no `.limit()` at all
  on either its ticket or request query — **[fixed this session: capped at
  200 rows each with a "showing first N" UI note, see Part 5]**.
- **Medium**: `dashboard()` issues ≥5 separate `.count()`/`.limit(8).all()`
  queries sequentially on every load of `/`, the busiest route in the app —
  not fixed this session, flagged as a follow-up (would benefit from a single
  combined query or short-lived cache). Global-search-style routes build
  Python-side ID sets from `.all()` before filtering by search term rather
  than pushing the predicate into the query — not fixed this session.
- **Low**: no missing-index gaps found; `tenant_id` columns are consistently
  indexed, `Ticket.number`/`kind`/`state` are indexed.

### 3. Stability / error handling

- **Medium**: `/admin/integrations/process` called `process_outbox()`
  (default `limit=50`) synchronously in the request thread — each event can
  make an SMTP call (10s timeout) and/or webhook POST (10s timeout, up to 3
  redirect hops), worst case ~500s against gunicorn's 60s timeout —
  **[fixed this session: capped to `limit=5`, see Part 5]**. The background
  `tools/outbox_worker.py` remains the correct unbounded drain path.
- Exception handling is otherwise disciplined: zero bare `except:` blocks,
  only 6 `except Exception` blocks total, each paired with rollback where a
  commit was in flight.
- **Low**: migration `20260726_0001`'s baseline intentionally raises on
  downgrade (correct per CLAUDE.md's "never destructively reset" rule) — any
  rollback tooling blindly calling `alembic downgrade base` will hard-fail by
  design; confirm rehearsal scripts account for this.

### 4. Security / tenant isolation

Overall notably better than average for this class of finding.
`tenant_context_id()` fails closed exactly as required: an authenticated user
with a null `tenant_id` raises `TenantResolutionError` rather than defaulting
to tenant 1. All ~30 tenant-owning tables consistently use
`default=tenant_context_id`.

- **Medium** (**[fixed this session]**): `find_record_by_number()` performed
  six separate lookups (Ticket/EnterpriseRecord/CatalogRequest/RequestedItem/
  CatalogTask/OperationalTask) with **no tenant filter on any of them** — a
  cross-tenant existence oracle via record-linking. Fixed: every branch now
  filters by tenant, joining through the owning parent where the child table
  itself carries no `tenant_id` (RITM/SCTASK join to `CatalogRequest`; CTASK/
  PTASK resolve their parent Ticket/EnterpriseRecord and compare tenant).
- **Medium** (open, tracked as B-231's larger follow-up): many child/detail
  tables (`Comment`, `TaskNote`, `Approval`, `GroupMember`, `TaskSLA`,
  `RequestedItem`, `CatalogTask`, `ChangeGovernance`, `TicketAssignmentGroup`,
  `RecordLink`, `TaskHistory`, `OperationalTask`, `TaskCI`, `ApprovalGate`,
  `ApprovalVote`, `ChecklistItem`, `CatalogItemRouting`,
  `ScheduleHoliday`, `ProblemProfile`, `ChangeRevision`,
  `MajorIncidentProfile`, `Favorite`, `RecentView`, `UserPreference`,
  `ExternalIdentity`, `DirectoryGroupMapping/Membership`) have no own
  `tenant_id` column. Safe today only because every current query path joins
  through an already-tenant-scoped parent — there is no DB-level constraint
  enforcing that convention, so a future query written without that join
  would silently violate isolation. This session added `tenant_id` directly
  to `CIRelationship` as one instance of closing this gap (see Part 5); the
  rest remains open and is the single largest remaining tenant-isolation
  risk in the codebase.
- **Good practice confirmed**: CSRF double-submit token verified centrally;
  session cookies HttpOnly/SameSite=Lax/Secure-by-default with a fail-closed
  startup guard; CSP present (`style-src 'unsafe-inline'` is a noted residual
  weakening — worth tightening with nonces if inline styles can be removed);
  SSRF-resistant webhooks (DNS/redirect re-validation, capped redirects,
  HMAC-signed payloads); open-redirect guard on stored start pages;
  `SECRET_KEY` length/presence enforced, sourceable from a mounted secret
  file.

### 5. UX

This app fares well here relative to typical findings: all `<img>` tags carry
`alt` text, no pseudo-button `onclick` divs/spans, flash messaging is
consistently `"error"`/`"success"` only. Gaps: no `"warning"`/`"info"` flash
category exists anywhere despite templates rendering a fixed category set (low
risk, none currently produced); an empty-state copy pass on `open_work.html`/
`tickets.html` was not completed this session (noted as a follow-up, not a
defect).

### 6. Current DB schema shape (as of pre-session baseline)

Migration `20260726_0001` **adopts** the existing SQLAlchemy-model-defined
schema (`db.metadata.create_all(bind)` on a truly empty database, or a
presence check on `{"user","platform_setting","ticket","support_group"}`
otherwise) rather than defining it via DDL — so `app.py`'s ~60 `db.Model`
classes *are* the schema of record, and migrations 0002 onward are
incremental `ALTER TABLE`s layered on top.

- **Ticket/ITIL model**: `Ticket` natively models INC and CHG only (`kind` in
  `{"incident","change"}`). PRB/PTASK/CTASK live in `EnterpriseRecord`
  (generic, `domain`-discriminated) and `OperationalTask` (covers PTASK+CTASK
  via a `task_kind`/`parent_type` discriminator). REQ/RITM/SCTASK are
  separate first-class tables (`CatalogRequest`/`RequestedItem`/
  `CatalogTask`). This matches CLAUDE.md's "do not collapse" rule — the
  record types are genuinely distinct models, though the PRB/PTASK/CTASK
  shared-container approach is a documented, deliberate partial compromise.
- **CMDB (pre-session)**: `ConfigurationItem` had only `name`, `ci_class`,
  `environment`, `operational_status`, `ip_address`, `owner`, `tenant_id`.
  `CIRelationship` had `parent_id`/`child_id`/`relationship_type` with a
  `(parent_id, child_id)` unique constraint and **no `tenant_id` column at
  all**. This matched `docs/BACKLOG.md` B-032's own accurate description of
  the CMDB as "implemented but partial" (no discovery-source field, no
  lifecycle-state history, no attribute schema beyond fixed columns). **This
  session closed the majority of this gap — see Part 5.**

### 7. Docs drift

No material drift found in the areas sampled (CMDB, REST API, tenant
isolation, CTASK detail pages) — this repository's documentation is unusually
disciplined about marking things "in progress" vs. "implemented" vs.
"verified" with specific evidence, and the backlog entries read as accurate
self-assessment rather than aspirational claims. `docs/BACKLOG.md` B-032 and
`docs/blueprints/BLUEPRINT_TRACEABILITY.md` §8.10 both correctly described the
pre-session CMDB as partial before this session's enrichment work began.

---

## Part 5 — This session's changes (implementation log)

This section is the authoritative record of what changed in this pass, for
the next AI/engineer to pick up from. All changes are additive/reversible
per CLAUDE.md's migration rules; nothing here was a rewrite.

### Schema

- **New migration**: `migrations/versions/20260729_0023_cmdb_enrichment.py`.
  Adds to `configuration_item`: `description` (Text), `lifecycle_state`
  (String, default `"In Use"`), `business_criticality` (String, default
  `"Medium"`), `serial_number`, `vendor`, `model`, `location`, `cost_center`
  (Strings), `discovery_source` (String, default `"Manual"`), `install_date`/
  `warranty_expiry_date` (Date), `attributes` (JSON, default `{}`),
  `support_group_id` (FK → `support_group.id`), `created_at`/`updated_at`
  (DateTime). Adds to `ci_relationship`: `tenant_id` (FK → `tenant.id`,
  NOT NULL, backfilled from the parent CI's tenant, indexed) and
  `created_at`; widens the unique constraint from `(parent_id, child_id)` to
  `(parent_id, child_id, relationship_type)`. Both directions (upgrade and
  downgrade) are idempotent-safe (checks existing columns/constraints before
  acting) and downgrade is a clean column/constraint drop, tested against a
  fresh database this session (see Verification below).
- **`app.py` model changes**: `ConfigurationItem` and `CIRelationship`
  classes updated to match, including the new `support_group`
  relationship on `ConfigurationItem` and the tightened `CIRelationship`
  unique constraint.

### Application code

- `app.py::find_record_by_number()` — added tenant filtering to every
  branch (see Part 4 finding).
- `app.py::integrations_process()` route — capped `process_outbox(limit=5)`
  (was unbounded default of 50).
- `app.py::tickets()` route — added `joinedload` for `requester`/`assignee`
  and batch-fetched `TicketAssignmentGroup`/`ChangeOwnership` for the current
  page instead of one query per row via `ticket_owning_group()`.
- `app.py::open_work()` route — capped both the open-ticket and open-request
  queries at 200 rows with a truncation flag surfaced to the template.
- `app.py::seed_itil()` — now creates default "Laptop Request"/"Software
  Request" `CatalogItem` rows on first bootstrap if the tenant has none,
  before the existing routing-assignment loop runs. This is an
  administrator-configurable starting point (explicitly commented as such in
  code), not hard-coded routing logic — an admin can edit/deactivate them
  freely afterward, consistent with CLAUDE.md's "catalog routing must be
  configurable... not hard-coded" rule.
- `app.py::ci_new()`/`ci_edit()`/`cmdb()`/`ci_relationship_add()`/
  `ci_relationship_delete()` routes — updated for the new CI fields, and
  `ci_relationship_delete()` simplified to use `tenant_record_or_404()` now
  that `CIRelationship` carries its own `tenant_id`.
- `app.py::parse_form_date()` — new small helper (mirrors the existing
  `parse_form_datetime()`) for the new date-only CI fields.

### Templates

- `templates/ci_form.html` — full rewrite exposing every new CI field
  (description, lifecycle state, business criticality, serial/vendor/model,
  location, cost center, discovery source, install/warranty dates, owning
  support group).
- `templates/cmdb.html` — list view extended with Lifecycle, Criticality,
  Location, and Owning team columns.
- `templates/open_work.html` — added truncation notices for both sections.

### New tooling

- `tools/load_demo_dataset.py` — realistic non-production dataset loader
  (see Part 2's backlog addition for full description). Requires
  `--confirm-non-production`. Builds ~19 CIs across three service trees
  (Customer Portal / Payroll Service / Email & Collaboration, each with
  Business Service → Application → Database → Server layers) plus shared
  network (`CORE-SW01`, `EDGE-FW01`, `LB01`, `VPN-GW01`) and storage
  (`SAN01`, `BACKUP-NAS01`) CIs, ~32 CI relationships, 2 per-team users for
  each of the 6 IT teams (manager + agent, the managers also added as CCB
  approvers), 5 requester accounts, 8 incidents across varied
  priority/state, 3 problems each with 2 PTASKs, 3 changes (Standard/
  Normal/Emergency) each with governance + CTASKs, 2 catalog
  requests/RITMs/SCTASKs, and 5 knowledge articles.
  - **Scope note, important for whoever uses this data next**: seeded
    changes/problems set a descriptive `state` directly rather than driving
    the live `ApprovalChain`/`ApprovalGate`/`ApprovalVote` engine, so records
    are immediately browsable without a pending approval blocking every
    screen. To exercise the *live* approval workflow itself, submit a *new*
    change/request through the UI against this seeded data (the CCB and
    manager approvers already exist and are eligible) — that exercises the
    real engine end-to-end.
- `Dockerfile` — extended the existing `rm -f` line that excludes
  `tools/load_test_fixture.py` from the production image to also exclude
  `tools/load_demo_dataset.py`, for the identical reason (well-known weak
  passwords, must never be `docker exec`-reachable in a production
  container).

### Verification performed this session

1. `python3 -c "import ast; ast.parse(...)"` on `app.py` and
   `tools/load_demo_dataset.py` after every edit — syntax-clean throughout.
2. `docker compose down -v && docker compose up -d --build` — full flush of
   the local dev PostgreSQL volume and Docker uploads volume, then a fresh
   build/deploy from current source.
3. Confirmed migration head after fresh install:
   `SELECT version_num FROM alembic_version;` → `20260729_0023`.
4. Confirmed `/health` → `{"status":"ok"}` and all three containers
   (`app`, `db`, `worker`) reported healthy.
5. Ran `tools/load_demo_dataset.py --confirm-non-production` inside a
   throwaway container built from the current image (mounted read-only,
   since the app container's root filesystem is intentionally read-only —
   itself a confirmed-good least-privilege container control). Output:
   `configuration_items: 19, ci_relationships: 32, tickets: 11, problems: 3,
   requests: 2, knowledge_articles: 5, users: 18`.
6. Logged in as `admin` over HTTP with a real CSRF-token round trip (GET
   `/login` → extract `_csrf_token` → POST credentials) and confirmed
   `HTTP 200` on `/`, `/cmdb`, `/tickets/incident`, `/tickets/change`,
   `/work/open`, `/knowledge`, `/cmdb/new`.
7. Confirmed the new CI fields render with real seeded data:
   `"Criticality"`, `"Lifecycle"`, `"PORTALDB01"`, `"CORE-SW01"`, `"Owning
   team"` all present in the rendered `/cmdb` HTML.

### Known gaps this session did not close (explicitly deferred, not silently skipped)

- The REST CMDB endpoint (`PUT /api/v1/cmdb/configuration-items`,
  `docs/API_REFERENCE.md` §9) was **not** extended to accept the new CI
  fields — it still only accepts `name`/`ci_class`/`environment`/
  `operational_status`/`ip_address`. Extending it (and its OpenAPI schema,
  and the field-projection registry in `config/field_projections.json` if
  CI records are ever exposed through governed export/search projections) is
  a clean, contained follow-up.
- The broader tenant-isolation follow-up from B-231 (the ~20 remaining
  child tables with no own `tenant_id`) was not addressed beyond
  `CIRelationship`.
- `dashboard()`'s chatty multi-query hot path (Part 4 finding) was not
  optimized this session.
- No automated test was added for the new CMDB fields/migration or the
  `find_record_by_number` tenant fix — `tests/test_app.py` should gain
  coverage for both before this is considered release-ready, per CLAUDE.md's
  "add negative authorization tests" and "add migration tests for schema
  changes" rules.
- The production Docker image itself was not rebuilt/pushed anywhere in this
  session — only the local dev Compose stack was flushed, rebuilt, and
  verified, per the user's explicit scope for this pass (local/dev only).

---

## Part 6 — Requirements traceability matrix

(Full text of `docs/TRACEABILITY_MATRIX.md`. Status meanings: **Verified**
has current automated evidence; **Implemented** has code but incomplete
external/runtime proof; **Gap** is not production-ready.)

| Requirement/source | ServiceOps evidence | Status | Backlog |
|---|---|---|---|
| Unified navigation, search, favorites, history, preferences | `templates/base.html`, `/ui/search`, favorites/recent views, tests | Verified | B-021 |
| User profile, user list and administration home | tenant-scoped `/profile`, `/admin/users`, `/admin/users/<id>`, `/admin` | Verified | B-248 |
| Categorized personal interface settings | `/preferences` categories; light-only governed by ADR-012 | Verified for implemented settings | B-248, B-240 |
| Lists, filters, forms, activity, attachments, checklists | shared task-derived record shell, Event history, rendered-browser tests | Verified | B-022, B-245, B-247, B-248 |
| Visual task boards | `/task-board`, move endpoint and test | Verified | B-023 |
| Branding/logo/theme configuration | installer and `/admin/settings`; light-only UI | Implemented | B-024 |
| Guided help/tours | interactive step-by-step tour; static help articles | Partial | B-120 |
| Full configurable workspace/page-builder | no page designer or metadata runtime | Gap | B-121 |
| Production-only initialization | seed, installer, Compose, cleanup tool and tests | Implemented | B-001 |
| Team-manager and CCB approval chain | named manager controls, explicit CCB grants, chains/gates/votes | Implemented | B-030 |
| Approval and lifecycle integrity | centralized transition guards, adversarial tests | Verified | B-034 |
| Assignment-group operational authorization | shared INC/CHG read, explicit owning-team mutation guard | Verified | B-035, B-042 |
| ITIL related-record network | `RecordLink`, `OperationalTask`, REQ/RITM/SCTASK hierarchy | Verified | B-031, B-037 |
| Ticket history and change reapproval | `TaskHistory`, `ChangeRevision`, superseded chains | Verified | B-036 |
| Task-to-CMDB relationships | primary/affected CIs, impacted services, conflict detection | Implemented | B-032 |
| Catalog hierarchy and task orchestration | multi-RITM REQ, multiple team-owned SCTASKs, roll-up | Verified | B-033 |
| Configurable catalog fulfillment routing | per-item routing, Windows defaults, Service Desk fallback | Verified | B-038 |
| Catalog item administration | admin create/edit/deactivation | Verified | B-041 |
| Catalog request visibility boundaries | participant/fulfillment/approver/admin policy | Verified | B-039 |
| Cross-module object and field authorization | centralized policies, fail-closed field registry | Implemented; independent review pending | B-005, B-040, B-203 |
| AD/LDAP and Keycloak authentication | authentication code, installer checks, group mapping | Implemented; external proof absent | B-061 |
| Docker and external PostgreSQL deployment | Compose definitions, `./serviceops` lifecycle | Implemented | B-050 |
| Kubernetes high availability | Helm resources/PDB/network policy | Implemented; cluster proof absent | B-051 |
| Versioned database migrations and tenant foundation | Alembic baseline + tenant revision, backfill, tests | Migration path verified at full scale (2026-07-28); tenant_id sprawl and review pending | B-002, B-005, B-202, B-231 |
| CSRF protection and hardened session lifecycle | central guard, injected tokens, rotation, tests | Verified | B-003, B-201 |
| Tamper-evident audit evidence | tenant-specific hash chains, key rotation, retention policy | Implemented; external validation pending | B-004 |
| Versioned REST API foundation | tenant/user-bound clients, scopes, projections, OpenAPI | Implemented for initial contract; broader resources pending | B-204 |
| Responsive PWA foundation | dynamic manifest, shell-only service worker with tests | Implemented; offline records deferred | B-205 |
| Durable integration foundation | transactional outbox, worker, retry/dead state, evidence | Implemented with simulated adapters | B-130 |
| Priority and SLA governance | Git-backed matrix, business schedules, breach notifications | Implemented; OLA/escalation pending | B-206 |
| Declarative workflow foundation | validated package, immutable versions, retries, evidence | Implemented; broader catalogue pending | B-207 |
| Durable workflow orchestration | wait cursor/resume, evidence, triggers, rate limits | Implemented; recurrence/subflows pending at time of writing (later delivered, see B-209) | B-208 |
| Scheduled workflows and subflows | subflow expansion, tenant schedules, scheduler claims | Implemented; calendar/blackout pending | B-209 |
| Bootstrap credential lifecycle | mounted-file priority, split Secrets, rotation | Implemented; external vault ceremony pending | B-006, B-210 |
| Supply-chain evidence | pinned deps/images/actions, Trivy, SBOM, Cosign, attestations | Implemented; GHCR/cluster proof pending | B-007, B-210 |
| Production observability/SLOs | health endpoints only | Gap | B-070 |

### Connection-dependent capability boundary

The following require the deploying organization's systems, policies,
credentials, and representative test environments: MFA/SCIM, email/SMS/
contact center, SIEM/EDR/scanners, infrastructure discovery, HRIS/ERP/CRM,
DevOps integrations, mobile/offline applications, external AI services, and
regulated retention/eDiscovery. They must be delivered through explicit
adapters and are not represented as built-in capabilities.

---

## Part 7 — UI capability mapping and BP-001 blueprint traceability

(Full text of `docs/UI_CAPABILITY_MAPPING.md` and
`docs/blueprints/BLUEPRINT_TRACEABILITY.md`/`BLUEPRINT_REGISTRY.md`.)

### Australia UI guide capability mapping

Source reviewed: *Australia ServiceNow AI Platform user interface*, 1,148
pages, updated July 7, 2026. This mapping uses the source guide as a
behavioral reference only — ServiceOps does not copy its text, images,
product names, or proprietary runtime.

| Source guide family | ServiceOps implementation |
|---|---|
| Next Experience and unified navigation | Unified top navigation, collapsible app nav, global search, favorites, history, notifications, help, preferences, role-aware landing pages |
| Landing pages and dashboards | Operational dashboard, analytics workspace, workload counters, role-based visibility, selectable start page |
| Configurable workspace | Purpose-built ticket/request/change/CMDB/catalog/approval/analytics/ITIL admin workspaces |
| CMDB discovery | Manual admin create/edit/retire for CIs and CI-to-CI relationships; automated registration via `PUT /api/v1/cmdb/configuration-items` and `tools/cmdb_sync_agent.sh` |
| Lists and filters | Searchable/filterable lists, states, priorities, badges, responsive tables, empty states |
| Forms and activity | Structured forms, validation, comments/activity stream, work notes, approvals, SLAs, checklists, attachments, audit events |
| Favorites and history | Per-user persistent favorites and recently viewed pages |
| Notifications | Per-user inbox with unread counts, clickable links to source records |
| Reference fields | Type-ahead lookups for CIs and cross-record linking |
| Assignment and reassignment | Group-level assignment always by team name; team-to-team reassignment restarts change approval |
| Manager/team work views | Manager portal, unified "My tasks" queue |
| Dashboard personalization | Admin-configurable dashboard sections, live P1/P2 signal |
| Personalization and accessibility | Categorized preferences; density/font/contrast/motion/tooltips; light-only (ADR-012) |
| User profile and administration | Self-service profile, admin-controlled identity/role/active/department, searchable user list |
| Service Portal | Employee catalog, knowledge search, request tracking, self-service cases |
| Visual Task Boards | Drag-and-drop lifecycle lanes backed by ticket state/audit/SLA |
| Global search | Tickets, knowledge, enterprise work, CIs |
| Attachments and checklists | Persistent uploads/downloads, actionable checklists |
| Guided help and onboarding | Help Center, contextual guidance, navigation tour |
| Themes and branding | Light-only design tokens; deployment-owned branding via installer/admin settings |
| Core UI developer tooling | Flask templates, reusable styles, routes, tests |
| CMS/UI Builder/widget APIs/Angular/Jelly/ServiceNow scripting | Not applicable — vendor-specific; ServiceOps uses Flask/Jinja/SQLAlchemy/CSS/JS |
| Advanced Work Assignment/Agent Chat/Virtual Agent/voice/predictive | Requires external messaging/telephony/workforce-routing/AI services; not represented as operational |
| Native mobile apps and offline distribution | Responsive web only; no native app publishing |

**Verification expectation**: every capability described as implemented must
have a working route/UI, persistent data, role enforcement, and automated or
live runtime verification.

### BP-001 programme traceability

BP-001 defines a multi-release platform programme, not a single feature.
"Covered" means a currently evidenced foundation exists, not that the
complete section is delivered.

| BP section | Current foundation | Major missing scope | Disposition |
|---|---|---|---|
| 1 Platform layers | Identity, tasks, ITIL records, service/CI links, approvals, UI, analytics, audit | Formal module boundaries, durable automation, complete governance plane | Programme |
| 2 Queue security | Central visibility helpers, governed REST/export/search projections | Compiled relationship-aware policy engine, independent review | P0 |
| 3 Queue catalogue | Ticket lists, task board, approvals, requests | Personal/team/practice/management queue catalogue | P1 |
| 4 Authorization | RBAC, tenant-aware root policies, transition guards, field permissions | ABAC/ReBAC policy compiler, independent review | P0 |
| 5 Access levels | Git-backed action vocabulary, role grants, governed projections | Relationship-aware compiled bindings, independent review | P0 |
| 6 Core data model | Ticket/EnterpriseRecord/request/task/history models | Common versioned work-item foundation | Architecture decision |
| 7 Relationships | INC/PRB/CHG/REQ/RITM/PTASK/CTASK/SCTASK and CI relationships | Duplicate/outage/alert/release/deployment/vendor relationships | P1 |
| 8.1 Interaction | No dedicated interaction model | Complete interaction intake/classification/conversion | P1 |
| 8.2 Incident | Core incident, parent/child, major profile, SLA, CI, relationships | Full hold reasons, routing, escalation, survey, auto-close | P1 |
| 8.3 Major incident | MajorIncidentProfile and coordination fields | Full roles, bridge, status page, PIR, follow-up actions | P1 |
| 8.4 Requests/catalog | REQ/RITM/SCTASK, admin, routing, approvals | Catalogs/typed variables/entitlements/pricing/order guides | P1 |
| 8.5 Problem | PRB, PTASK, known error, RCA/workaround/fix and links | Configurable models, clustering, risk acceptance, automation | P1 |
| 8.6 Change | Types, plan, risk, CCB, CTASK, conflicts, reapproval | Standard catalog, CAB meetings, blackout windows, PIR evidence | P1 |
| 8.7 Knowledge | Basic article list/create/search | Bases, lifecycle, versions, feedback, analytics, translation | P1 |
| 8.8 Service levels | Definitions, task SLAs, Git-backed matrix, calendars, breach escalation | OLA/contracts, prediction, retroactive recalculation | P0/P1 |
| 8.9 Events | No event/alert domain | Ingestion, normalization, correlation, suppression, CI binding | P1 |
| 8.10 CMDB | CI classes/relationships/task links/conflict checks/manual+REST CRUD; **this session enriched CI attribute depth substantially — see Part 5** | Identification/reconciliation, discovery beyond self-reported facts, history/certification | P1 |
| 8.11 Release/deployment | Change tasks only | Separate release/deployment models, evidence, waves | P1 |
| 8.12 Improvement | Generic enterprise module only | Purpose-built continual-improvement register | P2 |
| 9 Priority | Priority field | Impact/urgency matrix (implemented — this row is stale in the source doc), justification, controlled P1 criteria | P0 |
| 10 Assignment | Explicit teams, team-scoped assignees, catalog routing, team reassignment | Ordered configurable rules, skills, on-call, workload | P0/P1 |
| 11 Approvals | Chains, gates, any/all/majority, sequential stages, reapproval | Delegation, timeouts, dynamic resolution, signatures | P0/P1 |
| 12 Web UI | Shell, lists, forms, board, catalog, admin settings, type-ahead, manager portal | Advanced list engine, workspace personas, tabs, mobile | P1/P2 |
| 13 Rules/workflows | Git-backed versions, subflows, triggers, waits, retry, replay, simulation | Broader actions, blackout scheduling, concurrency quotas | P0 |
| 14 Service model | Services, offerings, CIs, assets, relationships | Full hierarchy, governance, reconciliation, import APIs | P1 |
| 15 Search | Access-aware global and domain search | Full text index, facets, typo/synonym, analytics | P1 |
| 16 Communication | In-app notifications, durable SMTP/webhook/Teams delivery | Templates, preferences, digests, inbound email, SMS/push | P0/P1 |
| 17 Identity/tenancy | Local, LDAP/AD, Keycloak OIDC, tenant migration/isolation | SAML, SCIM, MFA policy, session inventory, independent review | Architecture/P0 |
| 18 Security/compliance | Headers, CSRF, authorization, audit evidence, key rotation, SBOM | Representative registry/cluster validation, malware scanning, review | P0 |
| 19 Analytics | Basic access-aware dashboard | Full KPI definitions, time series, CSAT, scheduled reports | P1 |
| 20 APIs/integrations | REST v1 ticket/incident contract, scopes, cursor pagination, OpenAPI | Broader resources, OAuth2, rate limits, webhooks, imports | P0/P1 |
| 21 Architecture | Flask modular monolith, PostgreSQL, Docker/Helm | Decision on modularization vs. rewrite plus search/cache/event services | Architecture decision |
| 22 Config deployment | Container configuration and admin settings | Git-backed config packages, diff, validation, promotion, rollback | P0/P1 |
| 23 Implementation order | Several initial/core capabilities exist | Execute dependency-ordered programme with release gates | Governed roadmap |
| 24 Deferred features | Current product largely follows this constraint | Explicit decision records for intentionally deferred features | Governance |
| 25 Credible core | Chains, lifecycle controls, initial tenant isolation verified | Field security, durable timers, calendars, APIs, DR proof | Release gate |

**Programme acceptance gate**: no section becomes Verified until its atomic
requirements have automated tests, authorization tests, documentation,
migration/rollback evidence, deployment evidence, and any required
external-system validation. External services (AD, Keycloak, email, object
storage, search, Kubernetes) cannot be certified using mocks alone.

**Approved architecture disposition**: one organisation initially with
tenant-aware conventions enforced now; incremental bounded-module refactor,
no rewrite; light-only theme; PostgreSQL standard profile with enterprise
services as optional adapters; SMTP/webhooks/monitoring/Teams integration
priority; versioned REST first, GraphQL deferred; responsive PWA first,
preserving future native-client contracts; Git-backed declarative
configuration; security/platform foundations before visible expansion; data
preserved via reversible versioned migrations.

**Registered blueprint source**: BP-001, "Blueprint for building your own
ServiceNow-class ITSM platform," received 2026-07-26, SHA-256
`4c4d4f0b6e589e277b7663e6e99e2699817dca567cdeda853585ab9cf759df48`, 2,060
lines, 43,034 bytes. The registered source is immutable; requirement
interpretation belongs in this traceability section, not in silent rewrites
of the supplied wording.

---

## Part 8 — REST API reference

(Full text of `docs/API_REFERENCE.md`, version 1.0 · ServiceOps 1.19+. **Note
from this session**: the CMDB endpoint's five-field contract described below
is unchanged by this session's CI schema enrichment — see Part 5's "Known
gaps" for why, and treat extending this endpoint as a清 follow-up.)

### 1. Scope and base URL

Supported API is REST v1: `https://serviceops.example.com/api/v1`. Live
OpenAPI 3.1 document: `GET /api/v1/openapi.json`. Human-readable rendering:
`GET /api/v1/docs`. Current contract supports ticket discovery, incident
creation, controlled ticket updates, workflow triggering, CMDB
auto-registration, and monitoring-event ingestion. Browser session cookies
are not API credentials.

### 2. Create an API client

Sign in as administrator → **Administration → API clients** → select the
active user whose permissions the integration will exercise → select only
required scopes → create and copy the token immediately (shown once,
prefixed `sop_`; ServiceOps stores only an HMAC-derived verifier). Every
request executes as the selected user — a scope never bypasses that user's
tenant, role, team ownership, record visibility, lifecycle approvals, or
field-projection rules.

| Scope | Purpose |
|---|---|
| `tickets:read` | List and retrieve visible incidents and changes |
| `incidents:create` | Create incidents |
| `tickets:update` | Update an authorized owning-team ticket |
| `workflows:execute` | Trigger configured API workflows for an authorized ticket |
| `cmdb:write` | Upsert configuration items by name |

### 3. Authentication and common headers

```http
Authorization: Bearer sop_REDACTED
Accept: application/json
Content-Type: application/json
X-Request-ID: 9acdd549-4938-4eb2-bf8c-175ba8de2adc
```

State-changing endpoints also require `Idempotency-Key` (1–128 chars,
letters/digits/`.`/`_`/`:`/`-`). Repeating the same key/method/path/body
replays the stored response with `Idempotency-Replayed: true`; reusing the
key for a different request returns `409`.

### 4. List tickets

`GET /api/v1/tickets?type=incident&state=In%20Progress&limit=50&cursor=0`
(scope `tickets:read`). `type` optional (`incident`/`change`), `state`
optional exact match, `limit` 1–100 default 50, `cursor` last returned
numeric ID (start 0). The `internal` object (assignment group/assignee) is
returned only to agent/manager/admin audiences.

### 5. Retrieve one ticket

`GET /api/v1/tickets/INC0000041` (scope `tickets:read`). Case-insensitive
numbers. Out-of-tenant/visibility records return `404`.

### 6. Create an incident

`POST /api/v1/incidents` (scope `incidents:create`). Required: `title`,
`description`, `assignment_group_id` (must be an active IT fulfilment team
in the client's tenant). `priority` defaults `P3`. Unknown fields rejected.
Returns `201` with the governed ticket document; SLA/assignment/history/audit
created in the same transaction.

### 7. Update a ticket

`PATCH /api/v1/tickets/INC0000041` (scope `tickets:update`). Allowed fields:
`state`, `priority`, `assigned_to_id` (null clears it; non-null must be
active and in the owning team). Acting user must have update/assignment/
transition permission and be an active member/manager of the owning team
(or admin). Approval/lifecycle guards apply server-side — the API cannot
move a change into implementation merely because the token has update scope.

### 8. Trigger an API workflow

`POST /api/v1/tickets/INC0000041/workflow-events` (scope
`workflows:execute`). Acting user must be authorized to manage/transition the
ticket. Returns `202` with an `event_id`; execution is durable and
asynchronous.

### 9. CMDB auto-registration

`PUT /api/v1/cmdb/configuration-items` (scope `cmdb:write`). Idempotent by
design — **no** `Idempotency-Key` required, meant to be called on every agent
run. Matched by `name` within the tenant: first call `201`, later calls
`200`. **Only `name`, `ci_class`, `environment`, `operational_status`,
`ip_address` are currently accepted** — unknown fields rejected with `400`.
This means the new fields added in Part 5 (`serial_number`, `vendor`,
`model`, `location`, `cost_center`, `discovery_source`, `install_date`,
`warranty_expiry_date`, `lifecycle_state`, `business_criticality`,
`support_group_id`, `attributes`) are **not yet reachable via this
endpoint** — only via the `/cmdb` web UI. A ready-to-use shell agent is at
`tools/cmdb_sync_agent.sh`, with an example Puppet class at
`deploy/puppet/cmdb_sync.pp.example`.

### 10. Monitoring ingestion

Monitoring sources use separate one-time credentials (not API-client
tokens), created under **Administration → Integrations**.
`POST /api/v1/monitoring/{source_id}/events` requires `external_id`,
`severity` (`critical`/`high`/`medium`/`low`/`info`), `resource`, `summary`.
Deduplicated by source+`external_id`: first ingestion `201`, replay `200`
with `"deduplicated": true`. Creates an EVT record and routes an
investigation task to the source's configured team.

### 11. Error contract

```json
{"error": {"status": 403, "title": "Forbidden", "detail": "The API client lacks scope tickets:update.", "request_id": "9acdd549-4938-4eb2-bf8c-175ba8de2adc"}}
```

| Status | Meaning |
|---|---|
| `400` | Invalid JSON, fields, parameters, transition, or idempotency key |
| `401` | Missing, invalid, or revoked token |
| `403` | Scope, role, team, tenant, or action is not authorized |
| `404` | Record does not exist or is intentionally hidden |
| `409` | Idempotency conflict, integrity failure, or state conflict |
| `429` | Reserved for enforced rate limits in a future compatible revision |
| `500` | Unexpected server failure; retain the request ID for investigation |

Retry only transient `5xx` with exponential backoff + jitter and the same
idempotency key. Never auto-retry `400`/`401`/`403`/`404`/`409`.

### 12–13. Quick starts

cURL: set `SERVICEOPS_URL`/`SERVICEOPS_TOKEN`, use
`--fail-with-body --silent --show-error`, avoid the token on the command
line, `unset` it when done. Python: use `requests`, always set
connect/read timeouts, validate TLS, log request IDs not credentials.

### 14. Current compatibility boundary

REST v1 is the supported integration surface. GraphQL is intentionally
deferred (ADR-015). CMDB registration is the first CMDB REST resource,
deliberately narrow. The API does not yet expose catalog ordering, REQ/
RITM/SCTASK, PRB/PTASK, CHG/CTASK creation, CI relationship management,
approvals, attachments, knowledge, users, or reporting as public REST
resources — do not automate browser forms as a substitute.

---

## Part 9 — Complete platform manual (operations)

(Full text of `docs/OPERATIONS_MANUAL.md`, version 1.26.3 as last authored;
subsequent 1.27.x changes haven't required rewriting this section. As of
1.27.22, `OPERATIONS_MANUAL.md` gained two large new chapters — "3A. Visual
walkthrough" (22 real screenshots of every major workspace, each with an
explanatory caption) and "3B. Common task walkthroughs" (step-by-step
procedures for incident/change/catalog/manager-portal workflows) — plus a
`tools/generate_operations_manual.py` upgrade that renders Markdown tables as
real bordered/styled tables and images as scaled, captioned figures instead of
flattened text. These are deliberately **not** reproduced here: screenshots
are binary image files that cannot be represented in this Markdown merge, and
duplicating the walkthrough prose without its screenshots would misrepresent
what changed. Read `docs/OPERATIONS_MANUAL.md` directly (or the regenerated
`ServiceOps_Complete_Platform_Manual.pdf`) for the current, complete visual
and procedural content; this section remains the source for the still-current
narrative/reference material below it, which is otherwise unaffected.)

### 1. Purpose and operating model

ServiceOps is an enterprise service-management platform for requesters,
fulfillers, team managers, CCB members, and platform administrators:
incident, request, problem, change, catalog, knowledge, CMDB, asset, SLA,
approval, audit, analytics, and enterprise workspaces. No deployment
mechanism eliminates every infrastructure/operator failure — the standard
uses prevention, validation, observability, tested recovery, least
privilege, immutable releases, and documented rollback rather than claiming
infallibility.

### 2. Roles and teams

| Role | Normal responsibilities |
|---|---|
| Requester | Submit and track requests and incidents, search knowledge |
| Agent | Triage, assign, fulfill, document, and resolve operational work |
| Manager | Agent work plus team oversight and manager approvals |
| CCB member | Review planned changes, risk, evidence, schedule, and backout plan |
| Administrator | Identity, service operations settings, CMDB, audit, and platform operation |

CoreApps, Database, Network, Windows, Unix, and SSD are standard fulfillment
teams. AD groups (e.g. `gg_unix`) map to teams; membership reconciles at
login. Manager appointment and CCB authority remain explicit admin
decisions. Operational ownership is separate from approval authority: every
incident/request/change has one owning IT fulfillment team; an active
member of that team, its manager, or an admin can change operational
fields; assignees must stay active members of the owning team. All IT
teams' active members/managers can *read* every incident/change (triage,
handoffs, awareness); only the owning team or an admin can *change* it. CCB
membership grants approval authority only, never cross-team operational
control.

### 3. End-user guide

**REST API docs**: `docs/API_REFERENCE.md` / `/api/v1/docs` /
`/api/v1/openapi.json` (see Part 8).

**Governed record projections**: object visibility and field visibility are
separate controls. Central tenant-aware object policies decide record
access; `config/field_projections.json` (validated, Git-backed) decides
which fields leave the app for a given resource/audience. Requester
projections exclude internal assignment details; unknown resources/
audiences/duplicate fields fail application startup.

**Browser request security**: every unsafe request needs a session-bound
CSRF token (rendered into forms + a JS header for interactive actions,
rotated post-auth). Session cookies HttpOnly/SameSite=Lax,
`SESSION_COOKIE_SECURE` defaults `true` everywhere; app refuses to start
insecure without the explicit `ALLOW_INSECURE_SESSION_COOKIES=true` escape
hatch (dev/localhost only, never production). A user with no resolvable
`tenant_id` is logged out and rejected 403 rather than defaulted. CSP header
sent on every response.

**Database migration gate**: production schema changes are Alembic
revisions; Compose runs the gate before init, Kubernetes uses a dedicated
Helm migration Job (replicas set `AUTO_MIGRATE=false` and refuse to start on
a stale schema). `20260726_0001` adopts an existing schema or creates a
fresh one, with a deliberately non-destructive (backup-requires) downgrade.
`20260726_0002` creates the default tenant and backfills all root records.
Bundled rehearsal: `./serviceops rehearse-migrations 100000` (clones into an
isolated `_migration_rehearsal`-suffixed DB, adds representative records,
downgrades/rolls-forward, compares counts+fingerprints, always cleans up;
refuses in external-database mode).

**Tamper-evident audit**: `20260726_0003` extends every audit event with
UUID, correlation ID, source context, integrity algorithm, previous/event
hash; existing events sealed into a legacy chain, new events HMAC-SHA-256.
DB triggers reject audit UPDATE/DELETE. Admin audit page verifies the full
tenant chain before display; export blocked if verification fails,
otherwise returns signed JSON evidence
(`X-ServiceOps-Audit-Signature`/`-Key-ID`). `20260726_0011` adds per-event
key IDs and forward-only rotation from the audit page after full-chain
verification. Minimum seven-year retention + legal hold governed from the
same page; only active `siem` connections receive `audit.created` events.
Protect `AUDIT_INTEGRITY_KEY` as an independently rotated secret.

**Declarative action/field authorization**: `config/authorization.json` is
the Git-controlled role/action vocabulary (discover, read, comment, create,
update, assign, accept, transition, resolve, close, reopen, approve,
delegate, relate, export, report, delete, purge, configure, administer,
security-administration). Startup fails on malformed policy or unknown
role action. Field projection is separate from object visibility (see
above); requesters never receive internal ticket history, work notes,
change plans, approvals, SLA internals, MI coordination, affected-CI
internals, operational tasks, or checklists.

**REST API v1**: admins create/revoke identities under **Administration →
API clients**; each client binds to one active user and inherits their
authorization, further restricted by explicit scopes. Tokens shown once,
stored as HMAC hash+prefix. `API_TOKEN_PEPPER` rotation revokes every token
by design.

**Responsive PWA**: dynamic company/instance manifest, root-scoped service
worker caching only CSS/JS shell assets (never HTML/auth/API/tickets/
attachments). HTTPS required outside localhost. Offline operational
records explicitly deferred pending encrypted storage/revocation/data-loss
policy.

**Durable integrations and monitoring**: `20260726_0005` adds a
PostgreSQL-backed outbox, per-channel delivery evidence, encrypted webhook/
Teams connections, authenticated deduplicated monitoring sources. The
Compose/Kubernetes worker claims due events with `FOR UPDATE SKIP LOCKED`,
retries with bounded exponential delay, moves to `Dead` after 5 failures.
SMTP: STARTTLS by default, admin-controlled. Webhooks: HTTPS + HMAC-SHA-256
signature headers; literal loopback/private/link-local/non-HTTPS targets
rejected at config time; at delivery time the destination is re-resolved
and redirects are manually re-validated per hop (up to 3), closing most
DNS-rebinding/redirect-SSRF risk — a narrow TOCTOU window remains between
re-resolution and the HTTP client's own connect-time DNS lookup; true IP
pinning is tracked as future work. Monitoring sources bind to a team;
`POST /api/v1/monitoring/{source_id}/events` validates severity/payload,
dedupes by source+external ID, creates EVT+EVTASK, maps
critical/high/medium/low → P1/P2/P3/P4.

**Workflow state integrity**: approval-derived states are controlled by the
approval engine only — never manually selectable. A change stays `Awaiting
Approval` until manager+CCB gates complete. Admins cannot cast another
approver's vote. Invalid transitions return `409` with no data change.

**ITIL related-record model**:

| Record | Purpose and supported relationships |
|---|---|
| INC | Restore service; parent/child INC, primary/affected CIs, PRB, fix CHG, caused-by CHG, converted REQ |
| PRB | Root cause, workaround, known error, permanent fix; many INCs, PTASKs, multiple CHGs, knowledge |
| PTASK | Independently assigned investigation/resolution work under a PRB |
| CHG | Risk, authorization, schedule, overall implementation control; related INCs/PRBs/RITMs/CIs/services |
| CTASK | Planning/implementation/testing/review work under a CHG |
| REQ | User order container with one or more RITMs |
| RITM | Catalog item, variables, approvals, fulfillment stage; may link a controlled CHG |
| SCTASK | Independently assigned fulfillment work under a RITM |

A required open CTASK blocks its CHG completing; a required open PTASK
blocks its PRB completing; a RITM completes only once all SCTASK work is
terminal; a REQ completes only once all RITMs complete. Major-incident
coordination is an INC extension, not a separate prefix.

**Ticket history and approval-safe change revisions**: every record's
chronological history captures actor/time/event/field/old/new/details.
Material CHG approval inputs: purpose/description, type, risk, impact,
implementation/test/backout plan, planned window, primary CI. Editing any
of them preserves the previous chain as history, marks it Superseded,
increments the plan revision, returns the CHG to Awaiting Approval, creates
a fresh chain, and notifies every approver once. An old approval is never
silently applied to a materially different plan.

**Disposable test fixtures** (updated per this session):
`tools/load_test_fixture.py` (unchanged) creates an admin + one
manager/CCB approver per IT team with well-known weak passwords
(`admin`/`admin`, `coreapps`/`coreapps`, etc.) plus minimal disposable
catalog/CI/asset/knowledge/service-offering records; never automatic, always
excluded from the production image. **New this session**:
`tools/load_demo_dataset.py` — same non-production/exclusion guarantees, but
builds a much deeper realistic dataset (full CMDB service trees, per-team
named users, a representative INC/PRB/CHG/REQ/RITM/SCTASK/KB spread) — see
Part 5 for full detail. Neither should ever be exposed on a network-reachable
instance or reused for production data.

**Navigation**: role-appropriate left navigator; top bar has global search,
favorites, history, notifications, help, preferences. Preferences control
density/font-scale/contrast/motion/tooltips/keyboard/date-display/sidebar-pin/
start-page. Self-service profile covers name/email/title/phone/timezone/
date-format; role/active-state/department/team-membership/manager-authority/
CCB-authority are never self-service. Light-only, no theme selector
(ADR-012). Admin home is a capability-oriented entry point; Users & roles
gives tenant-scoped search + editable records, role/active/department
gated to `security_administer`.

**Incidents**: dense two-column operational form with a persistent
Update/Resolve header; body exposes number/caller/contact type/state/
category/subcategory/impact/urgency/calculated priority/service offering/
primary CI/assignment group/assignee/notification preference/short
description/description. Event history (field-level old/new + actor/time)
follows immediately. The same task-derived model covers changes, problems,
other enterprise records, and request containers; list workspaces share a
New/search/filter bar, filter summary, record count, pagination, priority
indicators, operational columns.

**Requests and catalog**: select item → variables/justification → submit →
REQ/RITM/approvals/SCTASK created. Fulfillment routing is
administrator-controlled under **Administration home → Service delivery and governance → Catalog and
fulfillment routing**; Laptop/Software route to Windows by default (and, as
of this session, both catalog items themselves are now auto-created on
first bootstrap — see Part 5). Legacy items without an explicit route fall
back to active Service Desk; ordering fails closed if neither exists.
Catalog request visibility is need-to-know: requested-by/for, fulfillment
team members/managers, SCTASK-assigned teams, named approvers, and admins
only.

**Changes**: must state type, affected CI, owning team, risk, impact,
planned window, implementation/test/backout plans. Review conflicts before
approval. CCB approval is authorization, not technical validation or
implementation-team membership. The New Change form now also accepts a
repeatable "Additional configuration items" picker alongside the primary CI,
linked via the existing `TaskCI` mechanism at creation time; adding an
affected CI to an approved change is still a material change (new approval
cycle).

**Sidebar profile card**: shows the signed-in user's name, avatar, and
active role. A user holding more than one granted role sees an "Acting as
{Role}" control there (not in the top nav) to switch active role without
signing out; single-role users never see it. A full-width, text-labeled
"Sign out" button sits below it.

**System Health** (Administration home → System): application-error table
(`ApplicationLog`) plus a raw `LOG_DIR` request-log-file viewer, both with
combinable Splunk-style filters (level, logger, path, request ID, date
range; method/status on the log-file viewer) and CSV/JSON/NDJSON/text export
(`/admin/system-health/errors/export`, `/admin/system-health/logs/export`,
admin-only, audited, 10k-row cap). `docker logs`/`kubectl logs` mirror the
same detailed JSON lines as the in-app viewer and the log file.

**Knowledge, CMDB, assets, boards**: search knowledge before duplicating
work; use the CMDB relationship view for service-impact understanding
(now considerably richer per Part 5 — lifecycle state, criticality,
location, owning team, vendor/model/serial, discovery source, install/
warranty dates); asset pages track accountable inventory; the visual task
board changes underlying ticket state and remains audited/role-controlled.
**Agentless SNMP discovery** (Admin → CMDB → Discovery, `DiscoveryTarget`,
`serviceops_core/network_discovery.py`) finds CIs and "Connects to"
relationships from switches/devices via SNMP GET/WALK (MIB-II/IF-MIB/IP-MIB
ARP/LLDP-MIB), on demand or scheduled via the outbox worker loop;
credentials encrypted at rest like `IntegrationConnection`. Complementary to
(not a replacement for) the agent-based `tools/cmdb_sync_agent.sh`. New
`/cmdb/topology` page renders CIs/relationships as a dependency-free
vanilla-JS force-directed graph. A device that doesn't answer SNMP (most
consumer/office devices don't) still gets a bare liveness check
(`tcp_liveness_probe`, a handful of common TCP ports against only the
configured target, no port scanning) plus a best-effort `reverse_dns_lookup`
via shared `probe_host()`, rather than being silently invisible.
Real-hardware validation: 1→96 devices found on the same real `/24` after
that fix. **A run never writes a CI directly** — it stages every result as
a `DiscoveryCandidate` row; the new `/cmdb/discovery/<id>/review` page lets
an administrator add selected devices, add all of them, or discard the
batch, and only that explicit decision calls `reconcile_facts_into_cmdb`
(which still never overwrites a manually-classified CI's identity fields,
and never downgrades an SNMP-profiled CI to a bare one on a later liveness-
only hit). Real production incident fixed in the same pass: `discover_host`
was constructing a brand-new `SnmpEngine()` (pysnmp's heaviest object, MIB
compilation on cold cache) per GET/WALK — ~9 per host — which under 40
concurrent sweep threads could exhaust memory; refactored to one shared
`SnmpEngine`/event-loop per host via `_SnmpSession`, verified bounded
memory (266MB isolated, ~470MB on the live stack) for a full `/24` sweep.

### 4. Deployment decision

| Environment | Application | Database | Upload storage |
|---|---|---|---|
| Single server | Docker Compose | Bundled PostgreSQL | Docker volume |
| Single production server | Docker Compose behind HTTPS proxy | Bundled or external PostgreSQL | Docker volume with backups |
| Enterprise production | Kubernetes/Helm, 3+ replicas | Managed HA PostgreSQL | RWX CSI volume or object-storage extension |

Production Kubernetes must use externally operated, highly available
PostgreSQL.

### 5. Docker installation

`./serviceops install web` → `http://127.0.0.1:8090` → configure profile/
database/identity/listener → validate → deploy. `./serviceops status`/
`health`/`logs`/`backup`/`restore`/`doctor` for lifecycle ops. Put an HTTPS
proxy in front of the loopback-bound app and terminate TLS there.

### 6. Kubernetes prerequisites

Kubernetes 1.27+, 3+ worker nodes for HA; Helm 3, kubectl, default-deny CNI,
CSI storage; private registry + immutable image tag/digest; external HA
PostgreSQL with TLS/backups/PITR; RWX upload storage for >1 replica;
ingress/DNS/TLS automation; Metrics Server; secrets controller/vault.

### 7. Kubernetes installation

Build/scan/sign/push an immutable image → copy
`deploy/kubernetes/values-production.example.yaml` →
`values-production.yaml` → set registry/tag/ingress/storage/replicas/
identity/role mappings → `./serviceops install kubernetes --preflight` →
`./serviceops install kubernetes` → confirm rollout/TLS/login/record
creation/upload/approval/notification/audit.

### 8. Kubernetes chart controls

Non-root UID/GID, RuntimeDefault seccomp, all capabilities dropped,
read-only root filesystem, disabled service-account-token mounts, distinct
startup/readiness/liveness probes, zero-unavailable rolling update, topology
spreading, PDB, optional HPA, resource requests/limits, NetworkPolicy,
persistent upload claim, JSON schema validation, Helm test hook.

### 9. Identity configuration

**Local admin**: one vaulted break-glass account, tested quarterly, rotated
after every use. **AD/LDAP**: LDAPS/StartTLS, cert validation,
least-privilege read-only bind, narrow base DN, escaped filter, explicit
group-role mappings; validate bind/search/user-bind/disabled-user/group-
mapping/cert-expiry/outage behavior. **Keycloak**: confidential OIDC
client, authorization-code flow, exact HTTPS redirect URI, short-lived
tokens, approved realm-role claims, client-secret rotation, restrictive
redirect/web-origin settings; validate login/logout/expired-session/
revoked-user/missing-email/role-change/provider-outage.

### 10. Post-deployment system settings

**Administration home → Platform settings**: platform/company name, PNG logo,
colors, support identity, display defaults, LDAP/Keycloak, encrypted
provider secrets, security limits, workflow defaults, notification
identity. Each field marked **Live** (read from PostgreSQL every request) or
**Restart required** (needs a full Compose restart / Kubernetes rollout).
Database topology/replicas/storage/ingress/TLS remain Compose/Helm-owned
and read-only in the UI. Sensitive values encrypted before storage, never
returned to the browser; `SETTINGS_ENCRYPTION_KEY` must be durable.

**Priority and SLA policy**: priority calculated from impact/urgency via
Git-backed `config/priority_matrix.json`; manager/admin override requires an
auditable ≥10-character reason. Business calendars use IANA timezones,
weekdays/hours, holiday exclusions; an SLA without a calendar is 24x7
wall-clock. The worker detects breaches, writes evidence, records ticket
history, notifies owning-team manager + assignee via the durable outbox.

**Declarative workflow operations**: source in `config/workflows.json`;
startup validates and publishes a new immutable runtime version only when
the canonical spec changes. Supported foundation: `ticket.state_entry`
events, equality/inequality/membership/empty-value conditions, three
actions (add history, notify requester, notify owning-team manager).
State transitions enqueue a correlated job in the same transaction; the
worker claims via PostgreSQL coordination, retries with bounded exponential
backoff, `Dead` after 5 attempts. Durable waits commit cursor+resume
timestamp. API triggers require `workflows:execute` + operational
permission + idempotency key. Reusable subflows (schema v2) validate
references before deployment, reject unknown deps/cycles. Recurring ticket
schedules are tenant-scoped, bounded-interval, PostgreSQL-row-locked,
coalesce missed intervals into one catch-up event.

**Bootstrap credential retirement**: `ADMIN_PASSWORD_FILE` takes precedence
over `ADMIN_PASSWORD`; Kubernetes separates bootstrap from runtime secrets
and never injects it into workers. After first install: sign in as local
admin → **Administration → Change password** (increments auth version,
invalidates other sessions) → store in vault → `./serviceops
retire-bootstrap-secret` → `./serviceops doctor` (worker-secret isolation
check).

**Release evidence**: tagged releases run the pinned supply-chain workflow
(full test suite, provenance build, Trivy HIGH/CRITICAL block, CycloneDX
SBOM, keyless Cosign signing, SLSA/SBOM attestations). Kubernetes values
must provide `image.digest`, never a mutable tag. Generate release records
with `python tools/release_evidence.py --version ... --image ... --output
...`. External vulnerability scanning, signing, provenance publication,
registry verification, admission enforcement remain required before
organizational production approval.

### 11. Security operations

Enforce TLS externally, enable HSTS only after HTTPS is proven; vault
secrets, never commit `.env`/values/kubeconfig; restrict namespace RBAC and
DB privileges; scan source/deps/image/manifests/endpoints in CI; sign
images and enforce admission verification; forward all relevant logs;
alert on login failures, admin changes, approval anomalies, SLA breaches,
crash loops, readiness loss, saturation, storage pressure; patch under
change control.

### 12. Backup and recovery

Back up PostgreSQL + uploads as one recovery set, encrypted, off-cluster,
retained/immutable, restore-tested. Quarterly: `./serviceops
rehearse-recovery` + `rehearse-pitr` → restore into isolated env → restore
DB to recovery point → restore uploads → deploy matching version → validate
counts/attachments/identities/approvals/audit/workflows → record actual
RPO/RTO. Logical recovery (`pg_dump`) deliberately reports
`pitr_proven=false`; the separate PITR rehearsal
(`pg_basebackup`+continuous WAL+named recovery target on disposable
clusters) reports `pitr_proven=true` only after boundary+integrity checks
pass.

### 13. Upgrades and rollback

`./serviceops rehearse-upgrade` first (verified rollback set, isolated
clone, candidate migration gate, health/schema/audit/attachment
validation, source health proof) → back up → review release notes/schema →
deploy to staging → `./serviceops doctor` → automated tests →
`./serviceops update` production → verify health/login/ticket
creation/approval routing/attachment access/backups. `--atomic` rolls back
Kubernetes *resources* on failure; database schema/data rollback still
needs a release-specific tested procedure.

### 14. Monitoring and SLOs

Monitor availability, request rate, latency percentiles, HTTP errors,
worker saturation, pod restarts, readiness, CPU/memory throttling, DB
connections/query latency, replication/backup health, volume capacity,
login errors, notification failures, SLA breach rate. Define
business-approved SLOs; page only on actionable symptoms.

### 15. Incident response

Declare severity + incident commander, preserve evidence, stabilize
service, communicate on a fixed cadence, use tested rollback/failover,
validate recovery, create a blameless problem record with corrective
actions. Never delete audit/operational evidence during response.

### 16. Production acceptance checklist

- [ ] Immutable, scanned image from trusted registry
- [ ] External HA PostgreSQL with TLS, PITR, and restore test
- [ ] Three or more application replicas across failure domains
- [ ] RWX persistent uploads and tested restore
- [ ] TLS ingress, DNS, HSTS, security headers
- [ ] Restricted Pod Security and least-privilege RBAC
- [ ] Network policies validated with the actual CNI and endpoint topology
- [ ] LDAP/Keycloak end-to-end tests and vaulted break-glass account
- [ ] Monitoring, logs, alert routing, dashboards, and runbooks
- [ ] Load, soak, failover, node-drain, rollback, and disaster-recovery tests
- [ ] Security review, penetration test, and formal go-live approval

---

## Part 10 — Deployment guide

(Full text of `docs/DEPLOYMENT.md` — see Part 9 for the complete
user/admin/identity/Kubernetes/security/monitoring/backup/recovery/upgrade/
rollback/incident-response runbook this file points back to.)

### Kubernetes production deployment

Supported enterprise topology: `charts/serviceops` Helm chart, immutable
image, 2+ replicas, external HA PostgreSQL, RWX upload storage, ingress
TLS, Restricted Pod Security, NetworkPolicy, probes, topology spreading,
disruption protection.

```bash
cp deploy/kubernetes/values-production.example.yaml deploy/kubernetes/values-production.yaml
./serviceops install kubernetes --preflight
./serviceops install kubernetes
```

Set `image.repository` and verified `image.digest`; export
`SERVICEOPS_GITHUB_ORGANIZATION`. Chart validation rejects missing digest,
single replica, bundled PostgreSQL. Installer deploys pinned Sigstore
policy controller + GitHub trust policy, enables attestation enforcement,
uses atomic Helm deployment.

### Web Installation Center

`./serviceops install web` → `http://127.0.0.1:8090`. Installer doesn't
receive the Docker socket; writes a request to a private local state
directory, host-side script performs Compose actions. Confirms Docker/
Compose readiness, writable storage, free disk, listener availability,
PostgreSQL auth/query execution, LDAP TLS bind/search, Keycloak discovery
metadata, production security policy. Generated env files mode `0600`;
validation never echoes passwords.

**Production-only initialization**: creates only the local bootstrap admin
and structural ITIL groups/SLA definitions — never demo personas, manager
placeholders, catalog/CMDB examples, assets, or knowledge articles. Use
`tools/production_cleanup.py` after backing up an older database containing
legacy bootstrap demo data.

### AD and LDAP

Service bind locates exactly one directory user, then binds as that user's
DN to verify the password. Production requires LDAPS/StartTLS + cert
validation. `LDAP_ROLE_MAPPINGS` maps full group DNs to
requester/agent/manager/admin (unmapped → requester). AD group→team
mapping accepts a short common name (`gg_unix`) or full DN; membership
reconciles at each AD login without overwriting manual manager/CCB
appointments.

### Keycloak

Confidential OIDC client, standard authorization-code flow, redirect URI
`https://serviceops.example.com/auth/keycloak/callback`. Enable `openid
profile email`, include realm roles in the ID token if role mapping is
needed. `KEYCLOAK_ROLE_MAPPINGS` maps realm role names to ServiceOps
roles. Keep the local admin credential vaulted for IdP outages.
`KEYCLOAK_ATTR_MAP` (mirrors `LDAP_ATTR_MAP`'s shape) additionally maps
title/department/division/employee_id/employee_type/business_phone/
mobile_phone/location from OIDC userinfo claims onto the user profile on
every login, same as LDAP sync does for interactive LDAP logins; LDAP sync
itself now also covers business_phone/mobile_phone/location, not just the
original five fields. Neither path ever nulls a field the current login's
claim/attribute set left out.

### Fast installation

Supported host: 64-bit Linux, 2+ CPU, 4GB+ RAM, 10GB+ free disk, Docker
Engine 24+, Compose v2, outbound registry access.

```bash
git clone <your-serviceops-repository> serviceops
cd serviceops
chmod +x serviceops
./serviceops install server
```

Unattended: `./serviceops install server --mode bundled --port 8080 --bind 127.0.0.1 --yes`.

### RPM packaging

For package-managed hosts: installs the control plane only (CLI, Compose
files, Helm chart, ops tooling) — **no application source or Dockerfile** —
so `dnf upgrade` never triggers a rebuild, only changes which image
`serviceops update` pulls next. Pass a digest as `build-dist.sh`'s third
argument to pin `repository@sha256:...` instead of a mutable tag.

| Path | Purpose |
|---|---|
| `/opt/serviceops` | Control plane (CLI, Compose files, Helm chart, tools) |
| `/etc/serviceops/serviceops.env` | Generated secrets/config (`0600`; symlinked from `/opt/serviceops/.env`) |
| `/var/lib/serviceops/backups` | DB/upload backups (symlinked from `/opt/serviceops/backups`) |
| `/usr/bin/serviceops` | Symlink to the CLI |
| `systemd` unit `serviceops.service` | Wraps `serviceops start`/`stop` |

```bash
bash packaging/build-dist.sh 1.26.3 ghcr.io/awijesundara/serviceops sha256:<pushed-image-digest>
rpmdev-setuptree
cp dist/serviceops-1.26.3.tar.gz packaging/systemd/serviceops.service ~/rpmbuild/SOURCES/
rpmbuild --define "version 1.26.3" -ba packaging/rpm/serviceops.spec
sudo dnf install ~/rpmbuild/RPMS/noarch/serviceops-1.26.3-1.*.noarch.rpm
sudo serviceops install server --yes
sudo systemctl enable --now serviceops
```

Requires Docker Engine + Compose plugin already installed; `%pre` adds the
`serviceops` system account to the `docker` group. The browser web
installer is not included in packaged installs — use `serviceops install
server`. `serviceops update` (or bump `SERVICEOPS_IMAGE` +
`serviceops restart`) moves to a new pinned image.

### Architecture A: bundled PostgreSQL

One-server installations, straightforward backups. PostgreSQL not published
to the host network; installer generates its password with a health gate
before app start.

```bash
cp .env.example .env
# Set secure values and DEPLOYMENT_MODE=bundled
docker compose --env-file .env -f compose.yaml up --build -d
```

### Architecture B: external PostgreSQL

Managed databases, HA clusters, separate backup ownership, multiple app
servers. Provision PostgreSQL 14+, create a dedicated owner role/DB, permit
the ServiceOps server through the firewall, require TLS
(`sslmode=verify-full` where possible):

```sql
CREATE ROLE serviceops LOGIN PASSWORD 'long-random-password';
CREATE DATABASE serviceops OWNER serviceops;
```

```bash
./serviceops install server --mode external \
  --database-url 'postgresql+psycopg://serviceops:password@db.internal:5432/serviceops?sslmode=verify-full' \
  --port 8080 --bind 127.0.0.1 --yes
```

Uses `compose.external-db.yaml`; no local DB container/volume.

### HTTPS and network exposure

Keep `BIND_ADDRESS=127.0.0.1`, place ServiceOps behind an HTTPS proxy,
expose only 80/443. Never expose PostgreSQL or 8080 publicly.

```caddyfile
serviceops.example.com {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8080
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

```nginx
server {
    listen 443 ssl http2;
    server_name serviceops.example.com;
    client_max_body_size 20m;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }
}
```

### Operations

```bash
./serviceops status
./serviceops health
./serviceops doctor
./serviceops logs
./serviceops restart
./serviceops update
```

Bundled backups: `./serviceops backup`, `rehearse-recovery`,
`rehearse-pitr` — writes a custom-format dump, upload archive, and SHA-256
manifest to `backups/` (owner-only permissions). External database backups
are intentionally delegated to the provider.

### Recovery objectives

Define and test: RPO, RTO, PostgreSQL PITR, upload-volume recovery, `.env`
secret escrow, DNS/TLS failover, quarterly restore exercises. Database and
uploads must recover from the same logical backup window.

### Upgrades

One released minor version at a time; skipping versions requires
rehearsing every intervening migration. `./serviceops rehearse-upgrade`
before every release (verified rollback set, isolated clone, candidate
migration gate, schema/audit/attachment/health/source-health validation;
never migrates production itself). Then: verified backup → review release
notes → staging deploy → `./serviceops doctor` → automated tests →
`./serviceops update` production → verify health/login/ticket
creation/approval routing/attachment access/backups.

### Security checklist

Replace bootstrap credentials immediately; keep `.env` owner-readable and
out of version control; HTTPS + secure cookies at the proxy; restrict
Docker socket access; non-root read-only container with `no-new-privileges`;
private PostgreSQL requiring TLS externally; host security
updates/monitoring/disk alerts/log forwarding/backup alerts; integrate
organizational SSO before wide deployment; review users/managers/CCB/audit
regularly.

### Scaling

External managed PostgreSQL; shared object storage for attachments (future
adapter); 2+ app nodes behind a load balancer; move session state/
background work to shared services before horizontal scaling; migrations
run once per release, not per node. The current Compose deployment targets
a highly reliable single application host, not a multi-region control
plane.

---

## Part 11 — Documentation index and synchronization rule

(Full text of `docs/DOCUMENTATION_INDEX.md`, plus this file's own entry.)

| Document | Purpose |
|---|---|
| `MASTER_REFERENCE.md` (this file) | Single merged reference for any AI/engineer: governance, backlog, ITIL model, audit findings, this session's changes, traceability, UI mapping, API reference, operations manual, deployment guide, all in one place |
| `API_REFERENCE.md` | REST API contract: authentication, scopes, endpoints, examples, errors |
| `OPERATIONS_MANUAL.md` | Complete platform manual: administration, security model, ITIL workflows, product use |
| `DEPLOYMENT.md` | Docker, Kubernetes, RPM packaging, identity, backup, and recovery instructions |
| `BACKLOG.md` | Authoritative completed and open work, with evidence references |
| `GOVERNANCE.md` | Architecture decisions, production-readiness verdict, non-deviation controls |
| `TRACEABILITY_MATRIX.md` | Implementation evidence mapped to requirements/backlog items |
| `UI_CAPABILITY_MAPPING.md` | Supplied ServiceNow UI PDF analysis and capability gaps |
| `ITIL_TICKET_HIERARCHY.md` | ServiceNow-pattern ticket hierarchy reference and Change Task governance rule mapping |
| `blueprints/BLUEPRINT_REGISTRY.md` / `BLUEPRINT_TRACEABILITY.md` | BP-001 controlled source and programme traceability |
| `ServiceOps_Complete_Platform_Manual.pdf` | PDF rendering of `OPERATIONS_MANUAL.md`, generated by `tools/generate_operations_manual.py` — regenerate after any `OPERATIONS_MANUAL.md` change |

### Keeping this synchronized

When implementing a change:

- Update this index if a document is added/removed/renamed.
- Update `BACKLOG.md`, marking items done only with corresponding evidence.
- Update `TRACEABILITY_MATRIX.md` if implementation status changed.
- Update `GOVERNANCE.md`'s decision log if an architectural decision changed.
- Update the relevant manual section
  (`OPERATIONS_MANUAL.md`/`DEPLOYMENT.md`/`API_REFERENCE.md`).
- **Update this file (`MASTER_REFERENCE.md`)** — it is a merge, not an
  independent source; if the above documents change and this file isn't
  regenerated from them, this file becomes the stale one. Treat "update the
  docs" instructions in `CLAUDE.md` as covering this file too from now on.
- Regenerate `docs/ServiceOps_Complete_Platform_Manual.pdf` via
  `python tools/generate_operations_manual.py` whenever
  `OPERATIONS_MANUAL.md` changes.

This directory is excluded from the public GitHub repository but must still
be maintained locally; do not delete it because it is gitignored.

### Outstanding synchronization task from this session

This session changed `app.py`/templates/migrations (Part 5) in ways that
individual source documents (`BACKLOG.md`, `OPERATIONS_MANUAL.md`,
`API_REFERENCE.md`) have **not yet been separately updated** to describe —
this merged file captures the changes accurately, but per the rule above,
the individual controlled documents should also be updated in a focused
follow-up pass (specifically: a new `BACKLOG.md` row for the CMDB
enrichment/tenant-fix/performance-fix work with a formal B-number, an
`OPERATIONS_MANUAL.md` CMDB section update describing the new fields, and
an `API_REFERENCE.md` note on the CMDB endpoint's five-field limitation
relative to the richer web-UI model) so the individual files don't silently
drift from this merged one.
