# ServiceOps complete feature catalogue

**Catalogue baseline:** ServiceOps 1.62.6<br>
**Last code audit:** 12 August 2026<br>
**Evidence base:** application routes, models, templates, configuration,
migrations, tools, deployment manifests, and automated tests in `ServiceOps`.
<br>Note: this pass targeted the specific gaps identified below (new
capabilities added since the 1.46.0 baseline, and the §24 boundary
contradiction); it is not a full section-by-section re-audit of every prior
entry.

This is the canonical inventory of implemented ServiceOps functionality. It
describes working product behavior, not roadmap aspirations. Features that
depend on external systems are labelled accordingly; incomplete or externally
unverified capabilities are listed under “Explicit boundaries.”

## 1. Application shell and user experience

- Authenticated shell with a compact persistent accordion navigator and global
  controls.
- Role-aware menus that hide inaccessible destinations.
- Canonical Home, My work, Self-service, Management, Operations, and
  Administration applications with one-at-a-time expansion, automatic current
  section opening, exact module highlighting, and a menu-only filter.
- Nested User management navigation for users, groups/teams/access,
  roles/permissions, and active sessions.
- Administration home with categorized entry points and consistent return
  context on child administration pages.
- Global search across authorized records and navigation destinations.
- PostgreSQL trigram-indexed global search with authorization-preserving ID
  subqueries and a separately tested immutable navigation catalogue.
- Type-ahead lookup and browser for configuration items and record links.
- User favorites and recently viewed page history.
- Application/workspace directory and cross-domain My Tasks/Open Work queues.
- Persisted sidebar scroll state and navigation state.
- Blocking desktop/mobile browser QA for Dashboard, Administration, CMDB, and
  Client Management, including console-error detection and axe-core WCAG 2.2
  AA serious/critical violation checks with failure traces and screenshots.
- Acting-role switcher limited to roles actually granted to the user.
- User preferences for density, font scale, date format, timezone, dashboard
  widgets, list-page size, high contrast, and reduced motion.
- Company/instance name, logo, primary color, and accent-color branding.
- Responsive layouts, print styles, keyboard skip link, focusable main
  landmark, labelled dialogs/actions, and reduced-motion support.
- Progressive Web App manifest and versioned service worker.
- Contextual help centre and inline explanatory tooltips.
- Notification inbox with unread state, target click-through, mark-all-read,
  clear, and navigation badges.
- Self-service profile, contact/location fields, directory-managed field
  indicators, timezone/date preferences, and validated PNG/JPEG avatar.
- Manager-based organization chart.

## 2. Identity, authentication, roles, sessions, and tenancy

### Authentication and recovery

- User-authenticated native mobile sessions for local and LDAP accounts, with
  MFA, short-lived access tokens, rotating refresh tokens, Keychain storage,
  revocation, tenant/role/team authorization, and per-user app/device audit
  attribution. Shared embedded API keys are not used by the iOS client.
- Optional foreground biometric lock using Face ID, Touch ID, Optic ID, or the
  device passcode recovery path, backed by device-only Keychain storage.
- Apple platform-passkey registration and passwordless sign-in using
  HTTPS-only, tenant/user-bound, expiring single-use WebAuthn challenges,
  user verification, signature-counter tracking, self-service credential
  inventory/revocation, request throttling, and audited mobile sessions.

- Local username/password authentication with Argon2id hashes.
- Transparent upgrade of legacy PBKDF2 hashes after successful login.
- Configurable password policy and audited password changes.
- LDAP/Active Directory authentication when configured.
- Keycloak OpenID Connect when configured, with optional exact `acr`
  requirement for identity-provider MFA assurance.
- TOTP MFA enrollment, verification, policy enforcement, one-time recovery
  codes, and recovery-code regeneration.
- Per-IP and per-account login throttling, failed-attempt tracking, temporary
  lockout, and audited blocked attempts.
- Non-enumerating forgot-password response; throttled, time-limited,
  single-use reset tokens; successful reset unlocks the account and revokes
  existing sessions.
- Authenticated synthetic-login monitoring probe.
- Guarded break-glass administrator recovery: explicit confirmation,
  pre-mutation recovery set, password rotation, unlock, session revocation,
  and audit event.

### Roles, sessions, and tenants

- Requester, agent, manager, administrator, and super-administrator roles.
- Authorization actions resolved from validated governed policy.
- Multi-role grants and user-selected acting role without privilege creation.
- Directory-managed/locked role grants.
- Server-recorded browser session inventory with creation, last seen, client,
  and revocation data.
