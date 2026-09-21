# AI assistance: administration and operations

Introduced in the local 1.92.0 candidate, migration `20260920_0095`. See [implementation plan](AI_IMPLEMENTATION_PLAN.md) and its validation record for delivery status. No model service or paid account is provisioned automatically.

## Administrator setup

Open **Administration → Platform & security → AI assistance** (`/admin/ai`). Only an active administrator/superadministrator with the `administer` action can configure AI. Settings and encrypted credentials belong to that administrator's tenant. Existing installations start disabled; there is no environment-variable bypass that enables a tenant.

1. Add one or more services: a server on your network, hosted OpenAI-compatible service, OpenAI, or Anthropic. For compatible services, model detection fills the exact model identifier when the provider exposes it. Routing may fail over between eligible services, but never crosses the configured privacy boundary.
2. For self-hosted inference, enter the server address. ServiceOps normalizes the compatible API path. The deployment operator must first allowlist the server using `AI_SELF_HOSTED_ENDPOINTS` (Compose) or `ai.selfHostedEndpoints` (Helm). Comma-separated server, host-and-port wildcard, or exact URL entries are supported. DNS must resolve exclusively to private addresses; link-local/metadata, multicast, unspecified and reserved destinations are denied. TLS verification remains enabled. Use a trusted certificate or an operator-approved private HTTP connection.
   Model calls have a wall-clock limit set by `AI_PROVIDER_TIMEOUT_SECONDS` (Helm `ai.providerTimeoutSeconds`; default 60, range 10-270 seconds). Hosted models answer in seconds; a CPU-only self-hosted model can take minutes (a 3B model measured about 6 tokens/second on 8 CPU cores), so raise it for such models. The ceiling keeps every call inside the AI worker's 5-minute interrupted-run lease. A larger answer cap (`max_output_tokens`) needs a proportionally larger limit.
3. Enter the provider key if required. It is encrypted with the existing ServiceOps settings cipher. Blank preserves the existing key; “Remove saved API key” deletes it. Changing provider or endpoint clears the old key, preventing credentials being forwarded to a different destination. All web/AI worker instances must share the same encryption key.
4. Hosted modes use their documented fixed API or the administrator-supplied public HTTPS compatible endpoint. Check external-processing authorization before testing or enabling one. Selected operational text leaves the deployment; no attachments are sent. Provider-side retention and account controls must be verified separately.
5. Set the daily investigation limit (UTC, 1–1000), maximum output tokens (128–4096), and result retention (1–30 days). Daily counts include failed/cancelled requests. Only one active investigation per user is accepted. The token cap includes provider-specific generation overhead; incomplete results are not published.
6. Save, then test the service. The test sends a synthetic prompt only, works while tenant assistance is disabled, may incur a provider charge, and is rate limited. Success verifies transport/authentication, not operational answer quality.
7. Enable both the organization master switch and incident investigations, then save. Pilot with selected operators and evaluate output before broader use.

## Operator workflow

Active agents, managers and administrators open an incident and select **Investigate with AI**. The confirmation screen identifies the provider mode/model and records that will be considered. Start investigation, refresh status, then review the draft and evidence links. Cancel queued or running work if no longer needed. Only the requesting operator can view that run; the current tenant, role, incident visibility and all source permissions are rechecked. Drafts are escaped plain text.

Retrieval is bounded: current incident and five recent comments, up to three matching published knowledge articles, two title-matching resolved incidents, and three permitted linked CIs. Title keyword matching is intentionally simple; it does not establish semantic similarity or guarantee the best match. Supplied sources are listed separately; `[S1]` references must name supplied evidence, but citation presence alone cannot prove a claim is supported. Verify all recommendations. Unless the separately controlled approved-action feature is enabled, the assistant cannot change state, priority, assignments, comments, approvals or infrastructure.

## Disable and recover

**Disable all AI now** requires no valid provider settings. It blocks new investigations and result access for the tenant, cancels queued/running work, and discards in-flight results. It cannot recall already-transmitted data or reliably cancel a remote provider charge. Re-enabling never revives cancelled jobs. Any configuration save also increments a revision and cancels old active jobs, so work cannot silently cross a provider/model/consent change.

