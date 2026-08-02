# Record of Processing Activities (Art. 30 GDPR)

Status: grounded in current `ServiceOps` schema as read from `app.py` (SQLAlchemy
models) on 2026-08-02. Field lists below are the actual columns found, not an
idealized model. Where a technical erasure/export implementation is in
progress concurrently, affected rows are marked **pending technical
verification** — see `DATA_SUBJECT_RIGHTS.md`.

## Deployment model and roles

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
`DPA_TEMPLATE.md` for how the processor relationship is documented when it
does apply.

## Processing activity 1: User/identity administration (accounts, auth, org data)

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
- **Retention**: see `RETENTION_POLICY.md`. Accounts are not hard-deleted by
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

## Processing activity 2: ITSM ticket content (incidents, requests, changes, problems)

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
- **Retention**: see `RETENTION_POLICY.md`. `Ticket.deleted_at` is a
  soft-delete marker, not a physical delete — records persist for ITIL
  history/reporting.
- **Cross-border transfer**: none beyond what applies to Processing activity 1.

## Processing activity 3: Attachments

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
  see `RETENTION_POLICY.md`.
- **Cross-border transfer**: none for local/customer-controlled storage; a
  transfer consideration arises only if the customer configures a
  cloud object-storage backend in another jurisdiction — controller
  responsibility.

## Processing activity 4: Audit/security logging

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
  tension documented in `DATA_SUBJECT_RIGHTS.md` and `DPIA.md`: an
  immutable, hash-chained audit trail is a security control that resists
  erasure by design.
- **Cross-border transfer**: none beyond the controller's own infrastructure
  and any configured downstream SIEM/outbox consumer.

## Processing activity 5: Notifications, SMTP, webhooks, Teams integration

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
- **Retention**: `Notification` rows persist per `RETENTION_POLICY.md`;
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

## Processing activity 6: CMDB / Configuration Items

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

## Summary table

| # | Activity | Primary tables | Legal basis (typical) | Retention | Transfer risk |
|---|---|---|---|---|---|
| 1 | Identity/accounts | User, ExternalIdentity, UserPreference | 6(1)(b)/(f) | Until erasure request + tombstone indefinite | Low (self-hosted); controller's LDAP/OIDC/SMTP choice |
| 2 | Ticket content | Ticket, Comment, TaskNote, ChecklistItem | 6(1)(b)/(f) | Per RETENTION_POLICY.md | Low |
| 3 | Attachments | FileAttachment + file store | 6(1)(b)/(f) | Tied to parent record | Low, unless cloud object storage |
| 4 | Audit log | Audit, AuditRetentionPolicy, AuditIntegrityKey | 6(1)(c)/(f) | ≥7 years, legal-hold extendable | Low, unless SIEM export |
| 5 | Notifications/webhooks/SMTP/Teams | Notification, OutboxEvent, PlatformSetting | 6(1)(b)/(f) | Short (delivery) + Notification retention | **Highest** — controller-chosen third parties |
| 6 | CMDB | ConfigurationItem | 6(1)(f) | Per RETENTION_POLICY.md | Low |

## Gaps / not yet found in source

- No dedicated consent-tracking table was found (expected — most bases here
  are contract/legitimate-interest, not consent, which is normal for
  internal ITSM).
- No explicit sub-processor registry in the codebase; that is a
  documentation artifact (`DPA_TEMPLATE.md`), not a runtime feature.
