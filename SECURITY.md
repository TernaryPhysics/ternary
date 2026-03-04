# Security Policy

TernaryPhysics pushes AI inference into kernel-space, so we take security reports seriously. Please follow the process below to keep users protected while we investigate and patch issues.

## Supported Versions

| Component | Supported Branches | Notes |
|-----------|-------------------|-------|
| `main` | ✅ | Active development. Security fixes land here first. |
| Latest release tag (e.g., `vX.Y.Z`) | ✅ | Maintainers backport critical patches when feasible. |
| Older releases | ⚠️ | May receive fixes on a best-effort basis. Please plan to upgrade. |

## Reporting a Vulnerability

1. **Do not disclose publicly** until a fix is available.
2. Open a private [GitHub Security Advisory](https://docs.github.com/code-security/security-advisories/repository-security-advisories/creating-a-repository-security-advisory) for the `TernaryPhysics/ternary` repository **or** email `security@ternaryphysics.com`.
3. Include:
   - A clear description of the issue and why it is a security problem.
   - Reproduction steps, proof of concept, or exploit script if possible.
   - Environment details (kernel version, NIC, eBPF hooks used, deployment mode).
   - Impact assessment (confidentiality, integrity, availability) and any mitigation ideas.
4. Encrypt email reports when feasible (PGP fingerprints will be published once available; until then, prefer GitHub advisories).

## Response Process

- A maintainer will acknowledge receipt within **3 business days**.
- The security team triages severity (Critical, High, Medium, Low) and keeps the reporter updated at least weekly.
- Fixes are developed in private forks until ready for coordinated disclosure.
- Once patches are ready, maintainers:
  1. Prepare advisories with CVE request when applicable.
  2. Backport patches to supported release branches.
  3. Publish releases and documentation describing mitigation steps.
- Reporters are credited (if desired) in the final advisory.

## Safe Harbor

Good-faith security research that respects this policy, does not exploit data belonging to others, and avoids privacy violations will not be pursued legally by the project maintainers. Coordinated disclosure keeps everyone safer.

Thank you for helping keep kernel AI inference secure.
