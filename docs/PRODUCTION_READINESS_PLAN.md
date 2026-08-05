# ServiceOps production-readiness release gates

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

## Delivery order

1. Tenant isolation and external security review.
2. Supply-chain cluster proof, recovery, and rollback rehearsals.
3. Observability and performance baselines.
4. Object storage and identity lifecycle controls.
5. Accessibility and privacy validation.

Production promotion remains blocked until gates 1–3 have no unresolved
critical/high issue and the accountable owner explicitly accepts residual risk.

## Current implementation checkpoint — 2026-08-05

ServiceOps 1.38.2 improves release consistency, CI quality checks, one redirect
boundary, and shared accessibility semantics. It does not close any gate in
the table above. The authoritative scope and next-release sequence are in
`REMEDIATION_PLAN_1.38.2.md`; the independently executed, environment-specific
evidence remains mandatory.
