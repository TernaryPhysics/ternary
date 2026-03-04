# Contributing to TernaryPhysics

Thanks for helping build AI at the kernel boundary! This document explains how to report issues, propose features, and submit patches across kernel-space BPF code, the BitNet userspace stack, and supporting docs.

## Ways to Contribute

- **Issues** – Report bugs, performance regressions, feature requests, or documentation gaps. Include environment details (kernel version, NIC, distro, Python version, etc.) and reproduction steps.
- **Discussions** – Use GitHub Discussions (or issues tagged `question`) for design reviews, architecture ideas, or roadmap topics.
- **Documentation** – Improve READMEs, guides, and diagrams. Kernel and ML concepts benefit from clear prose—never hesitate to document your findings.
- **Code** – Fix bugs, add tests, improve observability, extend actions, or unlock new BitNet workflows.
- **Operational Knowledge** – Share deployment recipes, benchmarking scripts, and lessons learned from real environments.

## Ground Rules

1. Follow the [Code of Conduct](CODE_OF_CONDUCT.md).
2. All contributions are licensed under the project’s dual-license policy (`LICENSE`, `LICENSE-APACHE-2.0`, `LICENSE-GPL-2.0`). By submitting a patch you certify you have the right to do so under these terms.
3. Seek consensus early. Draft design docs or short proposals for major user-facing changes or kernel-level interfaces before writing large patches.
4. Keep changes focused. Prefer multiple small pull requests over one giant merge.

## Development Environment

| Area | Minimum Setup |
|------|---------------|
| Kernel/BPF | Linux 6.1+, Clang/LLVM `>= 16`, `bpftool`, `libbpf` headers, `make`, `clang-format` |
| Userspace BitNet | Python 3.10+, `pip` / `uv`, virtualenv, pytest, numpy, torch (optional for CPU training) |
| Tooling | `just`/`make`, Docker or Podman for deployment testing, GitHub CLI (optional) |

Typical workflow:

```bash
git clone https://github.com/<you>/kernelphysics.git
cd bpf-inference
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make -C core build
pytest bitnet/tests
```

Document any additional steps you take so others can reproduce them.

## Pull Request Checklist

Before requesting review:

- Tests and static checks pass: `pytest`, `make lint`, `cargo test` (when relevant), plus any directory-specific scripts mentioned in READMEs.
- User-facing or behavioral changes include docs and configuration samples.
- Added or modified telemetry fields and actions include version gates to avoid breaking running deployments.
- Commits are rebased on the latest `main` (avoid merge commits).
- Pull request description links to the issue (or explains rationale) and highlights risky or delicate areas (BPF verifier changes, concurrency, etc.).

## Coding Guidelines

**Kernel / BPF**

- Prefer small helpers and inline functions to satisfy the BPF verifier and keep stack usage predictable.
- Keep public structs and map layouts backwards-compatible; document versioned changes in `docs/` and the changelog.
- Run `clang-format` (LLVM style) on C headers and programs.
- Keep feature flags explicit; avoid hidden `#ifdef` behavior in shared headers.

**Userspace (Python, Rust, Go)**

- Favor type annotations and dataclasses for telemetry payloads.
- Use `black` / `ruff` (or the formatter listed in directory READMEs) to keep style consistent.
- Write unit tests for parsing, model training, and deployment logic. For hardware-heavy code, add mocks/fakes and note hardware requirements in the test docstrings.

**Documentation**

- Provide context for diagrams and include sources for metrics/benchmarks.
- When describing interfaces, include both kernel and userspace version numbers.
- Keep Markdown wrapped at ~100 columns to ease reviews.

## Release Notes and Changelog

If a pull request changes runtime behavior, APIs, or CLI output, append a note under the unreleased section of `CHANGELOG.md` (or create it if missing). Mention migration steps and compatibility notes (e.g., “map schema change requires redeploy”).

## Design Proposals

For significant new features (new action types, new trainer loops, discovery primitives), open a design doc under `docs/proposals/` or start a discussion with:

1. Problem statement and motivation.
2. Background, including related tickets or incidents.
3. Proposed solution with diagrams and data formats.
4. Testing and rollout strategy.
5. Alternatives considered.

We value early collaboration far more than perfect initial designs.

## Review Expectations

- Maintainers target first response within 2 business days.
- Small PRs (<200 LOC) typically need 1 approval; larger or kernel-touching ones need 2.
- Reviewers focus on correctness, safety, and operational impact. Style nits should be actionable and ideally automated by linters/formatters.
- Authors should respond to review feedback within 10 days or mark the PR as draft until ready.

## Getting Help

- Tag maintainers or subject-matter experts using GitHub mentions (e.g., `@KernelPhysics/maintainers` if available).
- Join community syncs or office hours announced in `SUPPORT.md`.
- Report security vulnerabilities privately via [SECURITY.md](SECURITY.md) or email `security@ternaryphysics.com`.
- Browse existing discussions, docs, and design notes before starting a new thread—your question may already be answered.

Thank you for helping push AI inference into the kernel safely and responsibly!
