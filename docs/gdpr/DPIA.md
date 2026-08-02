# Data Protection Impact Assessment (Art. 35 GDPR)

Scope: the three highest-risk processing activities identified in
`ROPA.md` — (A) the immutable audit log (IP addresses + full activity
trail), (B) attachment storage (arbitrary file content), and (C)
LDAP/AD directory sync (bulk identity ingestion). This assessment is written
from the product's perspective (what ServiceOps as software does and does
not mitigate); the operating **controller** must complete their own DPIA for
their specific deployment, using this as an input, not a substitute.

A DPIA is legally required (Art. 35(3)(b)) here because audit logging
involves systematic monitoring of individuals (agents and requesters) on a
large scale within an organization, and LDAP sync involves bulk processing
of employee directory data.

## A. Audit log (IP addresses, user agents, full activity trail)

**Necessity/proportionality**: the audit log exists to satisfy
`ServiceOps/CLAUDE.md`'s explicit requirement for "immutable or
tamper-evident audit history" — a legitimate and, for change-governance
records (who approved what, when), often a compliance-mandated control.
The `Audit` table's hash-chained design (`event_hash`/`previous_hash`,
HMAC-SHA256, `audit()` in `app.py` ~line 1521) is genuinely purpose-built
for tamper evidence, not incidental logging sprawl.

**Risk 1 — re-identification / profiling via IP + user-agent + action
trail.** `Audit.source_ip` and `Audit.user_agent` are captured on every
audited action (`request.remote_addr`, `str(request.user_agent)[:255]`).
Combined with `Audit.action`/`target`/`details` and timestamp, this lets an
administrator (or anyone who obtains DB access) reconstruct a detailed
behavioral timeline per user — classic systematic-monitoring risk.
- *Mitigation in code*: access to `Audit` rows is gated behind
  administrator-only routes (`/admin/audit/*`), and tenant scoping
  (`Audit.tenant_id`) prevents cross-tenant visibility.
- *Mitigation gap*: no field-level redaction or IP-truncation option was
  found (e.g. no "log last-octet-masked IP" mode). No role narrower than
  full-admin was found for "audit read but not audit configuration."
  **Flag as gap**: consider a masked-IP audit view for lower-privilege
  security reviewers, and confirm (with the team implementing Art. 15/17
  routes) whether a data-subject access request can retrieve *their own*
  audit trail without granting them full admin audit access.

**Risk 2 — indefinite-feeling retention conflicting with data minimization.**
`AuditRetentionPolicy.retention_days` defaults to 2555 days (7 years) and
can be configured up to 36500 days (100 years), with an independent
`legal_hold` boolean that can suspend deletion entirely
(`/admin/audit/retention`, ~line 7531).
- *Mitigation in code*: retention is explicit and admin-visible (not silent
  infinite retention by omission), and is bounded (2555–36500 day range
  enforced server-side).
- *Mitigation gap*: no automatic purge/anonymization job for audit rows past
  `retention_days` was found in the grep of the codebase performed for this
  assessment — the policy is *configured* but whether a background job
  actually enforces it (deletes/archives rows once they age out) needs
  verification against `tools/outbox_worker.py` and any scheduled job.
  **Flag as gap pending verification.**

**Risk 3 — erasure vs. audit-immutability conflict.** This is the central
tension of the whole DPIA and is treated at length in
`DATA_SUBJECT_RIGHTS.md`: a hash-chained audit log is *designed* to resist
after-the-fact modification, which is in direct tension with an Art. 17
erasure request that would otherwise want to remove or alter a user's
`source_ip`/`user_id`-linked history. The product's answer (tombstone the
`User` row via `user_erase()`, not the `Audit` rows) is a defensible,
commonly-accepted balancing under Art. 17(3)(b)/(e) (compliance with legal
obligation; establishment/exercise/defense of legal claims), but it is a
policy choice that must be documented and justified per deployment, not
assumed.

**Residual risk**: Medium. Mitigated by access control, tenant isolation,
and tamper evidence (which cuts both ways — it's also a privacy control
against insider tampering). Not mitigated: no confirmed automated retention
enforcement, no IP-masking option, exposure scope of "who can read whose
audit trail" not fully verified in this pass.

## B. Attachment storage

**Necessity/proportionality**: attachments are core to ITSM (screenshots of
errors, logs, documents) — clearly necessary for the service.

