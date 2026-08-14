# Full IPFS storage mode

## Status

ServiceOps supports a complete, opt-in `STORAGE_MODE=ipfs` deployment. IPFS is
the sole durable application and attachment store; no PostgreSQL service or
persistent embedded database is used. The former B-335 login-only checkpoint
is migrated automatically at first boot.

Feature parity includes the dashboard, internal ticketing, client management,
catalog, knowledge, CMDB, discovery, workflows, administration, users and
roles, settings, notifications, audit history, server-side session inventory
and revocation, rate limiting, APIs, mobile authentication, attachments,
analytics, scheduled work, and health monitoring.

## Architecture

The existing ServiceOps domain layer contains 109 related SQLAlchemy tables
and hundreds of mature relational queries. IPFS cannot execute joins,
constraints, transactions, filters, or ordered queries. In IPFS mode:

1. `IPFSStorageBackend` resolves one instance-owned IPNS name.
2. It fetches and Fernet-decrypts the referenced checkpoint using
   `SETTINGS_ENCRYPTION_KEY` (or the documented `SECRET_KEY` derivation).
3. `IPFSRelationalProjection` restores every table into a uniquely named,
   process-local, shared-memory SQLite projection. This is an execution/query
   engine only: it has no disk file and is never authoritative.
4. The normal ServiceOps models, constraints, tenant filters, workflows, and
   forms run unchanged against that volatile projection.
5. Successful commits mark the projection dirty. A two-second checkpointer
   coalesces bursts, serializes every table with lossless tagged values for
   timestamps, dates, times, binary values, decimals, and UUIDs, encrypts the
   complete snapshot, adds and pins it to IPFS, and schedules the newest CID
   for IPNS publication.
6. One retrying publisher performs the potentially slow IPNS operation off the
   request path. `/ready` exposes `checkpoint_publish_pending`.
7. Attachment bytes are separately Fernet-encrypted before IPFS `add`; the
   table checkpoint stores their authorization metadata and CID.

The application runs one Gunicorn process in this mode. Threads share the same
projection. Scheduled processing (SLA, workflow, outbox, discovery, RT import,
client escalation/email, retention, performance and KPI work) runs inside that
process so there is one authoritative checkpoint writer.

## Upgrade from B-335

When no `relational_state` exists but the old checkpoint contains `tenant` and
`user` entity maps, startup imports those records, preserves password hashes
and IDs, runs the standard idempotent seed for all platform defaults, and
publishes a full checkpoint. This is automatic and does not require resetting
the Kubo volume or administrator account.

Do not rotate or discard `SETTINGS_ENCRYPTION_KEY`, `SECRET_KEY`, or the Kubo
key repository during the upgrade. Losing the encryption key makes checkpoint
and attachment content unrecoverable.

## Deployment

The reference side-by-side stack is `compose.ipfs-demo.yaml` in the ServiceOps
repository. It contains only `app` and `ipfs`; it deliberately contains no
PostgreSQL or separate worker service.

Required configuration:

- `STORAGE_MODE=ipfs`
- `IPFS_API_URL=http://ipfs:5001` for the bundled node
- stable, secret `SECRET_KEY` and `SETTINGS_ENCRYPTION_KEY`
- `ADMIN_PASSWORD` for first boot only
- `GUNICORN_WORKERS=1` (the entrypoint enforces this)

Use `/health` for liveness dependencies and `/ready` for IPFS reachability,
volatile-projection availability, checkpoint table/file counts, publication
state, and upload-path availability.

## Recovery and backup

Back up the complete Kubo data volume plus the separately protected encryption
keys. Recovery is:

1. Restore the Kubo volume and the same keys.
2. Start the IPFS node and wait for its health check.
3. Start ServiceOps with `STORAGE_MODE=ipfs`.
4. Confirm the startup log reports the expected table count.
5. Confirm `/ready` is 200 and `checkpoint_publish_pending` eventually becomes
   false.
6. Verify login, one ticket, one attachment, audit history, and session
   revocation.

## Deliberate operating boundary

This mode now has application feature parity, but it is not equivalent to the
PostgreSQL profile for scale or availability. The complete snapshot model has
O(total records) checkpoint cost, allows only one application process, and can
lose the most recent coalescing window if the process is killed before a dirty
projection is added and published. IPNS publication can be slow; requests do
not wait for it, and readiness reports pending durability explicitly.

Use PostgreSQL for horizontal scaling, high write volume, strict synchronous
durability, multi-node HA, or compliance regimes that require independently
validated database controls. Production promotion of IPFS mode still requires
load/soak limits, kill-during-checkpoint recovery evidence, independent tenant
isolation/security review, and a documented Kubo backup/restore rehearsal.
