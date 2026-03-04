# Governance

TernaryPhysics is an open-source project stewarded by the KernelPhysics maintainers. This document describes how decisions are made, who can merge code, and how we grow the community responsibly.

## Principles

- **Safety First** – Kernel and networking changes must prioritize reliability, reproducibility, and security over speed of delivery.
- **Transparency** – Design decisions, roadmap discussions, and enforcement actions happen in public channels whenever possible.
- **Merit & Accountability** – Maintainers earn trust by contributing high-quality work and supporting others. That trust can be revoked if responsibilities are neglected.
- **User Empathy** – Production operators, researchers, and experimenters all depend on stable APIs. Compatibility and migration guidance is mandatory.

## Roles

| Role | Description |
|------|-------------|
| **Contributor** | Anyone submitting issues, documentation, code, or feedback. |
| **Reviewer** | Contributors granted triage or review permissions for specific areas. They comment on PRs, label issues, and guide newcomers. |
| **Maintainer** | Responsible for end-to-end health of one or more subsystems (kernel BPF, BitNet, docs, deployment). Maintainers can merge PRs and cut releases. |
| **Project Lead** | Coordinates roadmap, resolves governance disputes, appoints or removes maintainers, and represents the project externally. |

Current maintainers and their primary areas are tracked in `MAINTAINERS.md` (create/update this file as the roster evolves). If the file does not yet exist, the KernelPhysics core team listed in the repository settings acts as the default maintainer set.

## Decision Making

1. **Lazy Consensus** – Most changes land when at least one maintainer approves and no other maintainer objects within 5 business days.
2. **Escalated Review** – Kernel verifier-impacting or externally facing API changes require two maintainer approvals, including at least one subject-matter expert for the affected subsystem.
3. **Request for Comment (RFC)** – Major initiatives (new runtime, sweeping refactors, license changes) follow the proposal process described in `CONTRIBUTING.md` and remain open for at least 14 days.
4. **Tie-Breaking** – If consensus cannot be reached, the Project Lead (or a delegate agreed upon by maintainers) makes the final decision after summarizing positions and rationale in the public thread.

## Elections and Succession

- **Adding Maintainers** – Any two existing maintainers may nominate a contributor. Nominations should describe the nominee’s track record, areas of expertise, and commitment level. Approval requires unanimous consent of current maintainers.
- **Stepping Down** – Maintainers may step down at any time by announcing it via issue or discussion so ownership can be reassigned.
- **Inactive Maintainers** – Maintainers inactive for 3 months without notice may be moved to *emeritus* status by majority vote so they no longer block reviews.
- **Project Lead Rotation** – The lead role is reviewed yearly. Another maintainer may volunteer or be nominated; selection requires majority support. If no alternate exists, the current lead continues.

## Releases

- Maintainers own the release cadence. Each release should have a captain responsible for branch cuts, changelog curation, and verifying that kernel maps and schemas remain compatible.
- Security or regression hotfixes may be cut outside the regular cadence. Release captains document any manual steps taken so future captains can follow the same playbook.
- Artifacts (packages, containers, drop-in configs) must be reproducible from the tagged commit. Signed tags (GPG/SSH) are strongly recommended.

## Incident Response

- Vulnerability reports follow the process in `SECURITY.md`.
- Operational incidents (failed release, data loss, regressions in deployed agents) require a retrospective posted in `docs/incidents/` or the relevant discussion area within 7 days.
- Maintainers coordinate fixes, backports, and communication with downstream users.

## Amendments

Changes to this governance document use the same RFC process as other policy updates. Explicit community feedback is required before merging modifications that alter voting rules, responsibilities, or the Code of Conduct.
