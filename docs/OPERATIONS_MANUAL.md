# ServiceOps user guide

Version 2026 edition

This guide covers everyday use of ServiceOps: signing in, working with
tickets, the service catalog, approvals, and every major screen. Deployment,
security hardening, and upgrade procedures are covered separately in the
deployment guide — this manual is for people using the
product, not installing it.

![System architecture: browser and iOS clients call the stateless Flask application over HTTPS; the application reads and writes PostgreSQL and the uploads store, and hands scheduled/event work to a worker process that delivers notifications, SLA breaches, and workflow automation, with AD/LDAP, Keycloak, SMTP, webhooks, and chat integrations as optional adapters.](diagrams/architecture.png)

## Who does what

| Role | Can do |
|---|---|
| Requester | Submit and track requests and incidents, search knowledge |
| Agent | Triage, assign, fulfill, and resolve operational work |
| Manager | Everything an agent can, plus team oversight and approvals |
| CCB member | Review and approve planned changes |
| Administrator | Configure identity, teams, catalog, and platform settings |

Every incident, request, and change belongs to one owning team. Only an
active member of that team (or their manager, or an administrator) can
change it — other teams can view it for awareness, but can't edit it.
Someone with more than one role can switch which one is active from the
**Acting as** control under their name in the sidebar.

## Signing in

The sign-in page shows whichever methods your administrator has enabled:
single sign-on (Keycloak), a company directory account (AD/LDAP), or a local
account. If both directory and local sign-in are available, a dropdown lets
you pick. Directory usernames work in any familiar form —
`jsmith`, `jsmith@company.com`, or `CORP\jsmith`.

## Finding your way around

The left sidebar groups everything into **Home**, **My work**,
**Self-service**, **Management**, **Operations**, and **Administration**.
Opening one section closes the previous one, and the section containing
whatever page you're on opens automatically. Use **Find menu** at the top of
the sidebar to jump straight to a module by typing part of its name.

The search bar in the top bar searches across tickets, requests, knowledge
articles, configuration items, and more at once — not just navigation.

Click your name at the bottom of the sidebar to edit your profile, switch
role (if you have more than one), or sign out.

## The dashboard

![The ServiceOps dashboard: stat tiles for Incidents, Requests, Changes and Open work across the top, followed by Assigned to me, SLA breached, SLA at risk and Recently updated panels.](screenshots/dashboard.png)

