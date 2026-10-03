# Rack equipment image verification — 2026-10-03

Requested behavior: show datacenter equipment images in CMDB rack views and
identify equipment from existing metadata without inventing an exact model.

## Implemented behavior

- Offline identification from recorded role, CI class, exact model/model family,
  then bounded name hints. Vendor aliases, repeated manufacturer names and model
  punctuation normalize conservatively; contradictory vendors or approximate
  models never become an exact bundled-image match.
- Original front/rear illustrations for 13 equipment categories plus unknown
  devices. Existing exact Dell/Cisco/Juniper images and authenticated NetBox
  model imagery remain preferred. Missing images follow a finite fallback chain.
- Every readable rack-linked device appears in the inventory. Horizontal PDUs
  mount at their U position; 0U/missing-position/out-of-bounds devices remain
  visible separately instead of being placed at U1. Fractional U usage is the
  union of mounted intervals, including front/rear overlaps.
- Names/model/status/category and identification basis are visible in inventory
  cards; category illustrations are explicitly distinguished from model images.
  Existing tenant/class access and the server-side NetBox credential boundary
  remain enforced. No external AI/image search service is involved.

## Verification

- Ruff, whitespace and synchronized version checks passed (v1.109.0).
- Focused identification, asset and authenticated rack route tests: 48 passed.
- Full Python suite: 1,284 passed, 124 environment-gated skips, two existing
  ldap3/pyasn1 deprecation warnings. Six skips are the added browser cases, run
  separately below. The final fractional-U regression also passed in the focused
  gate after the broad suite began; no schema change was introduced.
- Actual Dockerfile Linux/amd64 build with separate migration job and Gunicorn
  entrypoints; 527 shipped source/artwork checksums and executable entrypoints
  verified in the final candidate.
- Disposable PostgreSQL 16 upgraded from empty through 20261002_0108. Final
  authenticated route/image checks covered 22 devices in full/embed views
  (44 checks), plus authorization, tenant/class filtering, 0U/invalid placement,
  image availability and space usage.
- Chromium suite: 106 passed, including all six new desktop/mobile rack checks,
  WCAG scans, keyboard focus, no horizontal page overflow, escaped equipment
  names, missing NetBox and model image fallback, and compact embedded views.
  Fault simulation blocks service workers so network interception is effective.
  Browser acceptance uses an isolated database; no production credentials or
  production test data were changed.

## Backup and deployment

- Verified live baseline: v1.108.6, Helm revision 142, head 20261002_0108,
  two web replicas. Live shipped source matched this checkout apart from
  synchronized release-version files; newer deployed behavior was retained.
- Pre-upgrade backup job: serviceops-backup-rack-20261003.
  Archive: /backups/serviceops-20261003T014043Z.dump.
- Restore job serviceops-restore-rack-20261003 restored into a unique temporary
  database, verified head 20261002_0108, 6,006 configuration items and two racks,
  then dropped only the temporary restore database.
- Candidate digest: sha256:4f4340699858860b4f1e9e085d3067ac0608e4e696a2ca4fa1eda9216661a4ef.
- Helm render comparison verified only application image and backup reference
  changes. Existing live settings, two web replicas, both workers, external
  PostgreSQL and existing PVC references were preserved.
- Atomic upgrade succeeded: Helm revision 143, v1.109.0. Running web (2/2),
  outbox worker (1/1) and AI worker (1/1) all use the verified immutable digest.
  All 527 source/artwork checksums and executable entrypoints match live.
- /health and /ready returned 200; representative front/rear artwork assets
  returned 200. Migration job and retained Helm health test succeeded at
  unchanged head 20261002_0108. PostgreSQL retains 6,006 CIs and both racks;
  original PostgreSQL/uploads/backups PVCs remain Bound.
- Recent web/worker logs: 154 / 3 / 3 lines, zero error/critical/traceback/5xx
  matches. Public request with browser User-Agent returns Cloudflare Access
  302 to the protected login hostname (generic Python User-Agent was refused).
- Canonical MicroK8s values synchronized to the verified digest and backup
  reference after deployment, with all other live settings retained.

No commits, pushes, tags, GitHub pipeline or public release were created.
