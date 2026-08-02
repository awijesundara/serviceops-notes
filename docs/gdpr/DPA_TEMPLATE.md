# Data Processing Agreement — Template

This is a template for use when ServiceOps (the vendor) acts as a **Data
Processor** for a customer (the **Data Controller**). Per `ROPA.md`, this
applies when the vendor operates or has access to a customer's running
instance/data (e.g. a managed-hosting or SaaS variant, or vendor-provided
support requiring data access) — **not** to a purely self-hosted deployment
where the vendor has no access to the customer's database, files, or logs
at all (in that case there is no processor relationship for the vendor to
sign a DPA under, though the customer may still want this document's
security-measures section as a reference for their own internal records).

Bracketed `[...]` fields are to be filled in per engagement. This is a
drafting aid, not legal advice — have counsel review before execution.

---

## Data Processing Agreement

Between **[Customer Legal Name]** ("Controller") and **[ServiceOps Vendor
Legal Name]** ("Processor"), effective **[date]**, supplementing the
**[Master Services Agreement / Support Agreement reference]**.

### 1. Subject matter and duration

Processor provides **[hosting / managed operation / support access]** for
the Controller's ServiceOps instance. This DPA remains in effect for the
duration of that service and any period during which Processor retains
Controller Personal Data thereafter (see Retention, Section 7).

### 2. Nature and purpose of processing

Processor processes Personal Data solely to **[provide hosting
infrastructure / perform requested support actions / operate scheduled
maintenance]** for Controller's ServiceOps instance. Processor does not
process Controller Personal Data for its own purposes, including but not
limited to marketing, analytics not required for service delivery, or
disclosure to any party not listed in Section 5.

### 3. Categories of data subjects and personal data

Per `ROPA.md`, processed under this instance:

- **Data subjects**: Controller's employees, contractors, and any other
  individuals who use the ServiceOps instance as requesters, agents, or
  administrators.
- **Categories of personal data**: identity/contact data (name, email,
  phone, title, department, employee ID), authentication data (password
  hashes, external-identity provider subject IDs), ticket/service-request
  content (free text, potentially including personal data pasted by
  users), file attachments (arbitrary content), activity/audit data
  (IP addresses, user agents, action history), and, if configured, CMDB
  asset-owner associations. No special categories of data (Art. 9) are
  processed by design; Controller is responsible for not entering special
  category data into free-text fields, or for obtaining appropriate basis
  if they do.

### 4. Controller and Processor obligations

**Controller** shall: determine the lawful basis for all processing;
ensure data subjects are informed per Art. 13/14; configure the instance
(retention settings, authentication providers, integrations) consistent
with its own obligations; respond to or route data subject requests per
`DATA_SUBJECT_RIGHTS.md`, with Processor's support per Section 6 below;
ensure any third-party integrations it configures (SMTP relay, webhook
destinations, Teams, LDAP/OIDC provider) are themselves appropriately
governed, since Controller — not Processor — selects and controls those
destinations (see `ROPA.md` Processing activity 5).

**Processor** shall: process Personal Data only on documented instructions
from Controller (this DPA plus the underlying service agreement
constitute those instructions, absent a separate written instruction);
ensure personnel with data access are bound by confidentiality; implement
the technical and organizational measures in Section 8; assist Controller
with data subject requests, DPIAs, and breach notifications per Sections 6
and 9; not engage a sub-processor without the notice in Section 5; delete
or return Personal Data at the end of the engagement per Section 7; make
available information necessary to demonstrate compliance with this
Article-28-equivalent DPA and allow for audits per Section 10.

### 5. Sub-processors

