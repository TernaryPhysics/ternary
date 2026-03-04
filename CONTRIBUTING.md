# Contributing to TernaryPhysics

Thank you for your interest in contributing to TernaryPhysics! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a branch** for your changes: `git checkout -b feature/your-feature-name`
4. **Make your changes** following our coding standards
5. **Test your changes** thoroughly
6. **Commit** with clear, descriptive messages
7. **Push** to your fork
8. **Open a Pull Request**

## Development Setup

```bash
# Clone the repo
git clone https://github.com/TernaryPhysics/ternary.git
cd ternary

# Follow install instructions
./deploy/install.sh
```

## What We're Looking For

### High Priority
- Bug fixes and stability improvements
- Performance optimizations
- Documentation improvements
- Test coverage expansion
- eBPF verifier compatibility improvements

### Welcome Contributions
- New feature extractors
- Additional action types
- Improved training algorithms
- Better monitoring and observability
- Example deployments and use cases

### Bigger Projects (Discuss First)
- Major architectural changes
- New deployment targets (e.g., Windows, BSD)
- Alternative ML backends
- Breaking API changes

## Code Standards

### eBPF/Kernel Code
- Follow Linux kernel coding style
- Keep functions small and focused
- Document any non-obvious logic
- Ensure BPF verifier compatibility
- Use SPDX-License-Identifier: GPL-2.0

### Python/Userspace Code
- Follow PEP 8 style guidelines
- Add type hints where helpful
- Write docstrings for public APIs
- Keep dependencies minimal
- Use SPDX-License-Identifier: Apache-2.0

### Commit Messages
```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain the problem this commit solves and why you chose this
approach over alternatives.

Fixes #123
```

## Testing

Before submitting a PR:

1. **Run existing tests** (if available)
2. **Test manually** in a safe environment
3. **Document test steps** in your PR description
4. **Consider edge cases** and failure modes

### Testing BPF Programs
- Test with BPF verifier on multiple kernel versions
- Verify memory bounds checking
- Test with high packet rates
- Check for resource leaks

### Testing Training Pipeline
- Test with small datasets first
- Verify model convergence
- Check hot-swap deployment works
- Monitor memory usage over time

## Pull Request Process

1. **Update documentation** if you're changing behavior
2. **Add tests** for new functionality
3. **Keep PRs focused** - one feature/fix per PR
4. **Respond to feedback** promptly and professionally
5. **Rebase on main** before merging to keep history clean

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings or errors
- [ ] Commit messages are clear

## Reporting Bugs

Use GitHub Issues to report bugs. Include:

- **Clear title** describing the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details**:
  - OS and version
  - Kernel version
  - Python version
  - Relevant hardware specs
- **Logs or error messages**
- **Minimal reproducible example** if possible

## Suggesting Features

We love feature suggestions! Open a GitHub Discussion or Issue with:

- **Use case**: What problem does this solve?
- **Proposed solution**: How would it work?
- **Alternatives**: What other approaches did you consider?
- **Impact**: Who would benefit from this?

## Code of Conduct

This project follows the Contributor Covenant Code of Conduct. By participating, you agree to uphold this code. Report unacceptable behavior to security@ternaryphysics.com.

## License

By contributing to TernaryPhysics, you agree that your contributions will be licensed under:

- **GPL-2.0** for kernel/BPF code
- **Apache-2.0** for userspace code

See [LICENSE](LICENSE) for details.

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/TernaryPhysics/ternary/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/TernaryPhysics/ternary/issues)
- **Security issues**: security@ternaryphysics.com

## Recognition

Contributors will be recognized in:
- Release notes for their contributions
- GitHub contributor graphs
- Project README (for significant contributions)

Thank you for helping make TernaryPhysics better!
