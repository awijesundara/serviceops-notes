# ITIL categorisation standard

Adopted 2026-09-27 at the product owner's direction. This is ServiceOps's
standard for record types and categorisation. It is written from the guidance
below, not from the ITIL Version 5 publications themselves, which are only
available through PeopleCert Plus membership. ServiceOps is *aligned with*
this guidance; it does not claim ITIL certification or conformance.

## Source guidance

- ITIL Version 5 launched on 29 January 2026 with 34 practices. The Foundation
  syllabus covers value co-creation, the four dimensions of product and service
  management, the Product and Service Lifecycle Model (PSLM), and continual
  improvement.
- Categorisation guidance sits inside individual practices (for example
  Incident Management and Service Request Management). It requires consistent
  categorisation; it does not prescribe the categories.

## Record types

The top-level types follow from the practices and carry over from ITIL 4.

| ITIL record type | ServiceOps record |
|---|---|
| Incident (unplanned interruption or degradation) | `Ticket` with `kind = "incident"` (INC) |
| Service request (standard, pre-approved request) | `CatalogRequest` (REQ) → `RequestedItem` (RITM) → `CatalogTask` (SCTASK) |
| Problem (underlying cause of one or more incidents) | `EnterpriseRecord` domain `problem` (PRB) with `ProblemProfile`; `OperationalTask` (PTASK) |
| Change (addition, modification or removal of a service component) | `Ticket` with `kind = "change"` (CHG) and `ChangeGovernance`; `OperationalTask` (CTASK) |
| Event or alert (monitoring signal, often automatic) | `MonitoringEvent`, and `EnterpriseRecord` domain `event` |
| Known error (problem with a documented cause or workaround) | `ProblemProfile.known_error`, listed at `/known-errors` |

## Category model (incidents)

Two levels. The starter tree seeded for a new tenant, and applied to existing
tenants by migration `20260927_0106`:

| Category | Subcategories |
|---|---|
| Hardware | Desktop, Laptop, Server, Storage, Peripheral |
| Software / Application | Business application, OS, Licensing, Patching |
| Network | LAN, WAN, VPN, DNS, Firewall, Wi-Fi |
| Access / Identity | Account creation, Password reset, Permissions, MFA |
| Infrastructure / Platform | Compute, Virtualisation, Containers, Cloud, Backup |
| Security | Malware, Phishing, Vulnerability, Policy breach |
| Data / Database | Availability, Performance, Corruption, Restore |
| Communication | Email, Telephony, Collaboration tools |
| Facilities / Endpoint services | Printing, Workplace equipment |

Administrators may adapt the tree (Service operations settings → Ticket
categories). Service requests are categorised through the service catalog
(catalog item and its category) rather than this tree.

## Design rules and how ServiceOps applies them

| Rule | Implementation |
|---|---|
| Two levels, three at most | Category → subcategory; no third level exists. |
| No more than about 8–10 options per level | The admin page states the rule and warns when a level has more than 10 active options (`CATEGORY_LEVEL_OPTION_LIMIT`). Not a hard block. |
| Categorise by the affected service or CI, not by the fix | Stated on the admin page and the incident Resolution block; subcategories can suggest a service offering; incidents link a configuration item. |
| Record category at logging and at closure separately | `Ticket.category/subcategory` are the logging categorisation, required on the new-incident form. `closure_category/closure_subcategory` are captured when resolving (defaulting to the logging values if none is chosen) and are only saved when resolving or on a resolved record, so an early prefill can't go stale. |
| Pair categorisation with impact and urgency to derive priority | Incident priority is calculated from impact × urgency; overriding it requires a manager and a reason. |
| Changes: classify by change model plus affected CI or service, not a symptom tree | New changes store no category/subcategory; the change form and record show the change model (Standard, Normal, Emergency) and configuration item instead. |

### Resolution data

- `resolution_notes` documents how service was restored. Resolving an incident
  from the web UI (record form, Resolve button, task board) requires it. The v1
  REST API accepts it but keeps it optional so existing integrations don't
  break; this is the one intentional difference between channels.
- `resolved_at` records the latest entry into Resolved (or into Closed without
  passing through Resolved) and is cleared on reopen. Mean time to resolve and
  the "resolved in the last 30 days" figures use it, falling back to
  `updated_at` only for tickets resolved before the column existed and without
  ticket history (migration `20260927_0105` backfilled the rest from history).
- Analytics shows incidents by closure category (falling back to the logging
  category where none was recorded) and the share recategorised at closure.

### Taxonomy changes and existing tickets

- Renaming a category or subcategory relabels the tickets that carry it, so
  reporting is not split across two labels.
- Deactivated ("retired") categories stay on existing tickets. The form shows
  them as "(retired)" and keeps them on save instead of recategorising.
- Tickets whose submitted category matched nothing (older integrations) are
  stored as `General`, which is no longer offered on the form and reads as
  uncategorised in reports.
- Startup seeding only seeds a tenant with no categories, so administrator
  changes are never overwritten on restart.

## Not covered or not claimed

- ITIL Version 5 practice content beyond the guidance above (the 34 practices,
  PSLM) has not been reviewed against the publications, which were not
  available.
- Affected CI or service is surfaced but not mandatory on changes.
- Categories recorded on incidents while the category picker was broken
  (2026-09-26 to the fix in `b56b608`) were reset to `General` on save. Ticket
  history holds the prior values; restoring them is a separate, approved data
  repair.
