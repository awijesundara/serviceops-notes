# Data Subject Rights Procedures (Art. 15, 16, 17, 18, 20, 21 GDPR)

This document describes how each right maps onto ServiceOps' actual data
model (per `ROPA.md`) and existing/expected code (`app.py`). A separate,
concurrent engineering effort is implementing the Art. 17 erasure and Art.
15/20 export HTTP routes in `serviceops_core`/`app.py`. Everything below
marked **pending technical verification** must be checked against that
implementation once it lands — this document was written without sight of
it, based on the `user_erase()` function and schema that existed at the
time of writing (2026-08-02).

## The central tension: audit/history immutability vs. erasure

`ServiceOps/CLAUDE.md` states: *"Legacy identities referenced by historical
approvals or audit records must be disabled or tombstoned, not hard-deleted
if deletion would damage history."* GDPR Art. 17 gives data subjects a
right to erasure, subject to Art. 17(3) exceptions including "compliance
with a legal obligation" (17(3)(b)) and "establishment, exercise or defence
of legal claims" (17(3)(e)).

These are not actually in conflict once resolved carefully, but the
resolution must be explicit, not assumed:

- **What must be genuinely erasable**: directly identifying fields that
  serve no ongoing legal/audit/security purpose once a person's
  relationship with the organization has ended — name, email, phone,
  location, department/division text, avatar. These carry no evidentiary
  value for "who approved change X" once the fact of approval and its
  authorization chain are preserved by a stable reference (a tombstoned
  username/ID), not by the erased fields themselves.
- **What is legitimately retained (Art. 17(3)(b)/(e))**: the *fact* that
  user ID N approved/created/modified a given record, at a given time —
  because change-governance history (`ServiceOps/CLAUDE.md`'s "material
  modifications... recorded in ticket history" and CCB approval rules) has
  independent legal/audit value that outlives the individual's personal
  data. The audit hash chain (`Audit.event_hash`/`previous_hash`) is
  specifically designed to make selective row deletion detectable/breaking,
  which is a deliberate security property, not an oversight — deleting a
  row would either break the chain (evidence of tampering) or require
  recomputing the chain from that point forward (defeating the point of a
  tamper-evident log).
- **The reconciliation**: pseudonymize/tombstone, don't hard-delete, for
  anything referenced by audit/approval/change history. This is exactly
  what `user_erase()` already does (see below) for the `User` row itself.
  The same principle must extend to `Audit.details` and `Comment.body`/
  `Ticket.description` free text that happens to *contain* the erased
  person's name — see the Art. 17 section below for why that's a harder,
  only-partially-solved problem.

Document this reasoning in any customer-facing DPA/response-to-DSAR
correspondence — "we tombstone rather than delete for audit-referenced
records, per Art. 17(3)(b)/(e), because X" is a defensible answer to a
regulator or data subject; silent non-deletion is not.

## Art. 15 — Right of access

**What a complete response must include**, per `ROPA.md`'s data
categories: `User` row (all non-erased fields), `ExternalIdentity` rows
(provider + subject, i.e. confirm which directory identity is linked —
do not return the raw external subject if it's a sensitive internal ID
without redaction policy review), `UserPreference`, all `Ticket` rows where
the subject is `requester_id` or `assignee_id`, all `Comment`/`TaskNote`
rows where the subject is `user_id`, all `FileAttachment` rows where the
subject is `uploaded_by_id` (metadata; the files themselves should be
retrievable per-attachment, not necessarily bulk-zipped unless Art. 20
applies — see below), `Notification` rows where the subject is `user_id`,
and — this is the debatable one — **the subject's own audit trail**
(`Audit` rows where `Audit.user_id` matches), since an individual's own
security/activity log about themselves is their personal data under Art.
15 even though the same table is also a security-monitoring record.
- **Recommendation**: provide the data-subject their own `Audit` rows
  (action/target/timestamp), but consider whether `source_ip`/`user_agent`
  need inclusion — they usually should be included since they're the
  subject's own data, unless doing so would reveal another person's device
  fingerprint by association, which isn't the case here (source_ip is the
  subject's own connecting IP).
- **What must NOT be included**: other users' data incidentally referenced
  in the subject's tickets (e.g. an agent's internal-only `TaskNote` on the
  subject's ticket, if `visibility="internal"` and not meant for the
  requester) — apply the existing `visibility` field as the filter for what
  the requester-as-data-subject sees, consistent with how the product
  already gates internal notes from requesters in normal use.
