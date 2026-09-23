# ServiceOps AI implementation plan

Baseline: 2026-09-20. Owner: ServiceOps engineering; provider/data policy owner: tenant administrator.
Status: ServiceOps 1.101.3 is deployed at Helm revision 108. Transient activity UI, multiple-service privacy and quota routing, whole-product permission-scoped context, ticket drafts, explicit per-user memory, secure context retrieval, live self-hosted streaming, generated staff drafts, approved ticket actions, and exact authorized cross-module evidence are verified. Customer, service-request and restricted-domain content is forced onto private AI. Commercial live inference remains unverified. Estimates are engineering effort, not promised calendar delivery.
No hosted GitHub publication is part of this work.

## Product scope and timeline

| Milestone | Effort / target sequence | Tasks | Exit criteria | Status |
|---|---|---|---|---|
| AI-01 Control plane | Days 1–2 | Tenant-scoped settings; administrator master and incident-feature switches; encrypted credentials; audit; configuration revision; cancellation | Negative authorization, tenant isolation, disable/re-enable races, CSRF and secret handling pass | Complete |
| AI-02 Provider connections | Days 3–4; depends on AI-01 | Self-hosted compatible chat endpoint and external OpenAI Responses adapter; destination allowlist; DNS pinning; timeout and output limits; synthetic connection check | Both protocol contracts pass; real provider checks recorded separately | Complete |
| AI-03 Incident assistant | Days 5–7; depends on AI-01/02 | Durable jobs and dedicated worker; permission-filtered incident/comments, knowledge, similar incidents and related CIs; cited read-only recommendations; cancel/status UI | End-to-end flow, current-access checks, interrupted jobs and duplicate submissions pass | Complete |
| AI-04 Acceptance | Days 8–10; depends on AI-01–03 | PostgreSQL upgrade/rollback, functional/security/browser/accessibility, provider evaluation, backup restore, immutable image, MicroK8s rollout and runbook | Deployment evidence recorded; new configurations default off and existing administrator enablement is preserved | Deployed; provider evaluation gaps below |
| AI-05 Approved actions | Days 11–15; depends on AI-04 quality review | Exact proposed change; expiring approval bound to record version; reauthorize; existing mutation APIs; audit/idempotency | No approval bypass, stale action rejection, no duplicate mutation | Ticket comments, state, priority and assignment plus generated staff drafts are deployed; the separate action switch remains off by default |
| AI-06 Secure context retrieval | Days 16–17; can run alongside later AI-05 slices | Exact visible-record counts; expanded knowledge vocabulary; grounded conversational references; visible linked records and permitted CIs; safe provider-failure guidance | Model payload contains useful context and no hidden, cross-tenant, unpublished or forbidden records for every existing access scope | Verified in 1.101.3: citable enterprise records, requests/tasks, customer tickets and assets, with mandatory private routing for sensitive modules |

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

## Adaptive provider discovery (1.94.0)

Requested 2026-09-20. This extends the delivered chat and administrator controls. Estimates are incremental engineering effort; verification determines completion.

| Task | Sequence / estimate | Acceptance | Status |
|---|---|---|---|
| AD-01 Discover models and limits | Day 1 | Authenticated bounded listing, same-origin llama.cpp runtime properties, multiple-model choice | Implemented; protocol tests pass |
| AD-02 Persist trusted discovery | Day 1, after AD-01 | Signed preview bound to administrator, tenant, endpoint and credential | Implemented; negative binding tests pass |
| AD-03 Adapt requests | Days 1–2, after AD-01 | Preserve rules and question; shorten evidence/history; honor limits; omit unknown thinking parameters | Implemented; budget and privacy tests pass |
| AD-04 Acceptance | Day 2, after AD-01–03 | Migration, browser/accessibility, full regressions, immutable image, fresh backup restore, MicroK8s checks | Deployed; live inference limitation below |
| AD-05 Additional protocols | Subsequent increments | Documented adapter and contract/live tests per unsupported API | Backlog |

Verified: 135 focused tests; 10 PostgreSQL-backed browser/accessibility tests; migration 0096 to 0097, downgrade and roll-forward with 20,000 synthetic records preserved. Authenticated live llama.cpp metadata reports Qwen/Qwen3-8B-GGUF:Q4_K_M, runtime context 4096 and training context 40960. Metadata alone does not establish generation quality.

Adaptive acceptance evidence (2026-09-20):

- Full host suite: 857 passed, 112 skipped, one version/PWA mismatch caused by changing VERSION while the suite was in flight. The failed test passed independently after version synchronization; no runtime defect remained. Skipped tests are not passing evidence.
- Browser/accessibility: 10 passed against isolated PostgreSQL.
- Candidate: 1.94.0, private registry digest sha256:a67a37e3f1462824164688f3798a9afb72aaeeb04debda7be12c8dfe10bad7a7. Fresh OS package update; Trivy reports zero fixable HIGH/CRITICAL findings. No image signing or GitHub publication was performed.
- Fresh backup: serviceops-adaptive-20260920T141241Z, SHA-256 a8c98b45502860023818004c2b7d7ca40afb6bef2be18f600bce09340ecda589. Restore-tested locally; restored upgrade preserved all 19 tickets and existing AI settings, credentials and enablement.
- Static checks: ruff, JavaScript syntax, migration expand policy, version consistency, Helm lint and strict manifest validation passed.
- Live model limitation: authenticated models/props succeeded, but a synthetic READY request with thinking disabled timed out after 90 seconds. No operational records were sent. This does not identify a GPU, memory or model-load cause. Commercial credentials/inference and deployed authenticated browser access remain unverified.