The dashboard is your landing page after sign-in. The stat tiles across the
top link straight into the matching filtered list, and the Incidents tile
turns red whenever a high-priority incident is open. Below that:
**Assigned to me** lists your own open tickets by priority, **SLA
breached**/**SLA at risk** only show up when something needs attention, and
**Recently updated** shows the last records touched across everything you
can see — handy for picking back up after a context switch.

![My Workspace: a per-user, drag-configurable landing page built from widgets -- ticket stats, my open tickets, recent tickets, SLA-at-risk, approvals awaiting me, favorites, recently viewed, and notifications.](screenshots/my_workspace.png)

**My Workspace** (`/workspace`) is a personal alternative to the shared
dashboard — pick which widgets you want and lay them out however suits you.

## Working with tickets

### Report and resolve an incident

1. Click **+ Report an incident** on the dashboard, or **New** from the Incidents list.
2. Give it a concise title, describe the symptoms, and set business impact/urgency — ServiceOps calculates priority from those automatically.
3. Submit. The incident starts in state `New` and routes to its owning team.
4. An agent from that team sets it `In Progress` and works the issue — comments, attachments, and CI links all land in the Event history as they happen.
5. Once service is restored, the agent sets it `Resolved`; it moves to `Closed` once confirmed with the caller.

![The Incidents list workspace: a searchable, filterable, paginated table with Number, Opened, Short description, Caller, Priority, State, Category, Assignment group, Assigned to and Updated columns.](screenshots/incidents_list.png)

Every ticket list (Incidents, Changes, Requests) works the same way: a
**New** button, a state filter, free-text search, and pagination. Rows are
sorted newest-updated first, with a small dot marking priority (red for P1,
amber for P2). Click any row to open it.

![An open incident record: a lifecycle stepper (New → In Progress → Pending → Resolved → Closed) across the top, a two-column form with State, Priority, Category, Assignment group and Assigned to fields, and an Event history timeline below.](screenshots/incident_detail.png)

Every record type uses this same layout: a lifecycle stepper showing where
it is, a two-column form for its fields, and an Event history below
recording every change with who made it and when.

### Submit a change through approval

1. Open **New change**, pick the type (Standard/Normal/Emergency), and name the affected configuration item(s).
2. Fill in risk/impact, the planned window, and implementation, test, and backout plans.
3. Submit — the change enters `Awaiting Approval` and routes to the relevant manager and CCB.
4. Once every required approval is in, the change moves to `Approved` and can be scheduled and implemented.

![Normal change governance flow: Draft, then Team or manager approval, then CCB approval, then Approved, then Implementation with change tasks, then Post-implementation review. A material change made after Approved -- to scope, plan, risk, affected CIs, schedule, or assignment group -- invalidates the current approval chain and restarts the record at Draft.](diagrams/change_governance.png)

Editing an already-approved change's scope, plan, risk, or affected systems
resets it to `Draft` and starts a new approval cycle — this keeps the
approved record honest, so approving a change always means approving what
actually gets implemented.

![The Changes list workspace, filtered to a specific state, showing CHG-numbered records with their risk-bearing priority and assignment group columns.](screenshots/changes_list.png)

### Order something from the catalog

![The service catalog: a grid of orderable catalog items (Laptop Request, Software Request) each with a description, estimated delivery time, approval requirement and fulfilling team, and a "Request" button.](screenshots/catalog.png)

Browse the **Service catalog**, pick an item — each card shows up front
whether it needs approval and who fulfills it — fill in the form, and
submit. That creates a REQ (the order) and one RITM per item ordered.

![The Requests & RITMs list: REQ-numbered containers with Requested for, Items, State and Opened columns.](screenshots/requests_list.png)

Track your order afterward from **Requests & RITMs**.

![A RITM detail page showing its lifecycle stepper (Awaiting Approval → Open → Closed Complete), Opened/Opened by fields, and a Fulfillment tasks (SCTASK) panel below.](screenshots/ritm_detail.png)

Opening a RITM shows its own approval → fulfillment → completion journey,
plus every fulfillment task (SCTASK) needed to actually deliver it — the
RITM only completes once all of those do.

### Everything outstanding, in one place

![The Open work page: every incident, change and service request across the tenant that isn't resolved or closed yet, in one combined view.](screenshots/open_work.png)

**Open work** combines every unfinished incident, change, and request into
one list instead of three.

![The My tasks page: a queue of operational tasks and catalog fulfillment tasks assigned to the signed-in user, plus a secondary list of unassigned team work.](screenshots/my_tasks.png)

**My tasks** is your personal queue — everything assigned to you, plus a
second list of unclaimed team work you can pick up next. The sidebar link
shows a badge whenever something's waiting.

![A Kanban-style visual task board with New, In Progress, Pending, Resolved and Closed lanes, each containing draggable ticket cards.](screenshots/task_board.png)

The **task board** gives the same tickets a Kanban view — dragging a card
between lanes changes its state the same way editing the form would, so an
invalid move (like skipping a required approval) is rejected the same way.

### Approvals

![The My approvals page: pending approval chains grouped by target record, each showing its gates, the votes already cast, and inline approve/reject controls for the ones waiting on the signed-in user.](screenshots/approval_chains.png)

If you're a manager or CCB member, **My approvals** lists everything waiting
on your decision in one place, instead of you having to check every change
or request individually. A sidebar badge tells you when something's there.

### Review team performance as a manager

![The manager portal: one panel per team showing team-level open incident/change/task counts and SLA-breach totals, followed by a per-member table with status, workload and SLA columns.](screenshots/manager_portal.png)

Each team you manage gets its own panel in the **manager portal**: who's
active, how much is open against them, what they've resolved in the last 30
days, and their SLA performance. **Export CSV** and **Print / Save as PDF**
turn this straight into a report for a status meeting.

![A vertically indented org chart showing manager-to-report reporting lines, with each person's name, title, department and a role badge.](screenshots/org_chart.png)

The **org chart** is generated automatically from everyone's manager field —
no separate data entry required.

### Analytics

![The analytics page: SLA compliance and breach/at-risk stat tiles, a 14-day created-vs-resolved trend chart, backlog aging buckets, mean-time-to-resolve by priority, change success rate, priority/state distribution bars, and a busiest-teams ranking.](screenshots/analytics.png)

This is the tenant-wide performance view. The trend chart is the fastest way
to see if the backlog is growing or shrinking; backlog aging often catches
problems earlier than a raw open-ticket count does; and mean-time-to-resolve
by priority is the number most worth tracking week over week.

### Notifications

![The notifications inbox: a list of system notifications with unread items visually distinguished by a colored left border and accent dot.](screenshots/notifications.png)

You're notified for things worth reacting to — an SLA breach on your
ticket, a new approval request, a comment on something you're following.
Unread items stay visually marked until you open the record they refer to.

### Knowledge base

![The knowledge base: a card grid of published articles with title, summary and category.](screenshots/knowledge.png)

Search here before opening a ticket — a known-error article or workaround
can solve the problem immediately.

### CMDB and service map

![The CMDB page: a table of configuration items with Name, Class, Environment, Status, Lifecycle, Criticality, Location, Owning team and Owner columns, followed by a list of CI-to-CI relationships.](screenshots/cmdb.png)

The CMDB tracks every server, application, and service, and how they depend
on each other. Those relationships power conflict detection: scheduling a
change against something another in-flight change already touches surfaces
a warning before approval.

## For administrators

![The Platform settings page: tenant-wide configuration divided into identity and experience, protection and behavior, connections, and deployment groups; each field is marked Live or Restart required.](screenshots/admin_settings.png)

**Administration → Platform settings** is where tenant-wide configuration
lives: branding, security limits, SLA windows, LDAP/Keycloak, and more. Each
field shows whether a change applies immediately (**Live**) or needs a
restart to reach every running instance (**Restart required**).

![The Users & roles administration page: a searchable table of every user with username, name, role, department, active state and team membership, and a link into each user's editable record.](screenshots/users_roles.png)

**Users & roles** manages accounts, roles, and team membership. Directory
(AD/LDAP) accounts keep reconciling their team membership automatically on
every login — editing membership here only sticks for locally-managed
accounts.

![The audit log: a chronological, tamper-evident table of every recorded action across the tenant — actor, action, target and timestamp.](screenshots/audit_log.png)

The **audit log** records every create, update, and approval decision,
cryptographically chained so tampering would be detectable — the first
thing an auditor or incident responder would ask for.

![The Service delivery and governance page: operational records for catalog routing, people and teams, change governance, service mapping, calendars, and commitments.](screenshots/itil_admin.png)

**Service delivery and governance** is where the process framework itself
is configured: default catalog routing, SLA targets, business calendars,
and CCB membership. Changes here govern future tickets, not ones already in
flight.

![Guided tours administration: a list of admin-authored, versioned tours with ordered steps and role targeting, plus the tour-creation form.](screenshots/guided_tours_admin.png)

**Guided tours** lets you author step-by-step onboarding walkthroughs,
scoped to specific roles, that new users see as an on-page overlay.

![Data governance administration: retention policies, legal holds, and data classification, plus a queue for reviewing GDPR-style export/erasure requests.](screenshots/data_governance_admin.png)

**Data governance** manages retention policies, legal holds, and
export/erasure requests for client contacts.

![Client support mailbox administration: a list of configured IMAP/SMTP-polled inboxes with active/inactive toggles, and the mailbox-creation form.](screenshots/client_mailboxes_admin.png)

**Client support mailboxes** turns a real inbox into Client tickets —
inbound mail is threaded onto existing tickets or creates a new one; agent
replies go back out the same way.

### Installing, upgrading, and backing up

Installation, upgrades, backup/recovery, monitoring, and security hardening
are covered in full in the separate deployment guide. In short:

- Install via a signed RPM (`sudo serviceops setup`), Docker Compose, or Kubernetes/Helm for production scale.
- `sudo serviceops backup` / `rehearse-recovery` verify backups actually restore, not just that they exist.
- `sudo serviceops rehearse-upgrade` tests a pending upgrade against a disposable copy of production data before you run it for real.
- Every release ships as a signed, immutable image with provenance — upgrades are pinned by digest, never a moving tag.

See the deployment guide for the full installation walkthrough, production
checklist, and incident-response procedure.
