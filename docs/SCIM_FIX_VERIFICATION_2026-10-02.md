# SCIM provisioning corrections — 2026-10-02 (verified 2026-10-03)

The project review reproduced three defects through authenticated SCIM routes:
a valid pathless `replace` with `value: {"active": false}` returned 200 while
leaving the account active; replacing an email with an existing user's email
returned 500; and non-object JSON bodies returned 500.

The fix validates request objects, attribute types, and every PATCH operation
before applying changes. Both explicit paths and pathless objects support
`active`, `displayName`, and `emails`. Unsupported operations and paths return
400 rather than reporting a successful no-op. Deactivation increments
`auth_version` and revokes active sessions through the existing audited
transaction. Invalid later operations leave earlier operations unapplied.

Email updates check case-insensitive uniqueness while excluding the current
user. The SCIM transaction catches database unique violations during flush,
audit, and commit, rolls back, and returns 409 `uniqueness`; unrelated integrity
failures are not mislabeled. Malformed requests return SCIM error documents
with 400 status. Existing administrator, bearer scope, and tenant checks remain
in place. No schema or migration change is needed.

Regression coverage is in `ServiceOps/tests/test_scim.py`, alongside the existing
SCIM lifecycle test in `tests/test_operational_resilience.py`. Focused validation
passed 66 tests. The first full run passed 1,143 tests and skipped 118, with
31 local socket/network checks denied by the execution sandbox; all 31 passed
when rerun with the required access. The clean full run passed 1,174 tests,
skipped 118 environment-gated tests, and emitted two existing ldap3/pyasn1
deprecation warnings. There are 54 new SCIM regression cases. Ruff, Python
compilation, canonical-version consistency, supply-chain policy, Helm lint,
candidate upgrade rendering, and whitespace checks passed.

Pre-upgrade backup: `/backups/serviceops-20261002T143318Z.dump`, created by
`serviceops-backup-scim-20261002`. Restore Job
`serviceops-restore-test-scim-20261002` succeeded against an isolated database,
verifying migration head `20260928_0107` and 20 restored tickets. The original
PostgreSQL and uploads PVCs remain in place.

Docker Desktop returned daemon API errors and could not restart. A fresh
amd64 OCI image was assembled with `crane append` from the current verified
runtime image `ghcr.io/awijesundara/serviceops-server@sha256:f79ed751abca0fb1e440602989463b2748fdf94c221018ea2dcf6fdb17afe139`
and a deterministic layer containing all 539 eligible files from the current
checkout, including the new regression tests. Secrets, runtime state, and the
three production-excluded disposable fixture loaders were excluded. Runtime
dependencies and startup configuration are inherited from the verified base;
this is an OCI source-layer build, not a Dockerfile rebuild. The candidate is
stored only in the local MicroK8s registry as
`localhost:32000/serviceops@sha256:472a394e631010efcaa4c08333139532340a08d19378e341a8776d19bcfcc3fd`.
The application version remains 1.108.0; the local image tag is
`1.108.0-scim-20261002-r2`. No GitHub commit, push, tag, pipeline, or release was
requested or performed.

## Final acceptance

- The exact candidate image verified all 539 source checksums and passed
  33 SCIM checks against the freshly migrated isolated PostgreSQL database
  `serviceops_20261002_scim_test`. The checks include deactivation/revocation,
  pathless add/replace, duplicate and case-variant email conflicts, a real
  PostgreSQL unique violation after the precheck, malformed bodies and
  operations, atomic rejection, and successful subsequent reads.
- Real browser tests against that image/database passed 14 checks for profile,
  session inventory, security settings, keyboard access, focus visibility,
  320px reflow, and axe accessibility. An additional Playwright journey signed
  in as the isolated employee, sent pathless SCIM deactivation through a
  separate bearer client, and confirmed the existing browser session redirected
  to login on its next protected request.
- During validation the shared values file changed independently to 1.108.4.
  The user explicitly selected the current live configuration for this fix.
  The canonical values now preserve that configuration, including two web
  replicas, with only the local image and verified backup reference changed.
  Its rendered upgrade manifest is byte-identical to the candidate rendered
  from the captured live values. A further shared-file reversion made revision
  139 retain the original image; the successful upgrade used the captured
  approved values plus explicit image and backup overrides. Canonical values
  were synchronized afterward with the verified deployment.