- Self-service and tenant-administrator session revocation.
- Authentication-version invalidation after security-sensitive changes.
- Tenant model and tenant-aware user, operational, CMDB, service, workflow,
  integration, audit, and configuration data.
- Authenticated tenant resolution fails closed instead of guessing tenant 1.
- Super-administrator tenant administration and tenant-aware root isolation.
- Object authorization on lists, direct IDs, dashboards, boards, analytics,
  searches, attachments, approvals, links, requests, and tasks.

## 3. Users, teams, directory, and organization

- Searchable tenant-scoped user administration.
- Local user creation and editing; active status, primary/additional roles,
  department, manager, and profile fields.
- User self-service profile and personal-data export.
- Governed erasure/anonymization that preserves required record/audit integrity.
- Support groups/teams, membership, and manager designation.
- Team-scoped assignee selection and explicit team reassignment.
- Team aliases for spelling, historical, and imported names; safe duplicate
  team merge through alias governance.
- Directory group-to-team mappings.
- Separate tracking of directory-managed and local memberships.
- Manual, dry-run, and scheduled LDAP directory synchronization.
- Directory sync updates linked users’ profile attributes, reporting manager,
  and mapped team memberships; tenant failures are isolated in the worker.

## 4. Shared work and ticket behavior

- Unique record numbers, requester, ownership, assignee, state, source,
  priority, timestamps, and audit/event history.
- Priority calculated by configurable impact/urgency matrix.
- Permission-controlled priority override with reason.
- Configurable new-record default priority.
- Team assignment/reassignment and team-limited assignee choices.
- Comments/work notes, file attachments, checklist items, linked records,
  linked configuration items, related tasks, and lifecycle stepper.
- Soft deletion where governed record removal is supported.
- Search, filter, pagination, column preferences, and CSV exports.
- Visual task board protected by the same server lifecycle guards as forms.
- Cross-domain open-work and My Tasks queues.
- Cross-record relationships among supported operational records.
- Satisfaction/CSAT prompt and response for eligible completed work.

## 5. Incident management

- Incident creation/editing with caller, contact type, impact, urgency,
  calculated priority, category, service/CI context, team, assignee, state,
  description, notes, and resolution information.
- Incident queues, assigned views, dashboard counts, analytics, and export.
- Central transition enforcement; resolved records lock protected edits while
  allowing controlled comments and reopen.
- Parent/child incidents and optional parent-state synchronization.
- Major-incident promotion, impact statement, commander, communications,
  timeline, review fields, and post-incident review.
- Related problems, changes, requests, CIs, tasks, and record links.
- Monitoring-event ingestion with deduplication/correlation into incidents.

## 6. Problem, known error, and continual improvement

- Problem lifecycle, ownership, priority, related incidents/CIs, and tasks.
- Root-cause, workaround, known-error, and permanent-fix analysis.
- Known-error register derived from governed problem analysis.
- Problem task creation and history.
- Continual-improvement register with source record, owner, benefit, priority,
  status, target date, progress updates, and detail view.

## 7. Enterprise operational workspaces

ServiceOps provides a consistent governed record experience for operational
domains that do not use the dedicated incident, change, request, or asset data
models. Each workspace has a searchable/filterable list, creation form, record
detail, lifecycle state, priority and risk, requester, due date, ownership,
approval option, related records, linked CIs, work tasks, history, attachments,
global-search results, analytics, and overdue reporting where applicable.

- **Customer service:** Support case, Complaint, Return/RMA, and Onboarding.
- **HR service delivery:** Benefits, Payroll, Employee relations, HR systems,
  and Onboarding.
- **Security operations:** Security incident, Vulnerability, Data loss, and
  Threat intelligence.
- **Risk and compliance:** Risk, Control test, Policy exception, and Audit
  finding.
- **Strategic portfolio:** Demand, Project, Program, Objective, and Agile epic.
- **Field service:** Work order, Installation, Repair, and Preventive
  maintenance.
- **IT operations events:** Alert, Infrastructure event, Service degradation,
  and RT Ticket.
- **Releases:** Release, Deployment, and Readiness review.
- Customer, HR, security, and risk records use involvement and owning-team
  visibility rules to protect sensitive work; administrators retain governed
  tenant-scoped access.
