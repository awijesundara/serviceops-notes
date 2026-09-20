# ServiceOps AI implementation plan

Baseline: 2026-09-20. Owner: ServiceOps engineering; provider/data policy owner: tenant administrator.
Status: implementation in progress. Estimates are engineering effort, not promised calendar delivery.
No hosted GitHub publication is part of this work.

## Product scope and timeline

| Milestone | Effort / target sequence | Tasks | Exit criteria | Status |
|---|---|---|---|---|
| AI-01 Control plane | Days 1–2 | Tenant-scoped settings; administrator master and incident-feature switches; encrypted credentials; audit; configuration revision; cancellation | Negative authorization, tenant isolation, disable/re-enable races, CSRF and secret handling pass | In progress |
| AI-02 Provider connections | Days 3–4; depends on AI-01 | Self-hosted compatible chat endpoint and external OpenAI Responses adapter; destination allowlist; DNS pinning; timeout and output limits; synthetic connection check | Both protocol contracts pass; real provider checks recorded separately | In progress |
| AI-03 Incident assistant | Days 5–7; depends on AI-01/02 | Durable jobs and dedicated worker; permission-filtered incident/comments, knowledge, similar incidents and related CIs; cited read-only recommendations; cancel/status UI | End-to-end flow, current-access checks, interrupted jobs and duplicate submissions pass | In progress |
| AI-04 Acceptance | Days 8–10; depends on AI-01–03 | PostgreSQL upgrade/rollback, functional/security/browser/accessibility, provider evaluation, backup restore, immutable image, MicroK8s rollout and runbook | All evidence recorded; AI remains off until administrator configures and enables it | Planned |
| AI-05 Approved actions | Days 11–15; depends on AI-04 quality review | Exact proposed change; expiring approval bound to record version; reauthorize; existing mutation APIs; audit/idempotency | No approval bypass, stale action rejection, no duplicate mutation | Planned; not part of first read-only release |

The initial implementation may advance faster than these estimates. Actual completion is tracked by evidence, not elapsed days. Dependencies: configured model endpoint/model and credentials; a reachable build engine; a working acceptance cluster. Both self-hosted and external modes are required by the user. Never silently fall back from local to hosted processing.

## First-release architecture

Authenticated incident page -> tenant-scoped durable AI run -> dedicated AI worker -> bounded server-controlled retrieval -> selected provider -> escaped draft with source links. This first release is a constrained investigation workflow, not autonomous remediation. No shell, arbitrary HTTP, SQL, attachment parsing, ticket writes or automatic approvals are available to the model.

AI configuration uses a dedicated tenant-primary-key table: general PlatformSetting keys are global and are unsuitable for tenant AI credentials. Configuration saves increment a revision and invalidate queued/running jobs. Every execution and result publication rechecks that revision and enablement. Disabling stops new work and discards in-flight responses; it cannot retract data already transmitted to a provider. Results remain private to the requesting user, and all evidence permissions are rechecked before display. Saved credentials never appear in HTML, logs, audit details or job payloads.

Self-hosted destinations must be explicitly allowlisted by the operator, independently of tenant configuration. Hosted traffic uses a fixed HTTPS endpoint. Redirects and ambient HTTP proxies are disabled; addresses are validated and pinned. Local mode never falls back to hosted mode. Content is bounded and common secret patterns are redacted; this is not a guarantee that all sensitive prose can be detected. Administrator external-data consent is required for hosted enablement.

Jobs have explicit queued/running/completed/failed/cancelled states, a bounded lease and no automatic provider retry (avoid duplicate billing after uncertain completion). Configurable per-tenant daily request limits and output caps bound use. Expired output is purged by the dedicated worker. Audit retains event metadata, not prompt bodies. IPFS mode is excluded from this release because its single-process projection is incompatible with a separate database job worker.

## Validation and release evidence

To be updated with exact results during implementation. Distinguish deterministic protocol fixtures from real inference; fixtures do not establish model quality. Live model evaluation must cover groundedness, missing evidence, malicious ticket instructions, tenant isolation, latency and usage. No provider credential is assumed or provisioned automatically.

## Sources

- OpenAI Responses API: https://developers.openai.com/api/reference/cli/resources/responses/methods/create
- OWASP agent security: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
