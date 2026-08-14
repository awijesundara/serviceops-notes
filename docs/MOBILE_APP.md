# ServiceOps iOS application

## Purpose and ownership

The native iPhone application is maintained in
[`awijesundara/ServiceOps_iOS`](https://github.com/awijesundara/ServiceOps_iOS).
It complements the ServiceOps web workspace; it does not replace the web
administration interface. The current release is iOS **1.3.0 (build 6)** and
connects to ServiceOps 1.70.1 through the versioned mobile REST API.

The web application exposes **ServiceOps mobile** in the Self-service menu,
global navigation search, and Help Center. That page links to the iOS source
and explains connection and APNs prerequisites.

## Authentication and audit identity

- Every mobile session belongs to a real ServiceOps local or LDAP user.
- Password authentication supports MFA and returns short-lived access plus
  rotating/revocable refresh tokens.
- Passkeys use the same tenant-bound WebAuthn relying-party policy as the web
  platform.
- Access and refresh tokens are stored only in the iOS Keychain.
- Face ID, Touch ID, or device-passcode recovery can lock a saved session when
  the app leaves the foreground.
- Mutations are attributed from the server-authenticated identity. Client
  headers provide iOS platform, version, build, and device context for audit
  evidence; they never choose the acting username.

## User capabilities

The five primary tabs are Home, My Work, Create, Inbox, and More. They provide:

- operational counts, major-incident visibility, recent work, and shortcuts;
- assigned incident/change lists with type filters and full-text client search;
- incident creation, state/priority updates, record refresh, and work notes;
- notification read/read-all behavior and unread badges;
- approval decisions, knowledge search, CMDB search, connection diagnostics,
  passkey management, biometric lock controls, sign-out, and the installed app
  version/build.

## Push notification architecture

The iPhone registers its APNs device token against the authenticated tenant
and user. ServiceOps stores the device identifier, token, environment, app
version, and last-seen state. Ticket, approval, and security notification
events enter the durable integration outbox. The worker signs an APNs JWT,
sends the notification using the configured sandbox or production endpoint,
records delivery outcomes, retries transient failures, and disables tokens
that APNs reports as invalid.

Required encrypted Platform settings are `APNS_TEAM_ID`, `APNS_KEY_ID`,
`APNS_PRIVATE_KEY`, and `APNS_BUNDLE_ID`. The bundle identifier must be
`wijesundara.com.ServiceOps`. The signing profile, entitlement, APNs endpoint,
and installed build environment must agree. Simulator inbox behavior can be
tested, but real remote APNs delivery requires a signed physical device build.

## Local development

The supported Docker development endpoint is `http://192.168.68.65:80` on the
`192.168.68.0/24` LAN. The app default omits `:80` because it is the HTTP
default. `127.0.0.1` works from the simulator for a Mac-hosted service but not
from a physical iPhone. Production and any non-isolated network use require
HTTPS.

No password, APNs key, signing identity, provisioning profile, device token,
or CoreDevice inventory belongs in either Git repository.

## Screenshot evidence

The iOS repository contains current iPhone 17 Pro simulator captures under
`docs/screenshots/` for Home, My Work, Notifications, and More. They were
captured from the real SwiftUI application with non-sensitive fixture records;
the temporary fixture was removed afterward, so no demo-data or
authentication-bypass path ships in source.

## Remaining external prerequisites

- Apple Developer team membership and a matching signed provisioning profile.
- An APNs `.p8` key configured outside Git.
- A physical-device sandbox delivery test, followed by a production-signed
  delivery test before distribution.
- Apple distribution/TestFlight or enterprise-distribution decisions and the
  associated privacy declarations.