- Dockerfile/Compose rebuilds remain unavailable because Docker Desktop is
  unhealthy. The verified OCI image and isolated PostgreSQL/browser checks
  above are actual evidence; they do not claim a Dockerfile rebuild or external
  identity-provider acceptance.

## Deployment interruption and recovery

The first upgrade attempt started with the pending values because the Python
values-preparation command failed on an unavailable YAML import and the shell
sequence did not stop on that failure. The Helm process was promptly canceled
and rolled back, but its pre-upgrade hook had already applied the unrelated
1.108.4 migration `20261002_0108`, making the original image fail readiness.
This was an execution error, not a SCIM regression.

The unexpected migration was inspected directly from its image. Its new
`configuration_item.field_sources` column contained no values other than `{}`.
Recovery Job `serviceops-scim-recovery-20261002` restored a fresh isolated copy
of the verified pre-upgrade backup, restored only the 12 CMDB fields the
migration had cleared (where still null), and ran the inspected Alembic
downgrade to `20260928_0107`. It preserved all 20 tickets and 8 users and removed
its temporary restore database. The web, outbox, and AI worker were confirmed
healthy after Helm rollback revision 136. Values preparation, rendering,
comparison, and mutation were then performed in separate checked steps before
retrying the tested image through atomic Helm.

The second candidate rollout exposed missing executable permissions on the
startup scripts in the OCI source layer. The Dockerfile explicitly sets those
files to 755, whereas their checkout modes are 644. That rollout was canceled
and atomically rolled back at revision 138; the original web replicas remained
available. The source-layer build was corrected to reproduce the Dockerfile
chmod for `tools/container-entrypoint.sh` and `tools/gunicorn-entrypoint.sh`.
The final image above again verified all 539 source checksums and passed all
33 PostgreSQL checks. It then launched through the real container and Gunicorn
entrypoints; the 14 focused browser/accessibility checks and real-browser
pathless deactivation journey passed again on that exact image.

## Verified deployment — 2026-10-03

Atomic Helm revision **140** is deployed in `operations`. All production
workloads consume the final immutable digest `sha256:472a394e631010efcaa4c08333139532340a08d19378e341a8776d19bcfcc3fd`: web 2/2,
outbox worker 1/1, and AI worker 1/1. All three rollouts completed. The live
container verified all 539 source checksums and both executable startup scripts.

`/health` returned 200 (`status: ok`, version 1.108.0). `/ready` returned 200
with database, migration, uploads, worker, and audit-encryption checks passing.
Both image and database migration heads are **20260928_0107**. Unauthenticated
SCIM returned 401. The retained `serviceops-health-test` Helm test succeeded.
Public `https://serviceops.wijesundara.com/` returned the expected Cloudflare
Access 302. Both new web pods and both workers had zero recent
error/critical/traceback/5xx log entries. PostgreSQL, uploads, and backups PVCs
remain bound to their original volumes. Production still has 20 tickets and
8 users. The verified pre-upgrade backup reference is recorded in Helm.

The disposable SCIM/browser pod and its ConfigMap were removed after
acceptance; its isolated database was dropped. Backup/restore evidence and
the retained Helm health test remain. The full-suite skips and unavailable
Dockerfile/Compose rebuild described above remain validation boundaries. No
external IdP interoperability, real Kubo, or broad unselected browser journeys
are claimed by this correction.

## Follow-up — published as 1.108.5 (2026-10-03)

The interim local image was superseded by the governed release. The fix was
committed to ServiceOps main as `f8840fb` (rebased onto 1.108.4; full suite
1243 passed / 118 skipped) and released as v1.108.5 (`94327ba`, image
`ghcr.io/awijesundara/serviceops-server@sha256:c9772cf3a8d5ffd1d6ed91acf97099fba87f0b834fd08f1991fcf913e4976ccf`).
Pre-upgrade backup `serviceops-20261002T231916Z.dump` was restore-verified
(`20260928_0107`, 20 tickets). Helm revision 141 applied migration
`20261002_0108`; web 2/2 and both workers ready, helm test passed, 20 tickets
and 8 users preserved, Cloudflare Access 302 and public status page 200.