- Requesters may create customer-service and HR records; broader operational
  workspaces require an operational role.
- Optional approval routes a newly created record to an active administrator,
  notifies the approver, and records the decision and comments in history.
- Work tasks are assigned to active IT fulfillment teams, constrain assignees
  to team members/managers, and enforce task-state transitions.

## 8. Change management and governance

- Standard, Normal, and Emergency changes.
- Planned window, implementation/test/backout plans, risk, environment,
  ownership, configuration items, and business context.
- Risk scoring and configurable governance policy.
- Approval chains, ordered gates, votes, and Change Control Board approval for
  governed environments, criticality, or explicit CI policy.
- Approval authority through teams and governance groups.
- Material plan changes supersede approval; plan editing is blocked after
  implementation starts.
- Enforceable change freeze windows with emergency exception behavior.
- Scheduling-conflict detection and evidence.
- Ordered planning, implementation, and review Change Tasks.
- Task unlocking follows approval/execution state; server guards prevent
  bypass through forms, boards, tasks, or direct requests.
- Post-implementation review with outcome/evidence.
- Change revisions and ownership history.

## 9. Service catalogue and request fulfillment

- Employee-facing active service catalogue.
- Catalogue item administration: name, category, description, delivery target,
  approval policy, active status, and fulfillment team routing.
- Inactive items fail closed.
- Service Desk fallback routing and seeded Laptop/Software Request items.
- Orders create Request (REQ), Requested Item (RITM), and Catalog Task (SCTASK)
  hierarchy.
- Request/RITM detail, lifecycle progress, opened/opened-by, approval, task,
  attachment, and item information.
- Approval prerequisites validated before record creation.
- Catalogue tasks support assignment, notes, controls, attachments, state,
  and audit history.
- Production work can require a linked approved change.
- RITM state aggregates from tasks; REQ state aggregates from items.
- Authorized addition of items to an existing request.
- Request queues and CSV export.

## 10. Knowledge management

- Searchable knowledge base with categories.
- Article create, view, edit, archive, author, active state, and timestamps.
- Article version history.
- Role-aware authoring and administration.
- Knowledge available from self-service and operational contexts.

## 11. CMDB, topology, imports, discovery, and assets

### Configuration Management Database

- Configuration items with class, environment, criticality, lifecycle,
  addresses, vendor/model, asset identifiers, location, owners/teams, cost
  context, discovery source, CCB policy, and extensible attributes.
- Authorized CMDB list, create/edit, filtering, column controls, and CSV export.
- Parent/child CI relationships and relationship types.
- Service-impact analysis using service-to-CI mapping and dependencies.
- Interactive draggable topology with discovered/manual visual distinction.

### Import and synchronization

- CSV CMDB import with parse, normalize, validate, dry-run, create/update, and
  summary behavior.
- Team/owner resolution and protection of NetBox-governed records.
- NetBox synchronization for devices and virtual machines, including
  interfaces, ports, power ports, inventory, location, IPv4/IPv6, out-of-band
  IP, vendor, platform, and additional attributes when supplied.
- NetBox URL, encrypted token, CA certificate, and explicitly marked
  last-resort TLS-verification bypass.
- Self-registering CMDB agent and Puppet deployment example.

### Agentless discovery and review

- Administrator-defined host or bounded CIDR targets with SNMP metadata,
  encrypted community material, port, optional schedule, and interval.
- Concurrent subnet discovery, SNMP enrichment, TCP-liveness fallback, reverse
  DNS, vendor inference, and CI-class inference.
- Manual Run now and scheduled worker execution with timestamp/status/summary.
- Candidates are staged; discovery never silently writes directly to CMDB.
- Review search is case/Unicode-normalized and token-aware across name,
  address, class, vendor, and source, including cross-column multi-word terms.
- Class, vendor, and source filters; shown/selected count; select/deselect
  filtered or every row; indeterminate master checkbox; clear filters.
- Add selected, add all, discard batch, and delete target.
- Reconciliation protects richer existing SNMP data from later bare liveness
  results.

### Assets

- Asset register with tag, name, type, status, assigned user, location,
  purchase/warranty dates, cost, and notes.
- Asset create and list/search/filter experience.

## 12. Services, schedules, SLAs, and outages

- Service offerings with description, owner, and active state.
- Service-to-CI mappings and impact context.
- SLA definitions by record type and priority with target minutes, schedule,
  and active state.
