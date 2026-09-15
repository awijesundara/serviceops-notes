# ServiceOps deployment guide

> For the complete zero-PostgreSQL profile, including upgrade, recovery and
> limitations, see [IPFS_STORAGE_MODE.md](IPFS_STORAGE_MODE.md).
>
> For the full user, administrator, identity, Kubernetes, security,
> monitoring, backup, recovery, upgrade, rollback, and incident-response
> runbook with diagrams and screenshots, see the
> [complete platform manual](OPERATIONS_MANUAL.md).

## Contents

**Choose and install**
[Deployment topologies](#deployment-topologies) ·
[Fast installation](#fast-installation) ·
[Architecture A: bundled PostgreSQL](#architecture-a-bundled-postgresql) ·
[Architecture B: external PostgreSQL](#architecture-b-external-postgresql) ·
[RPM packaging](#rpm-packaging-linux-distribution) ·
[Kubernetes production deployment](#kubernetes-production-deployment) ·
[Private registry mirrors (Nexus and similar proxies)](#private-registry-mirrors-nexus-and-similar-proxies) ·
[Web Installation Center](#web-installation-center) ·
[Air-gapped deployment boundary](#air-gapped-deployment-boundary)

**Configure identity and access**
[AD and LDAP](#ad-and-ldap) ·
[Keycloak](#keycloak) ·
[Passkeys and Apple Associated Domains](#passkeys-and-apple-associated-domains) ·
[Apple push notification configuration](#apple-push-notification-configuration)

**Expose and monitor**
[HTTPS and network exposure](#https-and-network-exposure) ·
[Service health and monitoring](#service-health-and-monitoring) ·
[Immutable recovery and object storage](#immutable-recovery-and-object-storage)

**Operate**
[Operations](#operations) ·
[Recovery objectives](#recovery-objectives) ·
[Upgrades](#upgrades) ·
[Account and emergency recovery](#account-and-emergency-recovery)

**Secure and scale**
[Security checklist](#security-checklist) ·
[Scaling](#scaling)

**Maintainer and CI notes**
[Mandatory browser quality gate](#mandatory-browser-quality-gate) ·
[Local development deployment convention](#local-development-deployment-convention)

## Deployment topologies

| Environment | Application | Database | Upload storage | Use when |
|---|---|---|---|---|
| Single server | Docker Compose | Bundled PostgreSQL | Docker volume | Evaluation or one-server production |
| Single server, external DB | Docker Compose | External PostgreSQL | Docker volume + backups | Separate backup ownership, managed database |
| Kubernetes | Helm, 3+ replicas | External HA PostgreSQL | RWX CSI volume or S3-compatible | High availability, horizontal scale |

```mermaid
flowchart LR
    subgraph A["Single server"]
        A1["ServiceOps app"] --> A2["Bundled PostgreSQL"] --> A3["Docker volume"]
    end
    subgraph B["Single server, external DB"]
        B1["ServiceOps app"] --> B2["External PostgreSQL"] --> B3["Docker volume + backups"]
    end
    subgraph C["Kubernetes"]
        C1["ServiceOps app x3+"] --> C2["External HA PostgreSQL"] --> C3["RWX / S3 storage"]
    end
```

Production Kubernetes must use an externally operated, highly available
PostgreSQL service — the chart rejects a configuration that omits it.

## Passkeys and Apple Associated Domains

Passkeys require a stable public HTTPS origin. Configure
`WEBAUTHN_RP_ID=serviceops.example.com`,
`WEBAUTHN_ORIGIN=https://serviceops.example.com`, an optional
`WEBAUTHN_RP_NAME`, and `APPLE_PASSKEY_APP_ID` as the Apple Team ID plus bundle
ID. The iOS target's `webcredentials:` associated domain must exactly match
`WEBAUTHN_RP_ID`. Confirm the unauthenticated
`/.well-known/apple-app-site-association` response is reachable without a
redirect or authentication challenge before enabling passkeys. Local
`http://192.168.*` deployments support password login and biometric app lock,
but not a real Apple passkey ceremony.

For the full user, administrator, identity, Kubernetes, security, monitoring,
backup, recovery, upgrade, rollback, and incident-response runbook, use the
[complete platform manual](OPERATIONS_MANUAL.md).

## Mandatory browser quality gate

Every pull request, push to `main`, and governed release runs a separate
`browser-quality-gate` job. It creates an isolated `serviceops-e2e` Docker
Compose project on `127.0.0.1:18080` with generated masked credentials, runs
the critical Dashboard, Administration, CMDB, and Client Management journeys
in Chromium at desktop and mobile viewport sizes, and blocks the change on an
HTTP/rendering failure, browser console error, or serious/critical axe-core
WCAG 2.2 AA finding. On failure, Playwright traces, full-page screenshots, and
Compose logs are retained as workflow artifacts. The job always destroys its
containers and volumes and never reuses the standing development deployment.

A successful supply-chain gate for the current `main` commit automatically
starts the governed-release workflow. That workflow creates the next patch
version and immutable tag, repeats the release gates, signs and attests the
digest-pinned image, clean-builds and install-tests every supported RPM target,
and publishes the verified stable release. It refuses stale commits, ignores
failed gates and fork-originated runs, serializes releases, and excludes its own
version commits to prevent recursive releases. Use the manual release dispatch
only when selecting a minor or major version increment.

## Air-gapped deployment boundary

Air-gapped production deployments use the released RPM plus a transfer bundle
prepared on an internet-connected Linux host. The bundle must contain the
signed, immutable ServiceOps release image and the digest-pinned PostgreSQL and
optional Kubo runtime images. `tools/offline/vendorize.sh` refuses mutable
application references, saves each image for one declared target platform, and
creates portable SHA-256 checksums. `tools/offline/build-offline.sh` rejects
unsafe archive paths, verifies every transferred file before loading images,
and confirms each locked digest after loading.

The bundle never contains secrets or database data. RPM, Docker Engine, and OS
dependencies remain the responsibility of the organization's signed offline OS
repository. Verify GitHub image provenance on the connected preparation host,
apply approved removable-media scanning and chain-of-custody controls, then use
the normal packaged setup, systemd, health, readiness, backup, and restore
procedures inside the restricted network.

## Local development deployment convention

During the active development period on Anushka's local machine, the Docker
Compose deployment must always publish ServiceOps at `http://localhost:80`
(normally entered as `http://localhost`). Keep the local, untracked
`ServiceOps/.env` setting as:

```dotenv
APP_PORT=80
```

After every application update, run `./tools/deploy-local.sh` and verify
`http://localhost/health`. Do not change the container's internal port 8080;
Compose maps host port 80 to that internal port. This workstation convention
does not change production ingress, reverse-proxy, or Kubernetes ports.

The local `.env` is part of the recovery set even though it is intentionally
not committed. In particular, never regenerate or replace
`SETTINGS_ENCRYPTION_KEY` while retaining an existing database: platform
secrets and retained audit-signing keys would become undecryptable. Store that
key separately with the local recovery material. Port changes require only
`APP_PORT`; they must not rotate encryption keys.

## Service health and monitoring

Use `/live` only for process liveness. `/ready` is the traffic-admission gate:
it checks PostgreSQL, the exact migration head, active-tenant audit-key
decryptability, worker heartbeat, upload writability, and configured object
storage. `/health` remains the lightweight Docker dependency check because the
Compose worker starts after the app; making app container health depend on that
worker would create a startup cycle.

Prometheus scrapes `/metrics`; set `METRICS_TOKEN` to require `Authorization:
Bearer ...`. Install `deploy/monitoring/prometheus-rules.yaml` and route its
critical alerts to a staffed destination. Run `tools/synthetic_login.py` from
outside the cluster with a dedicated unprivileged requester to prove the full
CSRF, password, session, and authenticated-page journey.

## Account and emergency recovery

Local users can request a non-enumerating, single-use 30-minute password-reset
link. Completion resets lockout state and revokes every existing browser
session. Users review their own sessions; tenant administrators can inventory
and revoke all tenant sessions. For operator recovery, use only:

```bash
./serviceops diagnose-recovery
./serviceops recover-admin USERNAME
./serviceops recover-audit-key TENANT_SLUG
```

Mutation commands take a checksummed recovery set first. Audit-key recovery is
an explicit integrity boundary; it never pretends that signatures made with a
lost key remain verifiable.

## Immutable recovery and object storage

Each recovery manifest records a non-secret fingerprint of the exact settings
encryption key. Configure `BACKUP_ARCHIVE_*` to upload database, uploads, and
manifest artifacts to S3-compatible storage. With
`BACKUP_REQUIRE_OBJECT_LOCK=true`, backup fails unless Object Lock is enabled.
Use a KMS key and a separate account/credential from the application.

Set `OBJECT_STORAGE_BUCKET` and related `OBJECT_STORAGE_*` values for
S3-compatible attachments. Empty bucket configuration retains the Docker
volume/PVC backend. Readiness validates the configured bucket before admitting
traffic.

## Kubernetes production deployment

The supported enterprise topology is the Helm chart in `charts/serviceops`
with an immutable application image, two or more replicas, external HA
PostgreSQL, RWX upload storage, ingress TLS, Restricted Pod Security,
NetworkPolicy, probes, topology spreading, and disruption protection.

1. Copy the example values file:

   ```bash
   cp deploy/kubernetes/values-production.example.yaml \
      deploy/kubernetes/values-production.yaml
   ```

2. Set `image.repository` and the verified `image.digest` from the successful
   tagged supply-chain workflow, then export `SERVICEOPS_GITHUB_ORGANIZATION`.
3. If ingress is enabled, set `networkPolicy.ingressNamespaceSelector` to the
   trusted ingress-controller namespace — an empty selector is rejected
   instead of silently trusting every namespace.
4. Run the preflight check, then install:

   ```bash
   ./serviceops install kubernetes --preflight
   ./serviceops install kubernetes
   ```

By default, tags are descriptive only and every workload runs
`repository@sha256:digest` (`image.pinning: digest` in `values.yaml`, the
default). If your registry cannot serve manifests by digest reference, see
[Private registry mirrors](#private-registry-mirrors-nexus-and-similar-proxies)
below for the `image.pinning: tag` alternative — the digest requirement and
its verification are unchanged either way, only the runtime pull reference
differs.

Chart validation rejects a missing digest, a single application replica,
disabled persistent upload storage, and bundled PostgreSQL — the optional
bundled PostgreSQL StatefulSet is not an approved production database
architecture. The installer additionally deploys the pinned Sigstore policy
controller and GitHub trust policy, enables attestation enforcement on the
namespace, uses atomic Helm deployment, waits for rollout, and runs the
packaged health test.

**What the chart guarantees:**

- **Credentials.** The chart never creates plaintext application credentials
  or stores them in a Helm release; it requires operator-managed
  `existingSecret` and `existingBootstrapSecret` objects. A first guided
  install creates both from separate mode-`0600` temporary files; an upgrade
  preserves both without rotation. A partial state (only one Secret) fails
  closed for operator recovery. Back up the runtime Secret in the approved
  vault — changing its settings-encryption, audit-integrity, or API-token
  keys can make encrypted configuration unreadable or break verification
  continuity.
- **Migrations.** The migration Job waits for PostgreSQL, then applies the
  schema exactly once through the supported application-context entrypoint,
  serializing PostgreSQL schema writers with an advisory lock, and stays
  available as evidence until the next upgrade replaces it. Never run raw
  `alembic` commands, manually update `alembic_version`, or delete a
  database/PVC to resolve a schema mismatch.
- **Startup ordering.** Web and worker pods use a separate init gate that
  waits for both connectivity and the exact Alembic head, leaving a clear
  `Init` state instead of repeatedly crashing while the database is
  unavailable or behind.
- **Readiness evidence.** The packaged Helm test has a bounded
  connection/total timeout, a digest-pinned helper image, and its own
  deny-by-default policy permitting only DNS and the web pods' application
  port. Its completed pod is retained until the next test so
  `helm test --logs` can collect evidence.

Do not use `kubectl set image`. In the default `image.pinning: digest` mode,
workloads consume `repository@digest`, so a tag override alone is
intentionally ineffective. In `image.pinning: tag` mode the workload does
consume `repository:tag`, but `kubectl set image` still bypasses the backup,
lint, supply-chain, and health-test gates below — always deploy through the
updater. Use:

```bash
export SERVICEOPS_BACKUP_REFERENCE="snapshot-YYYYMMDD-HHMM-before-serviceops-upgrade"
SERVICEOPS_VALUES=deploy/kubernetes/values-production.yaml \
  ./tools/safe_update_k8s.sh <stable-tag> sha256:<verified-64-character-digest>
```

This changes the descriptive tag and governed digest together, uses
`helm upgrade --atomic --wait`, waits for the web rollout, and runs the
packaged readiness test. Atomic rollback restores Kubernetes resources when a
hook, image pull, or readiness check fails; it does not reverse a database
migration. A verified pre-migration backup and migration rehearsal remain
mandatory. The updater fails closed unless the backup reference is supplied;
the chart records it on the migration Job and application pods.

### Stateless, progressive and GitOps operation

ServiceOps web replicas keep durable state in external PostgreSQL and shared
RWX or S3-compatible attachment storage. Signed cookie sessions are
replica-independent; revocation evidence is stored in PostgreSQL. Root
filesystems are read-only. Non-secret configuration is a checksummed ConfigMap
and secrets remain operator-managed Secret references.

Native rolling delivery defaults to `maxUnavailable: 0`, `maxSurge: 1`,
database/schema-aware readiness, startup/liveness probes, preStop drain and an
explicit termination grace period. Argo Rollouts is opt-in with
`progressiveDelivery.enabled=true`; optional Prometheus analysis aborts an
unhealthy canary. Install and rehearse its controller/CRDs before enabling it.
`featureFlags.netbox_sync=false` stops new NetBox synchronization jobs without
rolling back the image.

Use `deploy/gitops/application.example.yaml` to bootstrap Argo CD against a
separate protected environment repository. Promotions are reviewed commits
changing image tag, digest and backup reference. Self-heal is enabled while
automatic prune is disabled to protect stateful resources.

All supported REST routes are below `/api/v1`. Alembic changes use separate
expand, compatible-code/backfill and contract releases. CI blocks destructive
expand operations and requires contract revisions to state the minimum safe
application version.

Enable Prometheus Operator discovery with
`observability.serviceMonitor.enabled=true`. OpenTelemetry instrumentation is
available through an existing Operator Instrumentation resource; enable it
only after the Collector, egress and data-governance policy are verified.

### Protected CI/CD deployment

`.github/workflows/deploy-kubernetes.yml` can deploy automatically after the
governed release reaches terminal success, or by explicit manual dispatch. It
is disabled by default. Configure the repository variable
`KUBERNETES_DEPLOY_ENABLED=true`; optionally configure
`KUBERNETES_NAMESPACE`, `KUBERNETES_RELEASE`, and
`KUBERNETES_IMAGE_REPOSITORY`. Set `KUBERNETES_BACKUP_REFERENCE` to the
completed, restore-tested provider snapshot or dump identifier for each
upgrade; and store base64-encoded kubeconfig and values
content in the protected production environment secrets `KUBE_CONFIG_B64` and
`KUBERNETES_VALUES_B64`. The values file references existing Kubernetes
Secrets and must not contain plaintext application credentials.

The job checks out the immutable release tag, resolves the corresponding GHCR
manifest digest, verifies GitHub provenance, lints and renders the exact chart,
and performs an atomic install/upgrade followed by both rollout checks and
`helm test --logs`. Keep required reviewers and deployment-branch protection
enabled on the GitHub `production` environment.

## Private registry mirrors (Nexus and similar proxies)

Some organizations don't let the cluster pull directly from GHCR and instead
mirror images through an internal proxy such as Sonatype Nexus Repository.
Many Nexus Docker proxy/hosted repository configurations only serve manifests
by tag (`GET /v2/<name>/manifests/<tag>`) and reject a digest-only pull
(`GET /v2/<name>/manifests/sha256:<digest>`) for images they haven't already
cached under that tag — the chart's default `repository@digest` workload
reference then fails to pull, surfacing as a pod stuck in `ImagePullBackOff`
(or, if you instead tried to work around it by leaving `image.digest` blank,
as the `image.digest` Helm schema validation error, since the chart requires
a well-formed digest regardless of pull mode — see below for why).

**This is a pull-mechanism limitation, not a reason to skip verification.**
The digest is still what proves the image is the one that passed the
supply-chain workflow; it's only the *runtime pull reference* that Nexus
can't use. `charts/serviceops/values.yaml` has an `image.pinning` field for
exactly this:

- `image.pinning: digest` (default) — workloads run `repository@sha256:digest`.
  Use this when pulling directly from GHCR or from a registry/proxy that does
  support digest-based manifest requests.
- `image.pinning: tag` — workloads run `repository:tag` instead. Use this
  when the target registry (Nexus or similar) only serves by tag. `digest` is
  still a required field in the chart schema in this mode too, and
  `tools/safe_update_k8s.sh` still requires you to pass the digest you
  verified against GHCR (`gh attestation verify oci://ghcr.io/<org>/serviceops@<digest> --repo <org>/serviceops`)
  as its second argument.

**Set up the mirror once:**

1. Pull and re-tag the verified image, then push it into Nexus under an
   immutable, never-reused tag (the same descriptive version tag ServiceOps
   already cuts per release, e.g. `1.88.0` — never `latest` or a tag that
   gets overwritten):
   ```bash
   docker pull ghcr.io/<org>/serviceops@sha256:<verified-digest>
   docker tag ghcr.io/<org>/serviceops@sha256:<verified-digest> \
     nexus.internal.example.com/serviceops:1.88.0
   docker push nexus.internal.example.com/serviceops:1.88.0
   ```
2. In your values file, set `image.repository: nexus.internal.example.com/serviceops`
   and `image.pinning: tag`. If Nexus requires authentication for pulls,
   configure `imagePullSecrets` with a Secret holding those registry
   credentials (`kubectl create secret docker-registry ...`) — the chart
   already supports `imagePullSecrets` for this.

**Deploy through the updater, same as always**, but with pinning switched to
`tag`:

```bash
export SERVICEOPS_BACKUP_REFERENCE="snapshot-YYYYMMDD-HHMM-before-serviceops-upgrade"
SERVICEOPS_VALUES=deploy/kubernetes/values-production.yaml \
  SERVICEOPS_IMAGE_PINNING=tag \
  ./tools/safe_update_k8s.sh 1.88.0 sha256:<verified-digest>
```

Before touching the cluster, the updater re-resolves `nexus.internal.example.com/serviceops:1.88.0`
in the target registry (`docker buildx imagetools inspect`) and refuses to
deploy if it doesn't currently resolve to exactly the digest you verified —
this is what keeps `tag` mode from silently deploying a tag that moved after
you checked it. Never push a second image under an already-used tag in
Nexus; cut a new version tag instead, exactly as the existing release
tagging policy already requires for GHCR.

The `KUBERNETES_IMAGE_REPOSITORY` variable used by the CI/CD path
(`### Protected CI/CD deployment` above) points at the same
`image.repository` value; set it to your Nexus path there too if the
automated deploy workflow also needs to go through the mirror.

## Web Installation Center

Run `./serviceops install web` and visit `http://127.0.0.1:8090`. The temporary
installer does not receive the Docker socket. It writes a request into a
private local state directory; the host-side script performs Compose actions
and reports application health back to the browser.

The screen confirms Docker and Compose readiness, writable storage, free disk,
listener availability, PostgreSQL authentication/query execution, LDAP TLS
bind and base search, Keycloak discovery metadata, and Production security
policy. Generated environment files are mode `0600`, and validation results
never echo passwords.

### Production-only initialization

ServiceOps creates only the local bootstrap administrator and structural ITIL
groups/SLA definitions. It never creates demonstration personas, manager
placeholders, catalog examples, CMDB examples, assets, or knowledge articles.
Assign real managers and CCB members before governed changes can be submitted.
Use `tools/production_cleanup.py` after backing up an older database that
contains legacy bootstrap demonstration data.

### AD and LDAP

ServiceOps uses a service bind to locate exactly one directory user, then binds
as that user's DN to verify the password. Production requires LDAPS or StartTLS
with certificate validation. A typical AD filter is:

```text
(&(objectClass=user)(sAMAccountName={username}))
```

`LDAP_ROLE_MAPPINGS` maps full group DNs to `requester`, `agent`, `manager`, or
`admin`. Unmapped identities default to `requester`.

After LDAP connectivity is verified, use **Administration home → Service delivery and governance** to map AD
groups to fulfillment teams. A mapping accepts either a short common name such
as `gg_unix` or the complete DN. Membership reconciles at each AD login.
Directory synchronization removes only directory-managed memberships and does
not overwrite manual manager appointments or CCB authority.

### Keycloak

Create a confidential OpenID Connect client with standard authorization-code
flow and this redirect URI:

```text
https://serviceops.example.com/auth/keycloak/callback
```

Enable `openid profile email` and include realm roles in the ID token when
role mapping is needed. `KEYCLOAK_ROLE_MAPPINGS` maps realm role names to
ServiceOps roles. Keep the local administrator credential in an organizational
secrets vault for identity-provider outages.

## Fast installation

Supported host: a current 64-bit Linux server with at least 2 CPU cores, 4 GB RAM, 10 GB free disk, Docker Engine 24+, Docker Compose v2, and outbound access to container registries.

```bash
git clone <your-serviceops-repository> serviceops
cd serviceops
chmod +x serviceops
./serviceops install server
```

The installer performs preflight checks, generates cryptographically random secrets, writes a mode-specific `.env` with `0600` permissions, validates Compose, builds the image, starts services, waits up to three minutes for health, and displays bootstrap credentials once.

For unattended automation:

```bash
./serviceops install server --mode bundled --port 8080 --bind 127.0.0.1 --yes
```

## RPM packaging (Linux distribution)

For hosts that manage software as packages rather than a `git clone`, an RPM
is available. It installs the same control plane the git checkout gives
you -- the `serviceops` CLI, Compose service definitions, the Kubernetes
Helm chart, and operations tooling (backup, restore, migration and upgrade
rehearsal) -- but contains **no application source or Dockerfile**. The
application always runs from a pulled image, never a local build, so
`dnf upgrade` never triggers a container rebuild -- it only ever changes
which image reference the next `serviceops update` pulls. Pass the pushed
image's digest as `build-dist.sh`'s third argument to pin that reference to
an immutable `repository@sha256:...` digest instead of a mutable tag (see
below); without a digest, the package falls back to a mutable version tag
and prints a warning at build time.

Layout after installation:

| Path | Purpose |
|---|---|
| `/opt/serviceops` | Control plane (CLI, Compose files, Helm chart, tools) |
| `/etc/serviceops/serviceops.env` | Generated secrets and configuration (`0600`, real file; `/opt/serviceops/.env` is a symlink to it) |
| `/var/lib/serviceops/backups` | Database/upload backups (`/opt/serviceops/backups` is a symlink to it) |
| `/usr/bin/serviceops` | Symlink to the CLI |
| `systemd` unit `serviceops.service` | Wraps `serviceops start`/`serviceops stop` |
| `serviceops-health.timer` | Two-minute health check and automatic recovery |
| `serviceops-backup.timer` | Daily verified database/upload recovery set |
| `/etc/logrotate.d/serviceops` | Rotation for host-side operational logs |

### Supported RPM platforms

The release pipeline builds and clean-install tests separate packages for the
currently supported Enterprise Linux major families (EL8, EL9, and EL10) and
the currently supported Fedora releases (Fedora 43 and Fedora 44). This
covers current RHEL, Rocky Linux, AlmaLinux, and Oracle Linux releases that are
binary-compatible with the corresponding EL major. Only the current supported
minor release in each major family is supported; hosts must apply normal DNF
security and minor-version updates. Fedora packages follow Fedora's shorter
support lifecycle and must be upgraded as releases retire. Debian and
Ubuntu use `.deb` packages rather than RPM and are outside this RPM matrix.

Build the RPM from a release checkout:

```bash
# Digest-pinned (recommended): pass the pushed image's sha256 digest as the
# third argument so the packaged install uses an immutable repository@sha256:...
# reference instead of a mutable tag.
bash packaging/build-dist.sh 1.78.7 ghcr.io/awijesundara/serviceops-server sha256:<pushed-image-digest>
# Tag-pinned fallback (prints a warning; the tag can later be overwritten):
# bash packaging/build-dist.sh 1.78.7 <your-registry>/serviceops
bash packaging/build-rpms.sh 1.78.7
```

Install and bring it up:

```bash
# Docker CE packages come from Docker's repository, not the base EL repository.
sudo dnf install -y dnf-plugins-core
# RHEL:
# sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
# Rocky/Alma/Oracle Linux use the compatible CentOS repository:
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install ./serviceops-1.78.7-1.el$(rpm -E %rhel).noarch.rpm
sudo serviceops setup --mode bundled --yes
```

The RPM declares Docker Engine, the Compose plugin, systemd, Python, requests,
curl, OpenSSL, tar, gzip, and the remaining host tools as dependencies, so DNF
installs them from configured repositories. Docker's repository must be enabled
as shown above. The package's `%pre` scriptlet adds the
`serviceops` system account to the `docker` group so the systemd unit can
reach the socket without running as root. Until the installer creates
`/etc/serviceops/serviceops.env`, systemd intentionally refuses to start the
unit. Its preflight uses quiet Compose validation so secrets are not rendered
into the journal. `serviceops setup` explicitly enables Docker, initializes the
digest-pinned PostgreSQL and application containers, and enables the application,
health-recovery, and backup timers. Daily recovery sets are written with `0600`
permissions under `/var/lib/serviceops/backups`; by default, sets older than 35
days are pruned while at least seven complete sets are always retained. Configure
`BACKUP_ARCHIVE_*` values for off-host object-locked recovery storage.

The RPM intentionally does not open a firewall or request a public TLS certificate:
those operations require an operator-selected hostname, DNS ownership, and network
policy. The safe default binds ServiceOps to loopback; publish it through the
organization's managed HTTPS load balancer or reverse proxy. The browser-based web installer
(`serviceops install web`) is not included in packaged installs, since it
builds its own Flask app from source -- use `serviceops setup`
instead. Upgrading the RPM upgrades the control plane only; it does not by
itself change the running application version. Run `serviceops update`
(or bump `SERVICEOPS_IMAGE` in `/etc/serviceops/serviceops.env` and
`serviceops restart`) to move to a new pinned image, exactly as in a git
checkout.

## Architecture A: bundled PostgreSQL

Choose this for one-server installations and straightforward backups.

```mermaid
flowchart LR
    I["Internet"] -- HTTPS --> P["HTTPS proxy"] --> S["ServiceOps app"]
    S -- private Compose network --> D[("PostgreSQL")]
    S --> U[["serviceops_uploads volume"]]
    D --> V[["serviceops_postgres_data volume"]]
```

PostgreSQL is not published to the host network. The installer generates its password and starts it with a health gate before the application starts.

Manual equivalent:

```bash
cp .env.example .env
# Set secure values and DEPLOYMENT_MODE=bundled
docker compose --env-file .env -f compose.yaml up --build -d
```

## Architecture B: external PostgreSQL

Choose this for managed databases, high-availability database clusters, separate backup ownership, or multiple application servers.

Before installation:

1. Provision PostgreSQL 14 or newer.
2. Create a dedicated database and least-privilege owner:

   ```sql
   CREATE ROLE serviceops LOGIN PASSWORD 'long-random-password';
   CREATE DATABASE serviceops OWNER serviceops;
   ```

3. Permit the ServiceOps server through the database firewall or private network.
4. Require TLS and obtain the provider CA when using `sslmode=verify-full`.
5. Run:

   ```bash
   ./serviceops install server --mode external
   ```

6. Enter a SQLAlchemy-compatible URL:

   ```text
   postgresql+psycopg://serviceops:password@db.internal.example:5432/serviceops?sslmode=require
   ```

Non-interactive example:

```bash
./serviceops install server \
  --mode external \
  --database-url 'postgresql+psycopg://serviceops:password@db.internal:5432/serviceops?sslmode=verify-full' \
  --port 8080 \
  --bind 127.0.0.1 \
  --yes
```

The external deployment uses `compose.external-db.yaml`; it creates no local database container or database volume. Schema initialization and baseline records are applied through the authenticated database connection.

## HTTPS and network exposure

Keep `BIND_ADDRESS=127.0.0.1` and place ServiceOps behind an HTTPS reverse proxy. Expose only TCP 80/443 publicly. Do not expose PostgreSQL or port 8080 to the internet.

### Caddy

```caddyfile
serviceops.example.com {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8080
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

### Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name serviceops.example.com;
    client_max_body_size 20m;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }
}
```

Use your organization’s certificate automation and security standards.

## Operations

```bash
./serviceops status
./serviceops health
./serviceops doctor
./serviceops logs
./serviceops restart
./serviceops update
```

Bundled database backups:

```bash
./serviceops backup
./serviceops rehearse-recovery
./serviceops rehearse-pitr
```

This writes a PostgreSQL custom-format dump, upload-volume archive, and
SHA-256 recovery-set manifest into `backups/` with owner-only permissions.
`rehearse-recovery` verifies the manifest, rejects unsafe archive entries,
restores into a disposable database, restores uploads into a temporary
directory, verifies the migration head, audit chains, and every attachment
record, reports observed recovery time and recovery-point age, then removes the
isolated recovery environment. Copy recovery sets to encrypted, immutable
off-host storage.

The logical recovery rehearsal does **not** prove point-in-time recovery.
PostgreSQL PITR requires a verified base backup and an uninterrupted continuous
WAL archive. `rehearse-pitr` safely proves those mechanics without changing the
live database: it loads a production logical clone into a disposable
archive-enabled cluster, takes a physical base backup, creates a named recovery
point, archives later WAL, and restores another cluster to the target. It proves
the before-target marker exists and the after-target marker does not, then
validates the ServiceOps schema, audit chain, attachments, and health.
Managed/external PostgreSQL deployments must additionally retain equivalent
provider evidence.

External database backups are intentionally delegated to the database provider. Use provider snapshots, point-in-time recovery, and cross-region copies where appropriate. `./serviceops backup` explains this rather than creating an incomplete application-only database backup.

## Recovery objectives

Define and test:

- Recovery point objective (RPO)
- Recovery time objective (RTO)
- PostgreSQL point-in-time recovery
- Upload-volume recovery
- `.env` secret escrow
- DNS and TLS failover
- Quarterly restore exercises

The database and uploads must be recovered from the same logical backup window.

## Upgrades

```mermaid
flowchart LR
    A["serviceops backup"] --> B["rehearse-upgrade"] --> C["deploy / serviceops update"] --> D["verify health, login, workflows"]
    D -- failed --> E["atomic rollback restores prior release"]
    E -. "DB migrations are never auto-reversed" .-> F["restore from the verified backup"]
```

Supported application upgrades move one released minor version at a time.
Skipping versions requires rehearsing every intervening database migration.
Downgrading application code across an applied schema is unsupported unless the
release notes explicitly identify the schema as backward compatible. PostgreSQL
major upgrades are separate infrastructure changes and require a provider-tested
upgrade or a dump from tooling that is not older than the source server.

Before every ServiceOps release:

```bash
./serviceops rehearse-upgrade
```

This produces a verified rollback recovery set, clones production data into a
guarded disposable database, runs the candidate migration gate, and validates
schema head, tenant audit integrity, attachments, application health, and
continued source health. The command never migrates the production database.

1. Take a verified backup.
2. Review release notes and schema changes.
3. Deploy first to staging.
4. Run `./serviceops doctor`.
5. Run automated tests.
6. Upgrade production with `./serviceops update`.
7. Verify health, login, ticket creation, approval routing, attachment access, and database backups.

## Apple push notification configuration

Configure these encrypted Platform settings before enabling push:
`APNS_TEAM_ID`, `APNS_KEY_ID`, `APNS_BUNDLE_ID`, and the complete `.p8` value
in `APNS_PRIVATE_KEY`; then set `APNS_ENABLED=true`. Development builds register
sandbox tokens and Release builds register production tokens. The bundle ID and
Apple provisioning profile must match `APNS_BUNDLE_ID`.
For the maintained ServiceOps iOS target, set `APNS_BUNDLE_ID` to
`wijesundara.com.ServiceOps`; the web application's default now matches it.

Never commit the `.p8` file, provisioning profiles, certificates, or populated
environment/xcconfig files. Validate on a signed physical iPhone: sign in,
allow notifications, create a notification for that user, confirm delivery and
inbox state, then sign out and confirm the installation is unregistered.

## Security checklist

- Replace all bootstrap credentials immediately.
- Keep `.env` owner-readable only and out of version control.
- Use HTTPS and secure cookies at the reverse proxy boundary.
- Restrict Docker socket access to administrators.
- Keep the application container non-root and read-only.
- Use `no-new-privileges`.
- Keep PostgreSQL private and require TLS for external connections.
- Enable host security updates, monitoring, disk alerts, log forwarding, and backup alerts.
- Integrate organizational SSO before wide deployment.
- Review users, managers, CCB membership, and audit events regularly.

## Scaling

For a first high-availability architecture:

- Use an external managed PostgreSQL service.
- Store attachments in shared object storage through a future storage adapter.
- Run two or more ServiceOps application nodes behind a load balancer.
- Move session state and background work to shared services before horizontal scaling.
- Apply database migrations once per release, not independently from every node.

The current Docker Compose deployment is designed for a highly reliable single application host. It is not presented as a multi-region control plane.
