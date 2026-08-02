# Statement of Applicability — ISO/IEC 27001:2022 Annex A

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

Every gap/partial item below is expanded with a remediation in `GAP_ANALYSIS.md`.

## A.5 Organizational controls (37)

| # | Control | Applicable | Status | Evidence / Notes |
|---|---|---|---|---|
| A.5.1 | Policies for information security | Yes | Gap | No ISMS policy set existed before this review. Drafted in `ISMS_POLICIES.md`; needs owner sign-off and a review cadence to become "Implemented." |
| A.5.2 | Information security roles and responsibilities | Yes | Gap | No named security officer/role in GOVERNANCE.md. Product has technical roles (admin, team manager, CCB) but no ISMS-level accountable owner defined. |
| A.5.3 | Segregation of duties | Yes | Partially Implemented | App enforces role/team separation for ITIL workflows (CLAUDE.md change-governance rules, CCB approval chain) but no segregation defined for who can deploy migrations vs. approve them vs. administer prod secrets — that is left to the deploying customer. |
| A.5.4 | Management responsibilities | Yes | Gap | No documented management commitment statement. Addressed in `ISMS_POLICIES.md` Information Security Policy. |
| A.5.5 | Contact with authorities | Yes | Not Started | Self-hosted product — each customer/operator is responsible for their own regulator contacts. No ServiceOps-side procedure documented. |
| A.5.6 | Contact with special interest groups | Yes | Not Started | No documented subscription to CERT/vendor security advisories for the dependency stack (Flask, SQLAlchemy, psycopg, cryptography, etc.). |
| A.5.7 | Threat intelligence | Yes | Gap | No process found for tracking CVEs against `requirements.txt` pinned versions. See gap analysis (dependency scanning). |
| A.5.8 | Information security in project management | Yes | Partially Implemented | CLAUDE.md mandates production-grade standard and security-first prioritization for changes, which is a project-management control, but there's no formal security design-review gate before a feature merges. |
| A.5.9 | Inventory of information and other associated assets | Yes | Partially Implemented | CMDB (Configuration Item) model exists in-product for customers' IT assets (OPERATIONS_MANUAL.md), but ServiceOps has no asset inventory of its *own* build/release assets (container images, Helm chart versions, signing keys). |
| A.5.10 | Acceptable use of information and other associated assets | Yes | Gap | No AUP existed. Drafted in `ISMS_POLICIES.md`. |
| A.5.11 | Return of assets | Yes | Not Started | No leaver/offboarding procedure documented for ServiceOps maintainers (e.g., revoking repo/signing access). Product itself supports disabling AD/LDAP users (see A.5.18 tenant note) but that's tenant-level, not ISMS-level. |
| A.5.12 | Classification of information | Yes | Gap | No data classification scheme (e.g., public/internal/confidential/restricted) applied to ticket data, attachments, or audit records. |
| A.5.13 | Labelling of information | Yes | Gap | Follows from A.5.12 — no labelling scheme exists. |
| A.5.14 | Information transfer | Yes | Partially Implemented | TLS is required at the reverse-proxy layer (`deploy/nginx-serviceops.conf.example` listens on 443/ssl; `SESSION_COOKIE_SECURE` defaults true and the app refuses to start with insecure cookies without an explicit opt-out — app.py:4389-4416). No documented policy for email/webhook payload sensitivity. |
| A.5.15 | Access control | Yes | Partially Implemented | Strong tenant-aware RBAC (231 `tenant_id` references in app.py), AD group→team mapping, CCB/approval authority — see Access Control Policy in ISMS_POLICIES.md. No MFA (see A.8.5). |
| A.5.16 | Identity management | Yes | Implemented | Three supported identity sources — local bootstrap admin (no default password, app.py:4164 requires explicit admin_password), AD/LDAP (`serviceops_core/ldap_sync.py`), Keycloak/OIDC. Tenant resolution fails closed per CLAUDE.md. |
| A.5.17 | Authentication information | Yes | Partially Implemented | Passwords hashed with Werkzeug's `generate_password_hash` (PBKDF2-SHA256 by default in current Werkzeug, not bcrypt/Argon2id) — app.py:37,4164. Account lockout after configurable failed attempts (app.py:1802-1803, 5230-5272). No password complexity/rotation policy found in code. |
| A.5.18 | Access rights | Yes | Implemented | AD group→team mapping with priority/conflict resolution, disabled/removed-user handling mandated in CLAUDE.md and reflected in `ldap_sync.py`; visibility vs. mutation permission separation enforced per ITIL record model. |
| A.5.19 | Information security in supplier relationships | Yes | Gap | No Supplier/Vendor Security Policy existed. Drafted in `ISMS_POLICIES.md`. Integrations (webhooks, Teams, SIEM, monitoring ingestion, NetBox/RT import) are customer-configured adapters; no vendor risk assessment process for the ServiceOps dependency supply chain itself. |
| A.5.20 | Addressing security within supplier agreements | Yes | Not Started | No standard security addendum/DPA template for customers integrating third-party systems via webhooks. |
| A.5.21 | Managing security in the ICT supply chain | Yes | Gap | `requirements.txt` pins versions but no SBOM generation, no dependency-vulnerability scanning (no Trivy/Snyk/Dependabot config found in repo — confirmed absent by search). |
| A.5.22 | Monitoring, review and change management of supplier services | Yes | Not Started | No process for reviewing third-party services (ClamAV daemon, LDAP/Keycloak servers, SMTP, monitoring ingestion) customers point at ServiceOps. |
| A.5.23 | Information security for use of cloud services | Yes | Partially Implemented | Product is deployment-agnostic (Docker/K8s); DEPLOYMENT.md covers self-hosted and external-managed-DB models with guidance to rely on provider snapshots/PITR for externally managed Postgres, but no explicit cloud-shared-responsibility statement. |
| A.5.24 | Information security incident management planning | Yes | Gap | No incident management policy/runbook existed at ISMS level (product has ITIL incident *tickets*, which is a different thing — this is about security incidents in ServiceOps itself). Drafted in `ISMS_POLICIES.md`. |
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

## A.6 People controls (8)

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

## A.7 Physical controls (14)

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

## A.8 Technological controls (34)

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

## Summary counts

See top-level report for the rolled-up count by status across all four
Annex A themes (Organizational 37, People 8, Physical 14, Technological 34 —
93 controls total).
