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

During local development, publish this side-by-side profile on all host
interfaces so other devices on the trusted `192.168.68.0/24` LAN can test it:

```dotenv
BIND_ADDRESS=0.0.0.0
APP_PORT=8081
```

On Anushka's current workstation address, open
`http://192.168.68.65:8081`; `http://localhost:8081` continues to work on the
Mac itself. This is plain HTTP intended only for the trusted development LAN.
The Mac firewall must permit inbound TCP/8081, and the router must not expose
or forward this port to the internet. If DHCP changes the workstation address,
use its new `192.168.68.x` address without changing the Compose binding.

Required configuration:

- `STORAGE_MODE=ipfs`
- `IPFS_API_URL=http://ipfs:5001` for the bundled node
- stable, secret `SECRET_KEY` and `SETTINGS_ENCRYPTION_KEY`
- `ADMIN_PASSWORD` for first boot only
- `GUNICORN_WORKERS=1` (the entrypoint enforces this)

## Pinata provider (`IPFS_PROVIDER=pinata`)

An alternative to a self-hosted/bundled Kubo node: `IPFS_PROVIDER=pinata`
(default `kubo`) swaps in `PinataIPFSClient`
(`serviceops_core/storage/pinata_client.py`) as the client passed to
`IPFSStorageBackend`, so every checkpoint/attachment/entity code path is
unchanged -- only the underlying IPFS transport differs. This mirrors the
ServiceOps iOS app's `PinataWorkspaceClient`
(`XCode_Development/ServiceOps/ServiceOps/PinataWorkspaceClient.swift`),
which already used Pinata as a free, hosted, no-node-to-run backend for its
own separate (simpler, flat-file) workspace schema.

Required configuration:

- `IPFS_PROVIDER=pinata`
- `PINATA_JWT` -- a free Pinata account JWT (Pinata dashboard -> API Keys)
- `PINATA_GATEWAY_URL` -- **required**, e.g. `https://your-name.mypinata.cloud`.
  Pinata's shared public gateway (`gateway.pinata.cloud`) was found via live
  testing to be unreliable (requests to it hung/timed out entirely); every
  free account has its own dedicated gateway subdomain under Pinata
  dashboard -> Gateways, which must be configured explicitly instead.

No IPNS: Pinata has no mutable-pointer concept, so the checkpoint pointer is
a *named file* instead -- `name_publish()` uploads a new
`<key>-pointer` file whose content is the latest checkpoint CID and deletes
the previous pointer file(s); `name_resolve()` lists files by that name
(newest first) and reads the CID back. This is the same technique the iOS
app's `PinataWorkspaceClient.writeDocument()` uses for its own documents
(query by filename, newest wins, delete old versions) -- both to converge on
a single "latest" value on an otherwise-immutable content store and to stay
within the free tier's file-count limit.

Private network / signed reads: uploads through this API's endpoint were
found (via live testing) to land on Pinata's *private* IPFS network, which a
bare `<gateway>/ipfs/<cid>` fetch 403s on. `PinataIPFSClient.cat()` handles
this transparently: on a 403 it signs a short-lived download link via
`POST /v3/files/private/download_link` and fetches through that instead. No
configuration is needed for this -- it is automatic, verified live against a
real Pinata account and a real dedicated gateway (upload, gateway
fetch-with-403-fallback, pointer publish/resolve, and pointer-version
replacement all confirmed from inside a Docker container, matching the
network path the deployed app actually uses).

`docker compose` service note: there is no `ipfs` (Kubo) container at all in
Pinata-provider mode -- see `compose.pinata-demo.yaml` in the ServiceOps
repository, the Pinata-provider analog of `compose.ipfs-demo.yaml` (same
`app`-only shape, port 8082 instead of 8081, no `ipfs` service or its
volume).

The installer's Storage section exposes an "IPFS provider" choice (Kubo vs.
Pinata) plus the JWT and gateway-URL fields, gated the same way the existing
Kubo bundled/external choice is.

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
