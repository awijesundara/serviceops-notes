# ServiceOps privacy and security controls

Use the [documentation index](../README.md) to navigate the six maintained documents. Update this document directly; there is no generated master copy.

These policies, templates, assessments and control mappings retain their original scope, dates and evidence limitations. Drafts and historical gaps do not establish legal compliance or ISO certification; confirm current implementation and controller details before relying on them.

## Contents

- [Record of Processing Activities (Art. 30 GDPR)](#section-gdpr-ropa)
- [Data Protection Impact Assessment (Art. 35 GDPR)](#section-gdpr-dpia)
- [Data Subject Rights Procedures (Art. 15, 16, 17, 18, 20, 21 GDPR)](#section-gdpr-data_subject_rights)
- [Data Retention Policy](#section-gdpr-retention_policy)
- [Personal Data Breach Notification Procedure (Art. 33/34 GDPR)](#section-gdpr-breach_notification)
- [Data Processing Agreement — Template](#section-gdpr-dpa_template)
- [ServiceOps ISMS Core Policies (draft, ISO/IEC 27001:2022-aligned)](#section-iso27001-isms_policies)
- [Statement of Applicability — ISO/IEC 27001:2022 Annex A](#section-iso27001-soa)
- [ISO/IEC 27001:2022 Gap Analysis — ServiceOps](#section-iso27001-gap_analysis)

---

<a id="section-gdpr-ropa"></a>

## Record of Processing Activities (Art. 30 GDPR)

<a id="section-gdpr-ropa--record-of-processing-activities-art-30-gdpr"></a>

Status: grounded in current `ServiceOps` schema as read from `app.py` (SQLAlchemy
models) on 2026-08-02. Field lists below are the actual columns found, not an
idealized model. Where a technical erasure/export implementation is in
progress concurrently, affected rows are marked **pending technical
verification** — see [DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights).

<a id="section-gdpr-ropa--deployment-model-and-roles"></a>
### Deployment model and roles

ServiceOps is self-hosted software. The customer organization that installs
and operates it (its own PostgreSQL, its own SMTP relay, its own LDAP/AD or
Keycloak, its own webhook destinations) is the **Data Controller** for all
personal data processed by their instance. The ServiceOps software/vendor
acts as a **Data Processor** only to the extent the vendor is contracted to
provide hosting, support, or managed operation of a customer's instance
(e.g. a future managed/SaaS offering); for a purely self-hosted, customer-run
deployment with no vendor access to the running system or its database, the
vendor is not a processor of that instance's personal data at all — it is a
software supplier. This document assumes the general case (self-hosted,
controller-operated) and flags the SaaS/managed variant where relevant. See
[DPA_TEMPLATE.md](COMPLIANCE.md#section-gdpr-dpa_template) for how the processor relationship is documented when it
does apply.

<a id="section-gdpr-ropa--processing-activity-1-useridentity-administration-accounts-auth-org-data"></a>
### Processing activity 1: User/identity administration (accounts, auth, org data)

- **Purpose**: authenticate requesters, agents, and administrators; enforce
  role- and tenant-scoped authorization; route work by department/team;
  support organizational reporting lines.
- **Legal basis** (controller's, typically): Art. 6(1)(b) contract/necessity
  for provision of internal IT service management to employees, or Art.
  6(1)(f) legitimate interest (running internal IT operations), depending on
  the controller's employment-law basis for processing employee data (often
  governed by national labor law rather than consent).
- **Data categories** (`User` table, `app.py` ~line 162): `username`, `name`,
  `email`, `title`, `department`, `division`, `employee_id`, `employee_type`,
  `business_phone`, `mobile_phone`, `timezone`, `date_format`,
  `calendar_integration`, `avatar_path`, `location`, `password_hash`,
  `role`, `active`, `auth_version`, `failed_login_count`, `locked_until`,
  `created_at`, `erased_at`, `manager_id` (self-referential org-chart link).
- **Special/sensitive categories**: none observed by design (no health,
  religion, biometric, etc. fields). `employee_type`/`title`/`department`
  could indirectly reveal sensitive facts in edge cases (e.g. a title
  disclosing a disability-accommodation role) — controller responsibility to
  review for their own org structure.
- **Federated identity** (`ExternalIdentity` table, ~line 196): `provider`
  (`ldap`/`oidc`), `subject` (the external directory's unique identifier —
  e.g. an AD `objectGUID`/`sAMAccountName` or OIDC `sub` claim), linked to
  `user_id`. This is a persistent pseudonymous identifier tied to the
  source-of-truth directory, not a ServiceOps-generated one.
- **UI/UX preferences** (`UserPreference` table, ~line 1213): theme, density,
  font scale, accessibility toggles, `start_page`. Low sensitivity but
  personal (tied 1:1 to `user_id`).
- **Recipients**: internal (agents/administrators per role, tenant-scoped
  queries — enforced per `ServiceOps/CLAUDE.md`'s tenant-isolation rules);
  the customer's configured LDAP/AD or Keycloak/OIDC provider (bidirectional
  — ServiceOps reads attributes from it at sync/login); the customer's SMTP
  relay (notifications carry name/email); any configured outbound webhook
  destinations (see Processing activity 5).
- **Retention**: see [RETENTION_POLICY.md](COMPLIANCE.md#section-gdpr-retention_policy). Accounts are not hard-deleted by
  default (see `user_erase()`, `app.py` ~line 2256) — deactivation + erasure
  scrub identifying fields but preserve the row and a tombstoned
  `username` (e.g. `erased-user-<id>`) so audit/approval/ticket foreign keys
  stay valid.
- **Cross-border transfer**: none for a self-hosted deployment where the
  controller's own PostgreSQL, LDAP, and SMTP infrastructure are all within
  the controller's chosen jurisdiction. If the controller configures a
  cloud-hosted LDAP/OIDC provider (e.g. Entra ID/Azure AD, Okta) or a
  cloud SMTP relay outside their jurisdiction, that is a transfer the
  **controller** initiates and is responsible for (SCCs, adequacy, etc.) —
  ServiceOps does not intermediate or control where those third parties
  process data. If a future ServiceOps-operated SaaS/managed-hosting variant
  exists, the vendor's hosting region(s) become an additional transfer
  consideration and must be added here per deployment.

<a id="section-gdpr-ropa--processing-activity-2-itsm-ticket-content-incidents-requests-changes-problems"></a>
### Processing activity 2: ITSM ticket content (incidents, requests, changes, problems)

- **Purpose**: deliver the core IT service management function — logging,
  triaging, assigning, and resolving incidents/requests/changes/problems.
- **Legal basis**: Art. 6(1)(b)/(f), same reasoning as above; ticket content
  is the substantive record of the service relationship.
- **Data categories**: `Ticket` (`title`, `description` free text,
  `requester_id`, `assignee_id`, `deleted_at`/`deleted_by_id`), `Comment`
  (`body` free text, `user_id`), `TaskNote` (polymorphic work notes/RITM
  commentary, `body`, `user_id`, `visibility` internal/customer-facing),
  `ChecklistItem` (task text, no direct PII but scoped to a ticket).
  Free-text `description`/`body` fields are a material risk: requesters and
  agents can and do paste names, phone numbers, screenshots-as-text, or
  other third-party personal data into ticket narrative with no field-level
  validation preventing it.
- **Recipients**: assigned fulfillment team/agents (tenant- and
  team-scoped), any notification recipients, any configured webhook
  subscribed to ticket events.
- **Retention**: see [RETENTION_POLICY.md](COMPLIANCE.md#section-gdpr-retention_policy). `Ticket.deleted_at` is a
  soft-delete marker, not a physical delete — records persist for ITIL
  history/reporting.
- **Cross-border transfer**: none beyond what applies to Processing activity 1.

<a id="section-gdpr-ropa--processing-activity-3-attachments"></a>
### Processing activity 3: Attachments

- **Purpose**: allow requesters/agents to attach supporting files
  (screenshots, logs, documents) to tickets, comments, or enterprise
  records.
- **Legal basis**: Art. 6(1)(b)/(f), ancillary to ticket handling.
- **Data categories** (`FileAttachment`, ~line 1240): `original_name`,
  `stored_name`, `mime_type`, `size_bytes`, `sha256` (content hash),
  `scan_status`, `uploaded_by_id`, plus the file content itself (stored on
  disk/object storage, not in the DB) — which can contain arbitrary
  personal data (a screenshot of someone's inbox, an HR document, a photo).
  `original_name` alone is frequently personal (e.g.
  `John_Smith_passport.pdf`).
- **Recipients**: ticket-visible users per authorization rules; malware
  scanning/quarantine adapter if configured (per `ServiceOps/CLAUDE.md`
  security requirements) — a further internal recipient of file content.
- **Retention**: tied to parent ticket/comment/enterprise-record retention;
  see [RETENTION_POLICY.md](COMPLIANCE.md#section-gdpr-retention_policy).
- **Cross-border transfer**: none for local/customer-controlled storage; a
  transfer consideration arises only if the customer configures a
  cloud object-storage backend in another jurisdiction — controller
  responsibility.

<a id="section-gdpr-ropa--processing-activity-4-auditsecurity-logging"></a>
### Processing activity 4: Audit/security logging

- **Purpose**: tamper-evident record of who did what, for security
  investigation, non-repudiation, and change governance (approvals,
  material-change history per `ServiceOps/CLAUDE.md`).
- **Legal basis**: Art. 6(1)(c) (legal obligation, where security logging is
  mandated) and/or Art. 6(1)(f) (legitimate interest in system security and
  fraud/misuse investigation).
- **Data categories** (`Audit` table, ~line 312): `user_id`, `action`,
  `target`, `details` (free text — can restate ticket/user field content),
  `request_id`, `source_ip`, `user_agent`, `integrity_version`,
  `integrity_key_id`, `previous_hash`/`event_hash` (HMAC-SHA256 hash chain —
  see `audit()`, ~line 1521), `created_at`. **`source_ip` is personal data**
  (an IP address) under GDPR/EU case law (Breyer).
  `AuditRetentionPolicy` (~line 354) sets `retention_days` (default 2555 =
  7 years) and a `legal_hold` flag.
- **Recipients**: administrators with audit-view privilege; if
  `AUDIT_STREAM_ENABLED` is set, audit events are also emitted to an
  `OutboxEvent` stream for downstream consumption (e.g. a SIEM) — an
  additional internal/external recipient depending on where that stream is
  consumed.
- **Retention**: governed by `AuditRetentionPolicy.retention_days`
  (2555–36500 days, i.e. minimum 7 years, admin-configurable upward, with a
  `legal_hold` override). This is deliberately long and is the central
  tension documented in [DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights) and [DPIA.md](COMPLIANCE.md#section-gdpr-dpia): an
  immutable, hash-chained audit trail is a security control that resists
  erasure by design.
- **Cross-border transfer**: none beyond the controller's own infrastructure
  and any configured downstream SIEM/outbox consumer.

<a id="section-gdpr-ropa--processing-activity-5-notifications-smtp-webhooks-teams-integration"></a>
### Processing activity 5: Notifications, SMTP, webhooks, Teams integration

- **Purpose**: notify users of ticket/approval/change events by email,
  webhook, or Microsoft Teams.
- **Legal basis**: Art. 6(1)(b)/(f), ancillary to service delivery.
- **Data categories**: `Notification` (`user_id`, `title`, `body`,
  `target_type`/`target_id`); outbound email via customer-configured SMTP
  (`SMTP_HOST` setting, ~line 1822) carries requester/agent name, email,
  and ticket content in message bodies; outbound signed webhooks (SSRF- and
  DNS-rebinding-resistant per `integration_endpoint_valid`/
  `integration_endpoint_resolves_safely`, ~line 1918) can carry arbitrary
  ticket/user payload fields to whatever destination the administrator
  configures; Microsoft Teams integration similarly relays notification
  content to a Microsoft-hosted endpoint chosen by the controller.
- **Recipients**: the controller's own SMTP relay/mail provider; any
  administrator-configured webhook destination (third party, potentially
  outside the controller's jurisdiction); Microsoft (Teams), if configured.
- **Retention**: `Notification` rows persist per [RETENTION_POLICY.md](COMPLIANCE.md#section-gdpr-retention_policy);
  SMTP/webhook transmissions themselves are not stored by ServiceOps beyond
  delivery-attempt bookkeeping (`OutboxEvent`).
- **Cross-border transfer**: **this is the most likely real transfer path**
  in an otherwise self-hosted deployment — the controller chooses the SMTP
  provider, webhook destinations, and whether to enable Teams, and each of
  those may sit outside the controller's jurisdiction. ServiceOps enforces
  destination-safety at the network level (SSRF/DNS-rebinding protection)
  but has no GDPR-adequacy awareness of *where* a configured destination is
  hosted — that assessment is the controller's responsibility per
  destination.

<a id="section-gdpr-ropa--processing-activity-6-cmdb--configuration-items"></a>
### Processing activity 6: CMDB / Configuration Items

- **Purpose**: track infrastructure assets (servers, network devices) and
  their owners for incident/change context.
- **Legal basis**: Art. 6(1)(f), IT asset management.
- **Data categories** (`ConfigurationItem`, ~line 638): `ip_address`
  (device/asset IP — personal data only where it identifies a specific
  person's endpoint, e.g. a named user's laptop), `owner_id` (FK to
  `User`), `serial_number`, `location`, `attributes` (free-form JSON —
  unbounded, could contain anything an admin/import puts there).
- **Recipients**: internal (asset owners, CMDB admins); CSV export
  (`/cmdb/export`) and CSV/Google-Sheet import paths exist — both are
  data-flow points worth including in any DPIA the controller runs on their
  own CMDB usage.
- **Retention/transfer**: as above; CMDB import can pull from an external
  sheet URL, which is itself SSRF-validated but is a controller-configured
  external data source.

<a id="section-gdpr-ropa--summary-table"></a>
### Summary table

| # | Activity | Primary tables | Legal basis (typical) | Retention | Transfer risk |
|---|---|---|---|---|---|
| 1 | Identity/accounts | User, ExternalIdentity, UserPreference | 6(1)(b)/(f) | Until erasure request + tombstone indefinite | Low (self-hosted); controller's LDAP/OIDC/SMTP choice |
| 2 | Ticket content | Ticket, Comment, TaskNote, ChecklistItem | 6(1)(b)/(f) | Per RETENTION_POLICY.md | Low |
| 3 | Attachments | FileAttachment + file store | 6(1)(b)/(f) | Tied to parent record | Low, unless cloud object storage |
| 4 | Audit log | Audit, AuditRetentionPolicy, AuditIntegrityKey | 6(1)(c)/(f) | ≥7 years, legal-hold extendable | Low, unless SIEM export |
| 5 | Notifications/webhooks/SMTP/Teams | Notification, OutboxEvent, PlatformSetting | 6(1)(b)/(f) | Short (delivery) + Notification retention | **Highest** — controller-chosen third parties |
| 6 | CMDB | ConfigurationItem | 6(1)(f) | Per RETENTION_POLICY.md | Low |

<a id="section-gdpr-ropa--gaps--not-yet-found-in-source"></a>
### Gaps / not yet found in source

- No dedicated consent-tracking table was found (expected — most bases here
  are contract/legitimate-interest, not consent, which is normal for
  internal ITSM).
- No explicit sub-processor registry in the codebase; that is a
  documentation artifact ([DPA_TEMPLATE.md](COMPLIANCE.md#section-gdpr-dpa_template)), not a runtime feature.

---

<a id="section-gdpr-dpia"></a>

## Data Protection Impact Assessment (Art. 35 GDPR)

<a id="section-gdpr-dpia--data-protection-impact-assessment-art-35-gdpr"></a>

Scope: the three highest-risk processing activities identified in
[ROPA.md](COMPLIANCE.md#section-gdpr-ropa) — (A) the immutable audit log (IP addresses + full activity
trail), (B) attachment storage (arbitrary file content), and (C)
LDAP/AD directory sync (bulk identity ingestion). This assessment is written
from the product's perspective (what ServiceOps as software does and does
not mitigate); the operating **controller** must complete their own DPIA for
their specific deployment, using this as an input, not a substitute.

A DPIA is legally required (Art. 35(3)(b)) here because audit logging
involves systematic monitoring of individuals (agents and requesters) on a
large scale within an organization, and LDAP sync involves bulk processing
of employee directory data.

<a id="section-gdpr-dpia--a-audit-log-ip-addresses-user-agents-full-activity-trail"></a>
### A. Audit log (IP addresses, user agents, full activity trail)

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
[DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights): a hash-chained audit log is *designed* to resist
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

<a id="section-gdpr-dpia--b-attachment-storage"></a>
### B. Attachment storage

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

<a id="section-gdpr-dpia--c-ldapad-directory-sync"></a>
### C. LDAP/AD directory sync

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

<a id="section-gdpr-dpia--overall-dpia-conclusion"></a>
### Overall DPIA conclusion

No processing identified here is disproportionate to ServiceOps' stated
purpose (internal ITSM), and several required controls
(tenant isolation, hash-chained audit, SSRF-safe webhooks, malware-scan
hook) are real, verified-in-code mitigations, not aspirational claims.
The residual risks that need controller-level and/or follow-up
engineering attention are: (1) confirm automated audit-retention
enforcement exists, (2) confirm attachment file deletion is coupled to DB
row deletion, (3) confirm LDAP sync scoping and disable-propagation, (4)
decide and document, per deployment, the audit-immutability vs.
erasure-request balancing (see [DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights)). None of these
block using the product, but all four should be tracked in
`serviceops-notes/docs/BACKLOG.md` and [TRACEABILITY_MATRIX.md](BACKLOG.md#section-traceability_matrix) if not
already present.

---

<a id="section-gdpr-data_subject_rights"></a>

## Data Subject Rights Procedures (Art. 15, 16, 17, 18, 20, 21 GDPR)

<a id="section-gdpr-data_subject_rights--data-subject-rights-procedures-art-15-16-17-18-20-21-gdpr"></a>

This document describes how each right maps onto ServiceOps' actual data
model (per [ROPA.md](COMPLIANCE.md#section-gdpr-ropa)) and existing/expected code (`app.py`). A separate,
concurrent engineering effort is implementing the Art. 17 erasure and Art.
15/20 export HTTP routes in `serviceops_core`/`app.py`. Everything below
marked **pending technical verification** must be checked against that
implementation once it lands — this document was written without sight of
it, based on the `user_erase()` function and schema that existed at the
time of writing (2026-08-02).

<a id="section-gdpr-data_subject_rights--the-central-tension-audithistory-immutability-vs-erasure"></a>
### The central tension: audit/history immutability vs. erasure

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

<a id="section-gdpr-data_subject_rights--art-15--right-of-access"></a>
### Art. 15 — Right of access

**What a complete response must include**, per [ROPA.md](COMPLIANCE.md#section-gdpr-ropa)'s data
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

<a id="section-gdpr-data_subject_rights--art-16--right-to-rectification"></a>
### Art. 16 — Right to rectification

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

<a id="section-gdpr-data_subject_rights--art-17--right-to-erasure"></a>
### Art. 17 — Right to erasure

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
   short-lived/read-once) but should be covered by [RETENTION_POLICY.md](COMPLIANCE.md#section-gdpr-retention_policy)'s
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

<a id="section-gdpr-data_subject_rights--art-18--right-to-restriction-of-processing"></a>
### Art. 18 — Right to restriction of processing

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

<a id="section-gdpr-data_subject_rights--art-20--right-to-data-portability"></a>
### Art. 20 — Right to data portability

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

<a id="section-gdpr-data_subject_rights--art-21--right-to-object"></a>
### Art. 21 — Right to object

Applies primarily where processing is based on Art. 6(1)(f) legitimate
interest (much of [ROPA.md](COMPLIANCE.md#section-gdpr-ropa)'s basis for ticket/CMDB/notification
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

<a id="section-gdpr-data_subject_rights--summary-implementation-status"></a>
### Summary: implementation status

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

---

<a id="section-gdpr-retention_policy"></a>

## Data Retention Policy

<a id="section-gdpr-retention_policy--data-retention-policy"></a>

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
| `ExternalIdentity` link | `ExternalIdentity` | Should not outlive account erasure | Delete on `user_erase()` | **Gap** — not currently deleted by `user_erase()`; see [DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights) item 5 |
| Ticket content (open) | `Ticket`, `Comment`, `TaskNote`, `ChecklistItem` | Indefinite while ticket active/unresolved | N/A | N/A |
| Ticket content (closed/resolved) | same | Recommended: 3-7 years post-closure for ITIL/audit trend value, then archive or anonymize narrative fields, per controller's own record-keeping obligations | No automated archival job found in this pass | **Recommended, not yet enforced** |
| Soft-deleted ticket | `Ticket.deleted_at` set | Recommended: purge or hard-anonymize 30-90 days after soft-delete, unless referenced by active change/approval history | `deleted_at`/`deleted_by_id` exist; no purge job confirmed | **Gap — verify against `tools/outbox_worker.py` or scheduled jobs** |
| Attachments | `FileAttachment` + file store | Tied to parent ticket/comment/enterprise-record retention | `cascade="all, delete-orphan"` removes DB rows when parent hard-deleted | DB-row cascade implemented; **on-disk/object-store file deletion coupling not verified** (see [DPIA.md](COMPLIANCE.md#section-gdpr-dpia) Risk B.2) |
| Audit log | `Audit` | Minimum 2555 days (7 years), configurable up to 36500 days (100 years); `legal_hold` can suspend deletion entirely | `AuditRetentionPolicy.retention_days`, admin-configurable at `/admin/audit/retention` | Policy field implemented; **automated purge-on-expiry job not confirmed in this pass — flag as gap pending verification** |
| Audit integrity keys | `AuditIntegrityKey` | Retain for the life of any audit rows signed with that key (retiring a key must not invalidate historical hash verification) | `active`/`retired_at` fields | Implemented (rotation-aware) |
| Session data | Flask session cookie (server-side session data, if any) | `PERMANENT_SESSION_LIFETIME` (see `app.py` ~line 4392) | Cookie expiry; `SESSION_COOKIE_SECURE`/`HttpOnly`/`SameSite=Lax` enforced | Implemented (exact lifetime value depends on deployment config — not hardcoded in this doc) |
| Failed-login lockout state | `User.failed_login_count`, `locked_until` | Cleared on successful login / lockout window expiry | In-model fields | Implemented |
| Notifications | `Notification` | Recommended: 90-180 days, or until read + N days, whichever is later | No automated purge confirmed | **Recommended, not yet enforced** |
| CMDB / Configuration Items | `ConfigurationItem` | Lifecycle-tied to asset (retired status), not a fixed calendar period | `operational_status="Retired"` | Implemented as a status; automated purge after retirement not applicable/needed (asset history has ongoing CMDB value) |
| Outbox events (webhook/notification delivery bookkeeping, audit stream) | `OutboxEvent` | Recommended: short — 30-90 days after successful delivery, since these are transient delivery-attempt records, not the record of truth | Not verified in this pass | **Recommended, not yet enforced** |

<a id="section-gdpr-retention_policy--legal-holds"></a>
### Legal holds

`AuditRetentionPolicy.legal_hold` (boolean) exists and, per the admin route
at `/admin/audit/retention`, can be set independently of `retention_days`.
When a legal hold is active, retention/purge logic (wherever implemented)
must skip deletion entirely for that tenant's audit rows regardless of age.
No equivalent legal-hold flag was found on `Ticket`/`FileAttachment` —
**recommended gap**: a litigation/investigation hold on ticket or
attachment data currently has no first-class mechanism and would need to be
handled as a manual administrative exclusion from any future ticket-purge
job.

<a id="section-gdpr-retention_policy--what-deletion-means-per-category-cross-reference-to-data_subject_rightsmd"></a>
### What "deletion" means per category (cross-reference to DATA_SUBJECT_RIGHTS.md)

- **Hard delete** (row physically removed): appropriate for `Notification`,
  `OutboxEvent`, session data, and non-audit-referenced soft-deleted
  tickets past their retention window — nothing else depends on these rows
  existing.
- **Anonymize/tombstone** (row kept, identifying fields scrubbed):
  appropriate for `User` (already implemented via `user_erase()`), and
  should extend to `FileAttachment.original_name`/`Ticket.description`/
  `Comment.body` text where a specific erasure request targets narrative
  content (manual/escalated process — see [DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights)).
- **Never delete / append-only** (row retained regardless of subject
  requests, per Art. 17(3)(b)/(e)): `Audit` rows themselves, for the
  retention window set by `AuditRetentionPolicy` — the identifying `user_id`
  reference survives as a tombstoned-user FK, not as directly identifying
  data, which is the resolution documented in [DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights).

<a id="section-gdpr-retention_policy--open-items-for-backlogmd--traceability_matrixmd"></a>
### Open items for `BACKLOG.md` / [TRACEABILITY_MATRIX.md](BACKLOG.md#section-traceability_matrix)

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

---

<a id="section-gdpr-breach_notification"></a>

## Personal Data Breach Notification Procedure (Art. 33/34 GDPR)

<a id="section-gdpr-breach_notification--personal-data-breach-notification-procedure-art-3334-gdpr"></a>

This procedure applies to the operating **controller** (the customer
organization running a self-hosted ServiceOps instance). Where ServiceOps
acts as processor (a managed/SaaS deployment — see [DPA_TEMPLATE.md](COMPLIANCE.md#section-gdpr-dpa_template)), the
processor-to-controller notification SLA in that template feeds into step 2
below.

<a id="section-gdpr-breach_notification--1-detection"></a>
### 1. Detection

Realistic breach-detection signals in this product, mapped to what actually
exists in code today:

- **Unusual audit activity**: the `Audit` table (hash-chained,
  `Audit.action`/`target`/`source_ip`/`user_agent`) is queryable by
  administrators at `/admin/audit/*`. A breach investigation should start
  by querying `Audit` filtered by `tenant_id`, time window, and suspicious
  `action` values (mass exports, repeated failed logins, privilege
  changes, unusual `source_ip`).
- **Failed-login lockouts**: `User.failed_login_count`/`locked_until`
  provide a per-account brute-force signal; no aggregate/cross-account
  anomaly detection (e.g. "many accounts locked out from one IP in a short
  window") was found in this pass — **flag as gap**: this kind of
  cross-account correlation query is not a built-in report and would need
  to be run manually against `Audit`/`User` by an administrator with
  database access, or built as a proper admin report.
- **Integration/webhook signing failures or SSRF-block events**: the
  SSRF/DNS-rebinding checks (`integration_endpoint_valid`,
  `integration_endpoint_resolves_safely`) reject unsafe destinations at
  delivery time; whether a *rejected* delivery attempt is itself logged to
  `Audit` (a signal of a possible malicious webhook reconfiguration) was
  not confirmed in this pass — **flag as gap pending verification**.
- **Malware-scan hits on attachments**: `FileAttachment.scan_status`
  supports a quarantine state; a spike in flagged uploads is a signal
  worth including in breach-detection runbooks once the scanning adapter
  is confirmed wired up (adapter is pluggable per
  `ServiceOps/CLAUDE.md`, not verified as active in this pass).
- **Infrastructure-layer signals** (unauthorized DB access, container
  compromise, credential leak) are outside ServiceOps' application code
  and depend entirely on the controller's own infrastructure monitoring —
  this document cannot assess those; they are the controller's
  responsibility to instrument.

<a id="section-gdpr-breach_notification--2-internal-triage-and-severity-assessment-target-within-hours-of-detection"></a>
### 2. Internal triage and severity assessment (target: within hours of detection)

1. Whoever detects/suspects a breach (support engineer, admin, automated
   alert if the controller has built one) immediately notifies the
   controller's designated privacy/security contact (DPO if appointed, or
   equivalent role) — do not wait for full confirmation before this first
   internal notification.
2. Assess, using `Audit` query results and whatever infrastructure logs
   are available:
   - **Which tenant(s)** are affected — `Audit.tenant_id`,
     `User.tenant_id`, `Ticket.tenant_id` scoping means a breach confined
     to one tenant's credentials/session should not, if tenant isolation
     held, expose other tenants' data. Confirming that isolation held (not
     just assuming it) is itself part of triage — check for any
     cross-tenant query anomalies in the audit trail.
   - **What data categories** were exposed — cross-reference against
     [ROPA.md](COMPLIANCE.md#section-gdpr-ropa)'s six processing activities. An attachment-store breach
     (file content) is qualitatively different from a credential/session
     breach (access risk) or an audit-log breach (IP/activity trail
     exposure) — each drives different Art. 34 individual-notification
     criteria.
   - **How many data subjects** — count distinct `User.id`/
     `requester_id`/`assignee_id`/`uploaded_by_id` values touched, per
     tenant.
   - **Root cause category** — credential compromise, application
     vulnerability, infrastructure misconfiguration, insider action, third
     party (webhook/SMTP/LDAP provider) compromise.
3. Assign severity: does this meet the Art. 33(1) threshold ("a personal
   data breach ... unless the personal data breach is unlikely to result in
   a risk to the rights and freedoms of natural persons")? A leaked
   internal ticket title is a different risk tier than a leaked
   `password_hash` table or a leaked attachment containing HR documents.

<a id="section-gdpr-breach_notification--3-supervisory-authority-notification-72-hour-clock-art-33"></a>
### 3. Supervisory authority notification (72-hour clock, Art. 33)

- **Clock start**: from when the controller becomes *aware* of the breach,
  not from when it occurred — document the awareness timestamp explicitly
  (e.g. the `Audit` row timestamp of the detecting query, or the alert
  timestamp) since this is what a regulator will ask for first.
- **Who**: the controller's designated DPO/privacy contact notifies their
  relevant supervisory authority (determined by the controller's main
  establishment or the affected data subjects' location, per Art.
  55/56 — a controller-side legal determination, not something ServiceOps
  can determine on their behalf).
- **What to include** (Art. 33(3)): nature of the breach and approximate
  number of data subjects/records (derived from step 2's `Audit`/`User`
  count query); the DPO/contact's details; likely consequences; measures
  taken or proposed (e.g. forced password reset via `auth_version`
  increment — see `User.auth_version`, which exists precisely to
  invalidate all outstanding sessions/tokens for an account, a real,
  usable technical control for breach containment).
- **If full facts aren't known within 72 hours**: Art. 33(4) permits
  phased notification — notify with what's known, then supplement. Do not
  delay the initial notification waiting for a complete picture.

<a id="section-gdpr-breach_notification--4-data-subject-notification-art-34"></a>
### 4. Data subject notification (Art. 34)

Required when the breach is "likely to result in a high risk to the rights
and freedoms of natural persons." Given this product's data categories,
scenarios that likely cross that threshold:

- Exposure of `password_hash` values (even hashed, warrants a mandatory
  forced reset + notification given credential-stuffing risk).
- Exposure of attachment content containing sensitive documents.
- Exposure sufficient to enable identity-linked profiling (e.g. a large
  `Audit`-table export correlating identity + IP + detailed activity).
- Any exposure the controller's own risk assessment (informed by their
  DPIA, [DPIA.md](COMPLIANCE.md#section-gdpr-dpia)) rates high.

**Notification content**: plain-language description of the breach, the
DPO/contact's details, likely consequences, and measures taken —
consistent with Art. 34(2). Delivery channel: the controller's own SMTP
configuration (`SMTP_HOST` setting) is the natural mechanism, but if
account credentials themselves are suspected compromised, do not rely
solely on in-product notification (`Notification` table) — use an
out-of-band channel (direct email from a verified admin address, not
through the potentially-compromised system) for anything security-critical.

**Exemptions** (Art. 34(3)): not required if the exposed data was
effectively encrypted/rendered unintelligible (e.g. `password_hash` alone,
without other credentials, may qualify — a controller-side legal judgment,
document the reasoning if relying on this).

<a id="section-gdpr-breach_notification--5-containment-technical-actions-available-in-the-product-today"></a>
### 5. Containment technical actions available in the product today

- **Force session/credential invalidation**: increment `User.auth_version`
  for affected accounts (existing field, used to invalidate active
  sessions/tokens without deleting the account) — this is a real,
  immediately usable containment control.
- **Deactivate accounts**: `User.active = False` for compromised accounts,
  which also blocks login immediately (`is_active` property).
- **Rotate audit integrity key**: `AuditIntegrityKey.active`/`retired_at`
  support key rotation if an audit-signing key itself is suspected
  compromised, without invalidating historical hash verification
  (retired keys remain valid for verifying past entries).
- **Revoke/rotate webhook and API credentials**: `PlatformSetting`-stored
  webhook secrets and any `ApiClient`-style API credentials should be
  rotated; confirm the admin UI supports credential rotation without
  requiring a full reinstall (not verified in this pass).
- **Identify affected tenant(s) and record counts**: via tenant-scoped
  `Audit`/`User`/`Ticket` queries as in step 2 — this capability exists
  today (standard SQL/ORM queries against tenant-scoped tables); there is
  no purpose-built "generate a breach-scope report" admin feature — **flag
  as gap**: a dedicated admin report (affected tenant, affected user count,
  affected data categories, time range) would materially speed up Art.
  33(3)'s required content and is worth a backlog item.

<a id="section-gdpr-breach_notification--6-escalation-path-template--controller-must-name-actual-roles"></a>
### 6. Escalation path (template — controller must name actual roles)

1. Detector -> on-call/security contact (immediate)
2. Security contact -> DPO/privacy lead (within hours) — severity
   assessment per step 2
3. DPO/privacy lead -> supervisory authority (within 72 hours of
   awareness, if threshold met) — per step 3
4. DPO/privacy lead -> affected data subjects (without undue delay, if
   high-risk threshold met) — per step 4
5. Engineering/admin -> containment actions (step 5), in parallel with 2-4,
   not sequential after them
6. Post-incident: root-cause writeup, [TRACEABILITY_MATRIX.md](BACKLOG.md#section-traceability_matrix) update if a
   product gap contributed, `BACKLOG.md` entry for any fix, and — if the
   gap was one of the items flagged in [DPIA.md](COMPLIANCE.md#section-gdpr-dpia)/[RETENTION_POLICY.md](COMPLIANCE.md#section-gdpr-retention_policy) —
   cross-reference those documents so the same gap isn't independently
   rediscovered later.

<a id="section-gdpr-breach_notification--gaps-summary-for-backlogmd"></a>
### Gaps summary (for BACKLOG.md)

1. No cross-account brute-force/anomaly correlation report.
2. Unconfirmed whether SSRF-blocked webhook attempts are audit-logged.
3. No purpose-built "breach scope" admin report (tenant/user-count/data-category rollup).
4. Malware-scan-adapter wiring not confirmed active (referenced as pluggable, not verified live).

---

<a id="section-gdpr-dpa_template"></a>

## Data Processing Agreement — Template

<a id="section-gdpr-dpa_template--data-processing-agreement--template"></a>

This is a template for use when ServiceOps (the vendor) acts as a **Data
Processor** for a customer (the **Data Controller**). Per [ROPA.md](COMPLIANCE.md#section-gdpr-ropa), this
applies when the vendor operates or has access to a customer's running
instance/data (e.g. a managed-hosting or SaaS variant, or vendor-provided
support requiring data access) — **not** to a purely self-hosted deployment
where the vendor has no access to the customer's database, files, or logs
at all (in that case there is no processor relationship for the vendor to
sign a DPA under, though the customer may still want this document's
security-measures section as a reference for their own internal records).

Bracketed `[...]` fields are to be filled in per engagement. This is a
drafting aid, not legal advice — have counsel review before execution.

---

<a id="section-gdpr-dpa_template--data-processing-agreement"></a>
### Data Processing Agreement

Between **[Customer Legal Name]** ("Controller") and **[ServiceOps Vendor
Legal Name]** ("Processor"), effective **[date]**, supplementing the
**[Master Services Agreement / Support Agreement reference]**.

<a id="section-gdpr-dpa_template--1-subject-matter-and-duration"></a>
#### 1. Subject matter and duration

Processor provides **[hosting / managed operation / support access]** for
the Controller's ServiceOps instance. This DPA remains in effect for the
duration of that service and any period during which Processor retains
Controller Personal Data thereafter (see Retention, Section 7).

<a id="section-gdpr-dpa_template--2-nature-and-purpose-of-processing"></a>
#### 2. Nature and purpose of processing

Processor processes Personal Data solely to **[provide hosting
infrastructure / perform requested support actions / operate scheduled
maintenance]** for Controller's ServiceOps instance. Processor does not
process Controller Personal Data for its own purposes, including but not
limited to marketing, analytics not required for service delivery, or
disclosure to any party not listed in Section 5.

<a id="section-gdpr-dpa_template--3-categories-of-data-subjects-and-personal-data"></a>
#### 3. Categories of data subjects and personal data

Per [ROPA.md](COMPLIANCE.md#section-gdpr-ropa), processed under this instance:

- **Data subjects**: Controller's employees, contractors, and any other
  individuals who use the ServiceOps instance as requesters, agents, or
  administrators.
- **Categories of personal data**: identity/contact data (name, email,
  phone, title, department, employee ID), authentication data (password
  hashes, external-identity provider subject IDs), ticket/service-request
  content (free text, potentially including personal data pasted by
  users), file attachments (arbitrary content), activity/audit data
  (IP addresses, user agents, action history), and, if configured, CMDB
  asset-owner associations. No special categories of data (Art. 9) are
  processed by design; Controller is responsible for not entering special
  category data into free-text fields, or for obtaining appropriate basis
  if they do.

<a id="section-gdpr-dpa_template--4-controller-and-processor-obligations"></a>
#### 4. Controller and Processor obligations

**Controller** shall: determine the lawful basis for all processing;
ensure data subjects are informed per Art. 13/14; configure the instance
(retention settings, authentication providers, integrations) consistent
with its own obligations; respond to or route data subject requests per
[DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights), with Processor's support per Section 6 below;
ensure any third-party integrations it configures (SMTP relay, webhook
destinations, Teams, LDAP/OIDC provider) are themselves appropriately
governed, since Controller — not Processor — selects and controls those
destinations (see [ROPA.md](COMPLIANCE.md#section-gdpr-ropa) Processing activity 5).

**Processor** shall: process Personal Data only on documented instructions
from Controller (this DPA plus the underlying service agreement
constitute those instructions, absent a separate written instruction);
ensure personnel with data access are bound by confidentiality; implement
the technical and organizational measures in Section 8; assist Controller
with data subject requests, DPIAs, and breach notifications per Sections 6
and 9; not engage a sub-processor without the notice in Section 5; delete
or return Personal Data at the end of the engagement per Section 7; make
available information necessary to demonstrate compliance with this
Article-28-equivalent DPA and allow for audits per Section 10.

<a id="section-gdpr-dpa_template--5-sub-processors"></a>
#### 5. Sub-processors

Processor may engage the following sub-processors for the categories of
processing indicated. Processor will provide **[30] days'** advance notice
of any new sub-processor via **[notification channel — e.g. email to
Controller's designated contact, or a published sub-processor page]**,
during which Controller may object on reasonable data-protection grounds.

| Sub-processor | Purpose | Location | Data categories accessed |
|---|---|---|---|
| [Cloud infrastructure provider, if managed-hosting] | Hosting / infrastructure | [region] | All categories processed by the instance |
| [Email delivery provider, if Processor-operated SMTP] | Notification delivery | [region] | Name, email, notification content |
| [Object storage provider, if not customer-provided] | Attachment storage | [region] | Attachment content and metadata |
| [Monitoring/observability provider] | Infrastructure monitoring | [region] | Operational telemetry; avoid application-level personal data in monitoring pipelines where possible |

If Controller operates a fully self-hosted instance with no Processor
access to infrastructure, this table should read "Not applicable — no
sub-processors, as Processor has no access to Controller's instance or
data."

<a id="section-gdpr-dpa_template--6-assistance-with-data-subject-rights"></a>
#### 6. Assistance with data subject rights

Processor shall, upon Controller's request and within **[X business
days]**, provide reasonable technical assistance for Controller to fulfill
data subject requests under Art. 15-21, consistent with the mechanisms and
known gaps documented in [DATA_SUBJECT_RIGHTS.md](COMPLIANCE.md#section-gdpr-data_subject_rights) (e.g. Processor will
support Controller in retrieving a data-subject export bundle or executing
an erasure request against the instance, using the product's built-in
`user_erase()`-equivalent mechanism and any export routes provided).
Processor is not itself the point of contact for data subjects unless
separately agreed; Controller remains responsible for determining the
lawful response to each request.

<a id="section-gdpr-dpa_template--7-retention-and-deletion-at-termination"></a>
#### 7. Retention and deletion at termination

Processor retains Controller Personal Data only per Controller's
configured retention settings ([RETENTION_POLICY.md](COMPLIANCE.md#section-gdpr-retention_policy)) during the term.
Upon termination, Processor shall, at Controller's election, **[return all
Personal Data in a structured export format]** and/or **[delete all
Personal Data, including backups, within [X days]]**, except where
retention is required by applicable law (e.g. financial record-keeping),
in which case Processor shall isolate and protect such data and limit
processing to the retention purpose only.

<a id="section-gdpr-dpa_template--8-security-measures"></a>
#### 8. Security measures

Processor implements, at minimum, the technical and organizational
measures already required of the ServiceOps product per
`ServiceOps/CLAUDE.md`'s Security requirements section, including:
tenant-scoped authorization enforced server-side; CSRF protection; secure
session lifecycle (`SESSION_COOKIE_SECURE`, `HttpOnly`,
`SameSite`); tamper-evident audit history (HMAC-SHA256 hash-chained audit
log); file-upload validation, content-type/extension verification,
cryptographic attachment hashing, and malware-scanning/quarantine hook;
SSRF-resistant, signed, DNS-rebinding-protected outbound webhooks; secret
redaction in logs (no passwords, tokens, connection strings, or LDAP bind
credentials logged); rate limiting and idempotency on mutating
integrations; least-privilege database roles and container configuration;
dependency and container image scanning. Where Processor also provides
infrastructure (managed-hosting variant), it additionally maintains
**[encryption at rest / encryption in transit / access logging / patching
SLA — fill in per actual infrastructure]**.

<a id="section-gdpr-dpa_template--9-breach-notification"></a>
#### 9. Breach notification

Processor shall notify Controller **without undue delay, and in any event
within [24-48] hours** of becoming aware of a Personal Data breach
affecting Controller's instance, providing the information available at
that time and supplementing it as the investigation per
[BREACH_NOTIFICATION.md](COMPLIANCE.md#section-gdpr-breach_notification) progresses, so Controller can meet its own
Art. 33 72-hour supervisory-authority notification obligation.

<a id="section-gdpr-dpa_template--10-audit-rights"></a>
#### 10. Audit rights

Controller may request, no more than **[once annually, or following a
security incident]**, evidence of Processor's compliance with this DPA,
including relevant audit reports, penetration test summaries, or, subject
to reasonable confidentiality and scheduling constraints, an on-site/remote
audit.

<a id="section-gdpr-dpa_template--11-international-transfers"></a>
#### 11. International transfers

Where Processor or any sub-processor processes Personal Data outside
Controller's jurisdiction or the EEA/UK (as applicable), such transfer is
made subject to **[Standard Contractual Clauses / an adequacy decision /
other approved transfer mechanism]**, attached as Annex **[X]**. For a
purely self-hosted deployment where Controller's own infrastructure (and
Controller-chosen SMTP/LDAP/webhook destinations) is the only place
Personal Data is processed, this Section is not applicable to Processor
(Controller remains responsible for its own third-party selections, per
[ROPA.md](COMPLIANCE.md#section-gdpr-ropa) Processing activity 5).

<a id="section-gdpr-dpa_template--12-liability-and-indemnity"></a>
#### 12. Liability and indemnity

**[Per Master Services Agreement / standard liability clauses — not
drafted here, requires counsel input specific to the commercial
relationship.]**

---

*Annexes to attach per engagement: (A) full sub-processor list if not
inlined above; (B) SCCs or other transfer mechanism if Section 11 applies;
(C) security measures detail beyond Section 8's summary, if Controller
requires an extended Annex II-style technical/organizational measures
document.*

---

<a id="section-iso27001-isms_policies"></a>

## ServiceOps ISMS Core Policies (draft, ISO/IEC 27001:2022-aligned)

<a id="section-iso27001-isms_policies--serviceops-isms-core-policies-draft-isoiec-270012022-aligned"></a>

Status: **Draft — pending owner sign-off.** These are first drafts scoped to
what ServiceOps actually is and how it's actually deployed: a self-hosted
ITSM platform (Flask/FastAPI + PostgreSQL, Docker/Kubernetes, AD/LDAP +
Keycloak/OIDC, multi-tenant), maintained by a small team per CLAUDE.md's
collaboration model. They deliberately avoid generic boilerplate that
doesn't fit that reality (e.g., no office-badge-access language, no SaaS
shared-responsibility clauses beyond what the deployment model needs).

Each policy names an owner placeholder, a review cadence, and references the
concrete mechanisms already in the codebase where they exist, plus the gap
they don't yet cover (cross-referenced to [GAP_ANALYSIS.md](COMPLIANCE.md#section-iso27001-gap_analysis)).

---

<a id="section-iso27001-isms_policies--1-information-security-policy"></a>
### 1. Information Security Policy

**Owner:** [ISMS owner — not yet named; see GAP_ANALYSIS.md item 16]
**Review cadence:** Annually, or after any material architecture change.

<a id="section-iso27001-isms_policies--purpose"></a>
#### Purpose
Establish ServiceOps' commitment to protecting the confidentiality,
integrity, and availability of information it processes — primarily
customers' ITSM data (incidents, changes, CMDB, attachments, audit history)
across a multi-tenant deployment.

<a id="section-iso27001-isms_policies--scope"></a>
#### Scope
Applies to the ServiceOps codebase, its Docker/Helm deployment artifacts,
and the engineering practices used to build and release it. Does not
prescribe controls for customers' own infrastructure beyond what
DEPLOYMENT.md documents as required/recommended configuration.

<a id="section-iso27001-isms_policies--policy-statements"></a>
#### Policy statements
1. Tenant isolation is a non-negotiable security boundary. Per CLAUDE.md,
   `tenant_id` enforcement must fail closed everywhere — queries, writes,
   relationships, background jobs, notifications, webhooks, API endpoints,
   audit records, unique constraints, admin screens, import/export. Any
   change that risks weakening this boundary requires explicit security
   review before merge.
2. Authentication defaults to secure settings: session cookies are
   HttpOnly/SameSite=Lax/Secure by default, and the application refuses to
   start with insecure cookies outside an explicit development opt-in
   (`ALLOW_INSECURE_SESSION_COOKIES`) — this behavior must not be weakened.
3. No production instance may run with demo data, seeded tickets, shared
   demo accounts, or default/weak credentials, per CLAUDE.md's
   Production-only policy — this is treated as a security control, not just
   a product-quality one.
4. Every release is versioned, tagged, and its migrations reversible;
   security-relevant changes are recorded in `docs/BACKLOG.md` with
   evidence, per the existing traceability convention in this repo.
5. Known gaps (see [GAP_ANALYSIS.md](COMPLIANCE.md#section-iso27001-gap_analysis)) are tracked to closure, not silently
   accepted — MFA, dependency scanning, and secret redaction are the current
   highest-priority open items.
6. Management (the ISMS owner, once named) reviews this policy set and the
   SOA annually and after any significant incident.

---

<a id="section-iso27001-isms_policies--2-access-control-policy"></a>
### 2. Access Control Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually.

<a id="section-iso27001-isms_policies--identity-sources"></a>
#### Identity sources
ServiceOps supports exactly three authentication patterns (CLAUDE.md):
local bootstrap administrator (no known default password — the installer
requires an explicit admin password, app.py:4164), Active Directory/LDAP,
and Keycloak/OIDC. No other authentication mechanism may be added without
updating this policy.

<a id="section-iso27001-isms_policies--authorization-model"></a>
#### Authorization model
- Access is tenant-scoped first, then role/team-scoped within a tenant.
  Tenant resolution must fail closed — an authenticated user with a missing
  `tenant_id` must never be defaulted to tenant 1.
- AD group→team mappings (e.g., `gg_unix -> Unix`) drive automatic
  provisioning and team assignment; administrators configure mapping
  priority, conflict resolution, and disabled/removed-user handling.
- Visibility across IT teams (CoreApps, Database, Network, Windows, Unix,
  SSD) does not imply mutation rights. A team must not progress, assign,
  resolve, or close another team's work item merely because it's visible.
- Privileged actions (CCB approval, change authorization, team-manager
  authority) are explicit roles/flags, not inferred from general admin
  status.

<a id="section-iso27001-isms_policies--authentication-strength"></a>
#### Authentication strength
- Passwords are hashed (currently PBKDF2 via Werkzeug's
  `generate_password_hash`; see GAP_ANALYSIS.md item 4 for the planned
  Argon2id/scrypt upgrade).
- Failed-login lockout is enforced (`LOGIN_MAX_ATTEMPTS`,
  `LOGIN_LOCKOUT_MINUTES`, default 5 attempts / 15 minutes).
- **MFA is not yet implemented** (GAP_ANALYSIS.md item 1) and is the
  highest-priority open item in this policy area — required for admin and
  CCB-eligible accounts once delivered.
- CSRF tokens are required on all state-changing requests when
  `CSRF_ENABLED` is true (the production default).

<a id="section-iso27001-isms_policies--access-review"></a>
#### Access review
Access rights (AD group mappings, team membership, CCB eligibility,
approval authority) should be reviewed by the deploying customer at least
quarterly; ServiceOps' admin screens are the system of record for this
review (per CLAUDE.md's configurability requirements).

---

<a id="section-iso27001-isms_policies--3-incident-management-policy"></a>
### 3. Incident Management Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually, or after any actual security incident.

This policy covers **security incidents affecting ServiceOps itself**
(e.g., a suspected tenant-isolation bypass, a leaked credential, a
vulnerability report) — distinct from the product's own ITIL Incident (INC)
ticket type, which handles customers' *service* incidents and is documented
in [docs/ITIL_TICKET_HIERARCHY.md](ENGINEERING_REFERENCE.md#section-itil_ticket_hierarchy).

<a id="section-iso27001-isms_policies--reporting"></a>
#### Reporting
A security concern about ServiceOps should be reportable through a clearly
published channel. **Currently missing** — GAP_ANALYSIS.md item 7
recommends adding a `SECURITY.md`/`security.txt` with a disclosure contact
and target acknowledgement time (recommend 3 business days).

<a id="section-iso27001-isms_policies--triage-and-severity"></a>
#### Triage and severity
Suggested severity tiers, modeled on the product's own incident-priority
logic (`serviceops_core/priority.py`) but applied to security events:
- **Critical** — active tenant-boundary bypass, remote code execution,
  authentication bypass. Immediate response; consider taking the affected
  deployment offline if the reporter is a customer describing live
  exploitation.
- **High** — credential/secret exposure, privilege escalation without
  active exploitation evidence, SSRF bypass of the existing guard
  (app.py:1906-1944).
- **Medium** — vulnerable dependency with no known exploit path yet,
  missing defense-in-depth control (e.g., missing rate limiting on a
  non-auth endpoint).
- **Low** — hardening recommendations, informational findings.

<a id="section-iso27001-isms_policies--response"></a>
#### Response
1. Acknowledge the report within the published target time.
2. Reproduce and confirm scope (which tenants/deployments/versions are
   affected).
3. Fix, following the same reversible-migration and versioned-release
   discipline CLAUDE.md requires for all changes — security fixes are not
   exempt from testing against real dependencies where feasible.
4. Notify affected parties per contractual/regulatory obligation (this
   overlaps with GDPR breach-notification duties — coordinate with the
   concurrent GDPR workstream rather than duplicating that analysis here).
5. Record the incident and remediation in `docs/BACKLOG.md`, with evidence,
   per this repo's existing convention.

<a id="section-iso27001-isms_policies--post-incident-review"></a>
#### Post-incident review
Every Critical/High security incident gets a written post-incident review
(mirroring the product's own PIR concept for changes) covering root cause,
detection gap (could the `Audit` log / SIEM stream have caught it sooner —
see GAP_ANALYSIS.md item 9), and the specific control added to prevent
recurrence.

---

<a id="section-iso27001-isms_policies--4-business-continuity--backup-policy"></a>
### 4. Business Continuity / Backup Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually, plus after every DR drill.

<a id="section-iso27001-isms_policies--backup-mechanism"></a>
#### Backup mechanism
- Bundled-database deployments: `./serviceops backup` produces SHA-256-
  manifested backup sets with owner-only file permissions
  (`docs/DEPLOYMENT.md`). PostgreSQL PITR is supported given an
  archive-enabled cluster and a verified base backup.
- External/managed-database deployments: backup responsibility is
  intentionally delegated to the database provider's snapshot/PITR
  tooling; `./serviceops backup` explains this rather than producing an
  incomplete application-only backup — this is a deliberate design choice,
  not a gap, and this policy defers to whatever the provider's own SLA
  documents.
- Recovery sets are validated with `tools/recovery_verify.py` before being
  trusted, and the database and uploads must be recovered from the same
  logical backup window (never mixed windows).

<a id="section-iso27001-isms_policies--targets"></a>
#### Targets
**RTO/RPO are not currently defined** (GAP_ANALYSIS.md item 10). Until
formal targets are set by the ISMS owner, the working assumption based on
documented backup frequency guidance in DEPLOYMENT.md should be made
explicit here once that guidance is reviewed — this policy will be updated
with concrete numbers rather than left as a placeholder past the next
review cycle.

<a id="section-iso27001-isms_policies--testing"></a>
#### Testing
At least one restore drill per year, executed against a non-production
environment using `tools/recovery_verify.py`, with the measured time-to-
recover logged against the (once defined) RTO target. Results recorded in
`docs/BACKLOG.md`.

<a id="section-iso27001-isms_policies--retention"></a>
#### Retention
Backup retention periods are not currently standardized in documentation
(distinct from the in-product `AuditRetentionPolicy` model, app.py:352,
which governs audit-record retention, not backup retention). This policy
recommends the ISMS owner set an explicit backup retention window (e.g.,
30 daily + 12 monthly) consistent with each customer's regulatory
obligations, since ServiceOps itself doesn't operate the storage for
self-hosted customers.

---

<a id="section-iso27001-isms_policies--5-supplier--vendor-security-policy"></a>
### 5. Supplier / Vendor Security Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually, or when a new integration category is added.

<a id="section-iso27001-isms_policies--scope-1"></a>
#### Scope
Two distinct supplier relationships apply to ServiceOps:
1. **ServiceOps' own build-time dependencies** — Python packages
   (`requirements.txt`), base container images, and the Helm chart's own
   dependencies (e.g., bundled PostgreSQL image).
2. **Customer-configured runtime integrations** — LDAP/AD servers,
   Keycloak, SMTP, webhooks, Microsoft Teams, monitoring ingestion, SIEM
   streaming, NetBox/RT import, and the optional ClamAV daemon. These are
   the deploying customer's supplier relationships, not ServiceOps Inc.'s,
   but ServiceOps is responsible for connecting to them safely.

<a id="section-iso27001-isms_policies--build-time-dependency-controls"></a>
#### Build-time dependency controls
- Dependencies are version-pinned in `requirements.txt`.
- **Not yet implemented:** automated CVE/vulnerability scanning and SBOM
  generation (GAP_ANALYSIS.md item 5) — this is the top action item for
  this policy area.

<a id="section-iso27001-isms_policies--runtime-integration-controls-already-implemented-kept-as-policy-baseline"></a>
#### Runtime integration controls (already implemented, kept as policy baseline)
- Outbound webhook/export destinations are validated by an SSRF guard that
  blocks loopback, link-local, multicast, unspecified, and reserved
  addresses (app.py:1906-1944; `serviceops_core/netbox_sync.py:367`) —
  this must remain in place for any new outbound-integration feature.
- LDAP connections default to StartTLS (`LDAP_START_TLS=true` in
  compose.yaml).
- Integration secrets (webhook signing secrets, LDAP bind password,
  Keycloak client secret) are stored Fernet-encrypted at rest, not in
  plaintext config (app.py:1847-1867).
- Optional malware scanning of uploaded attachments via a ClamAV daemon
  (app.py:2609-2648) — disabled by default; **recommend customers running
  multi-tenant production instances enable `CLAMAV_ENABLED`**, since
  it currently ships off.

<a id="section-iso27001-isms_policies--contractual-baseline"></a>
#### Contractual baseline
No standard security addendum currently exists for customers wiring
third-party systems into ServiceOps via webhooks (GAP_ANALYSIS.md item 8
inherits into this). The ISMS owner should draft a minimum-security
baseline (e.g., "webhook endpoints must present a valid TLS certificate;
shared secrets must not be reused across integrations") to publish
alongside DEPLOYMENT.md.

---

<a id="section-iso27001-isms_policies--6-acceptable-use-policy"></a>
### 6. Acceptable Use Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually.

Applies to anyone with access to ServiceOps source, build infrastructure,
or a running instance's administrative functions (maintainers and, where
customers grant it, ServiceOps support staff assisting a deployment).

<a id="section-iso27001-isms_policies--rules"></a>
#### Rules
1. No credentials, API tokens, or encryption keys (`SECRET_KEY`,
   `SETTINGS_ENCRYPTION_KEY`, LDAP bind password, Keycloak client secret)
   may be committed to source control, shared over unencrypted channels, or
   hard-coded — consistent with CLAUDE.md's explicit prohibition on
   hard-coded secrets and visible credentials.
2. No demo/test accounts, seeded records, or weak default passwords may be
   introduced into a production-configured instance, per CLAUDE.md's
   Production-only policy — this applies to anyone with admin access, not
   just to the codebase.
3. Privileged utility scripts (e.g., `tools/production_cleanup.py`) must be
   run in their default dry-run mode first; `--apply` is only used after a
   verified backup exists, per that tool's own documented requirement.
4. Access to a customer's production instance (e.g., for support) is
   logged and time-bounded; the `Audit` table is the system of record for
   who accessed what and when — accessing customer data outside a
   documented support request is prohibited.
5. Legacy/former user identities are disabled or tombstoned per CLAUDE.md,
   never hard-deleted where doing so would damage audit history — this
   applies to anyone with admin rights, who must not work around this by
   deleting records to "clean up."
6. Development/test work must not use real customer data. Where production
   data is genuinely needed for debugging, it must be handled under the
   same confidentiality expectations as production (see A.8.33 gap in
   [GAP_ANALYSIS.md](COMPLIANCE.md#section-iso27001-gap_analysis) — masking of production data used in test is not yet
   formalized; treat production data as sensitive in test contexts in the
   meantime).

<a id="section-iso27001-isms_policies--enforcement"></a>
#### Enforcement
Violations are handled per the ServiceOps organization's own personnel
policy (out of this document's scope — organizational HR matter, not a
product control).

---

<a id="section-iso27001-isms_policies--adoption-checklist"></a>
### Adoption checklist

- [ ] ISMS owner named and recorded in [docs/GOVERNANCE.md](ENGINEERING_REFERENCE.md#section-governance) decision log.
- [ ] Each policy above reviewed and formally approved (sign-off recorded).
- [ ] RTO/RPO targets filled in for the Business Continuity/Backup Policy.
- [ ] `SECURITY.md`/disclosure contact published per Incident Management
      Policy.
- [ ] First annual review date scheduled for all six policies.

---

<a id="section-iso27001-soa"></a>

## Statement of Applicability — ISO/IEC 27001:2022 Annex A

<a id="section-iso27001-soa--statement-of-applicability--isoiec-270012022-annex-a"></a>

Scope: ServiceOps ITSM platform (FastAPI/Flask + PostgreSQL, Docker/Kubernetes
deployable, AD/LDAP + Keycloak/OIDC authentication, multi-tenant). This SOA
covers the ServiceOps product and its documented deployment model as a
self-hosted, customer-operated application — it does not cover ServiceOps
Inc.'s own corporate IT (HR systems, office network, etc.), which is out of
scope until the company operates a hosted/SaaS offering.

Status legend:

- **Implemented** — verified directly in source, migrations, Helm charts, or
  compose files as of this review (2026-08-02).
- **Partially Implemented** — some mechanism exists but is incomplete,
  optional/disabled by default, or not enforced everywhere it should be.
- **Gap** — control is applicable and required but no implementation was found.
- **Not Started** — applicable, intended per CLAUDE.md/backlog, but no code exists yet.
- **N/A** — not applicable, with justification.

Evidence citations reference `/Users/anushka/Github/ServiceOps` (app.py line
numbers, charts/, compose.yaml, docs/) as read on 2026-08-02. Where a control
is organizational/procedural rather than technical, "evidence" refers to
serviceops-notes docs (GOVERNANCE.md, DEPLOYMENT.md, OPERATIONS_MANUAL.md) or
notes the absence of such a document.

Every gap/partial item below is expanded with a remediation in [GAP_ANALYSIS.md](COMPLIANCE.md#section-iso27001-gap_analysis).

<a id="section-iso27001-soa--a5-organizational-controls-37"></a>
### A.5 Organizational controls (37)

| # | Control | Applicable | Status | Evidence / Notes |
|---|---|---|---|---|
| A.5.1 | Policies for information security | Yes | Gap | No ISMS policy set existed before this review. Drafted in [ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies); needs owner sign-off and a review cadence to become "Implemented." |
| A.5.2 | Information security roles and responsibilities | Yes | Gap | No named security officer/role in GOVERNANCE.md. Product has technical roles (admin, team manager, CCB) but no ISMS-level accountable owner defined. |
| A.5.3 | Segregation of duties | Yes | Partially Implemented | App enforces role/team separation for ITIL workflows (CLAUDE.md change-governance rules, CCB approval chain) but no segregation defined for who can deploy migrations vs. approve them vs. administer prod secrets — that is left to the deploying customer. |
| A.5.4 | Management responsibilities | Yes | Gap | No documented management commitment statement. Addressed in [ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies) Information Security Policy. |
| A.5.5 | Contact with authorities | Yes | Not Started | Self-hosted product — each customer/operator is responsible for their own regulator contacts. No ServiceOps-side procedure documented. |
| A.5.6 | Contact with special interest groups | Yes | Not Started | No documented subscription to CERT/vendor security advisories for the dependency stack (Flask, SQLAlchemy, psycopg, cryptography, etc.). |
| A.5.7 | Threat intelligence | Yes | Gap | No process found for tracking CVEs against `requirements.txt` pinned versions. See gap analysis (dependency scanning). |
| A.5.8 | Information security in project management | Yes | Partially Implemented | CLAUDE.md mandates production-grade standard and security-first prioritization for changes, which is a project-management control, but there's no formal security design-review gate before a feature merges. |
| A.5.9 | Inventory of information and other associated assets | Yes | Partially Implemented | CMDB (Configuration Item) model exists in-product for customers' IT assets (OPERATIONS_MANUAL.md), but ServiceOps has no asset inventory of its *own* build/release assets (container images, Helm chart versions, signing keys). |
| A.5.10 | Acceptable use of information and other associated assets | Yes | Gap | No AUP existed. Drafted in [ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies). |
| A.5.11 | Return of assets | Yes | Not Started | No leaver/offboarding procedure documented for ServiceOps maintainers (e.g., revoking repo/signing access). Product itself supports disabling AD/LDAP users (see A.5.18 tenant note) but that's tenant-level, not ISMS-level. |
| A.5.12 | Classification of information | Yes | Gap | No data classification scheme (e.g., public/internal/confidential/restricted) applied to ticket data, attachments, or audit records. |
| A.5.13 | Labelling of information | Yes | Gap | Follows from A.5.12 — no labelling scheme exists. |
| A.5.14 | Information transfer | Yes | Partially Implemented | TLS is required at the reverse-proxy layer (`deploy/nginx-serviceops.conf.example` listens on 443/ssl; `SESSION_COOKIE_SECURE` defaults true and the app refuses to start with insecure cookies without an explicit opt-out — app.py:4389-4416). No documented policy for email/webhook payload sensitivity. |
| A.5.15 | Access control | Yes | Partially Implemented | Strong tenant-aware RBAC (231 `tenant_id` references in app.py), AD group→team mapping, CCB/approval authority — see Access Control Policy in ISMS_POLICIES.md. No MFA (see A.8.5). |
| A.5.16 | Identity management | Yes | Implemented | Three supported identity sources — local bootstrap admin (no default password, app.py:4164 requires explicit admin_password), AD/LDAP (`serviceops_core/ldap_sync.py`), Keycloak/OIDC. Tenant resolution fails closed per CLAUDE.md. |
| A.5.17 | Authentication information | Yes | Partially Implemented | Passwords hashed with Werkzeug's `generate_password_hash` (PBKDF2-SHA256 by default in current Werkzeug, not bcrypt/Argon2id) — app.py:37,4164. Account lockout after configurable failed attempts (app.py:1802-1803, 5230-5272). No password complexity/rotation policy found in code. |
| A.5.18 | Access rights | Yes | Implemented | AD group→team mapping with priority/conflict resolution, disabled/removed-user handling mandated in CLAUDE.md and reflected in `ldap_sync.py`; visibility vs. mutation permission separation enforced per ITIL record model. |
| A.5.19 | Information security in supplier relationships | Yes | Gap | No Supplier/Vendor Security Policy existed. Drafted in [ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies). Integrations (webhooks, Teams, SIEM, monitoring ingestion, NetBox/RT import) are customer-configured adapters; no vendor risk assessment process for the ServiceOps dependency supply chain itself. |
| A.5.20 | Addressing security within supplier agreements | Yes | Not Started | No standard security addendum/DPA template for customers integrating third-party systems via webhooks. |
| A.5.21 | Managing security in the ICT supply chain | Yes | Gap | `requirements.txt` pins versions but no SBOM generation, no dependency-vulnerability scanning (no Trivy/Snyk/Dependabot config found in repo — confirmed absent by search). |
| A.5.22 | Monitoring, review and change management of supplier services | Yes | Not Started | No process for reviewing third-party services (ClamAV daemon, LDAP/Keycloak servers, SMTP, monitoring ingestion) customers point at ServiceOps. |
| A.5.23 | Information security for use of cloud services | Yes | Partially Implemented | Product is deployment-agnostic (Docker/K8s); DEPLOYMENT.md covers self-hosted and external-managed-DB models with guidance to rely on provider snapshots/PITR for externally managed Postgres, but no explicit cloud-shared-responsibility statement. |
| A.5.24 | Information security incident management planning | Yes | Gap | No incident management policy/runbook existed at ISMS level (product has ITIL incident *tickets*, which is a different thing — this is about security incidents in ServiceOps itself). Drafted in [ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies). |
| A.5.25 | Assessment and decision on information security events | Yes | Gap | Follows from A.5.24 — no triage/severity criteria documented for security events specifically (vs. ITSM incident severity, which exists). |
| A.5.26 | Response to information security incidents | Yes | Gap | Same as above. |
| A.5.27 | Learning from information security incidents | Yes | Gap | ITIL Problem/PIR process exists for service incidents; no equivalent post-incident-review requirement tied to security events. |
| A.5.28 | Collection of evidence | Yes | Partially Implemented | `Audit`/`AuditIntegrityKey` models exist (app.py:312-352) suggesting tamper-evidence intent, but see GAP_ANALYSIS for verification of hash-chaining actually being enforced on every write path. |
| A.5.29 | Information security during disruption | Yes | Partially Implemented | Backup/PITR procedures documented (DEPLOYMENT.md), recovery verification tool exists (`tools/recovery_verify.py`), but no defined RTO/RPO targets or tested BC/DR plan. |
| A.5.30 | ICT readiness for business continuity | Yes | Gap | No BC/DR test evidence found (no documented DR drill, failover test, or RTO/RPO measurement). |
| A.5.31 | Legal, statutory, regulatory and contractual requirements | Yes | Partially Implemented | GDPR-relevant work is understood to be in progress by a concurrent agent per task brief; not independently verified here. No consolidated legal/regulatory register found. |
| A.5.32 | Intellectual property rights | Yes | Not Started | No license-compliance scan of dependencies documented. |
| A.5.33 | Protection of records | Yes | Partially Implemented | Audit trail and backup manifests (SHA-256, owner-only permissions per DEPLOYMENT.md) support record protection; no defined records-retention schedule beyond the `AuditRetentionPolicy` model (app.py:352) — unclear if retention periods are actually configured/enforced anywhere.|
| A.5.34 | Privacy and protection of PII | Yes | Partially Implemented | Multi-tenant isolation is strongly enforced (CLAUDE.md fail-closed tenant rules); GDPR-specific work (subject access/export/erasure) is reportedly being handled by a concurrent workstream — not verified in this review. |
| A.5.35 | Independent review of information security | Yes | Gap | No evidence of an external/independent security audit or penetration test (no `security.txt`, pentest report, or third-party audit artifact found in the repo). |
| A.5.36 | Compliance with policies, rules and standards for information security | Yes | Gap | No policy set existed to check compliance against until this review; no compliance-review cadence defined. |
| A.5.37 | Documented operating procedures | Yes | Implemented | DEPLOYMENT.md, OPERATIONS_MANUAL.md, and GOVERNANCE.md are detailed and current; backup/restore/upgrade/rollback runbooks exist. |

<a id="section-iso27001-soa--a6-people-controls-8"></a>
### A.6 People controls (8)

| # | Control | Applicable | Status | Evidence / Notes |
|---|---|---|---|---|
| A.6.1 | Screening | Partially — self-hosted product means this applies to ServiceOps' own contributors, not customer staff | Not Started | No documented screening process for maintainers/contributors. |
| A.6.2 | Terms and conditions of employment | Applies to ServiceOps org, not the product | Not Started | Out of scope for this codebase-grounded review; note for org-level ISMS owner. |
| A.6.3 | Information security awareness, education and training | Yes | Gap | No training program or security-awareness material referenced anywhere in docs. |
| A.6.4 | Disciplinary process | Applies to ServiceOps org | Not Started | Not addressed by product; organizational HR matter. |
| A.6.5 | Responsibilities after termination or change of employment | Yes | Not Started | No offboarding checklist found (credential revocation, repo access, signing keys). |
| A.6.6 | Confidentiality or non-disclosure agreements | Applies to ServiceOps org/contractors | Not Started | No NDA template referenced in repo docs. |
| A.6.7 | Remote working | Yes (product enables customers' remote/hybrid IT teams) | N/A for the product itself; org-level for ServiceOps | ServiceOps is remote-friendly by design (PWA-first, responsive) but this control is about ServiceOps' own workforce practices, not a product feature. |
| A.6.8 | Information security event reporting | Yes | Partially Implemented | Product has an audit log and incident-ticket workflow customers can use to report *service* issues; no dedicated "report a security concern about ServiceOps itself" channel (no security.txt / disclosure email found). |

<a id="section-iso27001-soa--a7-physical-controls-14"></a>
### A.7 Physical controls (14)

Self-hosted, customer-deployed product — ServiceOps Inc. does not operate
customer-facing data centers. Most physical controls are the deploying
customer's responsibility, delegated via deployment documentation rather than
implemented by ServiceOps directly. Marked Applicable only where the product
gives operators guidance/tooling; otherwise N/A to the ServiceOps product
scope with the responsibility noted.

| # | Control | Applicable | Status | Evidence / Notes |
|---|---|---|---|---|
| A.7.1 | Physical security perimeters | Customer responsibility | N/A (product scope) | Delegated to deploying organization; not addressed by DEPLOYMENT.md. |
| A.7.2 | Physical entry | Customer responsibility | N/A | Same as above. |
| A.7.3 | Securing offices, rooms and facilities | Customer responsibility | N/A | Same as above. |
| A.7.4 | Physical security monitoring | Customer responsibility | N/A | Same as above. |
| A.7.5 | Protecting against physical and environmental threats | Customer responsibility | N/A | Same as above. |
| A.7.6 | Working in secure areas | Customer responsibility | N/A | Same as above. |
| A.7.7 | Clear desk and clear screen | Customer responsibility | N/A | Product enforces session timeout (`PERMANENT_SESSION_LIFETIME`, app.py:4392-4393) which materially supports this control even though it's a "physical" control category — noted as Partially Implemented via technical compensating control. |
| A.7.8 | Equipment siting and protection | Customer responsibility | N/A | Delegated. |
| A.7.9 | Security of assets off-premises | Customer responsibility | N/A | Delegated. |
| A.7.10 | Storage media | Yes (backup media) | Partially Implemented | Backup dumps written with owner-only permissions and SHA-256 manifests (DEPLOYMENT.md); no documented secure-erase procedure for retired media/volumes. |
| A.7.11 | Supporting utilities | Customer responsibility | N/A | Delegated (power, cooling, etc. for self-hosted infra). |
| A.7.12 | Cabling security | Customer responsibility | N/A | Delegated. |
| A.7.13 | Equipment maintenance | Customer responsibility | N/A | Delegated. |
| A.7.14 | Secure disposal or re-use of equipment | Customer responsibility | N/A | No product guidance found for secure disposal of DB volumes/backup media at decommission. |

<a id="section-iso27001-soa--a8-technological-controls-34"></a>
### A.8 Technological controls (34)

| # | Control | Applicable | Status | Evidence / Notes |
|---|---|---|---|---|
| A.8.1 | User endpoint devices | Customer responsibility (product is a web app) | N/A | ServiceOps is browser/PWA-delivered; endpoint hardening is the customer's concern. |
| A.8.2 | Privileged access rights | Yes | Implemented | Admin role, CCB eligibility, approval authority, team-manager authority all modeled distinctly; tenant-scoped admin (no cross-tenant superuser path implied by fail-closed tenant rule). |
| A.8.3 | Information access restriction | Yes | Implemented | Tenant isolation enforced across queries/writes/relationships/background jobs/webhooks per CLAUDE.md; visibility vs. mutation permission separation for ITIL records. |
| A.8.4 | Access to source code | Yes | Partially Implemented | ServiceOps repo is public on GitHub per README note in serviceops-notes (internal docs deliberately excluded); no documented branch-protection/code-review-required policy found in this review. |
| A.8.5 | Secure authentication | Yes | Partially Implemented | CSRF protection (app.py:4517-4529), session cookies HttpOnly/SameSite=Lax/Secure-by-default, account lockout after N failed attempts. **No MFA/TOTP found anywhere in app.py** — significant gap for admin and privileged accounts. |
| A.8.6 | Capacity management | Yes | Not Started | No capacity-planning documentation or autoscaling guidance found beyond generic K8s deployment. |
| A.8.7 | Protection against malware | Yes | Partially Implemented | Optional ClamAV integration for attachment scanning (app.py:1805-1807, 2609-2648) — **disabled by default** (`CLAMAV_ENABLED` default `false`); blocked scans are audited (`attach-blocked`). Host/endpoint malware protection is customer responsibility. |
| A.8.8 | Management of technical vulnerabilities | Yes | Gap | No dependency/CVE scanning found (no Trivy/Snyk/Dependabot/pip-audit config). Pinned `requirements.txt` with no automated update process. |
| A.8.9 | Configuration management | Yes | Implemented | Config is Git-backed and declarative per CLAUDE.md directive #7; Helm values, compose env vars, and `.env`-driven secrets keep runtime config out of ad hoc DB edits where practical. |
| A.8.10 | Information deletion | Yes | Partially Implemented | CLAUDE.md requires tombstoning legacy identities rather than hard-delete to preserve audit history — good for integrity, but this cuts against GDPR erasure requirements unless a separate purge-after-retention mechanism exists (not verified here; flagged for the concurrent GDPR workstream). |
| A.8.11 | Data masking | Yes | Gap | No secret-redaction utility found in app.py or serviceops_core (searched for "redact"/"mask_secret" — no matches). Secrets like LDAP bind password, webhook secrets appear encrypted at rest (Fernet, app.py:1847-1867) but log-output redaction was not found. |
| A.8.12 | Data leakage prevention | Yes | Gap | No DLP tooling or egress-filtering logic found; CSP (`default-src 'self'` etc., app.py:5208-5219) mitigates browser-side exfiltration somewhat but that's not DLP. |
| A.8.13 | Information backup | Yes | Implemented | `./serviceops backup` produces SHA-256-manifested backups with owner-only permissions; PITR supported for bundled DB; `tools/recovery_verify.py` validates recovery sets; external-DB deployments delegate to provider snapshots/PITR by design (DEPLOYMENT.md). |
| A.8.14 | Redundancy of information processing facilities | Yes | Not Started | Helm chart deploys app/worker/postgresql; no documented HA/multi-replica Postgres or multi-AZ guidance found. |
| A.8.15 | Logging | Yes | Partially Implemented | `Audit` model logs security-relevant events (login_failed, attach-blocked, etc.); optional SIEM streaming (`AUDIT_STREAM_ENABLED`, app.py:1801, 2418-2420) — disabled by default. No structured application/error-log-to-SIEM pipeline found beyond the audit-event stream. |
| A.8.16 | Monitoring activities | Yes | Partially Implemented | "Monitoring ingestion" is a configurable admin integration (customer's external monitoring pushes into ServiceOps), but there's no self-monitoring (metrics/alerting on ServiceOps' own health, e.g., Prometheus endpoint) found in this review. |
| A.8.17 | Clock synchronization | Yes | Unverified | No explicit NTP/clock-sync guidance in DEPLOYMENT.md; relevant because audit-log integrity partly depends on trustworthy timestamps. |
| A.8.18 | Use of privileged utility programs | Yes | Partially Implemented | `tools/production_cleanup.py` defaults to dry-run and requires `--apply` plus a prior backup per its own docstring — a reasonable safeguard, but no enforced approval workflow (e.g., requiring a change ticket) around privileged maintenance scripts. |
| A.8.19 | Installation of software on operational systems | Yes | Implemented | Containerized deployment (Docker/Helm) with pinned base images and migration jobs; installer (`installer/app.py`) manages controlled install/upgrade flow rather than ad hoc package installs. |
| A.8.20 | Networks security | Yes | Partially Implemented | SSRF guard blocks loopback/link-local/multicast/reserved addresses for outbound webhooks/exports (app.py:1906-1944, `netbox_sync.py:367`) — good. No network-segmentation guidance beyond generic K8s NetworkPolicy absence (not found in charts/). |
| A.8.21 | Security of network services | Yes | Partially Implemented | LDAP StartTLS supported and defaulted true in compose (`LDAP_START_TLS: true`); TLS termination expected at reverse proxy (nginx example config on 443/ssl); app itself refuses insecure session cookies without explicit override. |
| A.8.22 | Segregation of networks | Customer/deployment responsibility | Partially Implemented | Helm chart separates app/worker/postgresql as distinct Deployments (segmentable via K8s NetworkPolicy) but no NetworkPolicy manifests found in `charts/serviceops/templates/`. |
| A.8.23 | Web filtering | Customer responsibility | N/A | Not a product function. |
| A.8.24 | Use of cryptography | Yes | Partially Implemented | Fernet symmetric encryption for stored secrets (`SETTINGS_ENCRYPTION_KEY`, app.py:1847-1867); PBKDF2 password hashing (not the strongest available — Argon2id preferred by OWASP); TLS delegated to reverse proxy rather than terminated in-app. No documented key-rotation procedure for `SETTINGS_ENCRYPTION_KEY` or `SECRET_KEY`. |
| A.8.25 | Secure development life cycle | Yes | Partially Implemented | CLAUDE.md mandates production-grade verification, reversible migrations, and security-first prioritization — strong process intent — but no formal SDLC gate (e.g., mandatory security review checklist, SAST in CI) found. |
| A.8.26 | Application security requirements | Yes | Implemented (documented) | CLAUDE.md explicitly enumerates required controls (CSRF, session lifecycle, CSP, tenant isolation, audit history, SSRF-resistant webhooks, attachment scanning, rate limiting, secret redaction, least-privilege containers) as binding requirements — most verified present in this review; secret redaction and general (non-API) rate limiting are the notable exceptions (see A.8.11, A.8.16, and Gap Analysis on rate limiting). |
| A.8.27 | Secure system architecture and engineering principles | Yes | Implemented | Least-privilege containers (`USER app` in Dockerfile; `runAsNonRoot`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `capabilities: drop: [ALL]` across deployment.yaml/migration-job.yaml/worker.yaml/postgresql.yaml). Fail-closed tenant resolution. |
| A.8.28 | Secure coding | Yes | Partially Implemented | Parameterized ORM queries (SQLAlchemy) reduce SQLi risk by default; CSRF/CSP/output-escaping patterns present; no SAST/linting-for-security step confirmed in CI (no CI config reviewed in this pass). |
| A.8.29 | Security testing in development and acceptance | Yes | Gap | `tests/` directory exists but this review did not find dedicated security test suites (authz-bypass tests, tenant-isolation fuzzing, CSRF-bypass tests). Flagged for verification, not confirmed absent — see Gap Analysis "Unverified" note. |
| A.8.30 | Outsourced development | Yes | N/A | No evidence of outsourced development; maintained in-house per CLAUDE.md collaboration model. |
| A.8.31 | Separation of development, test and production environments | Yes | Partially Implemented | `Dockerfile.test`, `compose.external-db.yaml` suggest separate test tooling; migration versioning (Alembic) supports environment promotion; no explicit documented environment-separation policy (e.g., prod secrets never present in dev). |
| A.8.32 | Change management | Yes | Implemented | Product itself *is* a change-management system (CHG/CTASK/CCB workflow) and CLAUDE.md applies equivalent discipline to ServiceOps' own releases (versioned, reversible migrations; semantic-versioned, tagged releases). |
| A.8.33 | Test information | Yes | Partially Implemented | Production-only policy explicitly forbids demo data, seeded tickets, and shared/test credentials in production (CLAUDE.md "Production-only policy") — strong control against test-data leakage into prod. No documented masking of production data when used in test/staging. |
| A.8.34 | Protection of information systems during audit testing | Yes | Not Started | No documented procedure for safely running penetration tests/audits against a production ServiceOps instance (e.g., pre-agreed rate-limit exemptions, read-only audit accounts). |

<a id="section-iso27001-soa--summary-counts"></a>
### Summary counts

See top-level report for the rolled-up count by status across all four
Annex A themes (Organizational 37, People 8, Physical 14, Technological 34 —
93 controls total).

---

<a id="section-iso27001-gap_analysis"></a>

## ISO/IEC 27001:2022 Gap Analysis — ServiceOps

<a id="section-iso27001-gap_analysis--isoiec-270012022-gap-analysis--serviceops"></a>

Companion to [SOA.md](COMPLIANCE.md#section-iso27001-soa). Every control marked Gap or Partially Implemented
there gets a concrete remediation item here. Items are grouped by priority
based on exploitability and blast radius for a multi-tenant ITSM platform
handling customers' incident/change/CMDB data.

Remediation items are written to be picked up directly by an engineer or the
ITIL/GDPR remediation agent — each names the file(s)/model(s) involved and a
concrete acceptance check, not just a restated goal.

<a id="section-iso27001-gap_analysis--p0--highest-priority-authtenant-boundarycrypto-risk"></a>
### P0 — highest priority (auth/tenant-boundary/crypto risk)

<a id="section-iso27001-gap_analysis--1-no-mfa-for-privileged-accounts-a85"></a>
#### 1. No MFA for privileged accounts (A.8.5)
**Gap.** No TOTP/MFA code path exists in app.py. Admin and CCB accounts are
protected only by password + lockout (5 attempts / 15 min, app.py:1802-1803).
A single leaked admin password (e.g., phished from a customer's AD) is a full
tenant-scope compromise.
**Remediation:** Add optional TOTP MFA (e.g., `pyotp`) enforced for the
`admin` role and any user with CCB/approval authority. New `User.mfa_secret`
column (encrypted via the existing `settings_cipher()`/Fernet pattern used
for other secrets, app.py:1847), a `/settings/mfa` enrollment flow, and a
`mfa_verified` check inserted into the login flow around app.py:5230-5272
before session issuance. Make it mandatory-by-role via a new
`REQUIRE_MFA_FOR_ADMIN` setting analogous to `LOGIN_MAX_ATTEMPTS`.

<a id="section-iso27001-gap_analysis--2-general-web-rate-limiting-is-absent-only-the-rest-api-has-it-a816-a515-partial"></a>
#### 2. General web rate limiting is absent; only the REST API has it (A.8.16, A.5.15 partial)
**Partially Implemented.** `enforce_api_rate_limit` (app.py:1631) throttles
REST API clients per `API_RATE_LIMIT_PER_MINUTE`, but there is no equivalent
guard on the interactive web login form, password-reset endpoint, or other
unauthenticated POST routes — only account lockout after failed logins,
which doesn't stop distributed low-and-slow credential stuffing across many
usernames.
**Remediation:** Add an IP+route-scoped rate limiter (reuse the existing
`ApiRateLimit`-style windowed-counter pattern, app.py:432, generalized to a
`route_rate_limit(key, limit, window_seconds)` helper) applied to
`/login`, `/forgot-password` (if present), and any other unauthenticated
POST endpoint. Acceptance check: a scripted test posting >N requests/min from
one IP to `/login` receives 429 with `Retry-After`, mirroring the existing
`g.rate_limit_retry_after` header pattern (app.py:5202-5203).

<a id="section-iso27001-gap_analysis--3-no-secretlog-redaction-utility-a811"></a>
#### 3. No secret/log redaction utility (A.8.11)
**Gap.** Grepping app.py and serviceops_core for "redact"/"mask_secret"
returns no matches, despite CLAUDE.md listing "secret redaction" as a
required control. Webhook secrets, LDAP bind passwords, and API tokens are
Fernet-encrypted at rest (good) but nothing was found preventing them from
landing in plaintext in application logs, error tracebacks, or the
`AuditIntegrityKey`/`Audit` tables if a code path logs a request body or
exception containing one.
**Remediation:** Add a `redact_secrets(text: str) -> str` helper in
`serviceops_core/security.py` that masks known secret-bearing field names
(`*_password`, `*_secret`, `secret_encrypted`, `Authorization` header
values) and wire it into the app's logging formatter and into `audit()`
call sites that log request/response payloads. Acceptance check: a unit
test that logs a dict containing `ldap_bind_password` and asserts the
rendered log line contains no substring of the real value.

<a id="section-iso27001-gap_analysis--4-password-hashing-uses-pbkdf2-werkzeug-default-not-argon2id-a824-a517"></a>
#### 4. Password hashing uses PBKDF2 (Werkzeug default), not Argon2id (A.8.24, A.5.17)
**Partially Implemented.** `generate_password_hash` (app.py:37, used at
4164/4279/5330/6921) uses Werkzeug's default scheme, which is PBKDF2-SHA256
unless explicitly configured otherwise — weaker against GPU/ASIC cracking
than Argon2id, OWASP's current recommendation, though not itself a critical
flaw given lockout is in place.
**Remediation:** Switch to `generate_password_hash(pw, method="scrypt")` or
adopt `argon2-cffi` via a small wrapper in `serviceops_core/security.py`,
with a migration path that rehashes on next successful login (check hash
prefix, upgrade in place) rather than forcing a mass password reset.
Acceptance check: new users get Argon2id/scrypt hashes; existing PBKDF2
hashes still verify and get transparently upgraded on next login.

<a id="section-iso27001-gap_analysis--5-dependencycve-scanning-absent-a88-a521"></a>
#### 5. Dependency/CVE scanning absent (A.8.8, A.5.21)
**Gap.** No Trivy, Snyk, Dependabot, or `pip-audit` configuration found
anywhere in the repo. `requirements.txt` is pinned but nothing tracks known
vulnerabilities in those pins over time — a real risk for a Flask+SQLAlchemy
+cryptography stack with a steady CVE cadence.
**Remediation:** Add a CI job (or scheduled job if no CI is in scope for
this review) running `pip-audit -r requirements.txt` and `trivy image` against
the built container, failing the build on High/Critical findings with a
documented exception process. Generate and store an SBOM (`cyclonedx-py`) per
release, referenced from `docs/BACKLOG.md` per the release-tagging policy in
CLAUDE.md.

<a id="section-iso27001-gap_analysis--p1--high-priority-integrity-incident-response-monitoring"></a>
### P1 — high priority (integrity, incident response, monitoring)

<a id="section-iso27001-gap_analysis--6-audit-log-tamper-evidence-not-verified-end-to-end-a528"></a>
#### 6. Audit-log tamper-evidence not verified end-to-end (A.5.28)
**Partially Implemented.** `Audit` and `AuditIntegrityKey` models exist
(app.py:312-352), implying a hash-chaining/HMAC design, but this review did
not trace every write path to confirm the chain is actually computed and
verified (vs. the models merely existing as schema). Given ITIL change
records rely on audit trail integrity for CCB legal defensibility, this needs
positive verification, not assumption.
**Remediation:** Have an engineer trace `Audit` row creation (search for all
`Audit(` construction sites) and confirm each includes a chained hash/HMAC
using `AuditIntegrityKey`. Add a migration-level test that inserts N audit
rows, tampers with one, and asserts a verification routine detects it. If no
verification routine exists yet, write one (`verify_audit_chain(tenant_id)`)
and schedule it as a periodic integrity check.

<a id="section-iso27001-gap_analysis--7-no-security-incident-management-policyrunbook-a524a527"></a>
#### 7. No security incident management policy/runbook (A.5.24–A.5.27)
**Gap.** ITIL Incident/Problem workflows exist for *service* incidents but
nothing defines how ServiceOps itself handles a *security* incident (e.g., a
reported vulnerability, a suspected tenant-isolation breach, a leaked
credential).
**Remediation:** Adopt the Incident Management Policy drafted in
[ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies); add a `security.txt`/`SECURITY.md` at the ServiceOps repo
root (or its equivalent internal location) with a disclosure contact and
target response times, referenced from GOVERNANCE.md.

<a id="section-iso27001-gap_analysis--8-no-independent-security-review-or-pentest-evidence-a535"></a>
#### 8. No independent security review or pentest evidence (A.5.35)
**Gap.** No pentest report, third-party audit artifact, or `security.txt`
found. For a multi-tenant platform holding customer ITSM/CMDB data, this is
a material gap for enterprise customers' own compliance needs.
**Remediation:** Commission (or schedule) an annual third-party penetration
test scoped to tenant-isolation bypass, auth bypass, and SSRF/webhook
handling specifically (the areas CLAUDE.md flags as hardened, which are also
the highest-value targets). Track findings and remediation in
`docs/BACKLOG.md` with severity and closure evidence, per this repo's
existing evidence-tracking convention.

<a id="section-iso27001-gap_analysis--9-no-self-monitoring--metrics-endpoint-found-a816"></a>
#### 9. No self-monitoring / metrics endpoint found (A.8.16)
**Partially Implemented.** The product ingests *customers'* monitoring
events (admin-configurable "Monitoring ingestion" integration) but this
review found no `/metrics` (Prometheus) or health-telemetry endpoint for
ServiceOps' own operational health beyond basic liveness.
**Remediation:** Add a `/metrics` endpoint (prometheus_client) exposing
request latency, error rate, rate-limit rejections, and failed-login counts;
document scrape config in DEPLOYMENT.md; wire failed-login-count and
attach-blocked counters as alertable signals (these are already audited
events — surface them as metrics too).

<a id="section-iso27001-gap_analysis--10-no-documented-bcdr-test-evidence-or-rtorpo-targets-a529-a530"></a>
#### 10. No documented BC/DR test evidence or RTO/RPO targets (A.5.29, A.5.30)
**Partially Implemented.** Backup/PITR mechanics are solid and documented
(DEPLOYMENT.md, `tools/recovery_verify.py`), but no RTO/RPO targets are
defined and no drill/failover test is recorded.
**Remediation:** Define RTO/RPO in the Business Continuity/Backup Policy
(drafted in [ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies)) and run (and record) at least one annual
restore drill using `tools/recovery_verify.py` against a non-production
environment, logging the measured recovery time against the target.

<a id="section-iso27001-gap_analysis--p2--medium-priority-hardening-process-maturity"></a>
### P2 — medium priority (hardening, process maturity)

<a id="section-iso27001-gap_analysis--11-no-kubernetes-networkpolicy-manifests-a820-a822"></a>
#### 11. No Kubernetes NetworkPolicy manifests (A.8.20, A.8.22)
**Partially Implemented.** `charts/serviceops/templates/` has strong pod
`securityContext` hardening but no `NetworkPolicy` resource restricting
pod-to-pod traffic (e.g., worker should not need to reach the internet
directly; postgresql should only accept traffic from app/worker/migration
pods).
**Remediation:** Add a `networkpolicy.yaml` template to the Helm chart
restricting ingress to `postgresql` to the app/worker/migration-job pod
selectors, and restricting egress from those pods per the SSRF-guard intent
already enforced at the application layer (app.py:1906-1944) — defense in
depth.

<a id="section-iso27001-gap_analysis--12-no-data-classificationlabelling-scheme-a512-a513"></a>
#### 12. No data classification/labelling scheme (A.5.12, A.5.13)
**Gap.** Ticket data, attachments, and CMDB records have no classification
tagging (e.g., confidential customer PII vs. internal operational data),
which matters for the GDPR workstream's export/erasure scoping too.
**Remediation:** Define a 3–4 tier classification scheme in a new
`docs/DATA_CLASSIFICATION.md` (or fold into ISMS_POLICIES.md's Access
Control Policy) and note which existing tables/fields fall into which tier,
as a reference for both this ISMS work and the concurrent GDPR work — but do
not implement enforcement code here per this task's read-only-on-code scope.

<a id="section-iso27001-gap_analysis--13-no-branch-protection--mandatory-code-review-policy-documented-a84-a825"></a>
#### 13. No branch protection / mandatory code review policy documented (A.8.4, A.8.25)
**Partially Implemented.** CLAUDE.md mandates a high production-grade bar for
changes but this review found no documented requirement for review-before-
merge or protected branches.
**Remediation:** Document (in GOVERNANCE.md or a new SDLC section) a
required-review policy for the `main` branch and confirm it's configured in
GitHub branch protection settings (outside this repo's tooling, but the
requirement should be traceable from here).

<a id="section-iso27001-gap_analysis--14-key-rotation-for-settings_encryption_keysecret_key-undocumented-a824"></a>
#### 14. Key rotation for `SETTINGS_ENCRYPTION_KEY`/`SECRET_KEY` undocumented (A.8.24)
**Partially Implemented.** Fernet encryption is used correctly for
settings/secrets at rest, but no rotation procedure is documented — if
`SETTINGS_ENCRYPTION_KEY` is ever compromised or rotated, there's no
described re-encryption path for existing `secret_encrypted` columns.
**Remediation:** Document (DEPLOYMENT.md) and, longer-term, implement a
`serviceops rotate-encryption-key` maintenance command that decrypts under
the old key and re-encrypts under a new one across all
`secret_encrypted`-bearing tables (`AuditIntegrityKey`, integration
credentials, etc.) inside a single transaction, with a dry-run mode
consistent with `tools/production_cleanup.py`'s existing dry-run-by-default
convention.

<a id="section-iso27001-gap_analysis--15-unverified-dedicated-securityauthz-test-coverage-a829"></a>
#### 15. Unverified: dedicated security/authz test coverage (A.8.29)
**Unverified — treat as Gap until confirmed.** `tests/` exists but this
review did not enumerate it for tenant-isolation-bypass or CSRF-bypass test
cases specifically.
**Remediation:** An engineer should grep `tests/` for tenant-isolation and
CSRF test coverage; if absent, add tests asserting that a user from tenant A
cannot read/write tenant B's tickets/CMDB/audit records via API, UI routes,
and background jobs (the three surfaces CLAUDE.md calls out by name).

<a id="section-iso27001-gap_analysis--p3--lower-priority--organizational"></a>
### P3 — lower priority / organizational

<a id="section-iso27001-gap_analysis--16-no-named-isms-owner--security-roles-a52-a51-a54"></a>
#### 16. No named ISMS owner / security roles (A.5.2, A.5.1, A.5.4)
**Gap.** Addressed procedurally by adopting [ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies) and assigning
an accountable owner in GOVERNANCE.md's decision log — no code change
needed.

<a id="section-iso27001-gap_analysis--17-no-asset-inventory-of-serviceops-own-build-artifacts-a59"></a>
#### 17. No asset inventory of ServiceOps' own build artifacts (A.5.9)
**Partially Implemented.** Recommend a lightweight `docs/ASSET_INVENTORY.md`
listing container images, Helm chart versions, signing keys, and where they
live, kept in sync with the existing release-tagging policy in CLAUDE.md.

<a id="section-iso27001-gap_analysis--18-no-vendorsupplier-security-review-process-a519a522"></a>
#### 18. No vendor/supplier security review process (A.5.19–A.5.22)
**Gap.** Addressed by the Supplier/Vendor Security Policy in
[ISMS_POLICIES.md](COMPLIANCE.md#section-iso27001-isms_policies); no code change required, but customers integrating
webhooks/Teams/SIEM should be pointed at a documented minimum-security
baseline for those endpoints.

<a id="section-iso27001-gap_analysis--19-no-security-awareness-training-program-a63"></a>
#### 19. No security-awareness training program (A.6.3)
**Gap.** Organizational, not code — track as a backlog item for the ISMS
owner once named.

<a id="section-iso27001-gap_analysis--20-storage-media-secure-disposal-undocumented-a710-a714"></a>
#### 20. Storage-media secure disposal undocumented (A.7.10, A.7.14)
**Gap.** Add a short section to DEPLOYMENT.md on secure erasure of DB
volumes/backup media at decommission (e.g., `shred`/cloud-provider
secure-delete guidance), since backups already carry sensitive customer
data with owner-only permissions.

<a id="section-iso27001-gap_analysis--how-to-use-this-with-the-concurrent-itilgdpr-workstream"></a>
### How to use this with the concurrent ITIL/GDPR workstream

Items 3 (secret redaction), 6 (audit chain verification), 12 (data
classification touching GDPR scoping), and 10 (BC/DR) overlap with what a
GDPR-focused workstream would also need. Recommend the ITIL/GDPR agent treat
this gap analysis as input rather than duplicating discovery — coordinate via
`docs/BACKLOG.md` so both workstreams don't independently re-derive the same
audit-log/redaction gaps.
