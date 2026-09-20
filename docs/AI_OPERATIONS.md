# AI assistance: administration and operations

Introduced in the local 1.92.0 candidate, migration `20260920_0095`. See [implementation plan](AI_IMPLEMENTATION_PLAN.md) and its validation record for delivery status. No model service or paid account is provisioned automatically.

## Administrator setup

Open **Administration → Platform & security → AI assistance** (`/admin/ai`). Only an active administrator/superadministrator with the `administer` action can configure AI. Settings and encrypted credentials belong to that administrator's tenant. Existing installations start disabled; there is no environment-variable bypass that enables a tenant.

1. Choose **Self-hosted compatible model** or **External: OpenAI**. Enter the exact model identifier available on that server/account. There is no automatic provider fallback.
2. For self-hosted inference, enter the full endpoint ending in `/v1/chat/completions`. The deployment operator must first allowlist that exact URL using `AI_SELF_HOSTED_ENDPOINTS` (Compose) or `ai.selfHostedEndpoints` (Helm). Comma-separated URLs are supported. DNS must resolve exclusively to private addresses; link-local/metadata, multicast, unspecified and reserved destinations are denied. TLS verification remains enabled. Use a trusted certificate or an operator-approved private HTTP connection.
   Model calls have a wall-clock limit set by `AI_PROVIDER_TIMEOUT_SECONDS` (Helm `ai.providerTimeoutSeconds`; default 60, range 10-270 seconds). Hosted models answer in seconds; a CPU-only self-hosted model can take minutes (a 3B model measured about 6 tokens/second on 8 CPU cores), so raise it for such models. The ceiling keeps every call inside the AI worker's 5-minute interrupted-run lease. A larger answer cap (`max_output_tokens`) needs a proportionally larger limit.
3. Enter the provider key if required. It is encrypted with the existing ServiceOps settings cipher. Blank preserves the existing key; “Remove saved API key” deletes it. Changing provider or endpoint clears the old key, preventing credentials being forwarded to a different destination. All web/AI worker instances must share the same encryption key.
4. Hosted mode uses only `https://api.openai.com/v1/responses`. Check external-processing authorization before testing or enabling it. Selected operational text leaves the deployment; no attachments are sent. `store=false` is requested, but this is not a promise of zero provider retention: verify account/provider data controls separately.
5. Set the daily investigation limit (UTC, 1–1000), maximum output tokens (128–4096), and result retention (1–30 days). Daily counts include failed/cancelled requests. Only one active investigation per user is accepted. The token cap includes provider-specific generation overhead; incomplete results are not published.
6. Save, then **Test saved connection**. The test sends a synthetic prompt only, works while tenant assistance is disabled, may incur a provider charge, and is limited to three tests per tenant per minute. Success verifies transport/authentication, not operational answer quality.
7. Enable both the organization master switch and incident investigations, then save. Pilot with selected operators and evaluate output before broader use.

## Operator workflow

Active agents, managers and administrators open an incident and select **Investigate with AI**. The confirmation screen identifies the provider mode/model and records that will be considered. Start investigation, refresh status, then review the draft and evidence links. Cancel queued or running work if no longer needed. Only the requesting operator can view that run; the current tenant, role, incident visibility and all source permissions are rechecked. Drafts are escaped plain text.

Retrieval is bounded: current incident and five recent comments, up to three matching published knowledge articles, two title-matching resolved incidents, and three permitted linked CIs. Title keyword matching is intentionally simple; it does not establish semantic similarity or guarantee the best match. Supplied sources are listed separately; `[S1]` references must name supplied evidence, but citation presence alone cannot prove a claim is supported. Verify all recommendations. The assistant cannot change state, priority, assignments, comments, approvals or infrastructure.

## Disable and recover

**Disable all AI now** requires no valid provider settings. It blocks new investigations and result access for the tenant, cancels queued/running work, and discards in-flight results. It cannot recall already-transmitted data or reliably cancel a remote provider charge. Re-enabling never revives cancelled jobs. Any configuration save also increments a revision and cancels old active jobs, so work cannot silently cross a provider/model/consent change.

AI failure does not block ordinary ticket work. `provider_failed` means connection, response format, incomplete response, or evidence citation checks failed; test the connection and start a new run after addressing configuration. `worker_interrupted` means the five-minute job lease expired; the worker does not automatically repeat uncertain provider calls. A cancelled job may indicate changed access/configuration. Check the dedicated worker readiness/liveness and logs; logs intentionally omit provider bodies and credentials.

## Deployment

The dedicated worker runs `python -m tools.ai_worker`; the existing SLA/outbox worker remains separate. Helm enables the worker deployment by default (`ai.workerEnabled: true`), while tenant AI remains off. Compose includes an `ai-worker` service. AI jobs are unavailable in IPFS mode. RPM installations require a separately supervised AI worker using the same environment and migration readiness gate; automatic RPM service provisioning is not part of this first release.

