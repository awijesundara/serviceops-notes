# ServiceOps release and version-control plan

## Policy

ServiceOps uses Semantic Versioning (`MAJOR.MINOR.PATCH`) and a single source
of truth: `ServiceOps/VERSION`. A release is immutable. A published tag is
never moved or rebuilt; a correction receives a new patch version.

- **Patch**: compatible fixes, security patches, and documentation/runtime corrections.
- **Minor**: backward-compatible capabilities or schema additions.
- **Major**: intentional breaking API, configuration, deployment, or schema contracts.

## Automated release path

1. Merge reviewed changes to `main`; branch protection requires the supply-chain gate.
2. Run **Governed release** and select patch, minor, or major.
3. The workflow reads `VERSION`, calculates the next version, and synchronizes the Helm chart, README badge, and service-worker cache identifiers.
4. It commits `chore(release): X.Y.Z`, creates the immutable annotated `vX.Y.Z` tag, and invokes the reusable supply-chain workflow against that exact tag.
5. The supply-chain gate runs the full application suite and dependency audit, builds and scans the image, generates an SBOM, pushes by source SHA, signs it, and publishes provenance/SBOM attestations.
6. Only after all gates pass does automation publish the GitHub release and generated release notes.

If a post-tag gate fails, there is no published GitHub release. Fix forward and
issue a new patch release; do not replace the failed tag.

## Branch and change controls

- Protect `main`: pull requests, one approval, conversation resolution, and the supply-chain check are mandatory.
- Disallow force pushes and tag deletion; restrict `v*` tag creation to release automation.
- Use short-lived branches and conventional commit subjects (`feat:`, `fix:`, `docs:`, `chore:`).
- Pair application changes with `serviceops-notes` changes whenever backlog, architecture, operational risk, or release evidence changes.
- Keep database migrations additive during a minor release line. Breaking migrations require a major release and a tested rollback/restore path.

## Required evidence

Each release retains the test run, dependency audit, container scan, CycloneDX
SBOM, image digest, Cosign signature, GitHub provenance attestation, migration
head, and generated release notes. Production promotion records the digest,
environment, approver, backup/recovery-set identifier, and rollback outcome.
