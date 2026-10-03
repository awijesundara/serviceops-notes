# ServiceOps collaboration instructions

ServiceOps is an independent, production-oriented ITSM platform. It is completely separate from the Ollama project. Never modify or use files from /Users/anushka/Github/Ollama while working on ServiceOps.

## Project direction

1. ServiceOps is inspired by established ITIL and enterprise ITSM patterns, but must not falsely claim complete ServiceNow compatibility or parity.
2. Preserve the existing product and improve it through bounded modules and stable interfaces. Do not perform a disguised rewrite.
3. PostgreSQL is the default, standard production database. An optional, install-time IPFS-backed storage mode exists for self-hosted, database-less deployments (`STORAGE_MODE=ipfs`); it is not a substitute for PostgreSQL in multi-tenant, high-scale, or compliance-sensitive production deployments unless and until it has separately documented production-readiness evidence per the "Validation expectations" section. It ships as an optional adapter behind the same interface, not a fork, per rule 10.
4. REST is the primary API. Do not introduce GraphQL without a demonstrated consumer requirement.
5. The UI is light-mode only. Dark mode is an explicit governed non-requirement.
6. The product is responsive and PWA-first. Preserve authentication and API designs that could support native clients later.
7. Configuration should be Git-backed and declarative where practical. Database records represent deployed runtime configuration.
8. Prioritize security and platform foundations before decorative or low-value feature expansion.
9. Preserve existing data through reversible, versioned migrations. Never modify production schemas ad hoc.
10. Enterprise integrations must be optional adapters, not separate architectural forks.

## Production-grade standard (effective 2026-07-30)

Per explicit user direction, every change from this date forward is held to a production-grade standard by default, without needing to be asked each time:

- Build and test against real dependencies (live PostgreSQL, live LDAP/OIDC test instances, actual Docker builds) wherever the environment allows it, rather than stopping at unit tests or mocks.
- Follow this file's existing "Deployment after changes" and "Collaboration report format" sections in full for every change, not just large ones.
- "Production ready" still requires documented production-readiness evidence per the "Validation expectations" section below, and is never inferred from a passing unit-test suite. This standard raises the bar on verification; it does not relax the honesty requirements elsewhere in this file — never report a change as tested, deployed, or production ready unless it was actually verified.
- When live infrastructure (Postgres, LDAP, Kubernetes, etc.) is unavailable in the working environment, say so explicitly as a remaining risk rather than skipping the verification silently.

## Versioning, tagging and commit identity (updated 2026-10-03)

Versions and tags are produced only by the **Governed release** workflow (see
"Complete release obligation" below). This replaces the 2026-07-30 rule of
bumping versions and tagging by hand on every push.

1. Never edit the version files by hand (`VERSION`, `charts/serviceops/Chart.yaml`
   `version`/`appVersion`, `values.yaml` image tag, `README.md` badge,
   `static/service-worker.js`, `.env.example`, `installer/app.py`,
   `tools/install/server.sh`, `packaging/rpm/serviceops.spec`). The release
   workflow reads `VERSION`, bumps it and writes all of them in its own
   `chore(release): X.Y.Z` commit. A hand-edited version blocks or skews the
   next release.
2. Semantic versioning, judged from the actual diff: patch for fixes, minor for
   new user-facing capability or additive schema, major for breaking changes.
   Every successful quality gate on `main` releases a patch automatically; use
   the workflow's manual dispatch (`increment: minor` or `major`) for larger
   changes.
3. The workflow creates its release commit through the GitHub API, so GitHub
   signs it (`main` requires verified signatures), and creates the tag only
   after that commit lands. If a version's tag already exists from an earlier
   run that never reached `main`, the workflow skips to the next version of the
   same increment. Never move or delete a tag to make room.
4. Record the version in the relevant `docs/BACKLOG.md` entry so its rationale
   is traceable.
5. Never retag or move an existing tag to a different commit; if a tag was
   wrong, cut a new version. The only exceptions were full-history rewrites the
   user explicitly authorized (2026-08-04, 2026-08-05, 2026-10-02/03).
6. Every commit is authored and committed as `Anushka Wijesundara
   <anushka@wijesundara.com>` and SSH-signed (`commit.gpgsign=true`,
   `gpg.format=ssh`) so GitHub shows it as Verified. No AI or bot attribution
   anywhere: no Claude, Codex, Copilot or other agent identity as author or
   committer, no `Co-authored-by:` or `Claude-Session:` trailers, and no
   `claude/` or `codex/` branch names in merged history. The one standing
   exception is the release workflow's own `chore(release)` commit by
   `github-actions[bot]`, which GitHub signs.
