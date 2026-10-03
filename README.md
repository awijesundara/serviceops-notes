# ServiceOps documentation

This repository is the authoritative source for ServiceOps documentation.
Start here for navigation.

## Six maintained documents

| Document | Read it for |
|---|---|
| [Operations and capabilities](docs/OPERATIONS_MANUAL.md) | User workflows, feature inventory, administration ownership, iOS and AI administration. Source for the public PDF manual. |
| [Engineering and governance](docs/ENGINEERING_REFERENCE.md) | Architecture decisions, ITIL models, UI mapping, controlled blueprints and AI design. |
| [Deployment and recovery](docs/DEPLOYMENT.md) | Installation, identity, upgrades, backup/restore, IPFS, self-hosted inference and release gates. |
| [REST API contract](docs/API_REFERENCE.md) | Authentication, scopes, endpoints, examples and errors. Maintained original of the public API reference. |
| [Privacy and security controls](docs/COMPLIANCE.md) | GDPR records, procedures and templates; ISO 27001 control mappings, policies and assessed gaps. |
| [Work register and verification history](docs/BACKLOG.md) | Open/completed work, requirements traceability, dated reviews, acceptance evidence and historical reference excerpts. |

Each document has a contents list and stable section anchors. Update these
documents directly; there are no separate feature catalogues, traceability
files, archive copies or generated master references to synchronize. Historical
evidence retains its original dates and limitations and does not establish
the current state of a running deployment.

## Where to record a change

Update the work register and its requirements traceability section with the
implementation and verification evidence. Update the relevant operations,
engineering, deployment, API or compliance section in the same change. Record
architecture decisions in the engineering document and dated acceptance
reports in the work register. Add sections to these six documents rather than
creating another document for each feature or review.

## Sources, assets and public artifacts

- `docs/diagrams/`, `docs/screenshots/` and `docs/readme/` contain image assets;
  their existing paths are preserved for the generated manual.
- `docs/API_REFERENCE.md` is mirrored to the sibling
  `ServiceOps/docs/API_REFERENCE.md`; both copies must be byte-identical.

Internal Markdown sources stay here. The sibling ServiceOps repository retains
its public README, generated `docs/ServiceOps_Complete_Platform_Manual.pdf`,
the public API mirror and README image assets. Local documentation edits do
not authorize commits, pushes, tags, publication or GitHub pipelines.