Processor may engage the following sub-processors for the categories of
processing indicated. Processor will provide **[30] days'** advance notice
of any new sub-processor via **[notification channel — e.g. email to
Controller's designated contact, or a published sub-processor page]**,
during which Controller may object on reasonable data-protection grounds.

| Sub-processor | Purpose | Location | Data categories accessed |
|---|---|---|---|
| [Cloud infrastructure provider, if managed-hosting] | Hosting / infrastructure | [region] | All categories processed by the instance |
| [Email delivery provider, if Processor-operated SMTP] | Notification delivery | [region] | Name, email, notification content |
| [Object storage provider, if not customer-provided] | Attachment storage | [region] | Attachment content and metadata |
| [Monitoring/observability provider] | Infrastructure monitoring | [region] | Operational telemetry; avoid application-level personal data in monitoring pipelines where possible |

If Controller operates a fully self-hosted instance with no Processor
access to infrastructure, this table should read "Not applicable — no
sub-processors, as Processor has no access to Controller's instance or
data."

### 6. Assistance with data subject rights

Processor shall, upon Controller's request and within **[X business
days]**, provide reasonable technical assistance for Controller to fulfill
data subject requests under Art. 15-21, consistent with the mechanisms and
known gaps documented in `DATA_SUBJECT_RIGHTS.md` (e.g. Processor will
support Controller in retrieving a data-subject export bundle or executing
an erasure request against the instance, using the product's built-in
`user_erase()`-equivalent mechanism and any export routes provided).
Processor is not itself the point of contact for data subjects unless
separately agreed; Controller remains responsible for determining the
lawful response to each request.

### 7. Retention and deletion at termination

Processor retains Controller Personal Data only per Controller's
configured retention settings (`RETENTION_POLICY.md`) during the term.
Upon termination, Processor shall, at Controller's election, **[return all
Personal Data in a structured export format]** and/or **[delete all
Personal Data, including backups, within [X days]]**, except where
retention is required by applicable law (e.g. financial record-keeping),
in which case Processor shall isolate and protect such data and limit
processing to the retention purpose only.

### 8. Security measures

Processor implements, at minimum, the technical and organizational
measures already required of the ServiceOps product per
`ServiceOps/CLAUDE.md`'s Security requirements section, including:
tenant-scoped authorization enforced server-side; CSRF protection; secure
session lifecycle (`SESSION_COOKIE_SECURE`, `HttpOnly`,
`SameSite`); tamper-evident audit history (HMAC-SHA256 hash-chained audit
log); file-upload validation, content-type/extension verification,
cryptographic attachment hashing, and malware-scanning/quarantine hook;
SSRF-resistant, signed, DNS-rebinding-protected outbound webhooks; secret
redaction in logs (no passwords, tokens, connection strings, or LDAP bind
credentials logged); rate limiting and idempotency on mutating
integrations; least-privilege database roles and container configuration;
dependency and container image scanning. Where Processor also provides
infrastructure (managed-hosting variant), it additionally maintains
**[encryption at rest / encryption in transit / access logging / patching
SLA — fill in per actual infrastructure]**.

### 9. Breach notification

Processor shall notify Controller **without undue delay, and in any event
within [24-48] hours** of becoming aware of a Personal Data breach
affecting Controller's instance, providing the information available at
that time and supplementing it as the investigation per
`BREACH_NOTIFICATION.md` progresses, so Controller can meet its own
Art. 33 72-hour supervisory-authority notification obligation.

### 10. Audit rights

Controller may request, no more than **[once annually, or following a
security incident]**, evidence of Processor's compliance with this DPA,
including relevant audit reports, penetration test summaries, or, subject
to reasonable confidentiality and scheduling constraints, an on-site/remote
audit.

### 11. International transfers

Where Processor or any sub-processor processes Personal Data outside
Controller's jurisdiction or the EEA/UK (as applicable), such transfer is
made subject to **[Standard Contractual Clauses / an adequacy decision /
other approved transfer mechanism]**, attached as Annex **[X]**. For a
purely self-hosted deployment where Controller's own infrastructure (and
Controller-chosen SMTP/LDAP/webhook destinations) is the only place
Personal Data is processed, this Section is not applicable to Processor
(Controller remains responsible for its own third-party selections, per
`ROPA.md` Processing activity 5).

### 12. Liability and indemnity

**[Per Master Services Agreement / standard liability clauses — not
drafted here, requires counsel input specific to the commercial
relationship.]**

---

*Annexes to attach per engagement: (A) full sub-processor list if not
inlined above; (B) SCCs or other transfer mechanism if Section 11 applies;
(C) security measures detail beyond Section 8's summary, if Controller
requires an extended Annex II-style technical/organizational measures
document.*
