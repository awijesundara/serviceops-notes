# ServiceOps AI implementation plan

Baseline: 2026-09-20. Owner: ServiceOps engineering; provider/data policy owner: tenant administrator.
Status: read-only release implemented and verified locally; acceptance rollout pending. Estimates are engineering effort, not promised calendar delivery.
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

Recorded 2026-09-20 on the rebased 1.92.0 source (commit 7589df3). Provider tests use deterministic protocol fixtures against a controlled local server; they establish request/response handling, not model quality.

| Check | Result |
|---|---|
| Full suite (isolated test image) | 733 passed, 106 skipped; plus `test_docs_sync` on the host (needs sibling notes checkout) = 734 effective |
| AI unit/API tests | administrator-only access, CSRF, encrypted credentials, tenant isolation, duplicate submissions, daily limits, disable during in-flight run, unknown/absent citations, source re-authorization |
| PostgreSQL migration | upgrade 0094 to 0095, downgrade, roll-forward with 100,000 synthetic rows preserved; rollback refused once AI records exist |
| Real browser (PostgreSQL) | admin enable/disable and incident workflow at desktop, tablet and mobile, with axe WCAG 2 A/AA checks: 3 passed |
| Static gates | ruff, compileall, shell syntax, JavaScript syntax, migration-safety policy, Helm lint and client-side strict validation of every rendered manifest |
| Image scan (Trivy 0.58.2, HIGH/CRITICAL, fixed-only, from a `docker save` tarball, no Docker socket) | 13 findings, all Debian base-image packages (gzip, libpcre2, libsqlite3, perl-base); none in Python dependencies; requirements unchanged. To be re-scanned by the governed supply-chain gate on the released image |
| Backup restore | a fresh deployment backup restored and its 19 existing tickets survived the migration (recorded by the earlier acceptance run) |

Defect found during acceptance: the Helm ConfigMap wrote AI_SELF_HOSTED_ENDPOINTS under `metadata` as well as `data`. `helm lint` does not detect this, but Kubernetes rejects the unknown field, so it would have failed the upgrade. Fixed before release; the whole rendered chart now validates under strict client-side validation.

Not yet verified: live model evaluation (groundedness, missing evidence, malicious ticket instructions, latency, cost) against a real configured endpoint; the hosted/self-hosted round trip with real credentials; the MicroK8s rollout of the AI worker; and the governed release, image signature, SBOM and RPM evidence. AI remains disabled until an administrator configures and enables it.

## AI 2.0 delivery record (1.93.1)

Scope: streaming answers, visible reasoning, private role-scoped chat. Migration `20260921_0096`. Design and controls are documented in [AI_OPERATIONS.md](AI_OPERATIONS.md); backlog entry B-366.

| Check | Result |
|---|---|
| Privacy matrix | 34 tests; every test plants a canary in data a role must not reach and inspects the exact payload the model would receive; verified by mutation (removing an ownership filter fails the suite) |
| Chat API | 17 tests: owner-only conversations (admins included), role change blocks a conversation, deactivated user, deletion, purge on erasure, rate limit, one active answer, idempotent retry, no content in audit rows |
| Streaming | 16 tests including a real SSE server, Stop mid-stream, admin disable mid-stream, stale heartbeat, thinking token allowance |
| Real browser under the production CSP | 9 tests at 1440, 768 and 390 px with axe WCAG 2 A/AA: widget open by keyboard, streaming, reasoning panel, markdown injection stays inert text, history delete, Escape returns focus, full-page chat and Stop |
| PostgreSQL migration | 0095 to 0096, downgrade and roll-forward with 20,000 synthetic rows preserved |
| Full suite | 817 passed, 112 skipped in the isolated Docker image |
| Live models (MacBook, CPU, llama.cpp) | qwen3-4b: 59 s per streamed investigation with reasoning; qwen3-8b: 99 s; Qwen2.5 3B/7B/14B answer without a reasoning stream. Requester scenarios (own ticket, another user's ticket, request by name, user list, injection text in own ticket) produced no leak |

Not verified: behaviour under sustained concurrent chat load; quality beyond the five scenarios above; hosted-provider streaming (not implemented).

## Sources

- OpenAI Responses API: https://developers.openai.com/api/reference/cli/resources/responses/methods/create
- OWASP agent security: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
