# ServiceOps 1.39.0 operational-resilience release

> **Historical — superseded.** Target version 1.39.0 is ~23 releases behind
> current (1.62.5 as of this note). The gaps and evidence below are a
> point-in-time snapshot of that release; `BACKLOG.md` carries the current
> status for every item referenced here. Kept for historical record, not as
> a live plan.

## Objective

Close the application-controlled monitoring, authentication recovery, session
lifecycle, SCIM, storage, recovery-safety, and discovery-review gaps found in
the 2026-08-05 whole-project review without claiming evidence that requires an
independent assessor or the deploying organization's external systems.

## Delivered controls

- `/live` remains process-only; `/ready` validates database access, exact
  migration head, audit-key decryptability, worker heartbeat, uploads, and
  configured S3 storage.
- `/metrics`, W3C trace correlation, Prometheus alerts, backup-age signals,
  System Health recovery status, and an external authenticated synthetic probe.
- Throttled and non-enumerating local password recovery with hashed,
  single-use, 30-minute tokens; successful reset unlocks the account and
  revokes all sessions.
- User and tenant-administrator browser-session inventory and immediate
  revocation.
- Tenant-scoped SCIM user create/update/deactivate through limited API clients;
  deactivation invalidates sessions. Keycloak can require an exact MFA `acr`.
- Guarded recovery diagnosis, administrator reset, and explicit audit-key
  recovery-boundary commands with mandatory pre-mutation recovery sets.
- Recovery manifests reference the encryption key by non-secret fingerprint;
  optional S3-compatible Object Lock archival provides off-site immutability.
- Optional S3-compatible attachment storage with local fallback and readiness
  validation.
- Discovered-device review supports compound search/class/vendor/source
  filtering, live counts, filter-aware selection, and whole-batch selection.

## Verification gates

- Full isolated application suite: `310 passed, 1 skipped`; the only skip is
  the cross-repository documentation test because the sibling notes checkout
  is intentionally absent from the application image.
- Focused resilience, recovery, health, and discovery suite: `14 passed`.
- Ruff correctness, Python compilation, shell syntax, whitespace, canonical
  version, and supply-chain control verification passed.
- Live PostgreSQL migrated to `20260805_0058`; the app/database/worker are
  healthy on `http://localhost:80`; deep readiness and audit-key diagnosis
  pass; metrics report a fresh backup and worker; the login page is responsive
  and protected routes redirect unauthenticated callers. A 1,000-request,
  concurrency-20 stability probe completed with zero errors, 27.66 ms p95 and
  1,125.14 requests/s. Recent post-correction logs contain no traceback,
  critical, encryption-key, or migration failure.

## Honest external boundaries

The release does not manufacture external evidence. Penetration testing,
independent tenant-isolation review, representative IdP/SCIM/S3/SMTP and alert
delivery validation, hardware WebAuthn/passkeys, organization-approved RPO/RTO,
real Kubernetes failure/rollback, and on-call/runbook exercises remain open
until those environments and independent reviewers are available.