AI failure does not block ordinary ticket work. `provider_failed` means connection, response format, incomplete response, or evidence citation checks failed; test the connection and start a new run after addressing configuration. `worker_interrupted` means the five-minute job lease expired; the worker does not automatically repeat uncertain provider calls. A cancelled job may indicate changed access/configuration. Check the dedicated worker readiness/liveness and logs; logs intentionally omit provider bodies and credentials.

## Deployment

The dedicated worker runs `python -m tools.ai_worker`; the existing SLA/outbox worker remains separate. Helm enables the worker deployment by default (`ai.workerEnabled: true`), while tenant AI remains off. Compose includes an `ai-worker` service. AI jobs are unavailable in IPFS mode. RPM installations require a separately supervised AI worker using the same environment and migration readiness gate; automatic RPM service provisioning is not part of this first release.

For private model ports, supply narrow `ai.extraEgress` destination/port rules: they apply to the AI worker and web connection-test path. Defaults permit DNS, PostgreSQL and HTTPS. Ambient HTTP proxies and redirects are not used by the provider adapter. Keys belong in the encrypted administrator form, never Helm values or source control. The app and AI worker both need the same endpoint allowlist.

Before rollout, restore-test a fresh PostgreSQL backup. Deploy the exact immutable image digest using atomic Helm, preserving PostgreSQL/uploads PVCs. Verify web, existing worker and AI worker rollouts; `/health`, `/ready`, current Alembic head, retained Helm test, Cloudflare Access and recent logs. AI-worker heartbeat file readiness is 150 seconds; liveness is 240 seconds. Network read/connect timeouts and a bounded response reader constrain slow responses; interrupted work is not automatically billed again.

Migration rollback removes the new tables only when both are empty. If configuration or run data exists, rollback refuses data deletion: disable AI and roll back the application with the additive schema retained, or prepare a separately reviewed archival migration. Never stamp the revision to bypass that guard.

The AI worker purges expired run payloads; UI access also rejects expired runs. Audit events retain request/configuration/completion/cancellation metadata without prompt bodies. If the worker is stopped, database deletion waits until it resumes. Common secret patterns are redacted before inference, but this is not comprehensive PII/secret discovery.

## Several AI services, smart routing and sensitive-data protection (1.97.0, migration `20260922_0098`)

An organization can connect any number of AI services (on its own network or hosted) in `/admin/ai`. Each service has a name, provider, model, optional key, an **order**, a **weight** and how many requests it can take **at once**. An older single-provider setup is migrated to one service called "Primary".

**Sensitive requests never leave.** Before a request is sent, the question, the earlier chat turns and the *original* text of every record (before personal details are masked) are scanned for: personal details (email, phone, ID numbers; not the contact numbers in published knowledge), passwords and keys (assignments, private keys, cloud and API key shapes, JWTs), payment and bank numbers (card numbers that pass the checksum, IBANs), and the administrator's own words. If anything is found, only services on the organization's network are eligible. This is absolute: a busy, failing or missing private service is never replaced by a hosted one; the person is told the request needs the organization's own AI and none is available. Each detector can be switched off. The **Try it** box in the settings runs the real rules on a sample sentence and shows where it would go; nothing is sent to any AI.

**What may go outside** (only if the organization has authorized outside AI): nothing; only published knowledge; or anything not sensitive (default).

**Sharing methods.** Smart (default): own AI first, an outside service only as overflow when own services are at capacity or down; Private first; Spread the load (weighted random among allowed services, busy ones last); In order (by the order number, next only on failure). Load is the number of runs currently being answered by each service; a service with three consecutive failures is skipped for 60 seconds (still tried if everything is failing). If a service fails before it has started answering, the next allowed service is tried (up to three); once an answer has started there is no failover.

**Transparency.** Every answer shows "Private AI" or "External AI" and, when sensitivity decided the route, why. Audit rows record service name, location and whether the request was sensitive, never the content.

## Any provider, connected from an address and a key (1.94.0)

ServiceOps speaks four provider types; choose one in `/admin/ai` (or pick a **Quick setup** preset):

