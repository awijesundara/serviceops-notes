# ServiceOps administration information architecture

## Governing rule

The compact application sidebar is the primary navigator. Release 1.46.0 uses
a persistent GLPI-inspired accordion so the hierarchy remains visible while
the main content changes. Its top-level applications are Home, My work,
Self-service, Management, Operations, and Administration. Only sections the
acting role may use are rendered.

Each application expands in place, one at a time. The application containing
the current destination opens automatically, and the exact destination keeps a
high-contrast active marker. A menu-only filter searches every visible module,
opens matching application and nested groups, and reports an empty result
without navigating away. The existing global search remains responsible for
searching both navigation destinations and application records.

Administration no longer takes over or replaces the left navigator. It expands
inside the same persistent application list. **User management** is a nested
group containing Users, Groups/teams/access, Roles/permissions, and Active
sessions. The remaining canonical administration destinations sit beside it:
Administration home, Service delivery and governance, Platform settings,
Integrations and delivery, Automation rules, API access, Audit and evidence,
System health, and (for superadministrators) Platform tenants.

Each destination has one canonical menu location. Operational CMDB, asset, and
analytics links live under Operations and are not duplicated on Administration
home. Main-search navigation aliases make administrative and operational pages
discoverable without adding repeated menu entries.

The compact top bar provides the sidebar toggle, global search, saved/recent
utility popovers, notifications, help, and preferences. The experimental
All/Favorites/History/Workspaces/Admin tab strip and oversized overlay panel
remain intentionally removed because they obscured content and reduced
navigation scanability. Administration-home capability cards remain useful as
an overview, while the sidebar provides direct, persistent navigation.

The administration information architecture follows this order:

1. Overview
2. Users and access
3. ITSM configuration
4. CMDB
5. Workflow and automation
6. Data management
7. Integrations
8. Security
9. User interface
10. Development
11. Deployment
12. System

Groups contain modules that open real ServiceOps pages or a precise section of
a settings page. ServiceNow capabilities that ServiceOps does not implement are
not presented as non-functional menu items.

## Capability ownership

| Area | Owns | Does not own |
|---|---|---|
| Platform settings | Organization and appearance defaults, sign-in providers, directory connection, security limits, workspace defaults, email delivery credentials, NetBox/RT credentials, effective deployment values | Ticket defaults, teams, approvers, change-approval scope, freeze windows, service offerings, SLAs, automation definitions |
| Service delivery and governance | Ticket defaults, catalog routing, directory-to-team mapping, team aliases and ownership, change-approval scope, approver authority, enforceable freeze windows, governance groups, service-to-CI mapping, calendars and service commitments | Authentication credentials, UI defaults, generic advisory banners |
| Users and access | User lifecycle, roles, account status, profile attributes | API credentials and directory connection settings |
| API access | Application credentials, acting users, limited permissions, revocation | Human accounts and sign-in providers |
| Audit and evidence | Integrity keys, retention, legal hold, verified export, event review | Operational configuration itself |
| Integrations and delivery | Webhook, SIEM, Teams and monitoring endpoints; delivery/outbox status | SMTP/NetBox/RT credentials, which remain protected platform settings |
| Automation rules | Published event-driven rules, controlled manual runs, schedules, run status, failure replay and execution evidence | Ticket defaults, change approval policy, arbitrary scripts |

## What an automation rule is

An automation rule is a controlled **when / if / then** instruction:

- **When** a supported event occurs, such as a ticket state change, SLA breach,
  manual run, API trigger, or schedule;
- **if** the rule's declared conditions match the event data;
- **then** ServiceOps performs only supported actions, such as adding history,
  waiting, invoking a reusable subflow, or queuing a notification.

Rules are versioned, validated before publication, tenant-scoped, rate-limited,
retryable, and recorded for audit. They cannot execute arbitrary shell or
Python code. Technical JSON simulation and execution evidence stay collapsed
under advanced controls so the default page remains understandable.

## Duplication decision

The free-text `CHANGE_FREEZE_MESSAGE` control is removed from the settings UI.
Enforceable change freeze windows are the sole administrative mechanism for
blocking scheduled changes. `CCB_REQUIRED_ENVIRONMENTS` is managed under
**Service delivery and governance → Change approval policy**, immediately beside
CCB authority and freeze windows. The policy determines *where* approval is
required; CCB authority determines *who* can approve. Platform settings no
longer displays this operational governance control.
