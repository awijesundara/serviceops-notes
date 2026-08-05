# ServiceOps notes

Authoritative home for all ServiceOps development notes, governed backlog,
release-readiness evidence, engineering references, deployment guidance, and
internal and operator-facing documentation. The public `ServiceOps` repository
contains application code, tests, its root project README, and only the
generated `docs/ServiceOps_Complete_Platform_Manual.pdf` artifact; it links
here instead of duplicating documentation sources.

- `CLAUDE.md` — collaboration instructions for AI-assisted development on ServiceOps.
- `docs/FEATURE_CATALOG.md` — canonical detailed inventory of every implemented ServiceOps feature and its explicit boundaries.
- `docs/` — governance, backlog, traceability, ITIL, API, deployment, and engineering reference docs.

## Repository ownership rule

All documentation sources and their images must be edited here. Do not copy
the operations manual source, API reference, backlog, engineering reference,
release evidence, deployment guidance, or documentation images into
`ServiceOps`; link to the canonical file instead. Changes spanning code and
documentation should use paired pull requests that cross-link each other and
merge the notes update no later than the code update.

The generated manual PDF is deliberately written to the sibling `ServiceOps`
repository so it can ship as a self-contained release artifact.