| Provider | What it covers | Address | Key | Notes |
|---|---|---|---|---|
| Server on your network | llama.cpp `llama-server`, Ollama, vLLM, LM Studio, LocalAI, any OpenAI-compatible server | `http://HOST:PORT` (the `/v1/chat/completions` part is added) | optional | Operator allowlist required; private addresses only; live streaming and reasoning |
| Hosted OpenAI-compatible service | OpenRouter, Groq, Together, Mistral, Google Gemini (OpenAI-compatible endpoint), Azure-style gateways | `https://...` | required | HTTPS only; public addresses only; needs the external-processing authorization; streamed |
| OpenAI | api.openai.com Responses API | fixed | required | Needs external-processing authorization; answer delivered in one piece (not streamed) |
| Anthropic (Claude) | api.anthropic.com Messages API | fixed | required | Needs external-processing authorization; streamed; extended thinking is not requested |

**Model detection.** After the address (and key) are entered, ServiceOps calls the server's model list (`GET /v1/models`, the same call every OpenAI-compatible server offers) and fills in the model identifier automatically, and shows the server's context window when it reports one (llama.cpp does). Detection runs on the button and shortly after the fields are filled in. It uses the same network guards as a model call (allowlist, address pinning, no redirects, size and time limits), is limited to 10 attempts per tenant per minute, sends the typed key for that one request only, and reuses the saved key only when the provider and address are unchanged. Only well-formed model identifiers are returned to the browser. Because 1.95.0 shortens evidence to fit the detected context, a small window degrades answers rather than failing them; about 8192 tokens is still recommended for incident investigations (llama.cpp `-c 8192`).

**Operator allowlist.** `AI_SELF_HOSTED_ENDPOINTS` / Helm `ai.selfHostedEndpoints` accepts, comma-separated: a server (`http://192.168.68.68:8080`, covers every path on it), every port of a host (`http://192.168.68.68:*`), or one exact URL (the pre-1.94 form, still valid). Hostnames are matched case-insensitively and the scheme must match. If an address is not listed, the error names the exact entry to add. Also open the network path: add the host to `ai.extraEgress` (omit `ports` to allow every port on that host).

## Live answers, private reasoning and the chat assistant (1.93.1, UI revised in 1.96.0)

**Live answers.** Investigations and chat replies are written progressively. The browser polls `GET /ai/runs/<id>/stream?after=<seq>` about every 600 ms (short polling, chosen over SSE/WebSocket because it passes the Cloudflare tunnel and gunicorn unchanged and never holds a web worker). The worker streams from the model (OpenAI-compatible SSE from llama.cpp, Ollama, vLLM), writes partial text to the run row at most every 0.4 s, and refreshes a heartbeat; a run with no heartbeat for `AI_PROVIDER_TIMEOUT_SECONDS + 60` s is marked interrupted. The hosted OpenAI adapter is not streamed: its answer arrives as one chunk. Investigations still require at least one valid `[S#]` citation; chat citations are optional.

**Thinking display.** While a request runs, one small status line changes in place: for example, **Checking access**, **Reviewing evidence**, **Thinking**, then **Writing answer**. It disappears when the answer is complete. There is no expandable card, activity-step list, or model chain-of-thought in the interface. Reasoning deltas (`reasoning_content` or inline `<think>` blocks) are used only to select the transient **Thinking** label; their text is not persisted or returned by the run and conversation APIs. Administrators can enable **Allow deeper reasoning**, after which chat users may request **Think step by step** for a message. That changes model behavior and may be slower; it does not expose private reasoning text.

**Chat assistant.** Enable **Enable the chat assistant** in `/admin/ai` (independent of incident investigations; both need the master switch). Every signed-in user whose acting role is requester, agent, manager, admin or superadmin gets a floating **Ask AI** button and a full page at `/ai/chat`. There is no per-user allow list; access is by role, and the assistant states the asker's scope in the panel header.

*Privacy model.* The model has no tools and no database access. For every message the server decides who is asking from the authenticated session only (request data never widens it), then retrieves evidence deterministically through the same visibility rules the rest of ServiceOps uses (`visible_ticket_query`, published knowledge, `ci_class_read_allowed`):

| Role | Sees |
|---|---|
| Requester | own tickets, published knowledge |
| Agent / manager / admin / superadmin | incidents and changes their role and groups already permit, published knowledge, configuration items their role may read |

