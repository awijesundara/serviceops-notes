# ServiceOps controlled blueprint registry

This directory is the private source-of-truth register for supplied product
blueprints. A blueprint is an input specification, not evidence that a feature
is implemented. Delivery status is controlled through `BLUEPRINT_TRACEABILITY.md`,
`../BACKLOG.md`, tests, and release evidence.

## Registered sources

| ID | Title | Received | Source | Integrity |
|---|---|---|---|---|
| BP-001 | Blueprint for building your own ServiceNow-class ITSM platform | 2026-07-26 | Codex attachment `c43eee81-3c99-42be-8a2e-6cbdab3ae719/pasted-text.txt` | SHA-256 `4c4d4f0b6e589e277b7663e6e99e2699817dca567cdeda853585ab9cf759df48`; 2,060 lines; 43,034 bytes |

## Preservation rule

The registered source is immutable. Requirement interpretation, priorities and
acceptance criteria belong in the traceability document; the supplied wording
must not be silently rewritten. If a revised blueprint is supplied, register a
new source revision and record its relationship to BP-001.

## Non-deviation rule

Every BP-001 requirement must have:

1. a stable requirement identifier;
2. a disposition of verified, implemented, planned, deferred, rejected or
   externally dependent;
3. acceptance criteria and evidence;
4. a backlog or decision reference; and
5. release and live-validation evidence before it is called complete.

