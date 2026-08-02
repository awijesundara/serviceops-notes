# Product governance and non-deviation policy

## Product boundary

ServiceOps is an independently implemented service-management platform. It
must not be described as ServiceNow, ServiceNow-compatible, certified, or as
containing “all ServiceNow features.” Reference material may inform workflows
and usability; implementation status is proven only by repository evidence and
tests in the traceability matrix.

## Non-negotiable controls

1. Production-only runtime: no demo mode, shared personas, sample records, or
   default credentials.
2. No requirement is “done” without acceptance criteria, implementation
   evidence, tests, documentation, and an accountable reviewer.
3. Existing audit and approval history is preserved. Referenced removed users
   are tombstoned, never silently deleted.
4. Security-sensitive defaults fail closed. Secrets are supplied externally,
   encrypted where persisted, and never printed in validation results.
5. Schema changes require versioned, reversible migrations and backup/restore
   evidence before production rollout.
6. Production releases use immutable image tags or digests, two or more
   replicas on Kubernetes, external highly available PostgreSQL, TLS, and
   tested recovery.
7. LDAP/Keycloak, Kubernetes, restore, load, and security claims require tests
   against representative external systems. Static configuration is not proof.
8. Product changes update `BACKLOG.md`, `TRACEABILITY_MATRIX.md`, the decision
   log below when applicable, and the relevant manual in the same change.

## Change gate

Every release must pass unit/integration tests, dependency and image scans,
lint/type checks, migration rehearsal, backup/restore rehearsal, authorization
tests, and a production-like smoke test. Exceptions require a documented
owner, expiry date, impact, mitigation, and CCB approval.

## Architecture decision log

| ID | Date | Decision | Consequence |
|---|---|---|---|
| ADR-001 | 2026-07-25 | Product name is ServiceOps and is independent of ServiceNow. | No inherited branding, runtime, data, or parity claims. |
| ADR-002 | 2026-07-25 | Runtime is production-only. | Demo mode, sample seeding, shared personas, and login hints are prohibited. |
| ADR-003 | 2026-07-25 | Local admin is bootstrap/break-glass; AD/LDAP and Keycloak are enterprise identity sources. | Local auth can be disabled after enterprise identity verification. |
| ADR-004 | 2026-07-25 | Team managers and CCB approvers are explicitly appointed named users. | Change submission fails closed when governance configuration is incomplete. |
| ADR-005 | 2026-07-25 | Kubernetes production uses external HA PostgreSQL and shared attachment storage. | Bundled chart databases are not approved for production. |
| ADR-006 | 2026-07-25 | Removed referenced identities are tombstoned. | Audit and approval foreign keys remain valid while login is impossible. |
| ADR-007 | 2026-07-25 | The supplied 2026 ServiceNow UI PDF is a controlled UX reference. | Features remain gaps until implemented and verified. |
| ADR-008 | 2026-07-25 | AD team membership synchronizes at login; manager and CCB authority remain explicit grants. | Automated membership can reconcile without overwriting governance decisions. |
| ADR-009 | 2026-07-26 | BP-001 is a controlled multi-release product specification. | Every requirement requires traceability and evidence; blueprint wording alone never implies implementation or parity. |
| ADR-010 | 2026-07-26 | Each installation initially serves one organisation, while tenant identifiers and tenant-aware authorization conventions are introduced now. | Existing data is assigned to the installation's default tenant through reversible migrations; new tenant-owned models must never omit tenant scope. |
| ADR-011 | 2026-07-26 | Evolve the Flask product into bounded modules behind stable interfaces without a rewrite. | Refactors must preserve behavior, data and deployability; module extraction is independently tested. |
| ADR-012 | 2026-07-26 | ServiceOps is light-only. Dark mode is a governed non-requirement. | No dark theme controls, tokens or compatibility burden will be introduced unless this ADR is explicitly superseded. |
| ADR-013 | 2026-07-26 | Standard deployment requires PostgreSQL only; search, cache, object storage, event transport and workers are optional enterprise adapters. | Standard and enterprise profiles share domain behavior and APIs and must not become architectural forks. |
| ADR-014 | 2026-07-26 | Integration priority is SMTP/email, signed webhooks, monitoring ingestion, then Microsoft Teams. | Each adapter is separately configurable, observable, retryable and fail-safe. |
| ADR-015 | 2026-07-26 | Build a versioned REST API first; GraphQL is deferred until a demonstrated consumer requirement. | REST resources use OAuth/OIDC authorization, pagination, idempotency, rate limits and audit conventions. |
| ADR-016 | 2026-07-26 | Deliver a responsive installable PWA before native mobile applications. | API and authentication contracts must remain suitable for future native clients. |
| ADR-017 | 2026-07-26 | Configuration is Git-backed and declarative; the database contains deployed runtime configuration. | Packages require diff, validation, promotion, dependency and rollback evidence. |
| ADR-018 | 2026-07-26 | Security and platform foundations precede visible feature expansion. | Migrations, CSRF, authorization, audit, workflow durability, APIs and configuration versioning are release prerequisites. |
| ADR-019 | 2026-07-26 | Preserve existing data using reversible versioned migrations with tested upgrade, verification and rollback. | Destructive reset is not an accepted upgrade strategy. |

## Governed non-requirements

The following BP-001 suggestions are explicitly excluded from the current
programme unless an ADR supersedes this section:

- dark mode;
- GraphQL without an identified consumer;
- a frontend/backend rewrite disguised as modularisation;
- mandatory Redis, OpenSearch, object storage, event transport or workflow
  infrastructure in the standard PostgreSQL deployment;
- native mobile applications before the responsive PWA and REST contracts are
  proven.

## Current production-readiness verdict

**Not approved for enterprise production yet.** P0 backlog items include
versioned migrations, comprehensive CSRF and authorization assurance,
append-only audit controls, proven disaster recovery/failover, supply-chain
attestation, and independent penetration testing.

Approval requires clean-checkout quality gates, representative AD/Keycloak
tests, a real HA Kubernetes deployment, restore and failure-injection evidence,
load/soak results, security and accessibility assessments, and accountable
operations, security, privacy, and CCB sign-off.

The only exception is the explicit `tools/load_test_fixture.py` workflow on an
intentionally reset, isolated test database. It is never automatic, displays a
warning banner, and must be destroyed before any production assessment.