The 1.97.6 AI-06 update adds server-calculated counts for “how many incidents/changes/tickets can I see?”, expands common support wording such as email/mail/Outlook/SMTP, and resolves bounded follow-ups such as “what is its impact?” to the most recent grounded incident or change in that conversation. Impact, urgency, category and subcategory are included for visible tickets. When a follow-up asks for relationships, ServiceOps considers record links and attached CIs, but re-resolves every candidate through the same current ticket and CI permissions before placing it in the model payload. Knowledge-only questions retrieve only published, non-archived articles from the current tenant and do not add operational tickets or CIs.

Never available to the assistant for anyone: the user directory, audit log, client/customer data, attachments, settings and secrets, other tenants. A message asking for those, for other people's tickets by bulk, for credentials, or attempting to override the rules is answered with a fixed refusal **without calling the model** (audited as `ai chat denied`, reason code only). A reference to a ticket the asker cannot read is reported exactly as one that does not exist. Email addresses and phone numbers in ticket, comment and CI text are masked before the model sees them. Earlier answers are replayed to the model only if every source they cited is still readable; otherwise the history shows a withheld notice. Model output is checked: unknown record numbers become "[unverified reference removed]". A conversation is bound to the role it started under; using it as a different role is refused. Audit records carry counts, ids and reason codes, never questions or answers; nothing is logged.

*History.* Conversations are stored until the user deletes them (History, then Delete, confirm). Administrators cannot read another person's conversation. Deleting removes the messages and clears any run text still held. Erasing a user (GDPR) purges their conversations. Deletion is available even when chat is switched off. Limits: 2000 characters per question, 100 messages per conversation, 20 messages per user per minute, one active answer per user, and the tenant daily AI limit. Provider failures return safe operational guidance without exposing provider response bodies, credentials or internal exception text.

## Current boundaries

The 1.97.6 deployment can freeze a completed investigation answer as an exact ticket-comment proposal. This first AI-05 action has a separate administrator switch that defaults off, expires after 15 minutes, is bound to the ticket's exact update timestamp, repeats role/source/record authorization under a database lock, uses the existing comment service, and records proposal/rejection/stale/execution audits. Repeated approval cannot add a duplicate comment. State, assignment and priority actions, model-directed tool loops, embedding search and autonomous remediation remain outside the current implementation. Real commercial-model evaluation and production provider connectivity remain required before calling those providers verified.

## Adaptive setup and model limits (1.94.0)

Self-hosted: select the compatible server preset and enter its base address and API key if needed. The deployment operator must allowlist the destination. OpenAI or Anthropic: select the provider and enter its key; the address is built in. Other hosted compatible services: select a preset or enter the compatible base address and key. Hosted discovery and processing require administrator external-data consent. Custom authentication, Azure deployment/API-version routing and unrelated protocols need dedicated adapters; a key and URL cannot establish arbitrary API compatibility.

Use **Connect and detect models**. One listed model is selected automatically; choose explicitly when several exist. Save, then use **Test saved connection** for a synthetic prompt. Listing can succeed while inference permission, quota, loading or streaming fails. Discovery and the synthetic test send no operational records.

Only selected reported limits and capability indicators are stored, not raw templates or filesystem paths. llama.cpp runtime properties supply the active context and thinking-template support where available; router discovery disables autoload. Training context is never substituted for serving capacity. Rediscover after changing server runtime settings.

Requests use conservative UTF-8 byte accounting, not an exact tokenizer. Unknown limits use a 4096-token ceiling for a server on your network and 32,768 tokens for a hosted provider (which does not advertise its limit). Output is bounded by the administrator cap, reported output cap and one quarter of context. Required instructions and the newest question remain intact; older turns and evidence are shortened first. Oversized questions fail with an actionable message. Reasoning allowance is bounded too; unknown thinking controls are omitted. Provider context rejection fails closed without switching to another provider.

Streaming, tools, GPU memory, speed and pricing are not inferred from model names or successful listing. Existing administrator switches, private conversations, permission filtering, encrypted credentials and cancellation remain enforced. Migration does not alter existing enablement.