- Business schedules with timezone, weekdays, working hours, and holidays.
- Business-time deadline calculation.
- Task SLA instances with due time, pause/resume, breach state, and events.
- Background breach processing and notifications.
- Dashboard/analytics breached and at-risk indicators with configurable warning
  window.
- Service outage records and service availability reporting.
- Administration of services, commitments, calendars, and SLAs under Service
  delivery and governance.

## 13. Approvals and service governance

- Ordered approval chains and gates.
- Gate approver source, policy, individual votes, actor, decision, and time.
- My Approvals and chain-status views.
- Catalogue and change approval flows and notifications.
- Approval authority, governance groups, CCB policy, and freeze windows.
- Server lifecycle guards prevent approval bypass.
- Consolidated administration of ticket defaults, catalogue routing, directory
  mapping, aliases/ownership, services, schedules, SLAs, approval policy, and
  governance groups.

## 14. Workflow and automation

- Governed declarative workflow package and schema validation.
- Restricted conditions/actions, validated subflows, and subflow
  materialization.
- Immutable published versions and package digest.
- Event/record context matching.
- Durable PostgreSQL workflow jobs with retries, failure/dead states,
  correlation, execution evidence, step evidence, and idempotency.
- State-entry notification/history actions and scheduled workflows.
- Administrator validation, safe simulation, publication, and execution view.
- Controlled workflow-state repair utility.

## 15. Integrations and APIs

### REST and SCIM

- OpenAPI JSON and interactive API documentation.
- Hashed-secret API clients with tenant, scopes, expiry, revocation, and
  last-used tracking.
- Ticket list/detail, incident create, ticket patch, CMDB CI upsert,
  workflow-event, and monitoring-event endpoints.
- JSON errors, request identifiers, rate limits, stored idempotency, and
  role-aware response field projection.
- SCIM 2.0 Users list/create/get/replace/patch/deactivate using the
  tenant-scoped `users:provision` scope.
- SCIM external ID/email mapping, audited lifecycle, and immediate session
  invalidation on deactivation.

### Durable integrations and external adapters

- Administrator integration connections with encrypted secrets.
- Signed webhook, Microsoft Teams, and immutable audit/SIEM connection types.
- Durable outbox events, delivery evidence, retryable worker processing, and
  manual processing trigger.
- Tenant-scoped monitoring sources with one-time API tokens and assignment to
  an active IT fulfillment team.
- LDAP/AD authentication and sync; Keycloak OIDC; NetBox sync; RT migration;
  monitoring ingestion; and configured SMTP email delivery.
- RT import supports URL/token/CA/query/status mapping, dry run, queued job,
  incident/change/event mapping, priority/state/user/team/time/custom-field/
  correspondence/attachment preservation, external IDs, and duplicate
  prevention.

## 16. Dashboards, analytics, and reporting

- Role-aware dashboard with configurable assigned/recent/SLA/operational
  widgets.
- Manager portal for team workload and service performance plus CSV export.
- Analytics across incidents, requests, changes, problems, SLAs, services, and
  operational performance.
- Overdue-work detail report.
- KPI snapshots and snapshot-state tracking.
- CSV/data exports for supported ticket/request/CMDB/manager/audit/error/log
  queues and personal-data export.

## 17. Audit, privacy, and application security

### Audit and privacy

- Tenant-aware audit actor/action/target/detail/time/request context.
- Encrypted tenant audit keys and chained tamper-evident signatures.
- Key rotation, historical verification keys, and guarded recovery boundary.
- Audit browser, export, retention policy, and automated route-coverage tests.
- Personal-data export and governed erasure/anonymization.
- ROPA, DPIA, data-subject-rights, retention, breach, and DPA documentation in
  `docs/gdpr`.
- Secret redaction in structured application logging.

### Security controls

- Same-origin Content Security Policy, CSRF protection, secure session policy,
  configurable HSTS, frame/content-type/referrer/permissions headers.
- Validated internal redirects.
- Upload limits/type validation and authorization-aware downloads.
- Optional ClamAV attachment scanning.
- Encryption at rest for platform/integration credentials.
- Validated authorization, priority, projection, and workflow configuration.

## 18. Attachments and storage

- Attachments on supported tickets, enterprise records, catalogue tasks, and
  comment/work-note contexts.
- Authorized download and governed filename/type/size handling.
- Local persistent-volume storage by default.
- S3-compatible object storage option with readiness check and configured
  local fallback.
