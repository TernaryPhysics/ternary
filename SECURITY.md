# Security Policy

## Reporting Vulnerabilities

**Email:** security@ternaryphysics.com

Do not open public issues for security vulnerabilities.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Affected component (BPF code, userspace, training pipeline)
- Kernel version and environment details
- Impact assessment

## Response

| Timeframe | Action |
|-----------|--------|
| 48 hours | Acknowledgment |
| 7 days | Initial assessment and severity rating |
| 30 days | Fix for critical/high severity issues |

## Severity Levels

| Level | Definition |
|-------|------------|
| **Critical** | Remote code execution, privilege escalation, BPF verifier bypass |
| **High** | Information disclosure, denial of service affecting kernel stability |
| **Medium** | Local privilege escalation requiring specific conditions |
| **Low** | Minor issues with limited impact |

## Supported Versions

- `main` branch: Always supported
- Latest release tag: Supported
- Older releases: Best effort

## Safe Harbor

Security research conducted in good faith, following this policy, will not result in legal action. We ask for coordinated disclosure before public release.

## Recognition

Researchers who report valid vulnerabilities will be credited in release notes unless they prefer anonymity.