7. **Before merging any PR, check the merge commit message for an
   auto-inserted `Co-authored-by:` trailer and strip it.** GitHub adds one for
   every distinct commit author on the branch, including bots and agents.
   Prefer merging locally (fast-forward or a signed merge commit) so the result
   is signed by Anushka; a GitHub web merge records `web-flow` as committer.

## Release retention (effective 2026-09-26)

Per explicit user direction, keep only the newest release: after a new
version publishes and is verified deployed, delete every older git tag and
GitHub Release (the release object and its assets) so only the current one
remains. Do not delete GHCR container package versions this way -- that is
a separate resource with a different blast radius (another deployment could
still be pulling one by tag) and is only touched if separately requested.
This is a standing step in the governed release process now, not a one-time
cleanup: it was first performed on 2026-09-26 across 98 tags / 78+ releases
going back to v1.80.x.

## Complete release obligation (effective 2026-08-23)

Per explicit user direction, every improvement that is pushed must complete the
same governed release lifecycle, including documentation-only improvements:

1. Update application, operator, installation, and companion-repository
   documentation affected by the change.
2. Run the complete application, lint, compilation, migration, shell,
   JavaScript, Compose, browser, accessibility, dependency, and vulnerability
   gates applicable to the change. Record real limitations rather than silently
   substituting mocks for unavailable infrastructure.
3. Use the governed semantic-version workflow. Never move or reuse a tag.
4. Publish and verify the immutable GHCR image, signature, SBOM, and provenance.
5. Clean-build and install-test all supported RPM targets, publish every RPM and
   checksum as GitHub release assets, and verify their provenance.
6. Publish a non-draft, non-prerelease GitHub release and confirm that it is the
   current stable release with the expected artifacts.
7. Wait for hosted CI to reach a terminal successful state before reporting the
   release complete.

The governed release workflow must keep these steps automated. Every successful
quality-gate run for the current `main` commit automatically enters the patch
release pipeline; minor and major increments use its manual dispatch. If any
stage fails, fix the cause and cut a new version where immutability requires it;
never rewrite a published tag or replace an immutable artifact in place.

## Production-only policy

Never restore or introduce:

- Demo mode
- Demo-agent personas
- Shared demo accounts
- Temporary test credentials in the UI
- Weak default passwords
- Sample operational records in production
- Automatically seeded production tickets
- Visible credentials
- Hard-coded secrets
- JNX branding or company-specific text

Legacy identities referenced by historical approvals or audit records must be disabled or tombstoned, not hard-deleted if deletion would damage history.

The installer and administrator settings must support customizable:

- Company name
- Product display name
- PNG company logo
- Branding colors
- Authentication providers
- Database connection
- SMTP
- Webhooks
- Monitoring ingestion
- Microsoft Teams
- LDAP/Active Directory
- Keycloak/OIDC

## Authentication and authorization

Supported authentication patterns are:

- Local bootstrap administrator
- Active Directory/LDAP
- Keycloak/OIDC

The local bootstrap administrator must be handled securely and must not have a known default password.