- Optional malware scanning.

## 19. Administration and system health

- Administration home covering users/access, service governance, settings,
  integrations, API clients, workflows, audit, tenants, and health.
- Sticky administration breadcrumb/context and clear return path.
- Platform settings for organization/branding, appearance, local/LDAP/OIDC
  authentication, security/limits/sessions/uploads, workspace/dashboard
  defaults, email, NetBox, RT, and genuine infrastructure defaults.
- Live-versus-rollout-required setting indication, validation, and audit.
- Service delivery/governance workspace for operational configuration.
- System Health: application/database/worker status, version/migration,
  readiness, backup age/status, error inventory with clear/export, and
  application-log browser/export.

## 20. Observability and reliability

- `/health`, `/live`, and deep `/ready` endpoints.
- Readiness verifies PostgreSQL, exact Alembic head, active-tenant audit-key
  decryptability, worker heartbeat, upload writability, and configured S3.
- Prometheus metrics with optional bearer-token protection: HTTP requests,
  status/duration, worker, errors, backup age, and version.
- Deployable Prometheus alert rules.
- Structured JSON app/request/Gunicorn/worker logs.
- Response/log request IDs and W3C `traceparent` correlation.
- Database-backed application-error inventory.
- Synthetic login and concurrent stability probes with latency percentile,
  throughput, and error reporting.
- Worker isolates tenant/job failures so unrelated scheduled work continues.

## 21. Backup, recovery, and continuity

- PostgreSQL/uploads recovery sets with timestamp and checksummed manifest.
- Non-secret encryption-key fingerprint in recovery manifests.
- Manifest verification, safe extraction, database verification, restore, and
  post-restore validation tooling.
- PostgreSQL point-in-time recovery rehearsal.
- Blue/green deployment and rollback scripts.
- Pre-mutation backup for guarded administrator/audit-key recovery.
- Encrypted S3-compatible recovery archive with Object Lock/retention support.
- Backup-status recorder feeds metrics and System Health.
- Controlled production cleanup and workflow repair utilities.

## 22. Deployment, packaging, database, and releases

### Deployment and packaging

- Unprivileged Docker image.
- Docker Compose application, PostgreSQL, and worker; external-DB,
  blue/green, and web-installer profiles.
- Helm application/worker/migration job, service, ingress, secrets, service
  account, persistence, optional PostgreSQL, health test, HPA,
  PodDisruptionBudget, and NetworkPolicy.
- RPM and systemd packaging.
- Nginx and Caddy reverse-proxy examples.

### Database and release governance

- Alembic baseline/current migrations and startup migration gate.
- Fresh install, upgrade, downgrade/re-upgrade, and PostgreSQL rehearsal tests.
- Canonical semantic version synchronized across runtime, installer, chart,
  README, service worker, and deployment defaults.
- Governed major/minor/patch workflow refusing stale source.
- Pre-release full tests, Ruff, compilation, shell/JavaScript syntax,
  migration-head, and Compose validation.
- Python dependency CVE audit, immutable GHCR image, high/critical image scan,
  CycloneDX SBOM, keyless Cosign signature, SLSA/SBOM attestations, registry
  digest verification, GitHub release/tag, and generated release notes.
- Kubernetes installer support for image-attestation admission policy.

## 23. Test and demonstration support

- Explicit disposable test-fixture loader with users, teams, governance roles,
  and reference records plus visible non-production warning.
- Realistic demo-data loader across CMDB, incidents, problems, changes,
  requests, catalogue, and knowledge.
- Cleanup procedure for generated data.
- Automated coverage of application behavior, authorization, audit,
  compliance, CMDB/import/discovery, LDAP, NetBox, RT, workflow, recovery,
  migrations, installer, release versioning, and security hardening.

## 23a. Guided tours and contextual help ([[B-120]])

- Admin-authored guided tours (`GuidedTour`/`GuidedTourStep` models) with
  ordered steps, versioning, and role targeting.
- CSP-safe overlay player (`static/guided-tour.js`) driven by
  `/api/guided-tours/active` and per-step progress recorded via
  `/api/guided-tours/<id>/progress` (`UserTourProgress`).
- Admin authoring UI at `/admin/guided-tours`.

## 23b. Configurable personal workspace ("My Workspace", [[B-121]])