MicroK8s acceptance completed: Helm revision 87, web 2/2, outbox 1/1, AI worker 1/1 on the recorded digest. Health and readiness returned 200 with version 1.94.0 and Alembic head 20260921_0097. Retained Helm health test succeeded. PostgreSQL and uploads PVC bindings were preserved; recent workload logs contained no detected error/traceback lines. Public HEAD returned Cloudflare 302 to wijesundara.cloudflareaccess.com (an earlier urllib GET returned 403). Deployed authenticated model discovery confirmed runtime /props context 4096, training context 40960 and thinking-template support. Existing AI enablement remained enabled and its key remained configured. The live inference timeout is an unresolved verification gap, not a successful model test.

## Live verification continuation (2026-09-21)

The workspace and deployment had independently advanced to 1.95.0. This continuation made no application, model-server, credential or deployment configuration changes. Current readiness returned 200 for 1.95.0 with migration 20260921_0097.

Two synthetic checks, with no operational records, succeeded against the configured self-hosted server:

- Direct authenticated streaming: HTTP 200, READY received, stream completed; first content at 33.85 seconds, total 33.94 seconds.
- Deployed ServiceOps provider adapter: READY received, one content delta, no reasoning delta; first content at 7.668 seconds, total 7.72 seconds. The in-memory discovered profile used runtime context 4096, conservative byte budgeting and a 32-token output cap. No saved configuration was changed.

These results establish live protocol/adapter compatibility for this model and resolve the previously unverified streaming path. They do not explain the earlier 90-second timeout or establish reliable latency under load, operational answer quality, or commercial-provider behavior. The same fallback policy remains in 1.96.0: context 4096 for unknown self-hosted limits and 32768 for unknown hosted limits; fallback values are assumptions, not provider-reported capabilities.

## Transient activity interface acceptance (1.96.0)

The AI interface now presents one small changing activity label and removes it at completion. Model reasoning text is discarded rather than persisted or returned. The chat surface no longer draws an empty answer container or a Working/Complete badge. Progressive answer text, citations, Stop, Copy, deeper-reasoning requests, and administrator controls remain.

Validation on 2026-09-21: 61 focused tests; 10 PostgreSQL-backed Chromium/axe tests; 859 full-suite passes with 112 environment-dependent skips; streaming and completed desktop captures inspected; static/version/Helm/strict-manifest gates passed. The rebuilt image had zero fixable HIGH/CRITICAL scan findings. Backup `serviceops-ai-ui-20260921T010417Z` (SHA-256 `ccaba71a00ebfdc72b04d06778ee0f9afa36bf1d05d2d05873f123284d215c1d`, 1,565,964 bytes) restored successfully with migration `20260921_0097`, 19 tickets, 121 tables, and the existing enabled AI configuration preserved.

MicroK8s Helm revision 91 runs `localhost:32000/serviceops@sha256:b0f635418426acaf866a19bf34dd4cb4353654bed40810ac9192e141e96015dd`: web 2/2, outbox 1/1, AI worker 1/1. `/health` and `/ready` returned 200 for 1.96.0; the retained Helm test passed; PostgreSQL/uploads PVCs remained bound; recent web/outbox/AI-worker logs showed clean startup and probes; public access returned the expected Cloudflare Access 302. The deployed JavaScript contains the transient labels and no reasoning-text renderer. Existing AI/chat switches and the encrypted credential remained configured.

## Authorized application reach acceptance (1.99.2)

The assistant now retrieves the signed-in person's membership in every active support or governance group, including an explicit Change Control Board answer. Managers and administrators can receive governance-group manager and member-count facts. CMDB discovery matches name, serial number, vendor, model, IP address, location and external ID, and supplies a bounded safe specification set. Related-ticket counts and records still pass through current ticket visibility and CI-class authorization. Natural list and recency wording such as “Show me active changes” and “last incident received” is handled explicitly. Knowledge-note, client-organization and module-link suggestions use the relevant product context instead of unrelated generic “active” pages.

Security remains identity-bound: this extends what the assistant can retrieve from records the current user may already read. Credentials, settings, audit contents, arbitrary CI JSON, customer content outside the permitted client summary, and other users' private details are not exposed. Profile questions are marked personal and remain eligible only for an organization's own AI under the configured routing policy.

Validation on 2026-09-22: 213 focused AI/privacy/provider/streaming tests and the full suite (`985 passed`, `114 skipped`) passed; the governed release repeated the application suite, dependency audit, browser/accessibility journeys, image vulnerability gate, SBOM, signature and provenance, five RPM build/install matrices, and publication. Backup `serviceops-20260922T103918Z.dump` restored successfully at migration `20260925_0101` with 19 tickets. The signed linux/amd64 image `sha256:1964350eb0aee0cbbdd13ac18d1e7fa6e6193492128afd7a62ea454a1574f31a` deployed at Helm revision 103. Web 2/2, outbox 1/1 and AI worker 1/1 became ready; the retained health test reported 1.99.2 and migration 0101; PostgreSQL, uploads and backup PVCs remained bound; recent workload logs contained no matching error/exception/traceback lines; Cloudflare Access returned 302.

A sanitized live admin-scope check verified CCB membership context, `SN000002` lookup with class/serial/vendor/model fields, one newest incident, two active changes, CMDB server summary, knowledge count and client-organization count. It emitted pass/fail and aggregate counts only, not operational record contents. Model wording and commercial-provider quality remain separate evaluation concerns.
