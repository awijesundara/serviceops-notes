# BP-001 programme traceability

BP-001 defines a multi-release platform programme, not a single feature.
“Covered” below means a currently evidenced foundation exists. It does not mean
the complete section has been delivered.

| BP section | Current foundation | Major missing scope | Disposition |
|---|---|---|---|
| 1 Platform layers | Identity, tasks, ITIL records, service/CI links, approvals, UI, analytics, audit | Formal module boundaries, durable automation, complete governance plane | Programme |
| 2 Queue security | Central ticket/request/enterprise visibility helpers plus governed REST/export/search projections | Compiled relationship-aware policy engine and independent review | P0 |
| 3 Queue catalogue | Ticket lists, task board, approvals, requests | Personal/team/practice/management queue catalogue and saved queue definitions | P1 |
| 4 Authorization | RBAC, tenant-aware root policies, group/relationship checks, transition guards and fail-closed Git-backed field permissions | ABAC/ReBAC policy compiler and independent authorization review | P0 |
| 5 Access levels | Git-backed action vocabulary, role grants, object manage/view separation and governed projections for every supported record API/export/JSON response | Relationship-aware compiled bindings and independent review | P0 |
| 6 Core data model | Existing Ticket, EnterpriseRecord, request/task, history and related models | Common versioned work-item foundation and many listed organisation/metric fields | Architecture decision |
| 7 Relationships | INC/PRB/CHG/REQ/RITM/PTASK/CTASK/SCTASK and CI relationships | Duplicate/outage/alert/release/deployment/vendor/improvement relationships | P1 |
| 8.1 Interaction | No dedicated interaction model | Complete interaction intake/classification/conversion lifecycle | P1 |
| 8.2 Incident | Core incident, parent/child, major profile, SLA, CI and relationships | Full hold reasons, routing, escalation, confirmation, survey and auto-close | P1 |
| 8.3 Major incident | MajorIncidentProfile and coordination fields | Full roles, bridge, stakeholder comms, status page, PIR and follow-up actions | P1 |
| 8.4 Requests/catalog | REQ/RITM/SCTASK, catalog administration, routing, approvals | Catalogs/categories/typed variables/entitlements/bundles/pricing/drafts/order guides | P1 |
| 8.5 Problem | PRB, PTASK, known error, RCA/workaround/fix and links | Configurable models, RCA techniques, clustering, risk acceptance and automation | P1 |
| 8.6 Change | Types, plan, risk, CCB, CTASK, conflicts, reapproval | Standard catalog, CAB meetings, blackout windows, PIR/evidence and retrospectives | P1 |
| 8.7 Knowledge | Basic article list/create/search | Bases, lifecycle, versions, feedback, access rules, analytics and translation | P1 |
| 8.8 Service levels | Definitions, task SLAs, Git-backed priority matrix, governed overrides, business calendars/time zones/holidays, lifecycle evidence and worker breach escalation | OLA/contracts, prediction, retroactive recalculation policy and escalation ladders | P0/P1 |
| 8.9 Events | No event/alert domain | Ingestion, normalization, correlation, suppression, CI binding and incident creation | P1 |
| 8.10 CMDB | CI classes, relationships, task links, conflict checks, admin manual create/edit/retire for CIs and CI relationships, and a REST auto-registration endpoint (`cmdb:write`) with a lightweight Linux/Puppet sync agent | Identification/reconciliation, discovery beyond self-reported facts, health, certification and history | P1 |
| 8.11 Release/deployment | Change tasks only | Separate release/deployment models, evidence, waves, pipeline integration | P1 |
| 8.12 Improvement | Generic enterprise module only | Purpose-built continual-improvement register and outcome tracking | P2 |
| 9 Priority | Priority field | Impact/urgency matrix, justification and controlled P1 criteria | P0 |
| 10 Assignment | Explicit teams (assignment is always by team name, never by picking an individual manager/user), team-scoped assignees, catalog routing, and explicit team-to-team reassignment for incidents/changes that restarts change approval against the new owning team | Ordered configurable rules, skills, on-call, workload and loop detection | P0/P1 |
| 11 Approvals | Chains, gates, any/all/majority, sequential stages and reapproval | Delegation, timeouts, dynamic resolution, signatures and broader policies | P0/P1 |
| 12 Web UI | Shell, lists, forms, board, portal-style catalog, admin settings, type-ahead reference-field search for CIs and cross-record links, a manager portal and cross-record task queue, and admin-configurable dashboard widgets | Advanced list engine, workspace personas, delegation, tabs, tours and mobile | P1/P2 |
| 13 Rules/workflows | Git-backed versions, restricted conditions/actions, reusable cycle-safe subflows, state/manual/API/SLA/scheduled triggers, recurring scheduler, durable waits, step evidence, rate limits, retry/dead state, replay, terminal safe compensation, correlation, idempotency and simulation | Broader actions, calendar/blackout scheduling, concurrency quotas and configuration-promotion governance | P0 |
| 14 Service model | Services, offerings, CIs, assets and relationships | Full hierarchy, governance, reconciliation, certification and import APIs | P1 |
| 15 Search | Access-aware global and domain search | Full text index, facets, typo/synonym support and search analytics | P1 |
| 16 Communication | In-app notifications plus durable SMTP, signed webhook and Teams delivery with retry/dead state and evidence | Templates, preferences, digests, inbound email, SMS/push and external validation | P0/P1 |
| 17 Identity/tenancy | Local, LDAP/AD, Keycloak OIDC, default-tenant migration and tenant-aware root isolation | SAML, SCIM, MFA policy, session inventory, API identity and independent isolation review | Architecture/P0 |
| 18 Security/compliance | Headers, CSRF, server authorization, tenant-chained evidence, governed key rotation, retention/legal hold, signed SIEM delivery, digest-only images, vulnerability gates, keyless signatures, provenance/SBOM attestations and Sigstore admission | Representative registry/cluster/immutable-store validation, malware scanning and independent review | P0 |
| 19 Analytics | Basic access-aware dashboard | Full KPI definitions, time series, CSAT, scheduled reports and governed exports | P1 |
| 20 APIs/integrations | REST v1 ticket/incident contract, tenant/user-bound API identities, scopes (including `cmdb:write` CI auto-registration), cursor pagination, request IDs, OpenAPI and idempotent writes | Broader resources, OAuth2/client assertions, rate limits, webhooks, imports and adapters | P0/P1 |
| 21 Architecture | Flask modular monolith, PostgreSQL, Docker/Helm | Decision on modularization or rewrite plus search/cache/event/object-store services | Architecture decision |
| 22 Config deployment | Container configuration and admin settings | Git-backed configuration packages, diff, validation, promotion and rollback | P0/P1 |
| 23 Implementation order | Several initial/core capabilities exist | Execute dependency-ordered programme with release gates | Governed roadmap |
| 24 Deferred features | Current product largely follows this constraint | Explicit decision records for intentionally deferred advanced features | Governance |
| 25 Credible core | Chains, lifecycle controls and initial tenant isolation verified | Field security, durable timers, calendars, APIs, config versions and DR proof | Release gate |

## Programme acceptance gate

No section becomes `Verified` until its atomic requirements have automated
tests, authorization tests, documentation, migration and rollback evidence,
deployment evidence, and any required external-system validation. External
services such as AD, Keycloak, email, object storage, search and Kubernetes
cannot be certified using mocks alone.

## Approved architecture disposition

| Decision area | Approved BP-001 disposition |
|---|---|
| Tenancy | One organisation initially; enforce tenant identifiers and tenant-aware authorization conventions now |
| Application | Incremental bounded-module refactor behind stable interfaces; no rewrite |
| Theme | Light-only; dark mode is a governed non-requirement |
| Infrastructure | PostgreSQL standard profile; enterprise services are optional adapters over shared contracts |
| Integrations | SMTP/email, signed webhooks, monitoring ingestion, Microsoft Teams |
| API | Versioned REST first; GraphQL deferred pending a demonstrated consumer |
| Mobile | Responsive installable PWA first; preserve future native-client contracts |
| Configuration | Git-backed declarative source; database is deployed runtime state |
| Programme order | Security and platform foundations before visible expansion |
| Data | Preserve through reversible versioned migrations with upgrade, verification and rollback tests |
