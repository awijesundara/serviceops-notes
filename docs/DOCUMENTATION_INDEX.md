# ServiceOps documentation index

Controlled local documentation. Every entry below must stay synchronized with
the current source, migrations, and release evidence as part of any
meaningful change.

| Document | Purpose |
|---|---|
| [MASTER_REFERENCE.md](MASTER_REFERENCE.md) | Single merged reference (governance, backlog, ITIL model, traceability, UI mapping, API reference, operations manual, deployment guide, plus a whole-app audit) for any AI agent or engineer to read first |
| [API_REFERENCE.md](API_REFERENCE.md) | REST API contract: authentication, scopes, endpoints, examples, errors |
| [OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md) | Complete platform manual: administration, security model, ITIL workflows, product use |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Docker, Kubernetes, RPM packaging, identity, backup, and recovery instructions |
| [BACKLOG.md](BACKLOG.md) | Authoritative completed and open work, with evidence references |
| [GOVERNANCE.md](GOVERNANCE.md) | Architecture decisions, production-readiness verdict, non-deviation controls |
| [TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md) | Implementation evidence mapped to requirements/backlog items |
| [UI_CAPABILITY_MAPPING.md](UI_CAPABILITY_MAPPING.md) | Supplied ServiceNow UI PDF analysis and capability gaps |
| [ITIL_TICKET_HIERARCHY.md](ITIL_TICKET_HIERARCHY.md) | ServiceNow-pattern ticket hierarchy reference and Change Task governance rule mapping |
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