Cloudflare Access (or an equivalent reverse-proxy identity layer sitting in
front of the deployment) may additionally be trusted as a *login shortcut*
into one of the patterns above, never as a fifth independent authentication
backend: when `CLOUDFLARE_ACCESS_TEAM_DOMAIN`/`CLOUDFLARE_ACCESS_AUD` are
configured, `/login` verifies the edge-issued `Cf-Access-Jwt-Assertion`
JWT (signature, audience, expiry against Access's own JWKS) and, only on a
verified match to an existing active local user's email, establishes the
same session `login_user()`/local login already creates -- it does not
create, provision, or elevate accounts, and every other authentication
requirement in this section (lockout, MFA, audit, tenant scoping) still
applies to the account being logged into. This is additive to, not a
replacement for, local/LDAP/Keycloak: any deployment not fronted by such a
proxy is entirely unaffected, and the feature is a no-op unless both env
vars are explicitly set.

Enforce tenant_id and tenant-aware authorization everywhere, even when only one organization currently exists.

Tenant resolution must fail closed. Never silently default an authenticated user with a missing tenant_id to tenant 1.

Tenant boundaries must be enforced in:

- Queries
- Writes
- Relationships
- Background jobs
- Notifications
- Webhooks
- API endpoints
- Audit records
- Unique constraints
- Administration screens
- Import/export operations

AD group mappings must support automatic user provisioning and team assignment. For example:

gg_unix -> Unix

Administrators must be able to configure:

- AD group to ServiceOps team mappings
- Team membership
- Team manager
- CCB eligibility
- Approval authority
- Multiple applicable AD groups
- Conflict resolution and mapping priority
- Disabled and removed-user handling

## IT teams and governance

The established teams are:

- CoreApps
- Database
- Network
- Windows
- Unix
- SSD

Each team has a manager with management-level authority for that team. Team managers can be configured as CCB members.

CCB means Change Control Board.

Incidents and changes may be visible across IT teams, but mutation permissions must be more restrictive. Visibility never grants the authority to modify, assign, progress, resolve, approve, or close a record.

Requests, RITMs, catalog tasks, problem tasks, and change tasks must be visible and mutable according to requester, fulfiller team, assignment, managerial authority, approval role, and administrative privileges.

A team must not progress or resolve another team's assigned work merely because the record is visible.

## ITIL record model

Preserve the proper relationship model:

- INC: Incident
- PRB: Problem
- PTASK: Problem Task
- CHG: Change Request
- CTASK: Change Task
- REQ: Request container
- RITM: Requested Item
- SCTASK: Catalog fulfilment task
- KB: Knowledge article
- CI: Configuration Item

Key rules:

- INC restores service.
- PRB investigates root cause.
- PTASK is investigation work under a PRB.
- CHG controls and authorizes production modification.
- CTASK executes a work package under a CHG.
- REQ contains one or more RITMs.
- RITM represents an individual requested catalog item.
- SCTASK fulfils a RITM.
- Approvals are decision records, not CTASKs or SCTASKs.
- SLA records track commitments against tasks.
- Knowledge preserves reusable resolutions and workarounds.
- CMDB relationships identify affected and impacted infrastructure and services.

Do not collapse these records into one generic ticket workflow.

## Change governance

Support Standard, Normal, and Emergency changes with distinct governance.

A change must not reach implementation states unless its required approval chain is satisfied.

Normal-change governance should support:

- Technical/team-manager approval
- Change-manager authorization
- CCB approval
- Risk and impact assessment
- Planned implementation window
- Conflict detection
- Implementation plan
- Test plan
- Backout plan
- Affected CIs
- Impacted services
- Change tasks
- Post-implementation review

Emergency changes require an accelerated but auditable approval route. "Submitted late" is not an emergency justification.

Standard changes remain recorded but may use a governed pre-authorized template.

Material modifications after approval must:

1. Be recorded in ticket history.
2. Identify the actor and changed fields.
3. Preserve before and after values safely.
4. Invalidate affected approvals.
5. Return the record to the appropriate pre-approval state.
6. Create a new approval cycle.
7. Notify the correct active approvers exactly once.
8. Never reactivate obsolete approval records.

Examples of material change fields include scope, implementation plan, test plan, backout plan, affected CIs, risk, impact, schedule, assignment group, and business purpose.

## Catalog routing

Catalog item routing must be configurable by administrators and must not be hard-coded into application logic.

Current expected defaults include:

- Software Request -> Windows
- Laptop Request -> Windows

Administrators must be able to create new catalog items and configure:

- Owning fulfilment team
- Approval policy
- Form variables
- Fulfilment tasks
- Sequential or parallel fulfilment
- SLA policy
- Eligibility
- Automation
- Required change creation
- Active/inactive state

## Security requirements

Treat all authorization as server-side enforcement. Hiding a button is not authorization.

Required controls include:

- CSRF protection
- Secure session lifecycle
- SESSION_COOKIE_SECURE enabled in production
- HttpOnly and appropriate SameSite cookies
- Content Security Policy
- Safe return/start-page validation to prevent open redirects
- Tenant-scoped authorization
- Immutable or tamper-evident audit history
- Request size limits
- File-upload validation
- Malware scanning or quarantine adapter
- Content-type and extension verification
- Cryptographic attachment hashes
- Attachment authorization and retention controls
- SSRF-resistant webhooks
- DNS and redirect validation for outbound webhook destinations
- Signed webhooks
- Secret redaction
- Rate limiting
- Idempotency for mutating integrations
- Dependency and container scanning
- Least-privilege containers and database roles

Never log passwords, tokens, connection strings, LDAP bind passwords, session identifiers, or other secrets.

## Migrations and releases

Alembic migration history, source code, Docker image, Compose configuration, Helm chart, installer, documentation, and release evidence must agree on the same version and migration head.

Never:

- Rewrite an already-deployed migration
- Delete a migration to make a test pass
- Stamp a database without verifying its schema
- Reset or flush a database without explicit user authorization
- Use destructive Git commands
- Discard unrelated user changes

Every new migration must be:

- Versioned
- Reversible where technically possible
- Tested against PostgreSQL
- Verified from the previous supported revision
- Verified at head
- Tested for rollback
- Included in the built deployment image

## Deployment targets

Maintain support for:

- Docker Compose with bundled PostgreSQL
- Docker Compose with external PostgreSQL
- Kubernetes through Helm
- External LDAP/AD
- Keycloak/OIDC
- SMTP
- Signed webhooks
- Monitoring ingestion
- Microsoft Teams

The web installer and post-installation administration interface must validate connections without exposing secrets.

Installer success checks should cover:

- Database connectivity and privileges
- Migration status
- Persistent storage
- LDAP bind and search
- OIDC discovery and callback configuration
- SMTP connection
- Webhook destination
- Teams integration
- Background worker
- Application health
- Required secrets
- TLS/proxy assumptions

Do not claim that a connection works unless it has actually been tested.

## Engineering workflow

Before changing anything:

1. Read the repository status and current branch.
2. Inspect all relevant implementation, migration, test, deployment, and documentation files.
3. Preserve existing uncommitted changes.
4. Identify the root cause rather than patching only the visible UI.
5. State the intended bounded change.
6. Check whether an existing migration or interface already covers it.

When implementing:

1. Keep business rules in testable services or policy modules.
2. Avoid expanding the monolithic application file unnecessarily.
3. Enforce policy at the service/database boundary, not only in templates.
4. Add negative authorization tests, not only successful-path tests.
5. Add tenant-isolation tests.
6. Add migration tests for schema changes.
7. Keep API, UI, worker, and notification behavior consistent.
8. Update controlled documentation and backlog entries alongside implementation.
9. Do not mark backlog items complete without corresponding evidence.

## Documentation control

Internal engineering documentation (governance, backlog, traceability, engineering
reference, deployment guide, API reference, this file) lives in the sibling
`serviceops-notes` repo, not in this repo's GitHub history. Controlled documentation
begins at `serviceops-notes/README.md`. The six maintained documents are
`docs/OPERATIONS_MANUAL.md` (usage and capabilities),
`docs/ENGINEERING_REFERENCE.md` (architecture and governance),
`docs/DEPLOYMENT.md` (deployment and recovery), `docs/API_REFERENCE.md`
(public API contract), `docs/COMPLIANCE.md` (privacy and security controls),
and `docs/BACKLOG.md` (work register, traceability and dated evidence).
Update their sections directly. Do not recreate separate indexes, master
copies, per-feature documents or archive duplicates. Historical evidence
must remain dated and distinguished from current operating instructions.

This `ServiceOps` repo's GitHub-visible docs are limited to `README.md`,
`docs/ServiceOps_Complete_Platform_Manual.pdf` (the public user manual),
`docs/API_REFERENCE.md` (the public REST API reference — the one deliberate
carve-out, effective 2026-08-05, since integrators need it and it contains no
internal governance/backlog/security-posture material), plus the screenshots
referenced by the README. Everything else under `docs/` is gitignored here
(see `.gitignore`) and must never be re-added to this repo's git history.

`docs/API_REFERENCE.md` in this repo is the maintained original; the copy at
`ServiceOps/docs/API_REFERENCE.md` is a byte-identical mirror. Never let the
original diverge from what's published — after any edit here, re-run
`tools/sync_api_reference.sh` (or copy it manually) in the same change so
both are updated together.

Keep these synchronized in `serviceops-notes` where they exist:

- Documentation index
- Product backlog
- Traceability matrix
- Architecture decisions
- Security model
- ITIL workflow documentation
- API documentation
- Installation and deployment manual
- Administrator manual
- User manual
- Production-readiness assessment
- Migration and rollback instructions
- Release evidence

This file is maintained here in `serviceops-notes/CLAUDE.md`; the local, untracked
`ServiceOps/CLAUDE.md` must be a byte-identical copy.

After editing this file or any doc that belongs in `serviceops-notes`, copy the
changed file(s) into `/Users/anushka/Github/serviceops-notes` and commit there too —
see that repo's own README for the sync procedure. Do not delete local docs because
they are gitignored here; they must still be maintained, just in the notes repo.

## Validation expectations

For each meaningful change, run proportionate validation, including as applicable:

- Full automated test suite
- Focused regression tests
- PostgreSQL migration upgrade verification
- PostgreSQL rollback verification
- Linting
- Static typing
- Dependency audit
- Supply-chain verification
- Container image build
- Docker Compose startup
- Application and worker health checks
- Browser-level workflow testing
- Cross-team authorization testing
- Cross-tenant isolation testing
- Approval and reapproval testing
- Attachment security testing
- Webhook SSRF and signing tests
- LDAP/OIDC integration tests where configured
- Kubernetes template/lint checks
- Persistence and restart tests

A healthy /health endpoint alone is not sufficient production evidence.

## Deployment after changes (updated 2026-10-03)

The delivery target is the MicroK8s cluster, namespace `operations`,
`serviceops.wijesundara.com`. Environment values live in
`/Users/anushka/Github/k8s/serviceops-values-microk8s.yaml`; commit that file
(signed) whenever the deployed image changes, and never commit Secret values.

Two stages, never mixed up:

1. **Candidate (optional, before pushing).** A locally built image may be
   pushed to the in-cluster registry (`localhost:32000`) and deployed by digest
   for acceptance testing. A candidate is temporary.
2. **Release (always).** Once the change is pushed and the Governed release has
   published `vX.Y.Z`, deploy that release's GHCR image by digest
   (`ghcr.io/awijesundara/serviceops-server@sha256:...`, tagged by release
   commit SHA) with the chart from the same tag. Production must not be left on
   a candidate built from uncommitted source.

For every upgrade:

1. Only one agent or person deploys at a time. Before starting, confirm no other
   `helm` process is running and `helm history serviceops -n operations` shows
   no `pending-*` revision. Another collaborator may be mid-deploy.
2. Take a backup (`kubectl create job --from=cronjob/serviceops-backup`) and
   restore-test it into a scratch database; use that job as
   `database.backupReference`.
3. Run `helm upgrade ... --wait --timeout 10m` **without `--atomic`**. The
   migration job commits schema changes before the pods roll; an automatic
   rollback then leaves old pods that refuse the newer schema (this caused a
   full outage on 2026-10-02). If an upgrade fails, roll forward. Roll back only
   after restoring the verified backup.
4. Verify web and worker rollouts, `helm test`, `/health` and `/ready`, the
   Alembic head, ticket and user counts, Cloudflare Access (302) and recent
   logs. A skipped check is a reported gap.
5. Report the deployed version, digest, Helm revision and migration revision.

Do not tell the user a change is deployed until the running environment has been checked.

### MicroK8s footprint (effective 2026-10-03)

Per explicit user direction, only the Cloudflare tunnel and the jump host are
fail-safe; everything else runs one lean replica:

- `cloudflared`: two replicas, one per node, PodDisruptionBudget `minAvailable: 1`.
- Jump host: one pod; its Longhorn volume keeps two replicas, one per node, so it
  can restart on either node.
- ServiceOps web, workers, FlowOps, Baseline, website: one replica each with small
  requests and limits. ServiceOps uses `allowSingleReplica: true`.
- Longhorn: CSI controllers one replica each, UI scaled to zero, new volumes default
  to one replica.

## Current review priorities

Re-check these against the current source because another collaborator may already have changed them:

1. Ensure the deployed image contains the database's current Alembic revision.
2. Remove hard-coded migration-rehearsal revision assumptions.
3. Make tenant context fail closed.
4. Add tenant_id to dependent records and tenant-scope applicable constraints.
5. Investigate Gunicorn worker timeouts, worker deaths, and possible OOM conditions.
6. Align versions across the installer, Compose, Helm, environment examples, image tags, and release evidence.
7. Enable secure production cookie defaults.
8. Complete attachment scanning, quarantine, hashing, storage, and authorization.
9. Harden webhooks against DNS rebinding and redirect-based SSRF.
10. Prevent duplicate reapproval notifications.
11. Validate stored redirect/start-page destinations.
12. Add a Content Security Policy.
13. Continue decomposing oversized modules through stable bounded interfaces.
14. Expand REST API coverage only through governed, versioned endpoints.
15. Add browser, accessibility, load, failover, LDAP, Keycloak, SMTP, Teams, and Kubernetes evidence.

## Collaboration report format

At the end of each task, report:

- Outcome
- Files changed
- Schema/migration changes
- Security and authorization impact
- Tests executed and exact results
- Deployment image/version
- Deployed migration revision
- Runtime health checks
- Manual test URL and credentials only if securely created for an explicitly authorized test environment
- Documentation/backlog updates
- Remaining risks or unverified areas

Use precise language:

- "Implemented" means source code changed.
- "Tested" means name the exact test and result.
- "Deployed" means the running environment was rebuilt and verified.
- "Production ready" requires documented production-readiness evidence and cannot be inferred from a passing unit-test suite.

If you encounter an ambiguous product decision, collect all material questions and ask them together. Do not repeatedly interrupt the user for small implementation choices that can be safely inferred from the established architecture.
