# ISO/IEC 27001:2022 Gap Analysis — ServiceOps

Companion to `SOA.md`. Every control marked Gap or Partially Implemented
there gets a concrete remediation item here. Items are grouped by priority
based on exploitability and blast radius for a multi-tenant ITSM platform
handling customers' incident/change/CMDB data.

Remediation items are written to be picked up directly by an engineer or the
ITIL/GDPR remediation agent — each names the file(s)/model(s) involved and a
concrete acceptance check, not just a restated goal.

## P0 — highest priority (auth/tenant-boundary/crypto risk)

### 1. No MFA for privileged accounts (A.8.5)
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

### 2. General web rate limiting is absent; only the REST API has it (A.8.16, A.5.15 partial)
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

### 3. No secret/log redaction utility (A.8.11)
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

### 4. Password hashing uses PBKDF2 (Werkzeug default), not Argon2id (A.8.24, A.5.17)
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

### 5. Dependency/CVE scanning absent (A.8.8, A.5.21)
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

## P1 — high priority (integrity, incident response, monitoring)

### 6. Audit-log tamper-evidence not verified end-to-end (A.5.28)
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

### 7. No security incident management policy/runbook (A.5.24–A.5.27)
**Gap.** ITIL Incident/Problem workflows exist for *service* incidents but
nothing defines how ServiceOps itself handles a *security* incident (e.g., a
reported vulnerability, a suspected tenant-isolation breach, a leaked
credential).
**Remediation:** Adopt the Incident Management Policy drafted in
`ISMS_POLICIES.md`; add a `security.txt`/`SECURITY.md` at the ServiceOps repo
root (or its equivalent internal location) with a disclosure contact and
target response times, referenced from GOVERNANCE.md.

### 8. No independent security review or pentest evidence (A.5.35)
**Gap.** No pentest report, third-party audit artifact, or `security.txt`
found. For a multi-tenant platform holding customer ITSM/CMDB data, this is
a material gap for enterprise customers' own compliance needs.
**Remediation:** Commission (or schedule) an annual third-party penetration
test scoped to tenant-isolation bypass, auth bypass, and SSRF/webhook
handling specifically (the areas CLAUDE.md flags as hardened, which are also
the highest-value targets). Track findings and remediation in
`docs/BACKLOG.md` with severity and closure evidence, per this repo's
existing evidence-tracking convention.

### 9. No self-monitoring / metrics endpoint found (A.8.16)
**Partially Implemented.** The product ingests *customers'* monitoring
events (admin-configurable "Monitoring ingestion" integration) but this
review found no `/metrics` (Prometheus) or health-telemetry endpoint for
ServiceOps' own operational health beyond basic liveness.
**Remediation:** Add a `/metrics` endpoint (prometheus_client) exposing
request latency, error rate, rate-limit rejections, and failed-login counts;
document scrape config in DEPLOYMENT.md; wire failed-login-count and
attach-blocked counters as alertable signals (these are already audited
events — surface them as metrics too).

### 10. No documented BC/DR test evidence or RTO/RPO targets (A.5.29, A.5.30)
**Partially Implemented.** Backup/PITR mechanics are solid and documented
(DEPLOYMENT.md, `tools/recovery_verify.py`), but no RTO/RPO targets are
defined and no drill/failover test is recorded.
**Remediation:** Define RTO/RPO in the Business Continuity/Backup Policy
(drafted in `ISMS_POLICIES.md`) and run (and record) at least one annual
restore drill using `tools/recovery_verify.py` against a non-production
environment, logging the measured recovery time against the target.

## P2 — medium priority (hardening, process maturity)

### 11. No Kubernetes NetworkPolicy manifests (A.8.20, A.8.22)
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

### 12. No data classification/labelling scheme (A.5.12, A.5.13)
**Gap.** Ticket data, attachments, and CMDB records have no classification
tagging (e.g., confidential customer PII vs. internal operational data),
which matters for the GDPR workstream's export/erasure scoping too.
**Remediation:** Define a 3–4 tier classification scheme in a new
`docs/DATA_CLASSIFICATION.md` (or fold into ISMS_POLICIES.md's Access
Control Policy) and note which existing tables/fields fall into which tier,
as a reference for both this ISMS work and the concurrent GDPR work — but do
not implement enforcement code here per this task's read-only-on-code scope.

### 13. No branch protection / mandatory code review policy documented (A.8.4, A.8.25)
**Partially Implemented.** CLAUDE.md mandates a high production-grade bar for
changes but this review found no documented requirement for review-before-
merge or protected branches.
**Remediation:** Document (in GOVERNANCE.md or a new SDLC section) a
required-review policy for the `main` branch and confirm it's configured in
GitHub branch protection settings (outside this repo's tooling, but the
requirement should be traceable from here).

### 14. Key rotation for `SETTINGS_ENCRYPTION_KEY`/`SECRET_KEY` undocumented (A.8.24)
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

### 15. Unverified: dedicated security/authz test coverage (A.8.29)
**Unverified — treat as Gap until confirmed.** `tests/` exists but this
review did not enumerate it for tenant-isolation-bypass or CSRF-bypass test
cases specifically.
**Remediation:** An engineer should grep `tests/` for tenant-isolation and
CSRF test coverage; if absent, add tests asserting that a user from tenant A
cannot read/write tenant B's tickets/CMDB/audit records via API, UI routes,
and background jobs (the three surfaces CLAUDE.md calls out by name).

## P3 — lower priority / organizational

### 16. No named ISMS owner / security roles (A.5.2, A.5.1, A.5.4)
**Gap.** Addressed procedurally by adopting `ISMS_POLICIES.md` and assigning
an accountable owner in GOVERNANCE.md's decision log — no code change
needed.

### 17. No asset inventory of ServiceOps' own build artifacts (A.5.9)
**Partially Implemented.** Recommend a lightweight `docs/ASSET_INVENTORY.md`
listing container images, Helm chart versions, signing keys, and where they
live, kept in sync with the existing release-tagging policy in CLAUDE.md.

### 18. No vendor/supplier security review process (A.5.19–A.5.22)
**Gap.** Addressed by the Supplier/Vendor Security Policy in
`ISMS_POLICIES.md`; no code change required, but customers integrating
webhooks/Teams/SIEM should be pointed at a documented minimum-security
baseline for those endpoints.

### 19. No security-awareness training program (A.6.3)
**Gap.** Organizational, not code — track as a backlog item for the ISMS
owner once named.

### 20. Storage-media secure disposal undocumented (A.7.10, A.7.14)
**Gap.** Add a short section to DEPLOYMENT.md on secure erasure of DB
volumes/backup media at decommission (e.g., `shred`/cloud-provider
secure-delete guidance), since backups already carry sensitive customer
data with owner-only permissions.

## How to use this with the concurrent ITIL/GDPR workstream

Items 3 (secret redaction), 6 (audit chain verification), 12 (data
classification touching GDPR scoping), and 10 (BC/DR) overlap with what a
GDPR-focused workstream would also need. Recommend the ITIL/GDPR agent treat
this gap analysis as input rather than duplicating discovery — coordinate via
`docs/BACKLOG.md` so both workstreams don't independently re-derive the same
audit-log/redaction gaps.
