# ServiceOps engineering and governance

Use the [documentation index](../README.md) to navigate the six maintained documents. Update this document directly; there is no generated master copy.

## Contents

- [Product governance and non-deviation policy](#section-governance)
- [ITIL / ServiceNow-pattern ticket hierarchy reference](#section-itil_ticket_hierarchy)
- [ITIL categorisation standard](#section-itil_v5_categorisation)
- [Australia UI guide capability mapping](#section-ui_capability_mapping)
- [ServiceOps controlled blueprint registry](#section-blueprints-blueprint_registry)
- [BP-001 programme traceability](#section-blueprints-blueprint_traceability)
- [ServiceOps AI implementation plan](#section-ai_implementation_plan)
- [ServiceOps engineering reference](#section-engineering_reference)

---

<a id="section-governance"></a>

## Product governance and non-deviation policy

<a id="section-governance--product-governance-and-non-deviation-policy"></a>

<a id="section-governance--product-boundary"></a>
### Product boundary

ServiceOps is an independently implemented service-management platform. It
must not be described as ServiceNow, ServiceNow-compatible, certified, or as
containing “all ServiceNow features.” Reference material may inform workflows
and usability; implementation status is proven only by repository evidence and
tests in the traceability matrix.

<a id="section-governance--non-negotiable-controls"></a>
### Non-negotiable controls

1. Production-only runtime: no demo mode, shared personas, sample records, or
   default credentials.
2. No requirement is “done” without acceptance criteria, implementation
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
8. Product changes update `BACKLOG.md`, [TRACEABILITY_MATRIX.md](BACKLOG.md#section-traceability_matrix), the decision
   log below when applicable, and the relevant manual in the same change.

<a id="section-governance--change-gate"></a>
### Change gate

Every release must pass unit/integration tests, dependency and image scans,
lint/type checks, migration rehearsal, backup/restore rehearsal, authorization
tests, and a production-like smoke test. Exceptions require a documented
owner, expiry date, impact, mitigation, and CCB approval.

<a id="section-governance--architecture-decision-log"></a>
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

<a id="section-governance--governed-non-requirements"></a>
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

<a id="section-governance--current-production-readiness-verdict"></a>
### Current production-readiness verdict

**Not approved for enterprise production yet.** P0 backlog items include
versioned migrations, comprehensive CSRF and authorization assurance,
append-only audit controls, proven disaster recovery/failover, supply-chain
attestation, and independent penetration testing.

Approval requires clean-checkout quality gates, representative AD/Keycloak
tests, a real HA Kubernetes deployment, restore and failure-injection evidence,
load/soak results, security and accessibility assessments, and accountable
operations, security, privacy, and CCB sign-off.

The only exception is the explicit `tools/load_test_fixture.py` workflow on an
intentionally reset, isolated test database. It is never automatic, displays a
warning banner, and must be destroyed before any production assessment.

---

<a id="section-itil_ticket_hierarchy"></a>

## ITIL / ServiceNow-pattern ticket hierarchy reference

<a id="section-itil_ticket_hierarchy--itil--servicenow-pattern-ticket-hierarchy-reference"></a>

Reference material supplied by the product owner, preserved verbatim for future
implementation decisions. ServiceOps is inspired by these patterns but does not
claim full ServiceNow compatibility (see [GOVERNANCE.md](ENGINEERING_REFERENCE.md#section-governance)). Where ServiceOps'
current data model or state machine differs from what is described here, that
divergence is deliberate and documented in [TRACEABILITY_MATRIX.md](BACKLOG.md#section-traceability_matrix); this file
is the design reference, not a claim of current implementation status.

<a id="section-itil_ticket_hierarchy--governing-principle-implemented-in-serviceops-2026-07-29"></a>
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

---

<a id="section-itil_ticket_hierarchy--1-the-servicenow-itsm-ticket-hierarchy"></a>
### 1. The ServiceNow ITSM ticket hierarchy

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

<a id="section-itil_ticket_hierarchy--2-what-counts-as-a-sub-ticket"></a>
### 2. What counts as a sub-ticket

<a id="section-itil_ticket_hierarchy--21-execution-task"></a>
#### 2.1 Execution task

A defined piece of work: Incident Task, Problem Task, Change Task, Catalog
Task, Release Task. The parent owns the overall outcome; the task owns a
specific work package assigned to one group or person.

<a id="section-itil_ticket_hierarchy--22-child-ticket"></a>
#### 2.2 Child ticket

A full process record of the same or another class with its own lifecycle,
assignment, priority, SLA, work notes, and closure information (e.g. parent/child
incidents, Problem → Change, Incident → Change).

<a id="section-itil_ticket_hierarchy--23-approval-record"></a>
#### 2.3 Approval record

A decision record, not an execution task (`sysapproval_approver` in ServiceNow;
`ApprovalChain`/`ApprovalGate`/`ApprovalVote` in ServiceOps). Identifies what
requires approval, who must approve, the decision state, comments, timestamp,
and delegation information.

<a id="section-itil_ticket_hierarchy--24-linked-object"></a>
#### 2.4 Linked object

Context, not a ticket: CI, business service, affected service, outage,
knowledge article, attachment, SLA record, change conflict, maintenance
window, CAB meeting, risk assessment, test evidence.

<a id="section-itil_ticket_hierarchy--3-incident-management"></a>
### 3. Incident Management

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

<a id="section-itil_ticket_hierarchy--4-major-incident-management"></a>
### 4. Major Incident Management

Still fundamentally an Incident record, with additional controls, roles,
workbench functions, communications, and review process. Lifecycle: Potential
→ Candidate → Review → Accepted/Rejected → Promoted → Response/communication →
Restoration → Resolution → Post-Incident Review → Problem creation.

Ownership split: Major Incident Manager owns coordination/communication/
escalation/timeline/stakeholders/recovery governance; technical resolver
groups own diagnosis/workaround/restoration/evidence; the Problem Manager
owns the later root-cause process.

<a id="section-itil_ticket_hierarchy--5-problem-management"></a>
### 5. Problem Management

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

<a id="section-itil_ticket_hierarchy--6-change-management"></a>
### 6. Change Management

A Change Request must answer what is changing, why, which services/CIs are
affected, business impact, technical risk, implementation/test/backout plans,
required approvers, schedule, and post-implementation outcome.

<a id="section-itil_ticket_hierarchy--61-standard-change"></a>
#### 6.1 Standard Change
Low risk, repeatable, documented, pre-authorized via an approved template/model.
Does not normally require fresh CAB approval each occurrence, but each
instance still needs validation against the approved Standard Change
conditions.

<a id="section-itil_ticket_hierarchy--62-normal-change"></a>
#### 6.2 Normal Change
Neither Standard nor Emergency; full assessment and authorization (technical,
change-management, CAB as applicable).

<a id="section-itil_ticket_hierarchy--63-emergency-change"></a>
#### 6.3 Emergency Change
Used when delay would cause or extend serious business impact. Still requires
expedited assessment and authorization (Emergency CAB or designated emergency
approver) — never "no approval." May move directly toward Authorize rather
than every Normal Change stage.

<a id="section-itil_ticket_hierarchy--64-typical-change-states-legacytraditional-model"></a>
#### 6.4 Typical Change states (legacy/traditional model)
New → Assess → Authorize → Scheduled → Implement → Review → Closed (or
Canceled at any point). Current ServiceNow implementations may use
configurable Change Models with different states/transitions.

Detailed process per state — required information, permitted/blocked tasks,
assessment activities, authorization approver types, schedule entry
conditions, implementation activities/outcomes, review questions, and closure
requirements — is preserved in full in the original product-owner submission
(session transcript, 2026-07-29) and summarized in section 14 below as
governance rules.

<a id="section-itil_ticket_hierarchy--7-change-tasks"></a>
### 7. Change Tasks

Official task types: **Planning, Implementation, Testing, Review**. Created
manually or via workflow/flow.

<a id="section-itil_ticket_hierarchy--change-task-unlocking-model"></a>
#### Change Task unlocking model

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

<a id="section-itil_ticket_hierarchy--8-request-management"></a>
### 8. Request Management

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

<a id="section-itil_ticket_hierarchy--sctask-is-not-a-child-of-chg--implemented-2026-07-29"></a>
#### SCTASK is not a child of CHG — implemented 2026-07-29

SCTASKs belong to RITMs, not Change Requests. `CatalogTask` has no
`parent_id`/`parent_type` pointing at a `Ticket` — a Change Request relates to
a RITM only through `RecordLink` (`link_type="requested_item_change"`), the
same relationship mechanism used for every other cross-record link in
ServiceOps. There is no CHG→SCTASK parent-child relationship anywhere in the
schema, and none should be added.

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

<a id="section-itil_ticket_hierarchy--9-request-versus-incident"></a>
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

A Request can create an Incident or Change when fulfillment discovers an
operational issue or requires controlled production modification. ServiceNow
maintains the relationship between the Requested Item and the generated
Incident or Change Request; ServiceOps does this via `RecordLink`.

<a id="section-itil_ticket_hierarchy--10-universal-request"></a>
### 10. Universal Request

A common front-door ticket for when the requester does not know which
department/process should handle the matter. The Universal Request handles
the requester-facing conversation; the primary ticket (Incident, RITM, HR
Case, Customer Case) handles specialist execution. Use when employees should
not need to understand internal ticket types, work may transfer between
departments, or a consistent portal experience is required — not as an
unnecessary wrapper around every record. **Not currently implemented in
ServiceOps**; tracked as a candidate backlog item if a genuine multi-department
front door becomes a requirement.

<a id="section-itil_ticket_hierarchy--11-release-management"></a>
### 11. Release Management

Groups multiple Changes/deployment activities into a coordinated delivery
(planning, design, build, configuration, testing, deployment readiness,
communications, go-live, early-life support). A Release does not replace
Change authorization — each production-affecting Change still follows its
applicable Change model. **Not currently implemented in ServiceOps**.

<a id="section-itil_ticket_hierarchy--12-relationships-between-the-main-tickets"></a>
### 12. Relationships between the main tickets

- Incident → Problem: many Incidents → one Problem (shared underlying cause).
- Problem → Change: one Problem → one or more Changes (permanent fix).
- Incident → Change: service restoration requires a controlled modification.
- Request → Change: RITM → Change Request when fulfillment requires one.
- Major Incident → Problem: root-cause analysis and prevention.
- Change → Incident: a failed Change may create/link to an Incident.
- Change → Problem: a failed or repeatedly unsuccessful Change may lead to a
  Problem investigation.
- Release → Change: coordinated deployment governance.

<a id="section-itil_ticket_hierarchy--13-the-complete-operational-chain"></a>
### 13. The complete operational chain

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

<a id="section-itil_ticket_hierarchy--14-mandatory-governance-rules-for-serviceops"></a>
### 14. Mandatory governance rules for ServiceOps

<a id="section-itil_ticket_hierarchy--parent-ticket-controls"></a>
#### Parent ticket controls
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

<a id="section-itil_ticket_hierarchy--approval-controls"></a>
#### Approval controls
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

<a id="section-itil_ticket_hierarchy--change-task-controls--implemented-2026-07-29"></a>
#### Change Task controls — implemented 2026-07-29
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

<a id="section-itil_v5_categorisation"></a>

## ITIL categorisation standard

<a id="section-itil_v5_categorisation--itil-categorisation-standard"></a>

Adopted 2026-09-27 at the product owner's direction. This is ServiceOps's
standard for record types and categorisation. It is written from the guidance
below, not from the ITIL Version 5 publications themselves, which are only
available through PeopleCert Plus membership. ServiceOps is *aligned with*
this guidance; it does not claim ITIL certification or conformance.

<a id="section-itil_v5_categorisation--source-guidance"></a>
### Source guidance

- ITIL Version 5 launched on 29 January 2026 with 34 practices. The Foundation
  syllabus covers value co-creation, the four dimensions of product and service
  management, the Product and Service Lifecycle Model (PSLM), and continual
  improvement.
- Categorisation guidance sits inside individual practices (for example
  Incident Management and Service Request Management). It requires consistent
  categorisation; it does not prescribe the categories.

<a id="section-itil_v5_categorisation--record-types"></a>
### Record types

The top-level types follow from the practices and carry over from ITIL 4.

| ITIL record type | ServiceOps record |
|---|---|
| Incident (unplanned interruption or degradation) | `Ticket` with `kind = "incident"` (INC) |
| Service request (standard, pre-approved request) | `CatalogRequest` (REQ) → `RequestedItem` (RITM) → `CatalogTask` (SCTASK) |
| Problem (underlying cause of one or more incidents) | `EnterpriseRecord` domain `problem` (PRB) with `ProblemProfile`; `OperationalTask` (PTASK) |
| Change (addition, modification or removal of a service component) | `Ticket` with `kind = "change"` (CHG) and `ChangeGovernance`; `OperationalTask` (CTASK) |
| Event or alert (monitoring signal, often automatic) | `MonitoringEvent`, and `EnterpriseRecord` domain `event` |
| Known error (problem with a documented cause or workaround) | `ProblemProfile.known_error`, listed at `/known-errors` |

<a id="section-itil_v5_categorisation--category-model-incidents"></a>
### Category model (incidents)

Two levels. The starter tree seeded for a new tenant, and applied to existing
tenants by migration `20260927_0106`:

| Category | Subcategories |
|---|---|
| Hardware | Desktop, Laptop, Server, Storage, Peripheral |
| Software / Application | Business application, OS, Licensing, Patching |
| Network | LAN, WAN, VPN, DNS, Firewall, Wi-Fi |
| Access / Identity | Account creation, Password reset, Permissions, MFA |
| Infrastructure / Platform | Compute, Virtualisation, Containers, Cloud, Backup |
| Security | Malware, Phishing, Vulnerability, Policy breach |
| Data / Database | Availability, Performance, Corruption, Restore |
| Communication | Email, Telephony, Collaboration tools |
| Facilities / Endpoint services | Printing, Workplace equipment |

Administrators may adapt the tree (Service operations settings → Ticket
categories). Service requests are categorised through the service catalog
(catalog item and its category) rather than this tree.

<a id="section-itil_v5_categorisation--design-rules-and-how-serviceops-applies-them"></a>
### Design rules and how ServiceOps applies them

| Rule | Implementation |
|---|---|
| Two levels, three at most | Category → subcategory; no third level exists. |
| No more than about 8–10 options per level | The admin page states the rule and warns when a level has more than 10 active options (`CATEGORY_LEVEL_OPTION_LIMIT`). Not a hard block. |
| Categorise by the affected service or CI, not by the fix | Stated on the admin page and the incident Resolution block; subcategories can suggest a service offering; incidents link a configuration item. |
| Record category at logging and at closure separately | `Ticket.category/subcategory` are the logging categorisation, required on the new-incident form. `closure_category/closure_subcategory` are captured when resolving (defaulting to the logging values if none is chosen) and are only saved when resolving or on a resolved record, so an early prefill can't go stale. |
| Pair categorisation with impact and urgency to derive priority | Incident priority is calculated from impact × urgency; overriding it requires a manager and a reason. |
| Changes: classify by change model plus affected CI or service, not a symptom tree | New changes store no category/subcategory; the change form and record show the change model (Standard, Normal, Emergency) and configuration item instead. |

<a id="section-itil_v5_categorisation--resolution-data"></a>
#### Resolution data

- `resolution_notes` documents how service was restored. Resolving an incident
  from the web UI (record form, Resolve button, task board) requires it. The v1
  REST API accepts it but keeps it optional so existing integrations don't
  break; this is the one intentional difference between channels.
- `resolved_at` records the latest entry into Resolved (or into Closed without
  passing through Resolved) and is cleared on reopen. Mean time to resolve and
  the "resolved in the last 30 days" figures use it, falling back to
  `updated_at` only for tickets resolved before the column existed and without
  ticket history (migration `20260927_0105` backfilled the rest from history).
- Analytics shows incidents by closure category (falling back to the logging
  category where none was recorded) and the share recategorised at closure.

<a id="section-itil_v5_categorisation--taxonomy-changes-and-existing-tickets"></a>
#### Taxonomy changes and existing tickets

- Renaming a category or subcategory relabels the tickets that carry it, so
  reporting is not split across two labels.
- Deactivated ("retired") categories stay on existing tickets. The form shows
  them as "(retired)" and keeps them on save instead of recategorising.
- Tickets whose submitted category matched nothing (older integrations) are
  stored as `General`, which is no longer offered on the form and reads as
  uncategorised in reports.
- Startup seeding only seeds a tenant with no categories, so administrator
  changes are never overwritten on restart.

<a id="section-itil_v5_categorisation--not-covered-or-not-claimed"></a>
### Not covered or not claimed

- ITIL Version 5 practice content beyond the guidance above (the 34 practices,
  PSLM) has not been reviewed against the publications, which were not
  available.
- Affected CI or service is surfaced but not mandatory on changes.
- Categories recorded on incidents while the category picker was broken
  (2026-09-26 to the fix in `b56b608`) were reset to `General` on save. Ticket
  history holds the prior values; restoring them is a separate, approved data
  repair.

---

<a id="section-ui_capability_mapping"></a>

## Australia UI guide capability mapping

<a id="section-ui_capability_mapping--australia-ui-guide-capability-mapping"></a>

Source reviewed: *Australia ServiceNow AI Platform user interface*, 1,148 pages, updated July 7, 2026.

This mapping uses the source guide as a behavioral reference. ServiceOps does not copy its text, images, product names, proprietary runtime, or implementation.

| Source guide family | ServiceOps implementation |
|---|---|
| Next Experience and unified navigation | Unified top navigation, collapsible application navigation, global search, favorites, history, notifications, help, preferences, and role-aware landing pages |
| Landing pages and dashboards | Operational dashboard, analytics workspace, workload counters, role-based record visibility, selectable start page |
| Configurable workspace | Purpose-built ticket, request, change, CMDB, catalog, approval, analytics, and service operations settings workspaces |
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
| Native mobile apps and offline distribution | Native iOS 1.3.0 workspace implements authenticated tickets, approvals, knowledge, CMDB, passkeys, biometric locking, app-version evidence, and APNs/inbox notifications; App Store/TestFlight distribution and offline record synchronization are not included |

<a id="section-ui_capability_mapping--verification-expectations"></a>
### Verification expectations

Every capability described as implemented must have a working route or UI, persistent data where applicable, role enforcement, and automated or live runtime verification. Vendor-specific facilities are classified rather than represented by nonfunctional toggles.

---

<a id="section-blueprints-blueprint_registry"></a>

## ServiceOps controlled blueprint registry

<a id="section-blueprints-blueprint_registry--serviceops-controlled-blueprint-registry"></a>

This directory is the private source-of-truth register for supplied product
blueprints. A blueprint is an input specification, not evidence that a feature
is implemented. Delivery status is controlled through [BLUEPRINT_TRACEABILITY.md](ENGINEERING_REFERENCE.md#section-blueprints-blueprint_traceability),
`../BACKLOG.md`, tests, and release evidence.

<a id="section-blueprints-blueprint_registry--registered-sources"></a>
### Registered sources

| ID | Title | Received | Source | Integrity |
|---|---|---|---|---|
| BP-001 | Blueprint for building your own ServiceNow-class ITSM platform | 2026-07-26 | Codex attachment `c43eee81-3c99-42be-8a2e-6cbdab3ae719/pasted-text.txt` | SHA-256 `4c4d4f0b6e589e277b7663e6e99e2699817dca567cdeda853585ab9cf759df48`; 2,060 lines; 43,034 bytes |

<a id="section-blueprints-blueprint_registry--preservation-rule"></a>
### Preservation rule

The registered source is immutable. Requirement interpretation, priorities and
acceptance criteria belong in the traceability document; the supplied wording
must not be silently rewritten. If a revised blueprint is supplied, register a
new source revision and record its relationship to BP-001.

<a id="section-blueprints-blueprint_registry--non-deviation-rule"></a>
### Non-deviation rule

Every BP-001 requirement must have:

1. a stable requirement identifier;
2. a disposition of verified, implemented, planned, deferred, rejected or
   externally dependent;
3. acceptance criteria and evidence;
4. a backlog or decision reference; and
5. release and live-validation evidence before it is called complete.


---

<a id="section-blueprints-blueprint_traceability"></a>

## BP-001 programme traceability

<a id="section-blueprints-blueprint_traceability--bp-001-programme-traceability"></a>

BP-001 defines a multi-release platform programme, not a single feature.
“Covered” below means a currently evidenced foundation exists. It does not mean
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

<a id="section-blueprints-blueprint_traceability--programme-acceptance-gate"></a>
### Programme acceptance gate

No section becomes `Verified` until its atomic requirements have automated
tests, authorization tests, documentation, migration and rollback evidence,
deployment evidence, and any required external-system validation. External
services such as AD, Keycloak, email, object storage, search and Kubernetes
cannot be certified using mocks alone.

<a id="section-blueprints-blueprint_traceability--approved-architecture-disposition"></a>
### Approved architecture disposition

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

---

<a id="section-ai_implementation_plan"></a>

## ServiceOps AI implementation plan

<a id="section-ai_implementation_plan--serviceops-ai-implementation-plan"></a>

Baseline: 2026-09-20. Owner: ServiceOps engineering; provider/data policy owner: tenant administrator.
Status: ServiceOps 1.101.3 is deployed at Helm revision 108. Transient activity UI, multiple-service privacy and quota routing, whole-product permission-scoped context, ticket drafts, explicit per-user memory, secure context retrieval, live self-hosted streaming, generated staff drafts, approved ticket actions, and exact authorized cross-module evidence are verified. Customer, service-request and restricted-domain content is forced onto private AI. Commercial live inference remains unverified. Estimates are engineering effort, not promised calendar delivery.
No hosted GitHub publication is part of this work.

<a id="section-ai_implementation_plan--product-scope-and-timeline"></a>
### Product scope and timeline

| Milestone | Effort / target sequence | Tasks | Exit criteria | Status |
|---|---|---|---|---|
| AI-01 Control plane | Days 1–2 | Tenant-scoped settings; administrator master and incident-feature switches; encrypted credentials; audit; configuration revision; cancellation | Negative authorization, tenant isolation, disable/re-enable races, CSRF and secret handling pass | Complete |
| AI-02 Provider connections | Days 3–4; depends on AI-01 | Self-hosted compatible chat endpoint and external OpenAI Responses adapter; destination allowlist; DNS pinning; timeout and output limits; synthetic connection check | Both protocol contracts pass; real provider checks recorded separately | Complete |
| AI-03 Incident assistant | Days 5–7; depends on AI-01/02 | Durable jobs and dedicated worker; permission-filtered incident/comments, knowledge, similar incidents and related CIs; cited read-only recommendations; cancel/status UI | End-to-end flow, current-access checks, interrupted jobs and duplicate submissions pass | Complete |
| AI-04 Acceptance | Days 8–10; depends on AI-01–03 | PostgreSQL upgrade/rollback, functional/security/browser/accessibility, provider evaluation, backup restore, immutable image, MicroK8s rollout and runbook | Deployment evidence recorded; new configurations default off and existing administrator enablement is preserved | Deployed; provider evaluation gaps below |
| AI-05 Approved actions | Days 11–15; depends on AI-04 quality review | Exact proposed change; expiring approval bound to record version; reauthorize; existing mutation APIs; audit/idempotency | No approval bypass, stale action rejection, no duplicate mutation | Ticket comments, state, priority and assignment plus generated staff drafts are deployed; the separate action switch remains off by default |
| AI-06 Secure context retrieval | Days 16–17; can run alongside later AI-05 slices | Exact visible-record counts; expanded knowledge vocabulary; grounded conversational references; visible linked records and permitted CIs; safe provider-failure guidance | Model payload contains useful context and no hidden, cross-tenant, unpublished or forbidden records for every existing access scope | Verified in 1.101.3: citable enterprise records, requests/tasks, customer tickets and assets, with mandatory private routing for sensitive modules |

The initial implementation may advance faster than these estimates. Actual completion is tracked by evidence, not elapsed days. Dependencies: configured model endpoint/model and credentials; a reachable build engine; a working acceptance cluster. Both self-hosted and external modes are required by the user. Never silently fall back from local to hosted processing.

<a id="section-ai_implementation_plan--first-release-architecture"></a>
### First-release architecture

Authenticated incident page -> tenant-scoped durable AI run -> dedicated AI worker -> bounded server-controlled retrieval -> selected provider -> escaped draft with source links. This first release is a constrained investigation workflow, not autonomous remediation. No shell, arbitrary HTTP, SQL, attachment parsing, ticket writes or automatic approvals are available to the model.

AI configuration uses a dedicated tenant-primary-key table: general PlatformSetting keys are global and are unsuitable for tenant AI credentials. Configuration saves increment a revision and invalidate queued/running jobs. Every execution and result publication rechecks that revision and enablement. Disabling stops new work and discards in-flight responses; it cannot retract data already transmitted to a provider. Results remain private to the requesting user, and all evidence permissions are rechecked before display. Saved credentials never appear in HTML, logs, audit details or job payloads.

Self-hosted destinations must be explicitly allowlisted by the operator, independently of tenant configuration. Hosted traffic uses a fixed HTTPS endpoint. Redirects and ambient HTTP proxies are disabled; addresses are validated and pinned. Local mode never falls back to hosted mode. Content is bounded and common secret patterns are redacted; this is not a guarantee that all sensitive prose can be detected. Administrator external-data consent is required for hosted enablement.

Jobs have explicit queued/running/completed/failed/cancelled states, a bounded lease and no automatic provider retry (avoid duplicate billing after uncertain completion). Configurable per-tenant daily request limits and output caps bound use. Expired output is purged by the dedicated worker. Audit retains event metadata, not prompt bodies. IPFS mode is excluded from this release because its single-process projection is incompatible with a separate database job worker.

<a id="section-ai_implementation_plan--validation-and-release-evidence"></a>
### Validation and release evidence

Recorded 2026-09-20 on the rebased 1.92.0 source (commit 7589df3). Provider tests use deterministic protocol fixtures against a controlled local server; they establish request/response handling, not model quality.

| Check | Result |
|---|---|
| Full suite (isolated test image) | 733 passed, 106 skipped; plus `test_docs_sync` on the host (needs sibling notes checkout) = 734 effective |
| AI unit/API tests | administrator-only access, CSRF, encrypted credentials, tenant isolation, duplicate submissions, daily limits, disable during in-flight run, unknown/absent citations, source re-authorization |
| PostgreSQL migration | upgrade 0094 to 0095, downgrade, roll-forward with 100,000 synthetic rows preserved; rollback refused once AI records exist |
| Real browser (PostgreSQL) | admin enable/disable and incident workflow at desktop, tablet and mobile, with axe WCAG 2 A/AA checks: 3 passed |
| Static gates | ruff, compileall, shell syntax, JavaScript syntax, migration-safety policy, Helm lint and client-side strict validation of every rendered manifest |
| Image scan (Trivy 0.58.2, HIGH/CRITICAL, fixed-only, from a `docker save` tarball, no Docker socket) | 13 findings, all Debian base-image packages (gzip, libpcre2, libsqlite3, perl-base); none in Python dependencies; requirements unchanged. To be re-scanned by the governed supply-chain gate on the released image |
| Backup restore | a fresh deployment backup restored and its 19 existing tickets survived the migration (recorded by the earlier acceptance run) |

Defect found during acceptance: the Helm ConfigMap wrote AI_SELF_HOSTED_ENDPOINTS under `metadata` as well as `data`. `helm lint` does not detect this, but Kubernetes rejects the unknown field, so it would have failed the upgrade. Fixed before release; the whole rendered chart now validates under strict client-side validation.

Not yet verified: live model evaluation (groundedness, missing evidence, malicious ticket instructions, latency, cost) against a real configured endpoint; the hosted/self-hosted round trip with real credentials; the MicroK8s rollout of the AI worker; and the governed release, image signature, SBOM and RPM evidence. AI remains disabled until an administrator configures and enables it.

<a id="section-ai_implementation_plan--ai-20-delivery-record-1931"></a>
### AI 2.0 delivery record (1.93.1)

Scope: streaming answers, visible reasoning, private role-scoped chat. Migration `20260921_0096`. Design and controls are documented in [AI_OPERATIONS.md](OPERATIONS_MANUAL.md#section-ai_operations); backlog entry B-366.

| Check | Result |
|---|---|
| Privacy matrix | 34 tests; every test plants a canary in data a role must not reach and inspects the exact payload the model would receive; verified by mutation (removing an ownership filter fails the suite) |
| Chat API | 17 tests: owner-only conversations (admins included), role change blocks a conversation, deactivated user, deletion, purge on erasure, rate limit, one active answer, idempotent retry, no content in audit rows |
| Streaming | 16 tests including a real SSE server, Stop mid-stream, admin disable mid-stream, stale heartbeat, thinking token allowance |
| Real browser under the production CSP | 9 tests at 1440, 768 and 390 px with axe WCAG 2 A/AA: widget open by keyboard, streaming, reasoning panel, markdown injection stays inert text, history delete, Escape returns focus, full-page chat and Stop |
| PostgreSQL migration | 0095 to 0096, downgrade and roll-forward with 20,000 synthetic rows preserved |
| Full suite | 817 passed, 112 skipped in the isolated Docker image |
| Live models (MacBook, CPU, llama.cpp) | qwen3-4b: 59 s per streamed investigation with reasoning; qwen3-8b: 99 s; Qwen2.5 3B/7B/14B answer without a reasoning stream. Requester scenarios (own ticket, another user's ticket, request by name, user list, injection text in own ticket) produced no leak |

Not verified: behaviour under sustained concurrent chat load; quality beyond the five scenarios above; hosted-provider streaming (not implemented).

<a id="section-ai_implementation_plan--sources"></a>
### Sources

- OpenAI Responses API: https://developers.openai.com/api/reference/cli/resources/responses/methods/create
- OWASP agent security: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html

<a id="section-ai_implementation_plan--adaptive-provider-discovery-1940"></a>
### Adaptive provider discovery (1.94.0)

Requested 2026-09-20. This extends the delivered chat and administrator controls. Estimates are incremental engineering effort; verification determines completion.

| Task | Sequence / estimate | Acceptance | Status |
|---|---|---|---|
| AD-01 Discover models and limits | Day 1 | Authenticated bounded listing, same-origin llama.cpp runtime properties, multiple-model choice | Implemented; protocol tests pass |
| AD-02 Persist trusted discovery | Day 1, after AD-01 | Signed preview bound to administrator, tenant, endpoint and credential | Implemented; negative binding tests pass |
| AD-03 Adapt requests | Days 1–2, after AD-01 | Preserve rules and question; shorten evidence/history; honor limits; omit unknown thinking parameters | Implemented; budget and privacy tests pass |
| AD-04 Acceptance | Day 2, after AD-01–03 | Migration, browser/accessibility, full regressions, immutable image, fresh backup restore, MicroK8s checks | Deployed; live inference limitation below |
| AD-05 Additional protocols | Subsequent increments | Documented adapter and contract/live tests per unsupported API | Backlog |

Verified: 135 focused tests; 10 PostgreSQL-backed browser/accessibility tests; migration 0096 to 0097, downgrade and roll-forward with 20,000 synthetic records preserved. Authenticated live llama.cpp metadata reports Qwen/Qwen3-8B-GGUF:Q4_K_M, runtime context 4096 and training context 40960. Metadata alone does not establish generation quality.

Adaptive acceptance evidence (2026-09-20):

- Full host suite: 857 passed, 112 skipped, one version/PWA mismatch caused by changing VERSION while the suite was in flight. The failed test passed independently after version synchronization; no runtime defect remained. Skipped tests are not passing evidence.
- Browser/accessibility: 10 passed against isolated PostgreSQL.
- Candidate: 1.94.0, private registry digest sha256:a67a37e3f1462824164688f3798a9afb72aaeeb04debda7be12c8dfe10bad7a7. Fresh OS package update; Trivy reports zero fixable HIGH/CRITICAL findings. No image signing or GitHub publication was performed.
- Fresh backup: serviceops-adaptive-20260920T141241Z, SHA-256 a8c98b45502860023818004c2b7d7ca40afb6bef2be18f600bce09340ecda589. Restore-tested locally; restored upgrade preserved all 19 tickets and existing AI settings, credentials and enablement.
- Static checks: ruff, JavaScript syntax, migration expand policy, version consistency, Helm lint and strict manifest validation passed.
- Live model limitation: authenticated models/props succeeded, but a synthetic READY request with thinking disabled timed out after 90 seconds. No operational records were sent. This does not identify a GPU, memory or model-load cause. Commercial credentials/inference and deployed authenticated browser access remain unverified.

MicroK8s acceptance completed: Helm revision 87, web 2/2, outbox 1/1, AI worker 1/1 on the recorded digest. Health and readiness returned 200 with version 1.94.0 and Alembic head 20260921_0097. Retained Helm health test succeeded. PostgreSQL and uploads PVC bindings were preserved; recent workload logs contained no detected error/traceback lines. Public HEAD returned Cloudflare 302 to wijesundara.cloudflareaccess.com (an earlier urllib GET returned 403). Deployed authenticated model discovery confirmed runtime /props context 4096, training context 40960 and thinking-template support. Existing AI enablement remained enabled and its key remained configured. The live inference timeout is an unresolved verification gap, not a successful model test.

<a id="section-ai_implementation_plan--live-verification-continuation-2026-09-21"></a>
### Live verification continuation (2026-09-21)

The workspace and deployment had independently advanced to 1.95.0. This continuation made no application, model-server, credential or deployment configuration changes. Current readiness returned 200 for 1.95.0 with migration 20260921_0097.

Two synthetic checks, with no operational records, succeeded against the configured self-hosted server:

- Direct authenticated streaming: HTTP 200, READY received, stream completed; first content at 33.85 seconds, total 33.94 seconds.
- Deployed ServiceOps provider adapter: READY received, one content delta, no reasoning delta; first content at 7.668 seconds, total 7.72 seconds. The in-memory discovered profile used runtime context 4096, conservative byte budgeting and a 32-token output cap. No saved configuration was changed.

These results establish live protocol/adapter compatibility for this model and resolve the previously unverified streaming path. They do not explain the earlier 90-second timeout or establish reliable latency under load, operational answer quality, or commercial-provider behavior. The same fallback policy remains in 1.96.0: context 4096 for unknown self-hosted limits and 32768 for unknown hosted limits; fallback values are assumptions, not provider-reported capabilities.

<a id="section-ai_implementation_plan--transient-activity-interface-acceptance-1960"></a>
### Transient activity interface acceptance (1.96.0)

The AI interface now presents one small changing activity label and removes it at completion. Model reasoning text is discarded rather than persisted or returned. The chat surface no longer draws an empty answer container or a Working/Complete badge. Progressive answer text, citations, Stop, Copy, deeper-reasoning requests, and administrator controls remain.

Validation on 2026-09-21: 61 focused tests; 10 PostgreSQL-backed Chromium/axe tests; 859 full-suite passes with 112 environment-dependent skips; streaming and completed desktop captures inspected; static/version/Helm/strict-manifest gates passed. The rebuilt image had zero fixable HIGH/CRITICAL scan findings. Backup `serviceops-ai-ui-20260921T010417Z` (SHA-256 `ccaba71a00ebfdc72b04d06778ee0f9afa36bf1d05d2d05873f123284d215c1d`, 1,565,964 bytes) restored successfully with migration `20260921_0097`, 19 tickets, 121 tables, and the existing enabled AI configuration preserved.

MicroK8s Helm revision 91 runs `localhost:32000/serviceops@sha256:b0f635418426acaf866a19bf34dd4cb4353654bed40810ac9192e141e96015dd`: web 2/2, outbox 1/1, AI worker 1/1. `/health` and `/ready` returned 200 for 1.96.0; the retained Helm test passed; PostgreSQL/uploads PVCs remained bound; recent web/outbox/AI-worker logs showed clean startup and probes; public access returned the expected Cloudflare Access 302. The deployed JavaScript contains the transient labels and no reasoning-text renderer. Existing AI/chat switches and the encrypted credential remained configured.

<a id="section-ai_implementation_plan--authorized-application-reach-acceptance-1992"></a>
### Authorized application reach acceptance (1.99.2)

The assistant now retrieves the signed-in person's membership in every active support or governance group, including an explicit Change Control Board answer. Managers and administrators can receive governance-group manager and member-count facts. CMDB discovery matches name, serial number, vendor, model, IP address, location and external ID, and supplies a bounded safe specification set. Related-ticket counts and records still pass through current ticket visibility and CI-class authorization. Natural list and recency wording such as “Show me active changes” and “last incident received” is handled explicitly. Knowledge-note, client-organization and module-link suggestions use the relevant product context instead of unrelated generic “active” pages.

Security remains identity-bound: this extends what the assistant can retrieve from records the current user may already read. Credentials, settings, audit contents, arbitrary CI JSON, customer content outside the permitted client summary, and other users' private details are not exposed. Profile questions are marked personal and remain eligible only for an organization's own AI under the configured routing policy.

Validation on 2026-09-22: 213 focused AI/privacy/provider/streaming tests and the full suite (`985 passed`, `114 skipped`) passed; the governed release repeated the application suite, dependency audit, browser/accessibility journeys, image vulnerability gate, SBOM, signature and provenance, five RPM build/install matrices, and publication. Backup `serviceops-20260922T103918Z.dump` restored successfully at migration `20260925_0101` with 19 tickets. The signed linux/amd64 image `sha256:1964350eb0aee0cbbdd13ac18d1e7fa6e6193492128afd7a62ea454a1574f31a` deployed at Helm revision 103. Web 2/2, outbox 1/1 and AI worker 1/1 became ready; the retained health test reported 1.99.2 and migration 0101; PostgreSQL, uploads and backup PVCs remained bound; recent workload logs contained no matching error/exception/traceback lines; Cloudflare Access returned 302.

A sanitized live admin-scope check verified CCB membership context, `SN000002` lookup with class/serial/vendor/model fields, one newest incident, two active changes, CMDB server summary, knowledge count and client-organization count. It emitted pass/fail and aggregate counts only, not operational record contents. Model wording and commercial-provider quality remain separate evaluation concerns.

---

<a id="section-engineering_reference"></a>

## Historical excerpts: ServiceOps engineering reference

Historical source: `docs/ENGINEERING_REFERENCE.md`. Exact duplicate prose already retained in the maintained sections has been omitted. Original dates, claims and superseded operating conventions in these excerpts remain historical.
<a id="section-engineering_reference--serviceops-engineering-reference"></a>

The architecture record for engineers and AI agents working on this codebase:
governance and non-deviation policy, the requirements traceability matrix, the
ITIL ticket-hierarchy design reference, the supplied UX-source capability
mapping, and the controlled blueprint register. For product usage see
[OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md#section-operations_manual); for deployment see
[DEPLOYMENT.md](DEPLOYMENT.md#section-deployment); for open/completed work see
[BACKLOG.md](BACKLOG.md#section-backlog).

**In this document:**

1. [Governance and non-deviation policy](#section-engineering_reference--1-governance-and-non-deviation-policy)
2. [Requirements traceability matrix](#section-engineering_reference--2-requirements-traceability-matrix)
3. [ITIL / ServiceNow-pattern ticket hierarchy reference](#section-engineering_reference--3-itil--servicenow-pattern-ticket-hierarchy-reference)
4. [UI capability mapping](#section-engineering_reference--4-ui-capability-mapping)
5. [Blueprint registry and programme traceability](#section-engineering_reference--5-blueprint-registry-and-programme-traceability)

---

<a id="section-engineering_reference--1-governance-and-non-deviation-policy"></a>
### 1. Governance and non-deviation policy

<a id="section-engineering_reference--product-boundary"></a>
#### Product boundary

ServiceOps is an independently implemented service-management platform. It
must not be described as ServiceNow, ServiceNow-compatible, certified, or as
containing "all ServiceNow features." Reference material may inform workflows
and usability; implementation status is proven only by repository evidence and
tests in the traceability matrix (§2 below).

<a id="section-engineering_reference--non-negotiable-controls"></a>
#### Non-negotiable controls

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

<a id="section-engineering_reference--change-gate"></a>
#### Change gate

<a id="section-engineering_reference--architecture-decision-log"></a>
#### Architecture decision log

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

<a id="section-engineering_reference--governed-non-requirements"></a>
#### Governed non-requirements

<a id="section-engineering_reference--production-readiness-verdict"></a>
#### Production-readiness verdict

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

---

<a id="section-engineering_reference--2-requirements-traceability-matrix"></a>
### 2. Requirements traceability matrix

| Requirement/source | ServiceOps evidence | Status | Backlog |
|---|---|---|---|
| Unified navigation, search, favorites, history, preferences (UI PDF: Next Experience) | `templates/base.html`, `/ui/search`, immutable `serviceops_core.navigation` catalogue, authorization-preserving database subqueries, PostgreSQL trigram indexes, favorites/recent views, unit and blocking browser tests | Verified | B-021, B-323 |
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
| Catalog line-manager approval routing and prerequisite validation | Both catalog creation paths resolve the requested-for user's active, same-tenant, non-self line manager and active Service Desk voters before creating records; LDAP DN lookup is case-insensitive; persisted votes snapshot the submission-time authority; complete form-flow tests cover a never-logged-in LDAP manager, notification delivery, DN casing drift, no administrator substitution, immutable in-flight routing, and fail-closed zero-record behavior | Verified | B-254, B-342 |
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

<a id="section-engineering_reference--connection-dependent-capability-boundary"></a>
#### Connection-dependent capability boundary

---

<a id="section-engineering_reference--3-itil--servicenow-pattern-ticket-hierarchy-reference"></a>
### 3. ITIL / ServiceNow-pattern ticket hierarchy reference

Reference material supplied by the product owner, preserved verbatim for future
implementation decisions. ServiceOps is inspired by these patterns but does not
claim full ServiceNow compatibility (see §1 above). Where ServiceOps' current
data model or state machine differs from what is described here, that
divergence is deliberate and documented in §2's traceability matrix; this
section is the design reference, not a claim of current implementation status.

<a id="section-engineering_reference--governing-principle-implemented-in-serviceops-2026-07-29"></a>
#### Governing principle implemented in ServiceOps (2026-07-29)

<a id="section-engineering_reference--31-the-servicenow-itsm-ticket-hierarchy"></a>
#### 3.1 The ServiceNow ITSM ticket hierarchy

A practical hierarchy looks like this:

The formal Service Catalog hierarchy is:

```
REQ
└── RITM
    └── SCTASK
```

<a id="section-engineering_reference--32-what-counts-as-a-sub-ticket"></a>
#### 3.2 What counts as a sub-ticket

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

<a id="section-engineering_reference--33-incident-management"></a>
#### 3.3 Incident Management

<a id="section-engineering_reference--34-major-incident-management"></a>
#### 3.4 Major Incident Management

<a id="section-engineering_reference--35-problem-management"></a>
#### 3.5 Problem Management

<a id="section-engineering_reference--36-change-management"></a>
#### 3.6 Change Management

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

<a id="section-engineering_reference--37-change-tasks"></a>
#### 3.7 Change Tasks

**Change Task unlocking model:**

<a id="section-engineering_reference--38-request-management"></a>
#### 3.8 Request Management

**SCTASK is not a child of CHG** (implemented 2026-07-29): SCTASKs belong to
RITMs, not Change Requests. `CatalogTask` has no `parent_id`/`parent_type`
pointing at a `Ticket` — a Change Request relates to a RITM only through
`RecordLink` (`link_type="requested_item_change"`), the same relationship
mechanism used for every other cross-record link in ServiceOps. There is no
CHG→SCTASK parent-child relationship anywhere in the schema, and none should
be added.

<a id="section-engineering_reference--39-request-versus-incident"></a>
#### 3.9 Request versus Incident

<a id="section-engineering_reference--310-universal-request"></a>
#### 3.10 Universal Request

<a id="section-engineering_reference--311-release-management"></a>
#### 3.11 Release Management

<a id="section-engineering_reference--312-relationships-between-the-main-tickets"></a>
#### 3.12 Relationships between the main tickets

<a id="section-engineering_reference--313-the-complete-operational-chain"></a>
#### 3.13 The complete operational chain

For a requested service:

<a id="section-engineering_reference--314-mandatory-governance-rules-for-serviceops"></a>
#### 3.14 Mandatory governance rules for ServiceOps

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

---

<a id="section-engineering_reference--4-ui-capability-mapping"></a>
### 4. UI capability mapping

| Source guide family | ServiceOps implementation |
|---|---|
| Next Experience and unified navigation | Unified top navigation, collapsible application navigation, global search, favorites, history, notifications, help, preferences, and role-aware landing pages |
| Landing pages and dashboards | Operational dashboard, analytics workspace, workload counters, role-based record visibility, selectable start page |
| Configurable workspace | Purpose-built ticket, request, change, CMDB, catalog, approval, analytics, and service operations settings workspaces |
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
| Native mobile apps and offline distribution | Native iOS 1.3.0 workspace is implemented with user authentication, passkeys, biometric locking, operational workflows, app-version audit context, and APNs/inbox notifications; distribution and offline record synchronization remain external |

<a id="section-engineering_reference--verification-expectations"></a>
#### Verification expectations

---

<a id="section-engineering_reference--5-blueprint-registry-and-programme-traceability"></a>
### 5. Blueprint registry and programme traceability

This is the private source-of-truth register for supplied product blueprints.
A blueprint is an input specification, not evidence that a feature is
implemented. Delivery status is controlled through this section, `BACKLOG.md`,
tests, and release evidence.

<a id="section-engineering_reference--51-registered-sources"></a>
#### 5.1 Registered sources

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

<a id="section-engineering_reference--52-bp-001-programme-traceability"></a>
#### 5.2 BP-001 programme traceability

BP-001 defines a multi-release platform programme, not a single feature.
"Covered" below means a currently evidenced foundation exists. It does not mean
the complete section has been delivered.

**Programme acceptance gate**: no section becomes `Verified` until its atomic
requirements have automated tests, authorization tests, documentation,
migration and rollback evidence, deployment evidence, and any required
external-system validation. External services such as AD, Keycloak, email,
object storage, search and Kubernetes cannot be certified using mocks alone.

**Approved architecture disposition:**

<a id="section-engineering_reference--ai-module-boundary"></a>
### AI module boundary

<a id="section-engineering_reference--web-route-modules-b-401"></a>
### Web route modules (B-401)

`app.create_app()` configures the application, registers request hooks,
error handlers and template filters, and then calls `register(app)` on each
route module in `serviceops_core/web/`. It defines no routes itself, and
`tests/test_web_modules.py` fails if one is added back to `app.py`.

| Module | Routes |
| --- | --- |
| `platform.py` | Health, readiness, metrics, status page, PWA manifest and service worker, help |
| `auth.py` | Sign-in, sign-out, password reset, OIDC/LDAP/Cloudflare Access login, sessions |
| `api.py` | `/api/v1` REST and mobile API, SCIM, the embedded MCP endpoint |
| `workspace.py` | Home, profile, preferences, notifications, manager portal, analytics, lookups, UI state |
| `tickets.py` | Incidents, changes, problems, known errors, improvements, enterprise records, attachments |
| `service_requests.py` | Catalog, requests, RITMs, catalog tasks, approvals |
| `cmdb.py` | CMDB, assets, racks, topology, import and discovery |
| `knowledge.py` | Knowledge base |
| `client_management.py` | External customer support (client tickets, organisations, views) |
| `administration.py` | Administration, settings, ITIL administration |
| `common.py` | Helpers and constants shared by several route modules |

Endpoint names are unchanged from when the routes lived in `create_app()`
(each module registers directly on the app, not through a Flask blueprint),
so every `url_for()` call, template and API client keeps working. Route
modules import shared services from `app`; names that tests monkeypatch on
the `app` module (outbound delivery, scanning, LDAP, `setting_value`,
`tenant_context_id` and a few others) are read as `core.<name>` through
`import app as core`, so a patch on `app.<name>` reaches the routes too.

New routes go in the module for their area. Business rules still belong in
`serviceops_core/` service and policy modules, not in route handlers.
Moving module-level services out of `app.py` (about 7,300 lines of
services and helpers above `create_app()`) is the next decomposition step.

### Syslog forwarding boundaries

`serviceops_core/syslog_forwarding.py` uses a daemon worker and a 1,024-record bounded queue. Request threads enqueue already redacted/formatted messages without remote socket I/O. Records larger than 60,000 bytes are retained locally and produce a rate-limited warning. Socket operations have a two-second timeout; destination failures suppress further attempts for 30 seconds, with a local warning at most once per minute. Forwarder warnings bypass the remote handler to avoid recursive failures. TLS uses verified default SSL context; web and both workers read startup settings after database/migration initialization. Global receiver settings use the existing installation-settings administrator boundary.

### Offline interface localization and AI references

**Source.** Every interface string goes through one translation function. Templates call the Jinja globals `tr('Text {name}', name=value)`, `trn(count, singular, plural)` and `tr_value(value)`; Python uses `serviceops_core.localization.tr()` for flash messages, abort descriptions and user-facing exceptions (ValueError, workflow/trigger/priority configuration, RT import and AI provider errors); scripts call `tr()`/`trNoop()` from `static/i18n.js`. Values inside sentences are named parameters so word order can change; English source text is the message id and the final fallback. `tools/i18n_wrap_templates.py` and `tools/i18n_wrap_python.py` performed the migration and remain for new code; a test re-runs the template rewriter and fails if any template contains unwrapped interface text.

**Fixed values.** `serviceops_core/interface_values.py` is generated by `tools/i18n_interface_values.py` from source structure (enum constants, transition tables, model defaults, enum comparisons and assignments, display-label dictionaries and the settings schema). Pages show these values through `tr_value()`, which translates only registered values and returns anything else, including record content, unchanged. Form values, data attributes and stored data stay English.

**Catalogs.** `serviceops_core/locales/source.json` lists every extracted message (flagging those scripts need); `index.json` holds each language's own name, English name, ISO 15924 script, writing direction (derived from the script, so every right-to-left script is covered), fallback language (`pt-BR → pt`) and translated count; `messages/<code>.json` holds translations and CLDR month and weekday names. Language metadata and calendars come from Unicode CLDR through Babel at build time only (a dev dependency); the runtime reads JSON. Catalogs load lazily per worker (LRU of 64). `tools/i18n_build_catalogs.py` extracts sources, writes the index and assembles catalogs from layered inputs, rejecting a translation that changes placeholders, adds line breaks or markup, is implausibly long, repeats itself or is in the wrong script.

**Safety.** Template `tr()` escapes catalog text and every parameter that is not already `Markup`, so a translation can never inject markup; a translation whose placeholders differ from the source is logged and replaced by English. Script catalogs are embedded as `<script type="application/json">` via `tojson` and inserted with `textContent` only.

**Resolution.** Per request, resolved once in `before_request` (static files excluded) to avoid autoflush during business transactions: an explicit account preference; otherwise (`auto`, or signed out) the best `Accept-Language` match including aliases (`zh-TW → zh-Hant`, `no → nb`); otherwise the `DEFAULT_LANGUAGE` setting; otherwise English. Signed-out requests under `/api/` are machine clients and always get English. New preference rows start from `DEFAULT_LANGUAGE`. The installer uses the same module with browser negotiation only.

**Translation sources.** The 24 common terms per language authored on 2026-10-03 override machine output. Full catalogs are produced offline by `tools/i18n_translate_offline.py` with google/madlad400-3b-mt (Apache-2.0) converted to CTranslate2, run in a separate tooling environment; placeholders are protected as numbered markers and restored only when each appears exactly once. Machine translations are not native-speaker reviewed.

AI evidence IDs remain internal correlation keys for provider grounding. At the human boundary, `ai/references.py` resolves these to verified server-generated application paths with readable numbers/titles, also linking known ticket numbers. Posted notes accept local Markdown reference links and reject remote/protocol-relative/control-character/backslash URLs. Unsupported references lose opaque labels. Citation conversion runs only after source access checks; normal action expiry, stale record and explicit approval controls remain in force.
