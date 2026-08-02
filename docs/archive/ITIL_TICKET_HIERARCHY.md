# ITIL / ServiceNow-pattern ticket hierarchy reference

Reference material supplied by the product owner, preserved verbatim for future
implementation decisions. ServiceOps is inspired by these patterns but does not
claim full ServiceNow compatibility (see `GOVERNANCE.md`). Where ServiceOps'
current data model or state machine differs from what is described here, that
divergence is deliberate and documented in `TRACEABILITY_MATRIX.md`; this file
is the design reference, not a claim of current implementation status.

## Governing principle implemented in ServiceOps (2026-07-29)

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

## 1. The ServiceNow ITSM ticket hierarchy

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

## 2. What counts as a sub-ticket

### 2.1 Execution task

A defined piece of work: Incident Task, Problem Task, Change Task, Catalog
Task, Release Task. The parent owns the overall outcome; the task owns a
specific work package assigned to one group or person.

### 2.2 Child ticket

A full process record of the same or another class with its own lifecycle,
assignment, priority, SLA, work notes, and closure information (e.g. parent/child
incidents, Problem → Change, Incident → Change).

### 2.3 Approval record

A decision record, not an execution task (`sysapproval_approver` in ServiceNow;
`ApprovalChain`/`ApprovalGate`/`ApprovalVote` in ServiceOps). Identifies what
requires approval, who must approve, the decision state, comments, timestamp,
and delegation information.

### 2.4 Linked object

Context, not a ticket: CI, business service, affected service, outage,
knowledge article, attachment, SLA record, change conflict, maintenance
window, CAB meeting, risk assessment, test evidence.

## 3. Incident Management

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

## 4. Major Incident Management

Still fundamentally an Incident record, with additional controls, roles,
workbench functions, communications, and review process. Lifecycle: Potential
→ Candidate → Review → Accepted/Rejected → Promoted → Response/communication →
Restoration → Resolution → Post-Incident Review → Problem creation.

Ownership split: Major Incident Manager owns coordination/communication/
escalation/timeline/stakeholders/recovery governance; technical resolver
groups own diagnosis/workaround/restoration/evidence; the Problem Manager
owns the later root-cause process.

## 5. Problem Management

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

## 6. Change Management

A Change Request must answer what is changing, why, which services/CIs are
affected, business impact, technical risk, implementation/test/backout plans,
required approvers, schedule, and post-implementation outcome.

### 6.1 Standard Change
Low risk, repeatable, documented, pre-authorized via an approved template/model.
Does not normally require fresh CAB approval each occurrence, but each
instance still needs validation against the approved Standard Change
conditions.

### 6.2 Normal Change
Neither Standard nor Emergency; full assessment and authorization (technical,
change-management, CAB as applicable).

### 6.3 Emergency Change
Used when delay would cause or extend serious business impact. Still requires
expedited assessment and authorization (Emergency CAB or designated emergency
approver) — never "no approval." May move directly toward Authorize rather
than every Normal Change stage.

### 6.4 Typical Change states (legacy/traditional model)
New → Assess → Authorize → Scheduled → Implement → Review → Closed (or
Canceled at any point). Current ServiceNow implementations may use
configurable Change Models with different states/transitions.

Detailed process per state — required information, permitted/blocked tasks,
assessment activities, authorization approver types, schedule entry
conditions, implementation activities/outcomes, review questions, and closure
requirements — is preserved in full in the original product-owner submission
(session transcript, 2026-07-29) and summarized in section 14 below as
governance rules.

## 7. Change Tasks

Official task types: **Planning, Implementation, Testing, Review**. Created
manually or via workflow/flow.

### Change Task unlocking model

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

## 8. Request Management

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

### SCTASK is not a child of CHG — implemented 2026-07-29

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

## 9. Request versus Incident

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

## 10. Universal Request

A common front-door ticket for when the requester does not know which
department/process should handle the matter. The Universal Request handles
the requester-facing conversation; the primary ticket (Incident, RITM, HR
Case, Customer Case) handles specialist execution. Use when employees should
not need to understand internal ticket types, work may transfer between
departments, or a consistent portal experience is required — not as an
unnecessary wrapper around every record. **Not currently implemented in
ServiceOps**; tracked as a candidate backlog item if a genuine multi-department
front door becomes a requirement.

## 11. Release Management

Groups multiple Changes/deployment activities into a coordinated delivery
(planning, design, build, configuration, testing, deployment readiness,
communications, go-live, early-life support). A Release does not replace
Change authorization — each production-affecting Change still follows its
applicable Change model. **Not currently implemented in ServiceOps**.

## 12. Relationships between the main tickets

- Incident → Problem: many Incidents → one Problem (shared underlying cause).
- Problem → Change: one Problem → one or more Changes (permanent fix).
- Incident → Change: service restoration requires a controlled modification.
- Request → Change: RITM → Change Request when fulfillment requires one.
- Major Incident → Problem: root-cause analysis and prevention.
- Change → Incident: a failed Change may create/link to an Incident.
- Change → Problem: a failed or repeatedly unsuccessful Change may lead to a
  Problem investigation.
- Release → Change: coordinated deployment governance.

## 13. The complete operational chain

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

## 14. Mandatory governance rules for ServiceOps

### Parent ticket controls
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

### Approval controls
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

### Change Task controls — implemented 2026-07-29
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
