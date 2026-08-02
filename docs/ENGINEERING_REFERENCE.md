# ServiceOps engineering reference

The architecture record for engineers and AI agents working on this codebase:
governance and non-deviation policy, the requirements traceability matrix, the
ITIL ticket-hierarchy design reference, the supplied UX-source capability
mapping, and the controlled blueprint register. For product usage see
[OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md); for deployment see
[DEPLOYMENT.md](DEPLOYMENT.md); for open/completed work see
[BACKLOG.md](BACKLOG.md).

**In this document:**

1. [Governance and non-deviation policy](#1-governance-and-non-deviation-policy)
2. [Requirements traceability matrix](#2-requirements-traceability-matrix)
3. [ITIL / ServiceNow-pattern ticket hierarchy reference](#3-itil--servicenow-pattern-ticket-hierarchy-reference)
4. [UI capability mapping](#4-ui-capability-mapping)
5. [Blueprint registry and programme traceability](#5-blueprint-registry-and-programme-traceability)

---

## 1. Governance and non-deviation policy

### Product boundary

ServiceOps is an independently implemented service-management platform. It
must not be described as ServiceNow, ServiceNow-compatible, certified, or as
containing "all ServiceNow features." Reference material may inform workflows
and usability; implementation status is proven only by repository evidence and
tests in the traceability matrix (§2 below).

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
8. Product changes update `BACKLOG.md`, this document's traceability matrix,
   the decision log below when applicable, and the relevant manual in the
   same change.

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
| ADR-020 | 2026-08-01 | Adopt real Semantic Versioning (MAJOR.MINOR.PATCH) for `APP_VERSION`/Helm chart version/git tags going forward: MAJOR for breaking API or schema-downgrade-incompatible changes, MINOR for new backward-compatible functionality, PATCH for fixes and small non-functional tweaks. | The 56 tags published before this ADR (`v1.28.0`–`v1.29.51`) stayed at PATCH-only numbering — every change, feature or fix, bumped the same trailing digit — and are left as-is rather than retroactively rewritten, since their exact strings are load-bearing in already-published GHCR image references, Cosign signatures, and SLSA/SBOM attestations. The next release starts a new MINOR line (`v1.30.0`) to mark the changeover cleanly. |

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

### Production-readiness verdict

> This verdict was last assessed early in the programme (P0 items listed
> below). Several — versioned migrations, CSRF/authorization tests, the
> append-only HMAC audit chain, and supply-chain attestation — have since
> shipped; the remainder (independent penetration test, representative
> AD/Keycloak/HA proof, load/soak evidence) has not been re-run. Treat this
> section as due for a fresh assessment rather than a current verdict.

**Not approved for enterprise production yet**, pending: proven disaster
recovery/failover under representative failure injection, independent
penetration testing, a real HA Kubernetes deployment with representative
AD/Keycloak systems, and load/soak results.

Approval requires clean-checkout quality gates, representative AD/Keycloak
tests, a real HA Kubernetes deployment, restore and failure-injection evidence,
load/soak results, security and accessibility assessments, and accountable
operations, security, privacy, and CCB sign-off.

The only exception is the explicit `tools/load_test_fixture.py` workflow on an
intentionally reset, isolated test database. It is never automatic, displays a
warning banner, and must be destroyed before any production assessment.

---

## 2. Requirements traceability matrix

Status meanings: **Verified** has current automated evidence; **Implemented**
has code but incomplete external/runtime proof; **Gap** is not production-ready.

| Requirement/source | ServiceOps evidence | Status | Backlog |
|---|---|---|---|
| Unified navigation, search, favorites, history, preferences (UI PDF: Next Experience) | `templates/base.html`, `/ui/search`, favorites/recent views, `tests/test_app.py` | Verified | B-021 |
| User profile, user list and administration home (UI PDF: User Interface/User Administration) | tenant-scoped `/profile`, `/admin/users`, `/admin/users/<id>` and `/admin`; self-service contact fields are separated from admin-only role, active state and department authority; search and persistence/denial tests | Verified | B-248 |
| Categorized personal interface settings (UI PDF: System Settings) | `/preferences` categories for accessibility, lists, forms and notification navigation; persistent density, scale, contrast, motion, tooltips, date display and navigation settings; light-only governed by ADR-012 | Verified for implemented settings; vendor theme/developer controls are intentionally not reproduced | B-248, B-240 |
| Lists, filters, forms, activity, attachments, checklists (UI PDF: Core UI/Workspace) | shared task-derived record shell for INC/CHG/PRB/enterprise records/REQ, common two-column operational fields, action headers, field-level Event history, type-specific related sections and Incident section navigation, shared list toolbar/search/filter/record count/pagination/priority signals and lifecycle plus rendered-browser tests | Verified | B-022, B-245, B-247, B-248 |
| Visual task boards (UI PDF: VTB) | `/task-board`, move endpoint and test | Verified | B-023 |
| Branding/logo/theme configuration (UI PDF: Theme Builder/configuration) | installer and `/admin/settings`; light-only UI | Implemented | B-024 |
| Guided help/tours (UI PDF: Adoption services) | `templates/help.html` + `static/platform.js` interactive step-by-step tour with inline focus/advance/skip; static help articles alongside it | Partial; versioned content and role targeting remain open | B-120 |
| Full configurable workspace/page-builder capability | no page designer or metadata runtime | Gap | B-121 |
| Production-only initialization | `seed`, installer, Compose, cleanup tool and tests | Implemented | B-001 |
| Team-manager and CCB approval chain | named manager controls, explicit CCB approver grants, chains/gates/votes; change submission fail-closed | Implemented | B-030 |
| Approval and lifecycle integrity | centralized transition guards, approval-owned states, exact-voter enforcement, board/form/task bypass tests | Verified | B-034 |
| Assignment-group operational authorization | shared INC/CHG read visibility for active IT teams, explicit owning-team mutation guard, team-scoped assignees and adversarial cross-team read/write tests | Verified | B-035, B-042 |
| ITIL related-record network | governed `RecordLink`, `OperationalTask`, `ProblemProfile`, `MajorIncidentProfile`, REQ/RITM/SCTASK hierarchy, reverse related lists and relationship tests | Verified | B-031, B-037 |
| Ticket history and change reapproval | `TaskHistory`, `ChangeRevision`, material-field comparison, superseded chains, fresh notifications and adversarial approval-reset tests | Verified | B-036 |
| Task-to-CMDB relationships | primary/affected CIs, impacted services and multi-CI schedule-conflict detection | Implemented | B-032 |
| CMDB attribute depth (lifecycle, criticality, discovery source, ownership) | `ConfigurationItem` fields added by migration `20260729_0023`: description, lifecycle_state, business_criticality, serial_number, vendor, model, location, cost_center, discovery_source, install/warranty dates, JSON attributes, support_group_id; `CIRelationship` gained its own `tenant_id` and a tightened `(parent, child, type)` unique constraint | Implemented; no automated test added yet, REST `cmdb:write` endpoint not yet extended to the new fields | B-253 |
| Cross-record lookup tenant isolation (`find_record_by_number`) | every branch now filters by the caller's tenant, joining through the owning parent for RITM/SCTASK/CTASK/PTASK | Implemented; no adversarial test added yet | B-253 |
| Ticket lifecycle-transition errors stay inline (no generic error page) | `ticket_detail`'s `update`/`quick_resolve` actions now wrap `transition_ticket` in `try/except HTTPException`, matching `enterprise_detail`'s existing pattern; verified live against a real invalid-transition ticket | Verified | B-254 |
| Catalog order approval-prerequisite validation (no crash on missing approvers) | `catalog_order` validates an active admin and a non-empty Service Desk membership before creating any REQ/RITM rows, flashing a clear error instead of raising `AttributeError`/`ValueError`; verified live against the actual empty-membership case that produced the reported 500 | Verified | B-254 |
| RITM/SCTASK lifecycle stepper and Opened/Opened by fields | reused existing `build_state_track`/`_state_track.html` component with new `ritm`/`catalog_task` state orders; verified live via rendered HTML on real RITM/SCTASK records | Verified | B-254 |
| Org chart readability at scale | replaced fragile flex/connector-line tree with an indented vertical tree (`org2-*`); verified live against all 18 seeded users with no clipped/misaligned nodes | Verified | B-255 |
| Manager visibility into team performance/SLA exposure | `manager_portal_context()` computes per-member open incidents/changes/tasks, 30-day resolutions, and SLA breached/at-risk via batched aggregate queries; verified live across 6 teams / 12 members | Verified | B-255 |
| CSV/print export coverage | `csv_response()` helper wired into manager portal, tickets, open work, CMDB, and requests list; browser print/PDF via a dedicated print stylesheet | Verified | B-255 |
| Print/Save-as-PDF works under CSP | replaced inline `onclick` handlers (silently blocked by `script-src 'self'`) with `data-print-page` + a delegated listener in `platform.js`; verified CSP header unchanged and listener present in served JS | Verified | B-256 |
| Pending-approvals and open-task visibility in navigation | `pending_approvals_count`/`my_open_tasks_count` added to the shared `ui_context()` context processor, rendered as amber nav badges; verified live against a real pending approval | Verified | B-256 |
| Analytics reflects standard ITSM reporting metrics | SLA compliance, 14-day volume trend, backlog aging, MTTR by priority, change success rate, busiest teams — all computed from real `TaskSLA`/`Ticket` data with proportional (not arbitrary) chart scaling | Verified | B-256 |
| Sidebar collapse/scroll stability | persisted `nav-collapsed` via `localStorage` and moved scroll/collapse-state restoration into a blocking, CSP-compliant `static/nav-init.js` applied before first paint; verified live with CSP header unchanged and no JS errors | Verified | B-257 |
| Change approval invalidated on Affected CI/Impacted Service change | `task_ci_add` now calls `supersede_change_approval` for change tickets, matching the other three material-change paths | Verified | B-258 |
| Emergency change accelerated-but-auditable approval route | `change_approval_stages` gives Emergency changes a single-approver "expedited" CCB stage instead of the full-board majority gate; CCB authorization and audit trail remain mandatory | Verified | B-258 |
| LDAP bind fails closed on key-rotation/decrypt failure | `ldap_authenticate` resolves the bind password directly and aborts rather than falling back to an anonymous bind if a configured password can't be decrypted | Verified | B-258 |
| REST API rate limiting | new `api_rate_limit_window` table (migration `20260729_0024`), DB-backed per-client-per-minute counter enforced in `authenticate_api_request()`, configurable via `API_RATE_LIMIT_PER_MINUTE`; verified live returning `429`+`Retry-After` after the configured limit | Verified | B-258 |
| `ChangeGovernance.ccb_required` wired into CCB gating | previously defined and defaulted but never read; now respected by `change_approval_stages` (no UI to set it False yet — deliberately deferred, security-sensitive) | Implemented | B-258 |
| Attachment content-type/extension verification | `validate_attachment_upload()` allowlists extensions and cross-checks magic bytes, storing the verified MIME type instead of the client-supplied one; verified live against a rejected `.exe` and an accepted `.pdf` | Verified | B-258 |
| Attachment malware scanning and cryptographic hashing | optional ClamAV INSTREAM adapter (`scan_attachment()`, no new dependency, configurable host/port/enable), rejects/quarantines a positive scan result before any `file_attachment` row is created, records `sha256`/`scan_status` (migration `20260729_0026`); honestly reports `not_scanned` when unconfigured rather than claiming clean; verified live end-to-end (upload succeeds, `not_scanned` + hash recorded) | Verified | B-260 |
| `ChangeGovernance`/`ApprovalGate`/`ApprovalVote` own enforced `tenant_id` | previously reachable only by joining back through `approval_chain`/`ticket`; migration `20260729_0025` adds and backfills an own tenant_id column on each, same defense-in-depth precedent as `CIRelationship` (B-253); verified live against the running Postgres database with zero NULL backfills | Verified | B-260 |
| Catalog hierarchy and task orchestration | multi-RITM REQ, multiple team-owned SCTASKs, sequential/parallel dependency control and terminal-state roll-up | Verified | B-033 |
| Configurable catalog fulfillment routing | per-item `CatalogItemRouting`, administrator route UI, Windows defaults for Laptop/Software, Service Desk fallback and generated-SCTASK routing tests | Verified | B-038 |
| Catalog item administration | administrator create/edit controls for item metadata, delivery target, approval, availability and fulfillment route; create/edit/deactivation test | Verified | B-041 |
| Catalog request visibility boundaries | participant/fulfillment/approver/admin policy applied to REQ list, direct detail, dashboard counts and global search with cross-team denial tests | Verified | B-039 |
| Cross-module object and field authorization | centralized ticket/request/enterprise policies; direct-ID, list, search, attachment, analytics, approval, relationship and mutation tests; Git-backed action vocabulary plus validated fail-closed field registry for REST tickets, audit exports, JSON search, monitoring/workflow acknowledgements and UI mutation responses | Implemented; independent authorization review pending | B-005, B-040, B-203 |
| AD/LDAP and Keycloak authentication | authentication code, installer checks, AD group-to-team mapping and login reconciliation | Implemented; external proof absent | B-061 |
| LDAP directory sync (profile fields, manager chain, group membership) — manual and scheduled | `serviceops_core/ldap_sync.py`, `app.process_ldap_sync_schedule`, `tools/outbox_worker.py`, migrations `20260729_0027`/`20260730_0028`, `tests/test_ldap_sync.py`, `tests/test_ldap_sync_schedule.py` | Implemented and verified; unit tests mocked (7 scheduling tests + prior sync tests), full suite passed against real PostgreSQL 16, migration upgrade/downgrade/re-upgrade verified live, and manager chain/profile fields/group membership verified live end-to-end against a real throwaway OpenLDAP server | B-262 |
| Docker and external PostgreSQL deployment | Compose definitions, single `./serviceops` lifecycle command, internal installers, health endpoints | Implemented | B-050 |
| Kubernetes high availability | Helm resources/PDB/network policy | Implemented; cluster proof absent | B-051 |
| Versioned database migrations and tenant foundation | Alembic baseline plus tenant revision, existing-schema adoption, default-tenant backfill for 15 roots, tenant-aware list/search/direct-ID policies, Kubernetes migration Job, outdated-schema startup refusal, cross-tenant denial tests, and a guarded disposable PostgreSQL `20260727_0013 → 20260727_0012 → 20260727_0013` rehearsal with 100,717 records across 63 tables (dynamically resolved head/prior revision, not hardcoded) | Migration path verified at full scale (2026-07-28); `ApprovalGate`/`ApprovalVote`/`ChangeGovernance` closed by B-260; roughly 21 further dependent child tables and independent tenant-isolation review still pending | B-002, B-005, B-202, B-231, B-260 |
| CSRF protection and hardened session lifecycle | central unsafe-method guard, injected form tokens, JavaScript token headers, post-login rotation, HttpOnly/SameSite cookies and explicit rejection/acceptance tests | Verified | B-003, B-201 |
| Tamper-evident audit evidence | tenant-specific hash chains, per-event key IDs, non-destructive encrypted historical-key retention and rotation, file-mounted bootstrap key, request/source correlation, database UPDATE/DELETE denial triggers, minimum seven-year retention/legal hold policy, verification-gated signed export, and SIEM-only signed durable delivery | Implemented; representative external WORM/SIEM validation and independent review pending | B-004 |
| Versioned REST API foundation | tenant/user-bound hashed clients, scopes, shared policies and projections, cursor pagination, JSON errors/request IDs, OpenAPI, idempotent writes, auditing, one-time token display and revocation | Implemented for initial ticket/incident contract; broader resources, OAuth2, rate limiting and compatibility programme pending | B-204 |
| Responsive PWA foundation | dynamic manifest, company icon support, secure-context registration and static-shell-only service worker with tests proving no API/ticket caching | Implemented; encrypted governed offline records intentionally deferred | B-205 |
| Durable integration foundation | transactional outbox, Compose/Kubernetes worker, SKIP LOCKED coordination, bounded retry/dead state, SMTP/STARTTLS, signed webhooks, Teams payloads, encrypted secrets, delivery evidence, authenticated monitoring ingestion, deduplication and team-routed EVT/EVTASK | Implemented with simulated adapters; representative external-system validation and operational SLO evidence pending | B-130 |
| Priority and SLA governance | Git-backed validated impact/urgency matrix, controlled override evidence, IANA-timezone business schedules, holiday exclusions, immutable SLA lifecycle events, pause/resume accounting and worker-driven breach notifications | Implemented; OLA/contracts, escalation ladders and production-scale calendar/load rehearsal pending | B-206 |
| Declarative workflow foundation | validated Git package, immutable published versions, restricted expression/actions, state-entry jobs, PostgreSQL worker retries/dead state, correlation and execution evidence, idempotency, safe simulation and administrator deployment view | Implemented for ticket state-entry notification/history actions; broader trigger/action catalogue, waits, compensation, subflows, rate limits and promotion governance pending | B-207 |
| Durable workflow orchestration | PostgreSQL wait cursor/resume, action-step evidence, manual/API/SLA triggers, API scope/idempotency, per-workflow rate limits, bounded retry, controlled replay and final-attempt safe compensation | Implemented; scheduled recurrence, reusable subflows, broader actions and production failure/load evidence pending | B-208 |
| Scheduled workflows and subflows | reusable subflow expansion with unknown/cycle rejection, immutable materialized versions, tenant ticket schedules, concurrent scheduler claims, single due-event emission and missed-run coalescing | Implemented; calendar expressions, blackout policy, package dependencies, concurrency quotas and production-scale proof pending | B-209 |
| Bootstrap credential lifecycle | mounted-file priority, worker exclusion, split Kubernetes runtime/bootstrap Secrets, password rotation, auth-version session invalidation, verified retirement command | Implemented; external vault/provider rotation ceremony pending | B-006, B-210 |
| Supply-chain evidence | exact dependencies, digest-pinned bases, full-SHA-pinned CI actions, tests, Trivy high/critical gate, CycloneDX image SBOM, digest-only publication/deployment, keyless Cosign signature, GitHub SLSA/SBOM attestations, registry verification and Sigstore namespace admission enforcement | Implemented; representative tagged GHCR publication and cluster rejection proof pending | B-007, B-210 |
| Production observability/SLOs | health endpoints only | Gap | B-070 |

### Connection-dependent capability boundary

The following require the deploying organization's systems, policies,
credentials, and representative test environments: MFA/SCIM, email/SMS/contact
center, SIEM/EDR/scanners, infrastructure discovery, HRIS/ERP/CRM, DevOps
integrations, mobile/offline applications, external AI services, and regulated
retention/eDiscovery. They must be delivered through explicit adapters and are
not represented as built-in capabilities.

---

## 3. ITIL / ServiceNow-pattern ticket hierarchy reference

Reference material supplied by the product owner, preserved verbatim for future
implementation decisions. ServiceOps is inspired by these patterns but does not
claim full ServiceNow compatibility (see §1 above). Where ServiceOps' current
data model or state machine differs from what is described here, that
divergence is deliberate and documented in §2's traceability matrix; this
section is the design reference, not a claim of current implementation status.

### Governing principle implemented in ServiceOps (2026-07-29)

Planning and assessment tasks may proceed before approval. Implementation and
testing tasks must remain in Pending state until the Change Request has
received all approvals required for the current authorization gate. Review
tasks must remain pending until implementation and testing are complete.

Implemented as `change_task_gate_block()` in `app.py`, enforced both at
change-task creation (initial state) and at every state-transition attempt
(`transition_operational_task()` / `POST /operational-task/<id>`). See
`tests/test_app.py::test_change_task_unlocking_model_gates_implementation_and_review`
for the verified behavior.

### 3.1 The ServiceNow ITSM ticket hierarchy

ServiceNow does not store every record as an independent, unrelated "ticket."
Most operational records extend the base Task `[task]` table. This gives
incidents, problems, changes, catalog tasks, and other task classes common
fields such as number, state, priority, assignment group, assigned user,
approval, work notes, comments, active status, and SLA information.

A practical hierarchy looks like this:

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

The formal Service Catalog hierarchy is:

```
REQ
└── RITM
    └── SCTASK
```

Catalog submissions generate records in the Request, Requested Item, and
Catalog Task hierarchy. Variables entered by the user are principally
associated with the Requested Item.

**ServiceOps mapping**: `Ticket` (kind=incident/request/change) plays the role
of the base Task table for INC/CHG; `CatalogRequest`/`RequestedItem`/`CatalogTask`
implement REQ/RITM/SCTASK; `EnterpriseRecord` (domain=problem/event) implements
PRB; `OperationalTask` implements CTASK/PTASK.

### 3.2 What counts as a sub-ticket

**Execution task** — a defined piece of work: Incident Task, Problem Task,
Change Task, Catalog Task, Release Task. The parent owns the overall outcome;
the task owns a specific work package assigned to one group or person.

**Child ticket** — a full process record of the same or another class with
its own lifecycle, assignment, priority, SLA, work notes, and closure
information (e.g. parent/child incidents, Problem → Change, Incident → Change).

**Approval record** — a decision record, not an execution task
(`sysapproval_approver` in ServiceNow; `ApprovalChain`/`ApprovalGate`/
`ApprovalVote` in ServiceOps). Identifies what requires approval, who must
approve, the decision state, comments, timestamp, and delegation information.

**Linked object** — context, not a ticket: CI, business service, affected
service, outage, knowledge article, attachment, SLA record, change conflict,
maintenance window, CAB meeting, risk assessment, test evidence.

### 3.3 Incident Management

Standard lifecycle: New → In Progress → On Hold → Resolved → Closed →
Canceled. On Hold reasons: Awaiting Caller, Awaiting Change, Awaiting Problem,
Awaiting Vendor. Resolved means a satisfactory fix was provided; Closed means
it stayed resolved for the configured period or the resolution was confirmed.

Process: Intake → Classification → Prioritization (Impact + Urgency =
Priority; P1 Critical … P5 Planning) → Assignment → Investigation →
Resolution → Closure.

**Incident Task**: used when another group needs to complete specific work
without transferring ownership of the parent Incident. Inherits context from
the parent; has its own assignment/work notes; must not close the parent
directly; the parent should not resolve while mandatory tasks remain active;
canceling the parent should cancel/close remaining tasks per policy (commonly
a business rule, not assumed universal).

**Parent/Child Incidents**: used when many users/locations report the same
disruption. A child Incident is a separate reported impact (own SLA, own
caller communication), unlike an Incident Task (technical work, invisible to
end users, closed by the assignee).

### 3.4 Major Incident Management

Still fundamentally an Incident record, with additional controls, roles,
workbench functions, communications, and review process. Lifecycle: Potential
→ Candidate → Review → Accepted/Rejected → Promoted → Response/communication →
Restoration → Resolution → Post-Incident Review → Problem creation.

Ownership split: Major Incident Manager owns coordination/communication/
escalation/timeline/stakeholders/recovery governance; technical resolver
groups own diagnosis/workaround/restoration/evidence; the Problem Manager
owns the later root-cause process.

### 3.5 Problem Management

Incident Management asks "how do we restore service now?" Problem Management
asks "why did this happen, and how do we prevent it recurring?"

Typical lifecycle (varies by configured Problem model): New → Assess → Root
Cause Analysis → Fix planning/in progress → Resolved → Closed.

Process: Identification (from repeated incidents, MI review, trend analysis,
monitoring, failed change, capacity/availability issue, proactive analysis) →
Assessment → Root-cause investigation (Five Whys, fishbone, fault-tree,
timeline, Kepner-Tregoe, log correlation, config comparison, recent-change
analysis) → Workaround → Known Error (a state/knowledge record, not another
operational child ticket) → Permanent correction via a Change (`PRB → CHG →
CTASKS`; the Problem may stay open awaiting the Change) → Verification and
closure.

**Problem Task**: divides investigation work among subject-matter experts.
Task types: Root Cause Analysis, General. A Problem should not be marked
resolved while mandatory Problem Tasks remain active.

### 3.6 Change Management

A Change Request must answer what is changing, why, which services/CIs are
affected, business impact, technical risk, implementation/test/backout plans,
required approvers, schedule, and post-implementation outcome.

**Standard Change** — low risk, repeatable, documented, pre-authorized via an
approved template/model. Does not normally require fresh CAB approval each
occurrence, but each instance still needs validation against the approved
Standard Change conditions.

**Normal Change** — neither Standard nor Emergency; full assessment and
authorization (technical, change-management, CAB as applicable).

**Emergency Change** — used when delay would cause or extend serious business
impact. Still requires expedited assessment and authorization (Emergency CAB
or designated emergency approver) — never "no approval." May move directly
toward Authorize rather than every Normal Change stage.

**Typical Change states (legacy/traditional model)**: New → Assess →
Authorize → Scheduled → Implement → Review → Closed (or Canceled at any
point). Current ServiceNow implementations may use configurable Change Models
with different states/transitions.

Detailed process per state — required information, permitted/blocked tasks,
assessment activities, authorization approver types, schedule entry
conditions, implementation activities/outcomes, review questions, and closure
requirements — is preserved in full in the original product-owner submission
(session transcript, 2026-07-29) and summarized in §3.14 below as governance
rules.

### 3.7 Change Tasks

Official task types: **Planning, Implementation, Testing, Review**. Created
manually or via workflow/flow.

**Change Task unlocking model:**

| Change stage | Planning | Implementation | Testing | Review |
|---|---|---|---|---|
| New | Open | Pending | Pending | Pending |
| Assess | Open | Pending | Pending | Pending |
| Authorize | Usually complete | Pending | Pending | Pending |
| Scheduled before start | Closed | Pending | Pending | Pending |
| Implement | Closed | Open by sequence | Open when predecessor completes | Pending |
| Review | Closed | Closed | Closed | Open |
| Closed | Closed | Closed | Closed | Closed |

**Recommended unlocking conditions** (implemented in ServiceOps as
`change_task_gate_block()`):

- Implementation may move out of Pending only when the change's approval
  chain is fully Approved (or no chain applies) and any parent-level
  lifecycle/schedule conditions are met.
- Testing may open once at least one required Implementation task is Closed
  Complete.
- Review may open only once all required Implementation and Testing tasks
  are terminal (Closed Complete / Closed Incomplete / Cancelled).
- Planning is never gated by approval.

**Rejection behavior**: a rejected approval should clearly do one of: return
to New for correction, return to Assess, cancel the Change, mark Rejected
requiring resubmission, or create remediation tasks. ServiceOps's documented
behavior (see `app.py::supersede_change_approval`) returns the change to
Awaiting Approval and starts a fresh approval cycle when material fields
change after approval, and cancels the approval chain when a change is
soft-deleted or cancelled.

**Parent-child closure rules**: a Change cannot enter Review while mandatory
Implementation/Testing tasks are active; cannot close while any mandatory
task is active; cancelling cascades to Pending/Open tasks; closed tasks
retain audit history; failed tasks must not be silently marked successful;
backout must be its own task or explicit outcome; manually added tasks count
toward closure validation; optional tasks must be explicitly marked
optional/skipped.

### 3.8 Request Management

```
Request [sc_request]
└── Requested Item [sc_req_item]
    └── Catalog Task [sc_task]
```

REQ is the order-level container (one checkout, possibly several items).
RITM represents one catalog item in the order — each may have different
approval rules, fulfillment group, delivery target, variables, tasks, and
outcome. SCTASK represents fulfillment work under a RITM.

Process: Catalog selection → variables entered → REQ/RITM created → approval
where required → fulfillment flow starts → SCTASKs (sequential, parallel, or
conditional) → RITM fulfilled → REQ closes when all RITMs finish.

Approvals normally belong at the RITM level when different items need
different decisions; REQ-level approval is appropriate only when the whole
order must be approved as one unit.

**Closure aggregation** (implemented in ServiceOps
`catalog_task_update()`/RITM state sync): if all Catalog Tasks are Closed
Complete, the RITM becomes Closed Complete; if at least one is Closed
Incomplete, the RITM becomes Closed Incomplete; if all are Closed Skipped,
the RITM becomes Closed Skipped. The same aggregation applies from RITMs to
the parent Request.

**SCTASK is not a child of CHG** (implemented 2026-07-29): SCTASKs belong to
RITMs, not Change Requests. `CatalogTask` has no `parent_id`/`parent_type`
pointing at a `Ticket` — a Change Request relates to a RITM only through
`RecordLink` (`link_type="requested_item_change"`), the same relationship
mechanism used for every other cross-record link in ServiceOps. There is no
CHG→SCTASK parent-child relationship anywhere in the schema, and none should
be added.

When a RITM's SCTASK is linked to a Change Request, coordination work
(recording details, tracking approval, scheduling) may proceed freely, but
starting production/implementation work on that SCTASK is blocked while the
linked Change is still `New` or `Awaiting Approval`. Implemented in
`ritm_linked_change()` / `transition_catalog_task()`: attempting to move a
linked SCTASK to "Work in Progress" before its Change is authorized returns a
409 with a message directing the agent to keep the task at "Pending" and
explaining why — the task can still move to "Pending" (coordination) freely.
See `tests/test_app.py::test_catalog_task_blocks_production_work_until_linked_change_is_approved`.

This is a task-level check (any state transition attempt), not a
task-type distinction — ServiceOps's `CatalogTask` has no Planning/
Implementation/Testing/Review split the way `OperationalTask` (CTASK) does,
so it cannot yet auto-detect "this SCTASK IS the production change" versus
"this SCTASK is purely administrative." Adding a `purpose` field to
`CatalogTask` (Coordination vs. Production implementation) would allow
precise per-task control instead of blocking every SCTASK on a CHG-linked
RITM equally; flagged as a candidate follow-up, not implemented.

### 3.9 Request versus Incident

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

A Request can create an Incident or Change when fulfillment discovers an
operational issue or requires controlled production modification. ServiceNow
maintains the relationship between the Requested Item and the generated
Incident or Change Request; ServiceOps does this via `RecordLink`.

### 3.10 Universal Request

A common front-door ticket for when the requester does not know which
department/process should handle the matter. The Universal Request handles
the requester-facing conversation; the primary ticket (Incident, RITM, HR
Case, Customer Case) handles specialist execution. Use when employees should
not need to understand internal ticket types, work may transfer between
departments, or a consistent portal experience is required — not as an
unnecessary wrapper around every record. **Not currently implemented in
ServiceOps**; tracked as a candidate backlog item if a genuine multi-department
front door becomes a requirement.

### 3.11 Release Management

Groups multiple Changes/deployment activities into a coordinated delivery
(planning, design, build, configuration, testing, deployment readiness,
communications, go-live, early-life support). A Release does not replace
Change authorization — each production-affecting Change still follows its
applicable Change model. **Not currently implemented in ServiceOps**.

### 3.12 Relationships between the main tickets

- Incident → Problem: many Incidents → one Problem (shared underlying cause).
- Problem → Change: one Problem → one or more Changes (permanent fix).
- Incident → Change: service restoration requires a controlled modification.
- Request → Change: RITM → Change Request when fulfillment requires one.
- Major Incident → Problem: root-cause analysis and prevention.
- Change → Incident: a failed Change may create/link to an Incident.
- Change → Problem: a failed or repeatedly unsuccessful Change may lead to a
  Problem investigation.
- Release → Change: coordinated deployment governance.

### 3.13 The complete operational chain

```
Monitoring alert or user report
             ↓
          Incident
             ↓
Service restored using workaround
             ↓
Multiple or major incidents identified
             ↓
           Problem
             ↓
Root cause and permanent fix identified
             ↓
       Change Request
             ↓
Planning and assessment tasks
             ↓
Technical and business approvals
             ↓
Implementation and testing tasks
             ↓
Post-implementation review
             ↓
Change closed
             ↓
Problem verifies permanent correction
             ↓
Problem closed
             ↓
Knowledge and Known Error records updated
```

For a requested service:

```
User submits catalog item
             ↓
REQ and RITM created
             ↓
Approval
             ↓
SCTASK fulfillment
             ↓
Change created when production modification is required
             ↓
Change approved and implemented
             ↓
RITM fulfilled
             ↓
REQ closed
```

### 3.14 Mandatory governance rules for ServiceOps

**Parent ticket controls**
- A parent cannot close while mandatory child tasks are active. *(Implemented:
  `transition_ticket()` blocks Resolved/Closed while required OperationalTasks
  remain non-terminal.)*
- Canceling a parent cascades cancellation to eligible child tasks. *(Partially
  implemented for changes via `cancel_approval_chain`; full task cascade is a
  candidate follow-up.)*
- Closed child tasks remain immutable except through controlled reopening.
  *(Implemented: terminal states in `OPERATIONAL_TASK_TRANSITIONS`/
  `CATALOG_TASK_TRANSITIONS` only transition to themselves.)*
- Every task must have an assignment group. *(Implemented: `assignment_group_id`
  is non-nullable.)*
- Every closed task must have close code and close notes. *(Not yet enforced —
  candidate follow-up: require `work_notes` non-empty on terminal transition.)*
- Parent resolution must aggregate child outcomes. *(Implemented for RITM/REQ;
  partially implemented for Change via required-task gating.)*
- Failed, incomplete, and skipped outcomes must remain distinguishable.
  *(Implemented: Closed Complete / Closed Incomplete / Closed Skipped /
  Cancelled are distinct states.)*
- Work notes must be internal; customer comments externally visible.
  *(Implemented this round via `TaskNote.visibility`.)*
- All state changes, assignments, approvals, and field changes must be
  audited. *(Implemented via `log_history`/`log_field_changes`/`audit`.)*
- Cross-ticket relationships must be visible from both records. *(Implemented
  via `RecordLink`/`related_records()`.)*

**Approval controls**
- The requester must not approve their own high-risk Change. *(Not yet
  enforced — candidate follow-up.)*
- Approval delegation must be recorded. *(Implemented:
  `ApprovalVote.delegated_from_id`.)*
- Approval requirements must be recalculated when material fields change.
  *(Implemented: `supersede_change_approval`.)*
- Rejected approval must stop downstream execution. *(Implemented via change
  task gating.)*
- Approval comments should be mandatory for rejection. *(Not yet enforced —
  candidate follow-up.)*
- No approval record should be deleted to bypass a decision. *(Implemented:
  no delete path exists for `ApprovalVote`.)*
- All approvals retain timestamps and approver identity. *(Implemented.)*

**Change Task controls** — implemented 2026-07-29
- Planning tasks can open before approval.
- Implementation tasks remain Pending until authorization (approval chain
  fully Approved).
- Testing tasks depend on an implementation predecessor being Closed
  Complete.
- Review tasks open only after implementation and testing finish.
- A rejected or canceled Change blocks all unstarted tasks (via the approval
  chain check).

See `app.py::change_task_gate_block` and
`tests/test_app.py::test_change_task_unlocking_model_gates_implementation_and_review`.

Remaining Change Task controls not yet enforced (candidate follow-ups): task
dates fitting strictly within a live schedule exception window; automatic
Change-outcome review trigger on task failure; backout task auto-provisioning
on rollback declaration.

---

## 4. UI capability mapping

Source reviewed: *Australia ServiceNow AI Platform user interface*, 1,148 pages, updated July 7, 2026.

This mapping uses the source guide as a behavioral reference. ServiceOps does not copy its text, images, product names, proprietary runtime, or implementation.

| Source guide family | ServiceOps implementation |
|---|---|
| Next Experience and unified navigation | Unified top navigation, collapsible application navigation, global search, favorites, history, notifications, help, preferences, and role-aware landing pages |
| Landing pages and dashboards | Operational dashboard, analytics workspace, workload counters, role-based record visibility, selectable start page |
| Configurable workspace | Purpose-built ticket, request, change, CMDB, catalog, approval, analytics, and ITIL administration workspaces |
| CMDB discovery | Manual administrator create/edit/retire for configuration items and CI-to-CI relationships; automated registration from Linux hosts via `PUT /api/v1/cmdb/configuration-items` (idempotent upsert-by-name) and a lightweight shell agent, with an example Puppet class for scheduled fleet-wide sync |
| Lists and filters | Searchable/filterable record lists, states, priorities, badges, responsive tables, empty states; administrator user list searches name, username, email and department |
| Forms and activity | Structured forms, field validation, comments/activity stream, work notes, related approvals, SLAs, checklist, attachments, audit events, and Incident section navigation for Notes/Related Records/Resolution/Event History |
| Favorites and history | Per-user persistent favorites and recently viewed pages, exposed as a single combined star control (list + toggle) plus a distinct history clock, each page carrying its own title so entries are distinguishable |
| Notifications | Per-user notification inbox with unread counts, approval notifications, and clickable links back to the source ticket/record/approval queue |
| Reference fields | Type-ahead search-as-you-type lookups for configuration items and cross-record linking (`/internal/lookup/cis`, `/internal/lookup/records`), showing a description line per match, in place of long unlabeled `<select>` dropdowns |
| Assignment and reassignment | Group-level assignment is always by team name, never by picking an individual manager; incidents and changes can be reassigned to a different owning IT-fulfillment team from the record detail page, which restarts change approval against the new team's manager |
| Manager/team work views | Manager portal (per-team open change/incident/task counts) and a unified "My tasks" queue covering CTASK/PTASK/EVTASK/SCTASK assigned to the user or their teams across every parent record |
| Dashboard personalization | Admin-configurable dashboard sections (Assigned to me, SLA breached/at-risk with configurable warning window, Recently updated) via System Settings, plus a live P1/P2 signal on the Incidents tile |
| Personalization and accessibility | Categorized General/List/Form/Notification preferences; compact/comfortable density, font scaling, high contrast, reduced motion, accessible tooltips, keyboard/date display/data-pattern preferences, sidebar pin preference, semantic labels and responsive layouts. Light-only by governed decision (ADR-012); no dark/system theme option exists |
| User profile and administration | Self-service name/contact/timezone/date-format profile, administrator-controlled user identity/role/active/department records, searchable user list, and capability-based administration home. Directory membership remains governed by AD mapping and team administration rather than editable self-service fields |
| Service Portal | Employee catalog, knowledge search, request tracking, requested-item stages, attachments, and self-service cases |
| Visual Task Boards | Drag-and-drop lifecycle lanes backed by ticket state, audit, and SLA updates |
| Global search | Tickets, knowledge, enterprise work, and configuration items |
| Attachments and checklists | Persistent Docker-backed file uploads/downloads and per-ticket actionable checklists |
| Guided help and onboarding | Help Center, contextual task guidance, and an interactive navigation tour |
| Themes and branding | ServiceOps design tokens (light-only, no user-selectable theme, ADR-012); deployment-owned branding colors/logo via installer and admin settings |
| Core UI developer tooling | Adapted as server-rendered Flask templates, reusable styles, routes, and automated tests |
| CMS, UI Builder, widget developer APIs, Angular providers, Jelly, and ServiceNow scripting APIs | Not applicable: these are vendor-specific development runtimes. ServiceOps uses Flask, Jinja, SQLAlchemy, CSS, and JavaScript instead |
| Advanced Work Assignment, Agent Chat, Virtual Agent, voice guidance, predictive recommendations | Requires external messaging, telephony, workforce-routing, or AI services and is not represented as locally operational |
| Native mobile apps and offline distribution | Responsive web access is implemented; native app publishing is not included |

### Verification expectations

Every capability described as implemented must have a working route or UI, persistent data where applicable, role enforcement, and automated or live runtime verification. Vendor-specific facilities are classified rather than represented by nonfunctional toggles.

---

## 5. Blueprint registry and programme traceability

This is the private source-of-truth register for supplied product blueprints.
A blueprint is an input specification, not evidence that a feature is
implemented. Delivery status is controlled through this section, `BACKLOG.md`,
tests, and release evidence.

### 5.1 Registered sources

| ID | Title | Received | Source | Integrity |
|---|---|---|---|---|
| BP-001 | Blueprint for building your own ServiceNow-class ITSM platform | 2026-07-26 | Codex attachment `c43eee81-3c99-42be-8a2e-6cbdab3ae719/pasted-text.txt` | SHA-256 `4c4d4f0b6e589e277b7663e6e99e2699817dca567cdeda853585ab9cf759df48`; 2,060 lines; 43,034 bytes |

**Preservation rule**: the registered source is immutable. Requirement
interpretation, priorities and acceptance criteria belong in §5.2 below; the
supplied wording must not be silently rewritten. If a revised blueprint is
supplied, register a new source revision and record its relationship to
BP-001.

**Non-deviation rule**: every BP-001 requirement must have (1) a stable
requirement identifier; (2) a disposition of verified, implemented, planned,
deferred, rejected or externally dependent; (3) acceptance criteria and
evidence; (4) a backlog or decision reference; and (5) release and
live-validation evidence before it is called complete.

### 5.2 BP-001 programme traceability

BP-001 defines a multi-release platform programme, not a single feature.
"Covered" below means a currently evidenced foundation exists. It does not mean
the complete section has been delivered.

| BP section | Current foundation | Major missing scope | Disposition |
|---|---|---|---|
| 1 Platform layers | Identity, tasks, ITIL records, service/CI links, approvals, UI, analytics, audit | Formal module boundaries, durable automation, complete governance plane | Programme |
| 2 Queue security | Central ticket/request/enterprise visibility helpers plus governed REST/export/search projections | Compiled relationship-aware policy engine and independent review | P0 |
| 3 Queue catalogue | Ticket lists, task board, approvals, requests | Personal/team/practice/management queue catalogue and saved queue definitions | P1 |
| 4 Authorization | RBAC, tenant-aware root policies, group/relationship checks, transition guards and fail-closed Git-backed field permissions | ABAC/ReBAC policy compiler and independent authorization review | P0 |
| 5 Access levels | Git-backed action vocabulary, role grants, object manage/view separation and governed projections for every supported record API/export/JSON response | Relationship-aware compiled bindings and independent review | P0 |
| 6 Core data model | Existing Ticket, EnterpriseRecord, request/task, history and related models | Common versioned work-item foundation and many listed organisation/metric fields | Architecture decision |
| 7 Relationships | INC/PRB/CHG/REQ/RITM/PTASK/CTASK/SCTASK and CI relationships | Duplicate/outage/alert/release/deployment/vendor/improvement relationships | P1 |
| 8.1 Interaction | No dedicated interaction model | Complete interaction intake/classification/conversion lifecycle | P1 |
| 8.2 Incident | Core incident, parent/child, major profile, SLA, CI and relationships | Full hold reasons, routing, escalation, confirmation, survey and auto-close | P1 |
| 8.3 Major incident | MajorIncidentProfile and coordination fields | Full roles, bridge, stakeholder comms, status page, PIR and follow-up actions | P1 |
| 8.4 Requests/catalog | REQ/RITM/SCTASK, catalog administration, routing, approvals | Catalogs/categories/typed variables/entitlements/bundles/pricing/drafts/order guides | P1 |
| 8.5 Problem | PRB, PTASK, known error, RCA/workaround/fix and links | Configurable models, RCA techniques, clustering, risk acceptance and automation | P1 |
| 8.6 Change | Types, plan, risk, CCB, CTASK, conflicts, reapproval | Standard catalog, CAB meetings, blackout windows, PIR/evidence and retrospectives | P1 |
| 8.7 Knowledge | Basic article list/create/search | Bases, lifecycle, versions, feedback, access rules, analytics and translation | P1 |
| 8.8 Service levels | Definitions, task SLAs, Git-backed priority matrix, governed overrides, business calendars/time zones/holidays, lifecycle evidence and worker breach escalation | OLA/contracts, prediction, retroactive recalculation policy and escalation ladders | P0/P1 |
| 8.9 Events | No event/alert domain | Ingestion, normalization, correlation, suppression, CI binding and incident creation | P1 |
| 8.10 CMDB | CI classes, relationships, task links, conflict checks, admin manual create/edit/retire for CIs and CI relationships, and a REST auto-registration endpoint (`cmdb:write`) with a lightweight Linux/Puppet sync agent | Identification/reconciliation, discovery beyond self-reported facts, health, certification and history | P1 |
| 8.11 Release/deployment | Change tasks only | Separate release/deployment models, evidence, waves, pipeline integration | P1 |
| 8.12 Improvement | Generic enterprise module only | Purpose-built continual-improvement register and outcome tracking | P2 |
| 9 Priority | Priority field | Impact/urgency matrix, justification and controlled P1 criteria | P0 |
| 10 Assignment | Explicit teams (assignment is always by team name, never by picking an individual manager/user), team-scoped assignees, catalog routing, and explicit team-to-team reassignment for incidents/changes that restarts change approval against the new owning team | Ordered configurable rules, skills, on-call, workload and loop detection | P0/P1 |
| 11 Approvals | Chains, gates, any/all/majority, sequential stages and reapproval | Delegation, timeouts, dynamic resolution, signatures and broader policies | P0/P1 |
| 12 Web UI | Shell, lists, forms, board, portal-style catalog, admin settings, type-ahead reference-field search for CIs and cross-record links, a manager portal and cross-record task queue, and admin-configurable dashboard widgets | Advanced list engine, workspace personas, delegation, tabs, tours and mobile | P1/P2 |
| 13 Rules/workflows | Git-backed versions, restricted conditions/actions, reusable cycle-safe subflows, state/manual/API/SLA/scheduled triggers, recurring scheduler, durable waits, step evidence, rate limits, retry/dead state, replay, terminal safe compensation, correlation, idempotency and simulation | Broader actions, calendar/blackout scheduling, concurrency quotas and configuration-promotion governance | P0 |
| 14 Service model | Services, offerings, CIs, assets and relationships | Full hierarchy, governance, reconciliation, certification and import APIs | P1 |
| 15 Search | Access-aware global and domain search | Full text index, facets, typo/synonym support and search analytics | P1 |
| 16 Communication | In-app notifications plus durable SMTP, signed webhook and Teams delivery with retry/dead state and evidence | Templates, preferences, digests, inbound email, SMS/push and external validation | P0/P1 |
| 17 Identity/tenancy | Local, LDAP/AD, Keycloak OIDC, default-tenant migration and tenant-aware root isolation | SAML, SCIM, MFA policy, session inventory, API identity and independent isolation review | Architecture/P0 |
| 18 Security/compliance | Headers, CSRF, server authorization, tenant-chained evidence, governed key rotation, retention/legal hold, signed SIEM delivery, digest-only images, vulnerability gates, keyless signatures, provenance/SBOM attestations and Sigstore admission | Representative registry/cluster/immutable-store validation, malware scanning and independent review | P0 |
| 19 Analytics | Basic access-aware dashboard | Full KPI definitions, time series, CSAT, scheduled reports and governed exports | P1 |
| 20 APIs/integrations | REST v1 ticket/incident contract, tenant/user-bound API identities, scopes (including `cmdb:write` CI auto-registration), cursor pagination, request IDs, OpenAPI and idempotent writes | Broader resources, OAuth2/client assertions, rate limits, webhooks, imports and adapters | P0/P1 |
| 21 Architecture | Flask modular monolith, PostgreSQL, Docker/Helm | Decision on modularization or rewrite plus search/cache/event/object-store services | Architecture decision |
| 22 Config deployment | Container configuration and admin settings | Git-backed configuration packages, diff, validation, promotion and rollback | P0/P1 |
| 23 Implementation order | Several initial/core capabilities exist | Execute dependency-ordered programme with release gates | Governed roadmap |
| 24 Deferred features | Current product largely follows this constraint | Explicit decision records for intentionally deferred advanced features | Governance |
| 25 Credible core | Chains, lifecycle controls and initial tenant isolation verified | Field security, durable timers, calendars, APIs, config versions and DR proof | Release gate |

**Programme acceptance gate**: no section becomes `Verified` until its atomic
requirements have automated tests, authorization tests, documentation,
migration and rollback evidence, deployment evidence, and any required
external-system validation. External services such as AD, Keycloak, email,
object storage, search and Kubernetes cannot be certified using mocks alone.

**Approved architecture disposition:**

| Decision area | Approved BP-001 disposition |
|---|---|
| Tenancy | One organisation initially; enforce tenant identifiers and tenant-aware authorization conventions now |
| Application | Incremental bounded-module refactor behind stable interfaces; no rewrite |
| Theme | Light-only; dark mode is a governed non-requirement |
| Infrastructure | PostgreSQL standard profile; enterprise services are optional adapters over shared contracts |
| Integrations | SMTP/email, signed webhooks, monitoring ingestion, Microsoft Teams |
| API | Versioned REST first; GraphQL deferred pending a demonstrated consumer |
| Mobile | Responsive installable PWA first; preserve future native-client contracts |
| Configuration | Git-backed declarative source; database is deployed runtime state |
| Programme order | Security and platform foundations before visible expansion |
| Data | Preserve through reversible versioned migrations with upgrade, verification and rollback tests |
