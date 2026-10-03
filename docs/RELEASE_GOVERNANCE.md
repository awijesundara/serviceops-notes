# ServiceOps release and version-control plan

## Policy

ServiceOps uses Semantic Versioning (`MAJOR.MINOR.PATCH`) and a single source
of truth: `ServiceOps/VERSION`. A release is immutable. A published tag is
never moved or rebuilt; a correction receives a new patch version.

- **Patch**: compatible fixes, security patches, and documentation/runtime corrections.
- **Minor**: backward-compatible capabilities or schema additions.
- **Major**: intentional breaking API, configuration, deployment, or schema contracts.

## Automated release path

1. Push signed changes to `main`; every push runs the supply-chain gate.
2. When the gate succeeds, **Governed release** runs automatically as a patch
   release. For a minor or major release, run it by manual dispatch with
   `increment: minor` or `major`. Never edit the version files by hand.
3. The workflow reads `VERSION`, calculates the next version, and synchronizes the runtime version, Helm chart and default image tag, README badge, service-worker cache identifiers, example environment, graphical installer, and CLI server installer.
4. It commits `chore(release): X.Y.Z`, creates the immutable annotated `vX.Y.Z` tag, and invokes the reusable supply-chain workflow against that exact tag.
5. The supply-chain gate runs release-consistency, Ruff correctness, bytecode, migration-head, complete-test-suite, shell/JavaScript syntax, both Compose-mode, and dependency-audit checks; it then builds and scans the image, generates an SBOM, pushes by source SHA, signs it, and publishes provenance/SBOM attestations.
6. Only after all gates pass does automation publish the GitHub release and generated release notes.

If a post-tag gate fails, there is no published GitHub release. Fix forward and
issue a new patch release; do not replace the failed tag. The release commit is
created through the GitHub API (`tools/release_commit.py`), so GitHub signs it,
and the tag is created only after that commit lands on `main`. If a version's
tag already exists from an earlier run, the workflow skips to the next version
of the same increment.

After the new release is deployed to MicroK8s and verified, delete every older
git tag and GitHub release so only the newest remains (GHCR image versions are
kept).

## Branch and change controls

- Current state (2026-10-03): the active `security` ruleset on `main` requires
  verified signatures, blocks force pushes and branch deletion, and requests
  Copilot code review on push. The sole maintainer pushes directly, and the
  supply-chain gate runs on every push. Pull requests, approvals and tag
  restrictions are the target once more than one person contributes.
- Every commit is authored and committed as Anushka Wijesundara and SSH-signed
  (GitHub "Verified"); no AI or bot attribution except the release workflow's
  `chore(release)` commit.
- `v*` tags are created only by the release automation.
- Use short-lived branches and descriptive commit subjects.
- Pair application changes with `serviceops-notes` changes whenever backlog, architecture, operational risk, or release evidence changes.
- Keep database migrations additive during a minor release line. Breaking migrations require a major release and a tested rollback/restore path.

## Required evidence

Each release retains the test run, dependency audit, container scan, CycloneDX
SBOM, image digest, Cosign signature, GitHub provenance attestation, migration
head, and generated release notes. Production promotion records the digest,
environment, approver, backup/recovery-set identifier, and rollback outcome.
