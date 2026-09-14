# ServiceOps documentation index

- [iOS mobile application](MOBILE_APP.md) — features, authentication, audit attribution, APNs architecture, local setup, and release evidence.

Controlled local documentation. Every entry below must stay synchronized with
the current source, migrations, and release evidence as part of any
meaningful change.

| Document | Purpose |
|---|---|
| [FEATURE_CATALOG.md](FEATURE_CATALOG.md) | Canonical detailed inventory of every implemented product, administration, integration, security, observability, recovery, deployment, and release feature, with explicit capability boundaries |
| [MASTER_REFERENCE.md](MASTER_REFERENCE.md) | Single merged reference (governance, backlog, ITIL model, traceability, UI mapping, API reference, operations manual, deployment guide, plus a whole-app audit) for any AI agent or engineer to read first |
| [API_REFERENCE.md](API_REFERENCE.md) | REST API contract: authentication, scopes, endpoints, examples, errors |
| [OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md) | End-user guide (source for the public PDF manual): signing in, tickets, catalog, approvals, every major screen |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Docker, Kubernetes, RPM packaging, identity, backup, and recovery instructions |
| [IPFS_STORAGE_MODE.md](IPFS_STORAGE_MODE.md) | Full IPFS-mode architecture, B-335 upgrade, deployment, recovery, health signals, and operating boundaries |
| [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md) | Evidence gates that block production promotion |
| [REMEDIATION_PLAN_1.38.2.md](REMEDIATION_PLAN_1.38.2.md) | Scope, verification, release sequence, and explicitly open production-readiness work for 1.38.2 |
| [BACKLOG.md](BACKLOG.md) | Authoritative completed and open work, with evidence references |
| [GOVERNANCE.md](GOVERNANCE.md) | Architecture decisions, production-readiness verdict, non-deviation controls |
| [TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md) | Implementation evidence mapped to requirements/backlog items |
| [UI_CAPABILITY_MAPPING.md](UI_CAPABILITY_MAPPING.md) | Supplied ServiceNow UI PDF analysis and capability gaps |
| [ITIL_TICKET_HIERARCHY.md](ITIL_TICKET_HIERARCHY.md) | ServiceNow-pattern ticket hierarchy reference and Change Task governance rule mapping |
| [ADMINISTRATION_INFORMATION_ARCHITECTURE.md](ADMINISTRATION_INFORMATION_ARCHITECTURE.md) | Canonical ownership and naming of every administration area; prevents duplicated settings |
| [gdpr/ROPA.md](gdpr/ROPA.md) | Record of Processing Activities (Art. 30): personal data categories, purposes, legal basis, recipients, retention, transfer risk |
| [gdpr/DPIA.md](gdpr/DPIA.md) | Data Protection Impact Assessment for audit logging, attachment storage, and LDAP sync |
| [gdpr/DATA_SUBJECT_RIGHTS.md](gdpr/DATA_SUBJECT_RIGHTS.md) | Art. 15/16/17/18/20/21 procedures mapped to the actual data model, including the audit-immutability vs. erasure tension |
| [gdpr/RETENTION_POLICY.md](gdpr/RETENTION_POLICY.md) | Retention schedule by data category with deletion/archival triggers |
| [gdpr/BREACH_NOTIFICATION.md](gdpr/BREACH_NOTIFICATION.md) | Art. 33/34 breach detection, 72-hour notification, and escalation procedure |
| [gdpr/DPA_TEMPLATE.md](gdpr/DPA_TEMPLATE.md) | Data Processing Agreement template for controller/processor relationships |
| [iso27001/SOA.md](iso27001/SOA.md) | ISO/IEC 27001:2022 Statement of Applicability — all Annex A controls, applicability, and current implementation status with codebase evidence |
| [iso27001/GAP_ANALYSIS.md](iso27001/GAP_ANALYSIS.md) | Concrete gap descriptions and remediation items for every Gap/Partially-Implemented control in the SOA |
| [iso27001/ISMS_POLICIES.md](iso27001/ISMS_POLICIES.md) | Draft core ISMS policies (Information Security, Access Control, Incident Management, Business Continuity/Backup, Supplier/Vendor Security, Acceptable Use) |

## Keeping this synchronized

When implementing a change, update in the same change:

- This index, if a document is added, removed, or renamed.
- `BACKLOG.md`, marking items done only with corresponding evidence.
- `TRACEABILITY_MATRIX.md`, if implementation status changed.
- `GOVERNANCE.md`'s decision log, if an architectural decision changed.
- The relevant manual section (`OPERATIONS_MANUAL.md`/`DEPLOYMENT.md`/`API_REFERENCE.md`).
- `MASTER_REFERENCE.md`, since it is a merge of the documents above rather
  than an independent source — regenerate its affected section(s) whenever
  the underlying document changes so it doesn't silently go stale.

This directory is excluded from the public GitHub repository but must still
be maintained locally; do not delete it because it is gitignored.
