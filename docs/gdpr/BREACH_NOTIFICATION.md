# Personal Data Breach Notification Procedure (Art. 33/34 GDPR)

This procedure applies to the operating **controller** (the customer
organization running a self-hosted ServiceOps instance). Where ServiceOps
acts as processor (a managed/SaaS deployment — see `DPA_TEMPLATE.md`), the
processor-to-controller notification SLA in that template feeds into step 2
below.

## 1. Detection

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

## 2. Internal triage and severity assessment (target: within hours of detection)

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
     `ROPA.md`'s six processing activities. An attachment-store breach
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

## 3. Supervisory authority notification (72-hour clock, Art. 33)

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

## 4. Data subject notification (Art. 34)

Required when the breach is "likely to result in a high risk to the rights
and freedoms of natural persons." Given this product's data categories,
scenarios that likely cross that threshold:

- Exposure of `password_hash` values (even hashed, warrants a mandatory
  forced reset + notification given credential-stuffing risk).
- Exposure of attachment content containing sensitive documents.
- Exposure sufficient to enable identity-linked profiling (e.g. a large
  `Audit`-table export correlating identity + IP + detailed activity).
- Any exposure the controller's own risk assessment (informed by their
  DPIA, `DPIA.md`) rates high.

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

## 5. Containment technical actions available in the product today

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

## 6. Escalation path (template — controller must name actual roles)

1. Detector -> on-call/security contact (immediate)
2. Security contact -> DPO/privacy lead (within hours) — severity
   assessment per step 2
3. DPO/privacy lead -> supervisory authority (within 72 hours of
   awareness, if threshold met) — per step 3
4. DPO/privacy lead -> affected data subjects (without undue delay, if
   high-risk threshold met) — per step 4
5. Engineering/admin -> containment actions (step 5), in parallel with 2-4,
   not sequential after them
6. Post-incident: root-cause writeup, `TRACEABILITY_MATRIX.md` update if a
   product gap contributed, `BACKLOG.md` entry for any fix, and — if the
   gap was one of the items flagged in `DPIA.md`/`RETENTION_POLICY.md` —
   cross-reference those documents so the same gap isn't independently
   rediscovered later.

## Gaps summary (for BACKLOG.md)

1. No cross-account brute-force/anomaly correlation report.
2. Unconfirmed whether SSRF-blocked webhook attempts are audit-logged.
3. No purpose-built "breach scope" admin report (tenant/user-count/data-category rollup).
4. Malware-scan-adapter wiring not confirmed active (referenced as pluggable, not verified live).