**Risk 1 — uncontrolled personal-data content in uploaded files.**
`FileAttachment` stores only metadata in the DB (`original_name`,
`mime_type`, `size_bytes`, `sha256`, `scan_status`); the file itself is
opaque to the application beyond content-type/extension checks and malware
scanning (per `ServiceOps/CLAUDE.md`'s required "malware scanning or
quarantine adapter," "content-type and extension verification,"
"cryptographic attachment hashes"). Nothing in the model inspects file
*content* for personal data — a requester could upload an HR document, a
photo of a passport, or a spreadsheet of colleagues' salaries, and
ServiceOps has no way to know.
- *Mitigation in code*: `sha256` supports integrity verification and
  dedup/evidence; `scan_status` supports malware quarantine (external
  adapter — implementation-dependent, not verified in this pass);
  attachment access is presumably tied to ticket visibility (tenant/role
  scoped) — confirm against the actual authorization check on the
  attachment-download route.
- *Mitigation gap*: no DLP/content-scanning capability exists or is
  claimed. This is expected for a self-hosted ITSM tool (DLP is normally a
  separate control layer) but should be explicitly stated as **out of
  scope** so the controller doesn't assume ServiceOps screens attachment
  content for sensitive data.

**Risk 2 — attachment survives ticket-level anonymization inconsistently.**
`FileAttachment.uploaded_by_id` is a hard FK to `User`, not nullable.
`Ticket`/`Comment` deletion is soft-delete (`deleted_at`); attachments
cascade-delete with their parent (`cascade="all, delete-orphan"` on the
`ticket`/`comment`/`enterprise_record` relationships, ~line 1253-1257) —
meaning a *hard* delete of a `Ticket` row (if one is ever performed, e.g. by
a retention job) would cascade-delete its attachments' DB rows, but the
underlying file on disk/object storage is a separate deletion the app must
also perform — **flag as gap pending verification**: confirm the retention
enforcement job actually deletes the on-disk/object-store file, not just
the DB row, or attachments become orphaned files with no DB pointer (a
worse privacy outcome — undiscoverable personal data).

**Residual risk**: Medium-High, primarily because attachment content is
unscreened by design and the file-vs-DB-row deletion coupling is unverified.

## C. LDAP/AD directory sync

**Necessity/proportionality**: necessary to keep ServiceOps identities
consistent with the authoritative HR/IT directory (avoids duplicate manual
entry, respects the directory as source of truth for org structure).

**Risk 1 — bulk ingestion of directory attributes beyond ServiceOps'
minimum need.** `LdapSyncState` (per-tenant bookkeeping) confirms a
scheduled bulk sync process exists (`serviceops_core.ldap_sync.sync_directory`,
referenced ~line 216-220), separate from per-login just-in-time sync. A
bulk sync by nature pulls a batch of directory entries (potentially the
whole org) rather than only actively-logging-in users, which is a larger
processing footprint than login-time sync alone.
- *Mitigation in code*: `User` model fields receiving synced data are
  bounded and enumerable (name, email, title, department, division,
  employee_id, employee_type, phones, location, manager) — not an
  unbounded attribute bag; AD group→team mapping (per
  `ServiceOps/CLAUDE.md`) is admin-configured, not automatic-everything.
- *Mitigation gap*: whether sync only pulls users within configured
  OU/group scope (minimization) vs. entire directory was not verified in
  this pass — recommend the controller confirm their LDAP bind's search
  base is scoped to relevant OUs only, since that's a deployment-time
  configuration choice, not something ServiceOps enforces in code.

**Risk 2 — disabled/removed directory users.** `ServiceOps/CLAUDE.md`
explicitly requires "disabled and removed-user handling" as an admin
configuration. Correct behavior is that a directory-side deactivation
should flow to `User.active = False` (and eventually feed the erasure
workflow), not leave a stale, still-active ServiceOps account after someone
leaves the organization — a real access-control/privacy risk if sync
doesn't handle disablement promptly. **Flag as pending verification**
against the concurrent erasure-route implementation and the actual
`ldap_sync.py` disable-handling logic (not read in this pass).

**Residual risk**: Medium, contingent on verifying sync scope and
disable-propagation behavior — recommend follow-up review of
`serviceops_core/ldap_sync.py` directly.

## Overall DPIA conclusion

No processing identified here is disproportionate to ServiceOps' stated
purpose (internal ITSM), and several required controls
(tenant isolation, hash-chained audit, SSRF-safe webhooks, malware-scan
hook) are real, verified-in-code mitigations, not aspirational claims.
The residual risks that need controller-level and/or follow-up
engineering attention are: (1) confirm automated audit-retention
enforcement exists, (2) confirm attachment file deletion is coupled to DB
row deletion, (3) confirm LDAP sync scoping and disable-propagation, (4)
decide and document, per deployment, the audit-immutability vs.
erasure-request balancing (see `DATA_SUBJECT_RIGHTS.md`). None of these
block using the product, but all four should be tracked in
`serviceops-notes/docs/BACKLOG.md` and `TRACEABILITY_MATRIX.md` if not
already present.
