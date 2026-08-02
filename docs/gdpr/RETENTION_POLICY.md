# Data Retention Policy

Retention periods below are grounded in existing code where a concrete
control exists (cited), and are recommended defaults where no control
currently exists (marked **recommended, not yet enforced**). Every
self-hosted customer is the controller and may adjust these to their own
legal/regulatory requirements (e.g. sector-specific record-keeping laws) —
this is ServiceOps' default posture, not a universal mandate.

| Data category | Table(s) | Default retention | Trigger / mechanism | Status |
|---|---|---|---|---|
| Active user account | `User` | Indefinite while `active=True` | Deactivation on directory removal (LDAP sync) or admin action | Implemented (`active` flag) |
| Deactivated, un-erased account | `User` (`active=False`, `erased_at` null) | Recommended: erase within 90 days of confirmed departure unless legal hold | Admin/HR-triggered erasure workflow calling `user_erase()` | **Recommended, not yet enforced** — no automatic timer found; erasure is presently a manual action |
| Erased (tombstoned) account | `User` (`erased_at` set) | Indefinite (tombstone row itself, minus scrubbed fields) | N/A — tombstone is the terminal state, kept for FK/history integrity | Implemented |
| `ExternalIdentity` link | `ExternalIdentity` | Should not outlive account erasure | Delete on `user_erase()` | **Gap** — not currently deleted by `user_erase()`; see `DATA_SUBJECT_RIGHTS.md` item 5 |
| Ticket content (open) | `Ticket`, `Comment`, `TaskNote`, `ChecklistItem` | Indefinite while ticket active/unresolved | N/A | N/A |
| Ticket content (closed/resolved) | same | Recommended: 3-7 years post-closure for ITIL/audit trend value, then archive or anonymize narrative fields, per controller's own record-keeping obligations | No automated archival job found in this pass | **Recommended, not yet enforced** |
| Soft-deleted ticket | `Ticket.deleted_at` set | Recommended: purge or hard-anonymize 30-90 days after soft-delete, unless referenced by active change/approval history | `deleted_at`/`deleted_by_id` exist; no purge job confirmed | **Gap — verify against `tools/outbox_worker.py` or scheduled jobs** |
| Attachments | `FileAttachment` + file store | Tied to parent ticket/comment/enterprise-record retention | `cascade="all, delete-orphan"` removes DB rows when parent hard-deleted | DB-row cascade implemented; **on-disk/object-store file deletion coupling not verified** (see `DPIA.md` Risk B.2) |
| Audit log | `Audit` | Minimum 2555 days (7 years), configurable up to 36500 days (100 years); `legal_hold` can suspend deletion entirely | `AuditRetentionPolicy.retention_days`, admin-configurable at `/admin/audit/retention` | Policy field implemented; **automated purge-on-expiry job not confirmed in this pass — flag as gap pending verification** |
| Audit integrity keys | `AuditIntegrityKey` | Retain for the life of any audit rows signed with that key (retiring a key must not invalidate historical hash verification) | `active`/`retired_at` fields | Implemented (rotation-aware) |
| Session data | Flask session cookie (server-side session data, if any) | `PERMANENT_SESSION_LIFETIME` (see `app.py` ~line 4392) | Cookie expiry; `SESSION_COOKIE_SECURE`/`HttpOnly`/`SameSite=Lax` enforced | Implemented (exact lifetime value depends on deployment config — not hardcoded in this doc) |
| Failed-login lockout state | `User.failed_login_count`, `locked_until` | Cleared on successful login / lockout window expiry | In-model fields | Implemented |
| Notifications | `Notification` | Recommended: 90-180 days, or until read + N days, whichever is later | No automated purge confirmed | **Recommended, not yet enforced** |
| CMDB / Configuration Items | `ConfigurationItem` | Lifecycle-tied to asset (retired status), not a fixed calendar period | `operational_status="Retired"` | Implemented as a status; automated purge after retirement not applicable/needed (asset history has ongoing CMDB value) |
| Outbox events (webhook/notification delivery bookkeeping, audit stream) | `OutboxEvent` | Recommended: short — 30-90 days after successful delivery, since these are transient delivery-attempt records, not the record of truth | Not verified in this pass | **Recommended, not yet enforced** |

## Legal holds

`AuditRetentionPolicy.legal_hold` (boolean) exists and, per the admin route
at `/admin/audit/retention`, can be set independently of `retention_days`.
When a legal hold is active, retention/purge logic (wherever implemented)
must skip deletion entirely for that tenant's audit rows regardless of age.
No equivalent legal-hold flag was found on `Ticket`/`FileAttachment` —
**recommended gap**: a litigation/investigation hold on ticket or
attachment data currently has no first-class mechanism and would need to be
handled as a manual administrative exclusion from any future ticket-purge
job.

## What "deletion" means per category (cross-reference to DATA_SUBJECT_RIGHTS.md)

- **Hard delete** (row physically removed): appropriate for `Notification`,
  `OutboxEvent`, session data, and non-audit-referenced soft-deleted
  tickets past their retention window — nothing else depends on these rows
  existing.
- **Anonymize/tombstone** (row kept, identifying fields scrubbed):
  appropriate for `User` (already implemented via `user_erase()`), and
  should extend to `FileAttachment.original_name`/`Ticket.description`/
  `Comment.body` text where a specific erasure request targets narrative
  content (manual/escalated process — see `DATA_SUBJECT_RIGHTS.md`).
- **Never delete / append-only** (row retained regardless of subject
  requests, per Art. 17(3)(b)/(e)): `Audit` rows themselves, for the
  retention window set by `AuditRetentionPolicy` — the identifying `user_id`
  reference survives as a tombstoned-user FK, not as directly identifying
  data, which is the resolution documented in `DATA_SUBJECT_RIGHTS.md`.

## Open items for `BACKLOG.md` / `TRACEABILITY_MATRIX.md`

The following retention-adjacent gaps identified while writing this policy
should be tracked as backlog items if not already present (not verified
against `docs/BACKLOG.md` in this pass — cross-check before filing
duplicates):

1. Automated audit-log purge/archive job enforcing `AuditRetentionPolicy.retention_days`.
2. Automated soft-deleted-ticket purge job with an audit/approval-reference exclusion check.
3. On-disk/object-store attachment file deletion coupled to `FileAttachment` row deletion.
4. `ExternalIdentity` row cleanup on `user_erase()`.
5. Notification and OutboxEvent retention/purge jobs.
6. A ticket/attachment-level legal-hold flag, if litigation holds on ticket content become a requirement.