For private model ports, supply narrow `ai.extraEgress` destination/port rules: they apply to the AI worker and web connection-test path. Defaults permit DNS, PostgreSQL and HTTPS. Ambient HTTP proxies and redirects are not used by the provider adapter. Keys belong in the encrypted administrator form, never Helm values or source control. The app and AI worker both need the same endpoint allowlist.

Before rollout, restore-test a fresh PostgreSQL backup. Deploy the exact immutable image digest using atomic Helm, preserving PostgreSQL/uploads PVCs. Verify web, existing worker and AI worker rollouts; `/health`, `/ready`, current Alembic head, retained Helm test, Cloudflare Access and recent logs. AI-worker heartbeat file readiness is 150 seconds; liveness is 240 seconds. Network read/connect timeouts and a bounded response reader constrain slow responses; interrupted work is not automatically billed again.

Migration rollback removes the new tables only when both are empty. If configuration or run data exists, rollback refuses data deletion: disable AI and roll back the application with the additive schema retained, or prepare a separately reviewed archival migration. Never stamp the revision to bypass that guard.

The AI worker purges expired run payloads; UI access also rejects expired runs. Audit events retain request/configuration/completion/cancellation metadata without prompt bodies. If the worker is stopped, database deletion waits until it resumes. Common secret patterns are redacted before inference, but this is not comprehensive PII/secret discovery.

## Live answers, visible reasoning and the chat assistant (1.93.0, migration `20260921_0096`)

**Live answers.** Investigations and chat replies are written progressively. The browser polls `GET /ai/runs/<id>/stream?after=<seq>` about every 600 ms (short polling, chosen over SSE/WebSocket because it passes the Cloudflare tunnel and gunicorn unchanged and never holds a web worker). The worker streams from the model (OpenAI-compatible SSE from llama.cpp, Ollama, vLLM), writes partial text to the run row at most every 0.4 s, and refreshes a heartbeat; a run with no heartbeat for `AI_PROVIDER_TIMEOUT_SECONDS + 60` s is marked interrupted. The hosted OpenAI adapter is not streamed: its answer arrives as one chunk. Investigations still require at least one valid `[S#]` citation; chat citations are optional.

**Thinking display.** The panel shows two things: (1) an activity trace recorded by the pipeline itself ("Verified your access", "Collected evidence", "Checked your access again"), never invented by the model; (2) the model's own reasoning stream when the model is a reasoning model (llama.cpp `reasoning_content`, or inline `<think>` blocks) and **Show model reasoning** is on. Reasoning is model-written and can be wrong; the UI says so. Turn it off in `/admin/ai` to keep only the activity trace. Non-reasoning models (Qwen2.5) show the trace only. Chat users can tick **Think step by step** per message to request reasoning (`chat_template_kwargs.enable_thinking`); it is slower on CPU.

**Chat assistant.** Enable **Enable the chat assistant** in `/admin/ai` (independent of incident investigations; both need the master switch). Every signed-in user whose acting role is requester, agent, manager, admin or superadmin gets a floating **Ask AI** button and a full page at `/ai/chat`. There is no per-user allow list; access is by role, and the assistant states the asker's scope in the panel header.

*Privacy model.* The model has no tools and no database access. For every message the server decides who is asking from the authenticated session only (request data never widens it), then retrieves evidence deterministically through the same visibility rules the rest of ServiceOps uses (`visible_ticket_query`, published knowledge, `ci_class_read_allowed`):

| Role | Sees |
|---|---|
| Requester | own tickets, published knowledge |
| Agent / manager / admin / superadmin | incidents and changes their role and groups already permit, published knowledge, configuration items their role may read |

Never available to the assistant for anyone: the user directory, audit log, client/customer data, attachments, settings and secrets, other tenants. A message asking for those, for other people's tickets by bulk, for credentials, or attempting to override the rules is answered with a fixed refusal **without calling the model** (audited as `ai chat denied`, reason code only). A reference to a ticket the asker cannot read is reported exactly as one that does not exist. Email addresses and phone numbers in ticket, comment and CI text are masked before the model sees them. Earlier answers are replayed to the model only if every source they cited is still readable; otherwise the history shows a withheld notice. Model output is checked: unknown record numbers become "[unverified reference removed]". A conversation is bound to the role it started under; using it as a different role is refused. Audit records carry counts, ids and reason codes, never questions or answers; nothing is logged.

*History.* Conversations are stored until the user deletes them (History, then Delete, confirm). Administrators cannot read another person's conversation. Deleting removes the messages and clears any run text still held. Erasing a user (GDPR) purges their conversations. Deletion is available even when chat is switched off. Limits: 2000 characters per question, 100 messages per conversation, 20 messages per user per minute, one active answer per user, and the tenant daily AI limit.

## Current boundaries

The assistant is read-only. Model-directed tool loops, embedding search, autonomous remediation and approved write actions are later work (AI-05 and follow-up scope). Real model evaluation and production provider connectivity remain required before calling the feature production-ready.
