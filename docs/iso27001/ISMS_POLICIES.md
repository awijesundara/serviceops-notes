# ServiceOps ISMS Core Policies (draft, ISO/IEC 27001:2022-aligned)

Status: **Draft — pending owner sign-off.** These are first drafts scoped to
what ServiceOps actually is and how it's actually deployed: a self-hosted
ITSM platform (Flask/FastAPI + PostgreSQL, Docker/Kubernetes, AD/LDAP +
Keycloak/OIDC, multi-tenant), maintained by a small team per CLAUDE.md's
collaboration model. They deliberately avoid generic boilerplate that
doesn't fit that reality (e.g., no office-badge-access language, no SaaS
shared-responsibility clauses beyond what the deployment model needs).

Each policy names an owner placeholder, a review cadence, and references the
concrete mechanisms already in the codebase where they exist, plus the gap
they don't yet cover (cross-referenced to `GAP_ANALYSIS.md`).

---

## 1. Information Security Policy

**Owner:** [ISMS owner — not yet named; see GAP_ANALYSIS.md item 16]
**Review cadence:** Annually, or after any material architecture change.

### Purpose
Establish ServiceOps' commitment to protecting the confidentiality,
integrity, and availability of information it processes — primarily
customers' ITSM data (incidents, changes, CMDB, attachments, audit history)
across a multi-tenant deployment.

### Scope
Applies to the ServiceOps codebase, its Docker/Helm deployment artifacts,
and the engineering practices used to build and release it. Does not
prescribe controls for customers' own infrastructure beyond what
DEPLOYMENT.md documents as required/recommended configuration.

### Policy statements
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
5. Known gaps (see `GAP_ANALYSIS.md`) are tracked to closure, not silently
   accepted — MFA, dependency scanning, and secret redaction are the current
   highest-priority open items.
6. Management (the ISMS owner, once named) reviews this policy set and the
   SOA annually and after any significant incident.

---

## 2. Access Control Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually.

### Identity sources
ServiceOps supports exactly three authentication patterns (CLAUDE.md):
local bootstrap administrator (no known default password — the installer
requires an explicit admin password, app.py:4164), Active Directory/LDAP,
and Keycloak/OIDC. No other authentication mechanism may be added without
updating this policy.

### Authorization model
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

### Authentication strength
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

### Access review
Access rights (AD group mappings, team membership, CCB eligibility,
approval authority) should be reviewed by the deploying customer at least
quarterly; ServiceOps' admin screens are the system of record for this
review (per CLAUDE.md's configurability requirements).

---

## 3. Incident Management Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually, or after any actual security incident.

This policy covers **security incidents affecting ServiceOps itself**
(e.g., a suspected tenant-isolation bypass, a leaked credential, a
vulnerability report) — distinct from the product's own ITIL Incident (INC)
ticket type, which handles customers' *service* incidents and is documented
in `docs/ITIL_TICKET_HIERARCHY.md`.

### Reporting
A security concern about ServiceOps should be reportable through a clearly
published channel. **Currently missing** — GAP_ANALYSIS.md item 7
recommends adding a `SECURITY.md`/`security.txt` with a disclosure contact
and target acknowledgement time (recommend 3 business days).

### Triage and severity
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

### Response
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

### Post-incident review
Every Critical/High security incident gets a written post-incident review
(mirroring the product's own PIR concept for changes) covering root cause,
detection gap (could the `Audit` log / SIEM stream have caught it sooner —
see GAP_ANALYSIS.md item 9), and the specific control added to prevent
recurrence.

---

## 4. Business Continuity / Backup Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually, plus after every DR drill.

### Backup mechanism
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

### Targets
**RTO/RPO are not currently defined** (GAP_ANALYSIS.md item 10). Until
formal targets are set by the ISMS owner, the working assumption based on
documented backup frequency guidance in DEPLOYMENT.md should be made
explicit here once that guidance is reviewed — this policy will be updated
with concrete numbers rather than left as a placeholder past the next
review cycle.

### Testing
At least one restore drill per year, executed against a non-production
environment using `tools/recovery_verify.py`, with the measured time-to-
recover logged against the (once defined) RTO target. Results recorded in
`docs/BACKLOG.md`.

### Retention
Backup retention periods are not currently standardized in documentation
(distinct from the in-product `AuditRetentionPolicy` model, app.py:352,
which governs audit-record retention, not backup retention). This policy
recommends the ISMS owner set an explicit backup retention window (e.g.,
30 daily + 12 monthly) consistent with each customer's regulatory
obligations, since ServiceOps itself doesn't operate the storage for
self-hosted customers.

---

## 5. Supplier / Vendor Security Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually, or when a new integration category is added.

### Scope
Two distinct supplier relationships apply to ServiceOps:
1. **ServiceOps' own build-time dependencies** — Python packages
   (`requirements.txt`), base container images, and the Helm chart's own
   dependencies (e.g., bundled PostgreSQL image).
2. **Customer-configured runtime integrations** — LDAP/AD servers,
   Keycloak, SMTP, webhooks, Microsoft Teams, monitoring ingestion, SIEM
   streaming, NetBox/RT import, and the optional ClamAV daemon. These are
   the deploying customer's supplier relationships, not ServiceOps Inc.'s,
   but ServiceOps is responsible for connecting to them safely.

### Build-time dependency controls
- Dependencies are version-pinned in `requirements.txt`.
- **Not yet implemented:** automated CVE/vulnerability scanning and SBOM
  generation (GAP_ANALYSIS.md item 5) — this is the top action item for
  this policy area.

### Runtime integration controls (already implemented, kept as policy baseline)
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

### Contractual baseline
No standard security addendum currently exists for customers wiring
third-party systems into ServiceOps via webhooks (GAP_ANALYSIS.md item 8
inherits into this). The ISMS owner should draft a minimum-security
baseline (e.g., "webhook endpoints must present a valid TLS certificate;
shared secrets must not be reused across integrations") to publish
alongside DEPLOYMENT.md.

---

## 6. Acceptable Use Policy

**Owner:** [ISMS owner]
**Review cadence:** Annually.

Applies to anyone with access to ServiceOps source, build infrastructure,
or a running instance's administrative functions (maintainers and, where
customers grant it, ServiceOps support staff assisting a deployment).

### Rules
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
   `GAP_ANALYSIS.md` — masking of production data used in test is not yet
   formalized; treat production data as sensitive in test contexts in the
   meantime).

### Enforcement
Violations are handled per the ServiceOps organization's own personnel
policy (out of this document's scope — organizational HR matter, not a
product control).

---

## Adoption checklist

- [ ] ISMS owner named and recorded in `docs/GOVERNANCE.md` decision log.
- [ ] Each policy above reviewed and formally approved (sign-off recorded).
- [ ] RTO/RPO targets filled in for the Business Continuity/Backup Policy.
- [ ] `SECURITY.md`/disclosure contact published per Incident Management
      Policy.
- [ ] First annual review date scheduled for all six policies.
