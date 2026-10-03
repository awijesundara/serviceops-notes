# ServiceOps deployment and recovery

Use the [documentation index](../README.md) to navigate the six maintained documents. Update this document directly; there is no generated master copy.

## Contents

- [ServiceOps deployment guide](#section-deployment)
- [Full IPFS storage mode](#section-ipfs_storage_mode)
- [Running a model server for ServiceOps (llama.cpp, Apple/AMD GPU example)](#section-ai_self_hosted_server)
- [ServiceOps release and version-control plan](#section-release_governance)
- [ServiceOps production-readiness release gates](#section-production_readiness_plan)

---

<a id="section-deployment"></a>

## ServiceOps deployment guide

<a id="section-deployment--serviceops-deployment-guide"></a>

> For the complete zero-PostgreSQL profile, including upgrade, recovery and
> limitations, see [IPFS_STORAGE_MODE.md](#section-ipfs_storage_mode).
>
> For the full user, administrator, identity, Kubernetes, security,
> monitoring, backup, recovery, upgrade, rollback, and incident-response
> runbook with diagrams and screenshots, see the
> [complete platform manual](OPERATIONS_MANUAL.md#section-operations_manual).

<a id="section-deployment--contents"></a>
### Contents

**Choose and install**
[Deployment topologies](#section-deployment--deployment-topologies) ·
[Fast installation](#section-deployment--fast-installation) ·
[Architecture A: bundled PostgreSQL](#section-deployment--architecture-a-bundled-postgresql) ·
[Architecture B: external PostgreSQL](#section-deployment--architecture-b-external-postgresql) ·
[RPM packaging](#section-deployment--rpm-packaging-linux-distribution) ·
[Kubernetes production deployment](#section-deployment--kubernetes-production-deployment) ·
[Private registry mirrors (Nexus and similar proxies)](#section-deployment--private-registry-mirrors-nexus-and-similar-proxies) ·
[Web Installation Center](#section-deployment--web-installation-center) ·
[Air-gapped deployment boundary](#section-deployment--air-gapped-deployment-boundary)

**Configure identity and access**
[AD and LDAP](#section-deployment--ad-and-ldap) ·
[Keycloak](#section-deployment--keycloak) ·
[Passkeys and Apple Associated Domains](#section-deployment--passkeys-and-apple-associated-domains) ·
[Apple push notification configuration](#section-deployment--apple-push-notification-configuration)

**Expose and monitor**
[HTTPS and network exposure](#section-deployment--https-and-network-exposure) ·
[Service health and monitoring](#section-deployment--service-health-and-monitoring) ·
[Immutable recovery and object storage](#section-deployment--immutable-recovery-and-object-storage)

**Operate**
[Operations](#section-deployment--operations) ·
[Recovery objectives](#section-deployment--recovery-objectives) ·
[Upgrades](#section-deployment--upgrades) ·
[Account and emergency recovery](#section-deployment--account-and-emergency-recovery)

**Secure and scale**
[Security checklist](#section-deployment--security-checklist) ·
[Scaling](#section-deployment--scaling)

**Maintainer and CI notes**
[Mandatory browser quality gate](#section-deployment--mandatory-browser-quality-gate) ·
[Local development deployment convention](#section-deployment--local-development-deployment-convention)

<a id="section-deployment--deployment-topologies"></a>
### Deployment topologies

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

<a id="section-deployment--passkeys-and-apple-associated-domains"></a>
### Passkeys and Apple Associated Domains

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
[complete platform manual](OPERATIONS_MANUAL.md#section-operations_manual).

<a id="section-deployment--mandatory-browser-quality-gate"></a>
### Mandatory browser quality gate

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

<a id="section-deployment--air-gapped-deployment-boundary"></a>
### Air-gapped deployment boundary

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

<a id="section-deployment--outbound-proxy-for-notifications-email-and-update-checks"></a>
#### Outbound proxy for notifications, email, and update checks

The application itself still makes a handful of outbound HTTPS/SMTP calls at
runtime -- Google Chat, Telegram, Slack, Teams, and Discord notification
channels; SMTP mail relay (including Google Workspace's OAuth2 token
endpoint); and an optional daily GitHub release check. Air-gapped and
firewalled deployments route all of these through **Administration →
Connections & channels → Outbound proxy & updates**
(`OUTBOUND_PROXY_URL`), or the `OUTBOUND_PROXY_URL` environment variable as
its seeded default (an admin-saved value in Settings always wins over the
env var once one is saved, matching every other platform setting's
precedence).

Every individual notification channel can also override the platform
default from its own **Settings** page (`Outbound proxy`: use the default,
no proxy, or a proxy specific to that one channel) -- useful when only some
destinations are reachable through a given egress path. Email delivery has
the same three-state override (`SMTP_PROXY_MODE`/`SMTP_PROXY_URL`) on the
same settings page.

`OUTBOUND_PROXY_URL` and a channel's custom proxy are plain `http://` or
`https://` proxy URLs (optionally with `user:pass@` credentials), used
directly as `requests`' proxy for webhook/chat/GitHub calls. SMTP has no
native HTTP-proxy support (SMTP isn't HTTP), so the same URL is instead used
to tunnel the raw SMTP connection through the proxy's `CONNECT` method --
the standard technique browsers use for HTTPS through an HTTP proxy --
implemented in `serviceops_core/proxy_tunnel.py`. A SOCKS proxy is not
supported; if the only available egress path is SOCKS, front it with a
local `http://` CONNECT-capable proxy (e.g. a small `squid`/`privoxy`
sidecar) and point `OUTBOUND_PROXY_URL` at that instead.

When a channel or the update check has a proxy configured, ServiceOps
deliberately skips its own DNS-pinning/private-address pre-check for that
destination (see `deliver_webhook()`'s comment in `app.py`) -- the proxy
resolves the destination on its own side, not this host, so there is
nothing meaningful to pre-validate locally, and the check would otherwise
simply fail closed in a network where the destination hostname can't
resolve at all without going through the proxy. The configured proxy (and
whatever firewall/egress policy controls what it's allowed to reach) is the
trust boundary in that configuration, the same way this chart's Kubernetes
NetworkPolicy egress rules already are.

<a id="section-deployment--interactive-google-chat-bot-ack-escalate"></a>
#### Interactive Google Chat bot (/ack, /escalate)

Beyond the one-way notification channel above (an incoming webhook, alert
out only), ServiceOps can run an **interactive** Google Chat app that reads
`/ack` and `/escalate <team>` typed as threaded replies to an alert and
acts on the record it was sent about -- reusing the exact ticket
transition/reassignment rules the web UI already enforces, not a parallel
implementation. It requires no internet-facing endpoint: events are
delivered via **Cloud Pub/Sub** (ServiceOps pulls, it never receives an
inbound call), which is what makes this workable for an internal-only
deployment.

**One-time Google Cloud setup:**

1. Create or select a Google Cloud project. Enable the **Google Chat API**
   and the **Cloud Pub/Sub API**.
2. Chat API -> Configuration: set the app name/icon/description, enable
   "Join spaces and group conversations". Under **Connection settings**,
   choose **Cloud Pub/Sub topic** (not HTTP endpoint URL) and create/select
   a topic, e.g. `projects/<project>/topics/serviceops-chat-events`.
3. Create a **Pub/Sub subscription** on that topic (Pub/Sub -> Subscriptions
   -> Create), pull delivery type. Note its subscription ID.
4. Create a **Service Account** (IAM -> Service Accounts) for the app, grant
   it the **Pub/Sub Subscriber** role on that subscription and the
   **Chat App** role (or equivalent Chat API posting permission), and
   download its JSON key. This one key is used both to pull events and to
   post replies (`https://www.googleapis.com/auth/pubsub` and
   `https://www.googleapis.com/auth/chat.bot` scopes, exchanged for a
   short-lived access token via the standard JWT-bearer grant --
   `app.py`'s `_google_service_account_access_token()`, implemented with
   `joserfc` rather than adding a Google Cloud SDK dependency).
5. Add the bot to the target Space (search its name in Chat, add like any
   member).

**ServiceOps side** (Administration -> Connections & channels -> Google
Chat bot, and the notification channel's own settings):

1. **Administration -> Google Chat bot**: enable the app, set the Google
   Cloud project ID, the Pub/Sub subscription ID from step 3, and paste
   the service-account JSON key from step 4.
2. **Add a Google Chat notification channel** for the Space that should
   receive alerts and accept replies, with **Delivery mode: Interactive
   app** -- give it the Space resource name (`spaces/AAAAxxxxx`, from the
   Chat API or the Space's own settings) and the *same* service-account
   JSON key. (Delivery mode: Incoming webhook remains available as the
   simpler, non-interactive, lower-configuration option for channels that
   only need one-way alerts.)

The worker process polls the subscription on every cycle (same loop as
`process_outbox()` and every other `process_*_schedule` function --
`tools/outbox_worker.py`), so a reply is picked up within one worker tick,
not on a fixed daily/hourly schedule like the GitHub update check. A
message it can't act on (no thread match, sender email not matching an
active ServiceOps user, an ordinary non-command chat message) is
acknowledged and otherwise ignored rather than left to redeliver.

**Commands must @mention the bot**: reply `@ServiceOps /ack`, not a bare
`/ack` -- required if another Chat app (a different on-call/notification
tool) is also a member of the same space and also reacts to plain
`/ack`/`/close`-style text. Google Chat only ever delivers a *space's*
messages to an app that's explicitly @-mentioned in them (unless that app
opted into receiving every message in every space it's in, which
ServiceOps's own Chat app configuration deliberately does not request --
see step 2 above), so `@ServiceOps /ack` never reaches the other app and
`@OtherApp /ack` never reaches ServiceOps. `extract_message_event()` in
`serviceops_core/google_chat.py` also re-checks this itself (ignores any
message without a bot-mention annotation) rather than relying solely on
Google's delivery-side filtering.

<a id="section-deployment--local-development-deployment-convention"></a>
### Local development deployment convention

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

<a id="section-deployment--service-health-and-monitoring"></a>
### Service health and monitoring

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

<a id="section-deployment--account-and-emergency-recovery"></a>
### Account and emergency recovery

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

<a id="section-deployment--immutable-recovery-and-object-storage"></a>
### Immutable recovery and object storage

Each recovery manifest records a non-secret fingerprint of the exact settings
encryption key. Configure `BACKUP_ARCHIVE_*` to upload database, uploads, and
manifest artifacts to S3-compatible storage. With
`BACKUP_REQUIRE_OBJECT_LOCK=true`, backup fails unless Object Lock is enabled.
Use a KMS key and a separate account/credential from the application.

Set `OBJECT_STORAGE_BUCKET` and related `OBJECT_STORAGE_*` values for
S3-compatible attachments. Empty bucket configuration retains the Docker
volume/PVC backend. Readiness validates the configured bucket before admitting
traffic.

<a id="section-deployment--kubernetes-production-deployment"></a>
### Kubernetes production deployment

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
[Private registry mirrors](#section-deployment--private-registry-mirrors-nexus-and-similar-proxies)
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

<a id="section-deployment--stateless-progressive-and-gitops-operation"></a>
#### Stateless, progressive and GitOps operation

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

<a id="section-deployment--protected-cicd-deployment"></a>
#### Protected CI/CD deployment

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

<a id="section-deployment--private-registry-mirrors-nexus-and-similar-proxies"></a>
### Private registry mirrors (Nexus and similar proxies)

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

<a id="section-deployment--web-installation-center"></a>
### Web Installation Center

Run `./serviceops install web` and visit `http://127.0.0.1:8090`. The temporary
installer does not receive the Docker socket. It writes a request into a
private local state directory; the host-side script performs Compose actions
and reports application health back to the browser.

The screen confirms Docker and Compose readiness, writable storage, free disk,
listener availability, PostgreSQL authentication/query execution, LDAP TLS
bind and base search, Keycloak discovery metadata, and Production security
policy. Generated environment files are mode `0600`, and validation results
never echo passwords.

<a id="section-deployment--production-only-initialization"></a>
#### Production-only initialization

ServiceOps creates only the local bootstrap administrator and structural ITIL
groups/SLA definitions. It never creates demonstration personas, manager
placeholders, catalog examples, CMDB examples, assets, or knowledge articles.
Assign real managers and CCB members before governed changes can be submitted.
Use `tools/production_cleanup.py` after backing up an older database that
contains legacy bootstrap demonstration data.

<a id="section-deployment--ad-and-ldap"></a>
#### AD and LDAP

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

<a id="section-deployment--keycloak"></a>
#### Keycloak

Create a confidential OpenID Connect client with standard authorization-code
flow and this redirect URI:

```text
https://serviceops.example.com/auth/keycloak/callback
```

Enable `openid profile email` and include realm roles in the ID token when
role mapping is needed. `KEYCLOAK_ROLE_MAPPINGS` maps realm role names to
ServiceOps roles. Keep the local administrator credential in an organizational
secrets vault for identity-provider outages.

<a id="section-deployment--fast-installation"></a>
### Fast installation

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

<a id="section-deployment--rpm-packaging-linux-distribution"></a>
### RPM packaging (Linux distribution)

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

<a id="section-deployment--supported-rpm-platforms"></a>
#### Supported RPM platforms

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

<a id="section-deployment--architecture-a-bundled-postgresql"></a>
### Architecture A: bundled PostgreSQL

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

<a id="section-deployment--architecture-b-external-postgresql"></a>
### Architecture B: external PostgreSQL

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

<a id="section-deployment--https-and-network-exposure"></a>
### HTTPS and network exposure

Keep `BIND_ADDRESS=127.0.0.1` and place ServiceOps behind an HTTPS reverse proxy. Expose only TCP 80/443 publicly. Do not expose PostgreSQL or port 8080 to the internet.

<a id="section-deployment--caddy"></a>
#### Caddy

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

<a id="section-deployment--nginx"></a>
#### Nginx

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

<a id="section-deployment--operations"></a>
### Operations

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

<a id="section-deployment--recovery-objectives"></a>
### Recovery objectives

Define and test:

- Recovery point objective (RPO)
- Recovery time objective (RTO)
- PostgreSQL point-in-time recovery
- Upload-volume recovery
- `.env` secret escrow
- DNS and TLS failover
- Quarterly restore exercises

The database and uploads must be recovered from the same logical backup window.

<a id="section-deployment--upgrades"></a>
### Upgrades

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

<a id="section-deployment--apple-push-notification-configuration"></a>
### Apple push notification configuration

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

<a id="section-deployment--security-checklist"></a>
### Security checklist

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

<a id="section-deployment--scaling"></a>
### Scaling

For a first high-availability architecture:

- Use an external managed PostgreSQL service.
- Store attachments in shared object storage through a future storage adapter.
- Run two or more ServiceOps application nodes behind a load balancer.
- Move session state and background work to shared services before horizontal scaling.
- Apply database migrations once per release, not independently from every node.

The current Docker Compose deployment is designed for a highly reliable single application host. It is not presented as a multi-region control plane.


<a id="section-deployment--optional-ai-worker"></a>
### Optional AI worker

The local 1.92.0 candidate adds tenant-administrator-controlled, disabled-by-default AI incident investigations with self-hosted and external OpenAI provider modes. See [AI operations](OPERATIONS_MANUAL.md#section-ai_operations) for setup, permissions, job lifecycle and explicit limitations, and [AI implementation plan](ENGINEERING_REFERENCE.md#section-ai_implementation_plan) for the timeline and current validation evidence. The initial release produces read-only drafts; approved actions and real-model quality acceptance remain pending.

---

<a id="section-ipfs_storage_mode"></a>

## Full IPFS storage mode

<a id="section-ipfs_storage_mode--full-ipfs-storage-mode"></a>

<a id="section-ipfs_storage_mode--status"></a>
### Status

ServiceOps supports a complete, opt-in `STORAGE_MODE=ipfs` deployment. IPFS is
the sole durable application and attachment store; no PostgreSQL service or
persistent embedded database is used. The former B-335 login-only checkpoint
is migrated automatically at first boot.

Feature parity includes the dashboard, internal ticketing, client management,
catalog, knowledge, CMDB, discovery, workflows, administration, users and
roles, settings, notifications, audit history, server-side session inventory
and revocation, rate limiting, APIs, mobile authentication, attachments,
analytics, scheduled work, and health monitoring.

<a id="section-ipfs_storage_mode--architecture"></a>
### Architecture

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

<a id="section-ipfs_storage_mode--upgrade-from-b-335"></a>
### Upgrade from B-335

When no `relational_state` exists but the old checkpoint contains `tenant` and
`user` entity maps, startup imports those records, preserves password hashes
and IDs, runs the standard idempotent seed for all platform defaults, and
publishes a full checkpoint. This is automatic and does not require resetting
the Kubo volume or administrator account.

Do not rotate or discard `SETTINGS_ENCRYPTION_KEY`, `SECRET_KEY`, or the Kubo
key repository during the upgrade. Losing the encryption key makes checkpoint
and attachment content unrecoverable.

<a id="section-ipfs_storage_mode--deployment"></a>
### Deployment

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

<a id="section-ipfs_storage_mode--recovery-and-backup"></a>
### Recovery and backup

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

<a id="section-ipfs_storage_mode--deliberate-operating-boundary"></a>
### Deliberate operating boundary

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

---

<a id="section-ai_self_hosted_server"></a>

## Running a model server for ServiceOps (llama.cpp, Apple/AMD GPU example)

<a id="section-ai_self_hosted_server--running-a-model-server-for-serviceops-llamacpp-appleamd-gpu-example"></a>

ServiceOps talks to any OpenAI-compatible server. This page records the working reference setup used for testing: a 2019 MacBook Pro (Intel Core i9, AMD Radeon Pro 5500M with 8 GB VRAM) running llama.cpp's `llama-server` through Vulkan (MoltenVK). Any other server (Ollama, vLLM, LM Studio) works the same way from ServiceOps' side; see [AI_OPERATIONS.md](OPERATIONS_MANUAL.md#section-ai_operations).

<a id="section-ai_self_hosted_server--what-was-measured"></a>
### What was measured

| Setup | Qwen3-8B Q4_K_M | Notes |
|---|---|---|
| CPU only (8 threads) | about 5.5 tokens/s, 99 s per streamed investigation | Metal on this GPU was slower than CPU; Ollama also CPU |
| Vulkan on the Radeon Pro 5500M (`-ngl 99`) | about 21.6 tokens/s generation, 52 s per streamed investigation | Prompt processing is the slow part (first token 4-34 s for chat prompts) |

Qwen3 models can use a reasoning pass. ServiceOps shows a small temporary **Thinking** status but never displays or stores the model's private reasoning text. Qwen2.5 models generally answer without a reasoning stream.

<a id="section-ai_self_hosted_server--build-and-run"></a>
### Build and run

```
# Build once (Vulkan, not Metal)
cd ~/llama.cpp
cmake -B build-vk -DGGML_VULKAN=ON -DGGML_METAL=OFF && cmake --build build-vk --config Release -j8

# Environment the GPU path needs (put in ~/.zprofile for SSH sessions)
export DYLD_LIBRARY_PATH=/opt/local/lib
export VK_DRIVER_FILES=/opt/local/share/vulkan/icd.d/MoltenVK_icd.json
export MVK_CONFIG_LOG_LEVEL=0
export GGML_VK_VISIBLE_DEVICES=0        # 0 = Radeon, 1 = Intel UHD

./build-vk/bin/llama-cli --list-devices   # must list Vulkan0: AMD Radeon Pro 5500M

# Serve (keep the key in a file, not on the command line where `ps` shows it)
./build-vk/bin/llama-server -hf Qwen/Qwen3-8B-GGUF:Q4_K_M -dev Vulkan0 -ngl 99 -fa off \
  -c 8192 --jinja --host 0.0.0.0 --port 8080 --api-key-file ~/ai/api-key
```

`-c 8192` matters: ServiceOps investigations send up to about 10,000 characters of evidence, so a 4096-token context can be too small. 8 GB of VRAM holds the 8B Q4 model (about 5 GB) plus an 8192-token cache.

<a id="section-ai_self_hosted_server--connect-serviceops"></a>
### Connect ServiceOps

1. Operator: allow the server. Kubernetes: `ai.selfHostedEndpoints: "http://192.168.68.68:*"` and an `ai.extraEgress` rule for `192.168.68.68/32` (no `ports` = every port), then Helm upgrade. Compose: `AI_SELF_HOSTED_ENDPOINTS=http://192.168.68.68:*`.
2. Administrator: Administration, Platform and security, AI assistance. Choose **Server on your network**, address `http://192.168.68.68:8080`, paste the key. The model (for example `Qwen/Qwen3-8B-GGUF:Q4_K_M`) and its context window are detected automatically. Tick the master switch, incident investigations and the chat assistant; save; **Test saved connection**.
3. Try it: open an incident and choose **Investigate with AI**, or use **Ask AI** at the bottom right. Tick **Think step by step** in the chat to watch the reasoning.

<a id="section-ai_self_hosted_server--keep-it-running-macos"></a>
### Keep it running (macOS)

A launchd agent restarts the server and survives logout. Template (`~/Library/LaunchAgents/com.serviceops.llama-gpu.plist`), then `launchctl load` it while logged in to the desktop session:

```
<plist version="1.0"><dict>
  <key>Label</key><string>com.serviceops.llama-gpu</string>
  <key>EnvironmentVariables</key><dict>
    <key>DYLD_LIBRARY_PATH</key><string>/opt/local/lib</string>
    <key>VK_DRIVER_FILES</key><string>/opt/local/share/vulkan/icd.d/MoltenVK_icd.json</string>
    <key>GGML_VK_VISIBLE_DEVICES</key><string>0</string>
  </dict>
  <key>ProgramArguments</key><array>
    <string>/Users/USER/llama.cpp/build-vk/bin/llama-server</string>
    <string>-m</string><string>/Users/USER/ai/models/Qwen3-8B-Q4_K_M.gguf</string>
    <string>-dev</string><string>Vulkan0</string><string>-ngl</string><string>99</string>
    <string>-fa</string><string>off</string><string>-c</string><string>8192</string><string>--jinja</string>
    <string>--host</string><string>0.0.0.0</string><string>--port</string><string>8080</string>
    <string>--api-key-file</string><string>/Users/USER/ai/api-key</string>
  </array>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
</dict></plist>
```

A closed lid sleeps the Mac unless `sudo pmset -a disablesleep 1` is set (or the lid stays open on power).

<a id="section-ai_self_hosted_server--troubleshooting"></a>
### Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Pages stall, then load without styling | A request thread is blocked. Filter System Health → Logs by logger `serviceops.crash`: each stuck request (longer than `SLOW_REQUEST_REPORT_SECONDS`, default 30) is recorded with its thread stack, as are worker timeouts and arbiter SIGKILL/OOM messages. Records are spooled in `LOG_DIR/crash-spool` and imported by the next worker to boot |
| "This endpoint has not been allowlisted..." | The operator has not listed that server; the message names the entry to add |
| "Provider rejected the request" | Wrong or empty API key, or wrong model identifier |
| "The server rejected the API key" during detection | Key mismatch with `--api-key-file` |
| Answer never starts / times out | Server unreachable from the pod (`ai.extraEgress`), model still loading, or `AI_PROVIDER_TIMEOUT_SECONDS` too low for CPU inference |
| Very slow first word | Long prompt on a small GPU; use a smaller model or raise nothing else; prompt processing dominates |
| Context window warning | Restart the server with `-c 8192` or larger |

---

<a id="section-release_governance"></a>

## ServiceOps release and version-control plan

<a id="section-release_governance--serviceops-release-and-version-control-plan"></a>

<a id="section-release_governance--policy"></a>
### Policy

ServiceOps uses Semantic Versioning (`MAJOR.MINOR.PATCH`) and a single source
of truth: `ServiceOps/VERSION`. A release is immutable. A published tag is
never moved or rebuilt; a correction receives a new patch version.

- **Patch**: compatible fixes, security patches, and documentation/runtime corrections.
- **Minor**: backward-compatible capabilities or schema additions.
- **Major**: intentional breaking API, configuration, deployment, or schema contracts.

<a id="section-release_governance--automated-release-path"></a>
### Automated release path

1. Push signed changes to `main`; every push runs the supply-chain gate.
2. When the gate succeeds, **Governed release** runs automatically as a patch
   release. For a minor or major release, run it by manual dispatch with
   `increment: minor` or `major`. Never edit the version files by hand.
3. The workflow reads `VERSION`, calculates the next version, and synchronizes the runtime version, Helm chart and default image tag, README badge, service-worker cache identifiers, example environment, graphical installer, and CLI server installer.
4. It commits `chore(release): X.Y.Z`, creates the immutable annotated `vX.Y.Z` tag, and invokes the reusable supply-chain workflow against that exact tag.
5. The supply-chain gate runs release-consistency, Ruff correctness, bytecode, migration-head, complete-test-suite, shell/JavaScript syntax, both Compose-mode, and dependency-audit checks; it then builds and scans the image, generates an SBOM, pushes by source SHA, signs it, and publishes provenance/SBOM attestations.
6. Only after all gates pass does automation publish the GitHub release and generated release notes.

If a post-tag gate fails, there is no published GitHub release. Fix forward and
issue a new patch release; do not replace the failed tag. The release commit is
created through the GitHub API (`tools/release_commit.py`), so GitHub signs it,
and the tag is created only after that commit lands on `main`. If a version's
tag already exists from an earlier run, the workflow skips to the next version
of the same increment.

After the new release is deployed to MicroK8s and verified, delete every older
git tag and GitHub release so only the newest remains (GHCR image versions are
kept).

<a id="section-release_governance--branch-and-change-controls"></a>
### Branch and change controls

- Current state (2026-10-03): the active `security` ruleset on `main` requires
  verified signatures, blocks force pushes and branch deletion, and requests
  Copilot code review on push. The sole maintainer pushes directly, and the
  supply-chain gate runs on every push. Pull requests, approvals and tag
  restrictions are the target once more than one person contributes.
- Every commit is authored and committed as Anushka Wijesundara and SSH-signed
  (GitHub "Verified"); no AI or bot attribution except the release workflow's
  `chore(release)` commit.
- `v*` tags are created only by the release automation.
- Use short-lived branches and descriptive commit subjects.
- Pair application changes with `serviceops-notes` changes whenever backlog, architecture, operational risk, or release evidence changes.
- Keep database migrations additive during a minor release line. Breaking migrations require a major release and a tested rollback/restore path.

<a id="section-release_governance--required-evidence"></a>
### Required evidence

Each release retains the test run, dependency audit, container scan, CycloneDX
SBOM, image digest, Cosign signature, GitHub provenance attestation, migration
head, and generated release notes. Production promotion records the digest,
environment, approver, backup/recovery-set identifier, and rollback outcome.

---

<a id="section-production_readiness_plan"></a>

## ServiceOps production-readiness release gates

<a id="section-production_readiness_plan--serviceops-production-readiness-release-gates"></a>

No item below is complete merely because scaffolding exists. Each gate requires
dated evidence, an owner, a reviewed result, and remediation of release-blocking
findings in the governed backlog.

| Gate | Required outcome | Evidence needed |
|---|---|---|
| External security | Independent penetration test; all critical/high findings remediated or formally risk-accepted | Signed report, remediation PRs, retest letter |
| Tenant isolation | Independent review of every tenant-owned model, query, API, attachment, job, export, and migration | Review matrix plus adversarial cross-tenant test results |
| Supply chain | Real tagged GHCR build; signature/provenance verification; unsigned and untrusted images rejected by a representative cluster | Workflow URL, digest, attestations, admission logs |
| Recovery | Encrypted off-site immutable backup plus successful database/uploads restore within approved RPO/RTO | Recovery manifest, timings, integrity checks, approval |
| Upgrade and rollback | Two-version production-like rollout and forced migration/application failure with successful rollback | Runbook transcript, health evidence, restored fingerprints |
| Observability | Structured logs, metrics, traces, alert rules, SLO dashboards, and incident runbooks | Dashboard export, alert tests, SLO ownership |
| Performance | Load, soak, worker backlog, failover, and capacity tests against published targets | Workload model, results, bottlenecks, capacity envelope |
| Object storage | Supported encrypted object storage, malware scanning, retention/legal hold, and failure handling | Adapter tests, scan evidence, lifecycle policy |
| Identity | Enforced MFA through supported IdP, SCIM lifecycle, session inventory/revocation, and tested emergency access | IdP test record, joiner/mover/leaver evidence |
| Accessibility | Independent WCAG 2.2 AA audit with keyboard, screen-reader, zoom, contrast, and reduced-motion coverage | Audit and remediation verification |
| Privacy | Approved classification, retention, legal hold, access/export/deletion, regional controls, and DPA/DPIA operationalization | Control mapping and exercised data-subject workflows |

<a id="section-production_readiness_plan--delivery-order"></a>
### Delivery order

1. Tenant isolation and external security review.
2. Supply-chain cluster proof, recovery, and rollback rehearsals.
3. Observability and performance baselines.
4. Object storage and identity lifecycle controls.
5. Accessibility and privacy validation.

Production promotion remains blocked until gates 1–3 have no unresolved
critical/high issue and the accountable owner explicitly accepts residual risk.

<a id="section-production_readiness_plan--current-implementation-checkpoint--2026-08-13"></a>
### Current implementation checkpoint — 2026-08-13

ServiceOps 1.67.0 has substantially deepened the internal scaffolding behind
several gates since the 2026-08-05 checkpoint below — most notably Privacy
(classification/retention/legal-hold/GDPR export-deletion, tracked as
B-090, code-complete and internally verified), Object storage (S3-compatible
storage with a supported migration tool and outage-degradation evidence,
B-052), Observability (Prometheus/Alertmanager rules with real rehearsal
evidence, B-070/B-071), and Accessibility (a mandatory desktop/mobile
Playwright plus axe-core CI gate over four critical workflows, B-323). Global
search also has PostgreSQL trigram indexes and avoids request-time full-object
ID materialization. **None of this closes any gate in the table above**:
per this document's own standard, a gate requires independent or
organization-executed evidence (an external penetration test, an
organization's own approved DPA/DPIA sign-off, a real production-scale load
test), not internal code-level verification alone, however thorough. See
`BACKLOG.md` for current, item-by-item status; the historical 1.38.2
checkpoint and its remediation plan are below for record only.

<a id="section-production_readiness_plan--prior-checkpoint--2026-08-05-historical"></a>
#### Prior checkpoint — 2026-08-05 (historical)

ServiceOps 1.38.2 improved release consistency, CI quality checks, one
redirect boundary, and shared accessibility semantics. It did not close any
gate in the table above. Scope and evidence are in
[REMEDIATION_PLAN_1.38.2.md](BACKLOG.md#section-remediation_plan_1.38.2) (now superseded; see that file).

### Syslog receiver network access

Application settings or environment variables SYSLOG_ENABLED, SYSLOG_HOST, SYSLOG_PORT, SYSLOG_TRANSPORT and SYSLOG_LEVEL configure forwarding at process startup. In Kubernetes, allow the chosen receiver with narrow destination and port rules in Helm values `syslog.extraEgress`; the rules apply to web, outbox and AI worker NetworkPolicies. Keep the default empty list until a receiver is selected. Syslog records use [RFC 5424](https://www.rfc-editor.org/info/rfc5424/) and stream transports use octet-counting framing from [RFC 6587](https://www.rfc-editor.org/info/rfc6587/). TLS verifies the receiver using the system trust store. UDP cannot confirm receipt; TCP/TLS socket success also does not establish remote durable retention. Locally emitted records remain in the existing log sinks.