- **Status**: **pending technical verification** — confirm the concurrent
  export-route implementation actually assembles this full cross-table
  bundle rather than only the `User` row.

## Art. 16 — Right to rectification

- **Self-service fields**: name, email (subject to uniqueness constraint —
  `User.email` is `unique=True`), phone, location, timezone, and other
  profile fields the user's own settings UI already exposes — no new
  capability needed beyond what a profile-edit screen provides, as long as
  it's available to every role, not just admins editing others.
- **Directory-sourced fields**: for LDAP/OIDC-provisioned users, name/
  title/department/etc. are sourced from the external directory
  (`ExternalIdentity`/LDAP sync) and will be overwritten on next sync if
  edited locally — rectification for these users should be directed to the
  organization's HR/IT directory, not ServiceOps' local edit form, or the
  correction will be silently reverted at the next sync. This distinction
  should be surfaced in the UI (a disabled/read-only field with an
  explanation) — **flag as gap** if not already implemented; grep of
  `app.py` for a "sourced from directory, read-only" UI treatment was not
  performed in this pass.
- **Audit trail of rectification**: any profile edit should itself produce
  an `Audit` row (consistent with existing `audit()` calls elsewhere in the
  codebase) so rectification history is traceable.

## Art. 17 — Right to erasure

**Current implementation** (`user_erase()`, `app.py` ~line 2256, present at
time of writing — verify it hasn't been superseded by the concurrent work):
requires `target_user.active == False` first (fails closed — you cannot
erase an active account, preventing accidental self-lockout-via-erasure or
erasure of someone still employed), is idempotent (`if
target_user.erased_at: return target_user`), scrubs `name`, `email`
(replaced with `erased-user-<id>@erased.invalid`), `business_phone`,
`mobile_phone`, `department`, `division`, `location`, `avatar_path`, and
replaces `username` with a stable tombstone (`erased-user-<id>`), sets
`erased_at`, and writes an `Audit` row recording the erasure action itself.

**What this does NOT touch, and must be decided/implemented as part of a
complete Art. 17 flow**:

1. **`Ticket.description`, `Comment.body`, `TaskNote.body` free text.**
   These are not scrubbed by `user_erase()`. If the erased person's name,
   contact details, or other identifying content was typed into ticket
   narrative by themselves or someone else, it survives erasure verbatim.
   This is a real gap, not a design choice — free text cannot be safely
   auto-redacted without either (a) an NLP-based PII scrubber (error-prone,
   both under- and over-redacting) or (b) leaving it as an documented
   known limitation with a manual-review escalation path for a data
   subject who specifically requests narrative-text erasure. **Recommend
   documenting option (b)** as the interim answer and manual redaction
   as an admin action for specific, escalated requests, while flagging
   automatic narrative scrubbing as a backlog item.
2. **`Audit.details` free text.** Same issue — `audit()` calls often
   pass human-readable `details` strings (e.g. `f"days={retention_days};
   legal_hold={policy.legal_hold}"` or similar) that could theoretically
   include a name. Given the hash-chain immutability (see tension section
   above), this is *by design* not rectifiable/erasable after the fact —
   which is defensible under 17(3)(b)/(e) for the audit log specifically,
   but must be disclosed to data subjects as a documented limitation, not
   silently omitted from the DSAR response.
3. **`FileAttachment` file content and `original_name`.** Not addressed by
   `user_erase()` at all — attachments the erased person uploaded remain
   with their original filename and content. If erasure of an *entire*
   account (not just profile fields) is requested, the product needs a
   decision: does erasure delete the erased user's attachments, anonymize
   `original_name`, or leave them (on the theory they're now
   organizational/ticket-owned content, not the uploader's personal
   data)? **This is unresolved in the current code and should be a
   specific question to the concurrent implementation** — what does the
   new export/erasure route do with `FileAttachment` rows where
   `uploaded_by_id` is the target user?
4. **`Notification` rows.** Contain `title`/`body` that may reference the
   erased user by name (e.g. "Ticket assigned to John Smith") — not
   scrubbed by `user_erase()`. Lower urgency (notifications are typically
   short-lived/read-once) but should be covered by `RETENTION_POLICY.md`'s
   notification retention window rather than left indefinitely.
5. **`ExternalIdentity` row.** Not removed by `user_erase()` — the
   provider/subject link technically remains, pointing at a now-tombstoned
   user. Should likely be deleted (it has no historical-evidence value
   once the account is erased and deactivated at the source directory) —
   **flag as gap**.

**Erasure fails closed correctly**: the `active` precondition is a good
control (prevents erasing a live account by mistake) — document this in
any admin-facing erasure procedure as "deactivate first, then erase," a
two-step, two-decision-point flow that itself provides a safety margin
against accidental erasure.

**Status of the export/erasure HTTP routes themselves**: **pending
technical verification** against the concurrent implementation in
`serviceops_core`/`app.py` — confirm (a) an admin-facing or self-service
route exists to trigger `user_erase()` (the function existed at time of
writing; whether a route calls it was not confirmed), (b) the route
enforces the same `active` precondition and idempotency, (c) it addresses
or explicitly defers items 1-5 above, (d) it is itself tenant-scoped and
role-gated consistent with `ServiceOps/CLAUDE.md`'s authorization rules.

## Art. 18 — Right to restriction of processing

No dedicated "restricted" state was found on `User` or `Ticket` (only
`active`/`deleted_at`/`erased_at`). A restriction request (e.g. "don't
process my data further while we dispute accuracy") doesn't map cleanly
onto existing states:
- `User.active = False` is closest but is a broader "account
  deactivated" state (blocks login entirely), not a narrower
  "keep data, pause processing, still allow login" state Art. 18 expects.
- **Recommendation**: for most ServiceOps deployments, treat a restriction
  request as equivalent to deactivation (`active = False`) plus an
  administrative annotation (e.g. a `PlatformSetting`-style note or a
  ticket/case tracked outside the system) recording the restriction scope
  and duration, since building a dedicated partial-restriction state is
  disproportionate to how rarely Art. 18 is invoked relative to Art. 17.
  **Flag as gap**: no dedicated field; document the deactivation-based
  workaround in any DPA/DSAR procedure rather than claiming a feature that
  doesn't exist.

## Art. 20 — Right to data portability

Portability applies to data provided by the subject and processed by
automated means under consent/contract — practically, the subject's own
`User` profile fields, their own `Ticket`/`Comment`/`TaskNote` content they
authored, and their `FileAttachment` uploads, in a structured,
machine-readable format (JSON is the natural fit given the codebase is
already JSON-API-first per `ServiceOps/CLAUDE.md`'s "REST is the primary
API").
- **Overlap with Art. 15**: the export bundle described under Art. 15 above
  is largely the same data; the distinction is format (machine-readable,
  structured) and purpose (transmit to another controller) rather than
  content.
- **Status**: **pending technical verification** against the concurrent
  export-route work — confirm the export format is structured (JSON/CSV)
  rather than a human-readable rendering only, and confirm attachments are
  included as actual files (e.g. a zip bundle) not just metadata rows.

## Art. 21 — Right to object

Applies primarily where processing is based on Art. 6(1)(f) legitimate
interest (much of `ROPA.md`'s basis for ticket/CMDB/notification
processing). In an internal-employee-ITSM context, objection is unusual
(the processing is generally necessary to the employment/service
relationship, which typically overrides objection under Art. 21(1)'s
"compelling legitimate grounds" test) but must still have a procedure:
- **Recommendation**: route Art. 21 objections to the same manual/
  administrative review path as Art. 18 restriction requests — there is no
  dedicated in-product "objection" mechanism, nor should there necessarily
  be one, given how rarely it will apply in this employment/service
  context. Document the review criteria (does continued processing serve
  compelling legitimate grounds — e.g. ongoing incident/change audit
  history — that override the objection) in the customer's own privacy
  procedure, not in ServiceOps itself.

## Summary: implementation status

| Right | In-product mechanism | Status |
|---|---|---|
| Art. 15 access | Cross-table export bundle | Pending technical verification (concurrent work) |
| Art. 16 rectification | Profile self-edit; directory sync overwrite caveat | Partially implemented; directory read-only UX gap flagged |
| Art. 17 erasure | `user_erase()` scrubs `User` fields, tombstones username | Implemented for `User` row; gaps on ticket/comment/attachment/notification/audit text (items 1-5 above) |
| Art. 18 restriction | No dedicated state; `active=False` + manual annotation workaround | Gap — document workaround, don't claim a feature |
| Art. 20 portability | Same export bundle as Art. 15, structured format | Pending technical verification |
| Art. 21 objection | Manual/administrative review path | Gap — procedural only, no in-product mechanism, likely acceptable given context |

Once the concurrent Art. 15/17/20 route implementation is complete, revisit
this table and every "pending technical verification" marker above against
the actual code before presenting this document as authoritative to a
customer or regulator.
