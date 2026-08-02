# Australia UI guide capability mapping

Source reviewed: *Australia ServiceNow AI Platform user interface*, 1,148 pages, updated July 7, 2026.

This mapping uses the source guide as a behavioral reference. ServiceOps does not copy its text, images, product names, proprietary runtime, or implementation.

| Source guide family | ServiceOps implementation |
|---|---|
| Next Experience and unified navigation | Unified top navigation, collapsible application navigation, global search, favorites, history, notifications, help, preferences, and role-aware landing pages |
| Landing pages and dashboards | Operational dashboard, analytics workspace, workload counters, role-based record visibility, selectable start page |
| Configurable workspace | Purpose-built ticket, request, change, CMDB, catalog, approval, analytics, and ITIL administration workspaces |
| CMDB discovery | Manual administrator create/edit/retire for configuration items and CI-to-CI relationships; automated registration from Linux hosts via `PUT /api/v1/cmdb/configuration-items` (idempotent upsert-by-name) and a lightweight shell agent, with an example Puppet class for scheduled fleet-wide sync |
| Lists and filters | Searchable/filterable record lists, states, priorities, badges, responsive tables, empty states; administrator user list searches name, username, email and department |
| Forms and activity | Structured forms, field validation, comments/activity stream, work notes, related approvals, SLAs, checklist, attachments, audit events, and Incident section navigation for Notes/Related Records/Resolution/Event History |
| Favorites and history | Per-user persistent favorites and recently viewed pages, exposed as a single combined star control (list + toggle) plus a distinct history clock, each page carrying its own title so entries are distinguishable |
| Notifications | Per-user notification inbox with unread counts, approval notifications, and clickable links back to the source ticket/record/approval queue |
| Reference fields | Type-ahead search-as-you-type lookups for configuration items and cross-record linking (`/internal/lookup/cis`, `/internal/lookup/records`), showing a description line per match, in place of long unlabeled `<select>` dropdowns |
| Assignment and reassignment | Group-level assignment is always by team name, never by picking an individual manager; incidents and changes can be reassigned to a different owning IT-fulfillment team from the record detail page, which restarts change approval against the new team's manager |
| Manager/team work views | Manager portal (per-team open change/incident/task counts) and a unified "My tasks" queue covering CTASK/PTASK/EVTASK/SCTASK assigned to the user or their teams across every parent record |
| Dashboard personalization | Admin-configurable dashboard sections (Assigned to me, SLA breached/at-risk with configurable warning window, Recently updated) via System Settings, plus a live P1/P2 signal on the Incidents tile |
| Personalization and accessibility | Categorized General/List/Form/Notification preferences; compact/comfortable density, font scaling, high contrast, reduced motion, accessible tooltips, keyboard/date display/data-pattern preferences, sidebar pin preference, semantic labels and responsive layouts. Light-only by governed decision (ADR-012); no dark/system theme option exists |
| User profile and administration | Self-service name/contact/timezone/date-format profile, administrator-controlled user identity/role/active/department records, searchable user list, and capability-based administration home. Directory membership remains governed by AD mapping and team administration rather than editable self-service fields |
| Service Portal | Employee catalog, knowledge search, request tracking, requested-item stages, attachments, and self-service cases |
| Visual Task Boards | Drag-and-drop lifecycle lanes backed by ticket state, audit, and SLA updates |
| Global search | Tickets, knowledge, enterprise work, and configuration items |
| Attachments and checklists | Persistent Docker-backed file uploads/downloads and per-ticket actionable checklists |
| Guided help and onboarding | Help Center, contextual task guidance, and an interactive navigation tour |
| Themes and branding | ServiceOps design tokens (light-only, no user-selectable theme, ADR-012); deployment-owned branding colors/logo via installer and admin settings |
| Core UI developer tooling | Adapted as server-rendered Flask templates, reusable styles, routes, and automated tests |
| CMS, UI Builder, widget developer APIs, Angular providers, Jelly, and ServiceNow scripting APIs | Not applicable: these are vendor-specific development runtimes. ServiceOps uses Flask, Jinja, SQLAlchemy, CSS, and JavaScript instead |
| Advanced Work Assignment, Agent Chat, Virtual Agent, voice guidance, predictive recommendations | Requires external messaging, telephony, workforce-routing, or AI services and is not represented as locally operational |
| Native mobile apps and offline distribution | Responsive web access is implemented; native app publishing is not included |

## Verification expectations

Every capability described as implemented must have a working route or UI, persistent data where applicable, role enforcement, and automated or live runtime verification. Vendor-specific facilities are classified rather than represented by nonfunctional toggles.