- Per-user, drag-configurable landing page (`/workspace`) built from a
  closed, code-defined widget catalog (`WORKSPACE_WIDGET_REGISTRY`: ticket
  stats, my open tickets, recent tickets, SLA-at-risk, approvals awaiting
  me, favorites, recently viewed, notifications).
- Layout persisted per user (`UserWorkspaceLayout`); individual widgets can
  be disabled instance-wide via admin settings.
- **Not** a general-purpose page/metadata-runtime designer — see §24.

## 23c. Data classification, retention, and privacy ([[B-090]])

- `DataRetentionPolicy` and `RecordLegalHold` models governing retention and
  legal-hold state.
- `DATA_CLASSIFICATION_REGISTRY` mapping record types to classification.
- GDPR Art. 17/20-style erasure and export for `ClientContact` records, with
  an admin UI for reviewing/actioning requests.

## 23d. Client support mailbox (email-to-ticket, [[B-052]] adjacent)

- Client Management support mailbox admin page for configuring an
  IMAP/SMTP-polled inbox.
- Inbound polling creates/threads `ClientTicket`s from real email
  (`process_client_email_inbox`), with attachment ingestion through the same
  storage/malware-scan path as other attachments.
- Outbound replies sent via the configured mailbox's SMTP
  (`deliver_client_email_reply`), threaded via `In-Reply-To`/`References`.
- Basic-auth IMAP/SMTP only (no OAuth) — Gmail/O365 app-password or
  equivalent required; no content-based spam scoring beyond loop/rate-limit
  defenses.

## 23e. Native iOS operations workspace and push notifications ([[B-327]])

- User-authenticated iOS 1.3 workspace with local/LDAP, MFA, biometric lock,
  passkeys, rotating mobile sessions, and authoritative username/app/device
  audit attribution.
- APNs registration is bound to the authenticated tenant user. Device tokens
  are encrypted at rest, indexed only by a one-way hash, and disabled when
  Apple reports them invalid or unregistered.
- Durable push delivery runs through the integration outbox worker, preserving
  retries and delivery evidence. Notifications carry only display text and
  opaque record identifiers; protected record data is fetched under current
  authorization after the app opens.
- Native notification inbox with unread badge and read/read-all actions;
  mobile bootstrap/profile and assignment teams; ticket list/detail/update,
  incident creation and activity comments; tenant-scoped attachment listing,
  authenticated download, and native Quick Look preview; approval decisions; searchable
  knowledge; and searchable read-only CMDB inventory.
- iOS navigation uses Home, My Work, Create, Inbox, and More. More exposes
  Approvals, Knowledge, CMDB, and Settings/Security without overloading tabs.
- The installed application version and build are always visible under More >
  About and repeated in Settings > About. Both values come from the signed app
  bundle, so the UI cannot drift from Xcode release/build metadata.
- The web Self-service navigation, global search, and Help Center expose a
  dedicated ServiceOps mobile page with the maintained iOS repository link,
  supported capabilities, connection steps, and APNs prerequisites.
- Production APNs still requires an Apple push key, matching signed profile,
  physical device, and HTTPS-reachable ServiceOps deployment.

## 24. Explicit boundaries

ServiceOps does **not** claim these as complete built-in capabilities:

- General-purpose visual page/metadata-runtime designer (arbitrary new page
  layouts, custom fields-as-widgets, drag-in third-party components). A
  closed-catalog personal workspace exists — see §23b — but it is not this.
- Arbitrary low-code flow/action marketplace; workflow actions are restricted.
- Built-in SAML adapter; implemented enterprise identity adapters are LDAP and
  Keycloak OIDC.
- MID Server equivalent.
- Guaranteed network discovery of devices exposing neither SNMP nor a probed
  TCP liveness port.
- Completed external penetration test or independent tenant-isolation review.
- Production validation against every customer IdP, SCIM client, SMTP/S3,
  NetBox/RT, alert receiver, or Kubernetes admission environment.
- Approved organizational RPO/RTO or completed real-cluster disaster and
  rollback exercises. Rehearsal tooling exists; acceptance evidence is
  external.

See [BACKLOG.md](BACKLOG.md),
[PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md), and
[TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md) for evidence status and open
acceptance boundaries.

## 25. Maintenance rule

Every user-visible feature addition, removal, or material behavior change must
update this catalogue in the paired `serviceops-notes` change. A capability
must not be called implemented without a working route, API, background
process, deployment control, or operator command; persistent state where
required; authorization enforcement; and risk-appropriate automated or
recorded runtime evidence.
