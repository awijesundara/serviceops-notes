# ServiceOps 1.38.2 remediation and release plan

> **Historical — superseded.** This plan's date (2026-08-05) and target
> version (1.38.2) are ~24 releases behind current (1.62.5 as of this note).
> Every gap it lists as open is tracked with materially more current status
> directly in `BACKLOG.md` (e.g. the privacy/data-governance item this plan
> treats as not-yet-started is B-090, now Verified). Kept for historical
> record of that release's scope and evidence, not as a live plan.

Date: 2026-08-05  
Release type: patch  
Owner: ServiceOps maintainers

## Release goal

Ship a reproducible 1.38.2 patch that closes the defects confirmed by the
whole-project review without overstating production readiness. The release
must keep runtime, installer, chart, documentation badge, example environment,
and service-worker versions synchronized from `ServiceOps/VERSION`.

## Included remediation

| Area | Change | Acceptance evidence |
|---|---|---|
| Release integrity | Extend the version synchronizer to the CLI installer and Helm image tag; release automation stages every governed version file | `tools/release_version.py --check`; release-version regression tests |
| Application security | Reject scheme-relative external return paths from improvement creation | Negative redirect regression test |
| Continuous integration | Run Ruff correctness checks, bytecode compilation, single-Alembic-head validation, the complete test suite, shell syntax, JavaScript syntax, and both Compose configuration modes before image publication | Successful supply-chain workflow and local equivalent checks |
| Accessibility baseline | Add a shared skip link and focusable main landmark; expose navigation expansion state; name the CI browser dialog | Rendered-layout regression test; independent WCAG audit still required |
| Deployment metadata | Replace stale CLI and Helm default image tags with 1.38.2 | Version consistency test and rendered Compose/Helm review |
| Read-only runtime | Disable Gunicorn 26's unused control socket so it does not write beneath the non-login user's `/nonexistent` home | Entrypoint regression assertion and clean deployed logs |

No database schema change is included. The expected migration head remains
`20260805_0056`.

## Release sequence

1. Complete the local quality gates and full containerized test suite.
2. Build `serviceops-app:1.38.2` from the exact reviewed tree.
3. Deploy it to the local Docker Compose environment without destroying its
   database or uploads, then verify app, worker, database, migration head, and
   `/health`.
4. Commit the ServiceOps implementation and this controlled documentation in
   their respective repositories.
5. Create immutable `v1.38.2` tags and push the reviewed commits/tags.
6. Retain the GitHub Actions run, image digest, scan, SBOM, signature, and
   attestations as the remote supply-chain evidence. A failed gate is fixed by
   a later patch; a published tag is never moved.

## Production-readiness goals that remain open

The following work cannot be completed or claimed by a local code review. It
remains release-governed work with its existing backlog owner and evidence
requirements:

- external penetration test and remediation (`B-008`);
- independent end-to-end tenant-isolation review, including dependent tables
  that are scoped through their parent (`B-202`, `B-231`);
- real GHCR signature/provenance and representative cluster admission tests
  (`B-007`);
- approved off-site backup/restore and production-like rollback rehearsals
  (`B-009`, `B-010`);
- production observability and load/soak/failover evidence (`B-070`, `B-071`);
- governed object storage, lifecycle, and malware-scanning operations (`B-052`);
- organization-enforced MFA, SCIM lifecycle, session controls, and emergency
  access (`B-062`);
- independent WCAG 2.2 AA audit (`B-080`); and
- operational privacy, retention, legal-hold, and data-subject controls
  (`B-090`).

Production promotion remains blocked by `PRODUCTION_READINESS_PLAN.md`; a
successful 1.38.2 application release is not itself a production-readiness
approval.

## Local acceptance evidence

- Full containerized test suite: `304 passed, 1 skipped`.
- Cross-repository documentation/version controls: `5 passed`.
- Ruff correctness checks, Python compilation, shell/JavaScript syntax, one
  migration head, and bundled/external Compose rendering: passed.
- Local Docker deployment: `serviceops-app:1.38.2`; app, worker, and PostgreSQL
  healthy; `/health` reports `1.38.2`; migration head `20260805_0056`.
- No `ERROR`, traceback, or Gunicorn control-socket failure appears in the
  post-fix app/worker log window.

## Remote release evidence

- Immutable application commit: `72b025d79d1b4ee3ef909f29ac4bc7a5a26cdae8`.
- Tag workflow: `https://github.com/awijesundara/ServiceOps/actions/runs/30996357438`
  completed successfully, including dependency audit, Trivy high/critical
  gate, SBOM generation, Cosign signing, attestations, and verification.
- Published image: `ghcr.io/awijesundara/serviceops@sha256:c790eec3aaab4145f68fadbbdb540e56584f3cb687904e958c57bbd43a6e8dc7`.
- GitHub Release: `https://github.com/awijesundara/ServiceOps/releases/tag/v1.38.2`.

This is real registry evidence, but not representative cluster-admission
evidence. The latter remains open under B-007.
