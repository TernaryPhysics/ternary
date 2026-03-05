# TernaryPhysics

**AI at the kernel boundary. The decision happens at the moment the packet exists.**

Autonomous neural networks running in eBPF, making microsecond decisions on every packet at line rate.

[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)](LICENSE)
[![Patent](https://img.shields.io/badge/Patent-Pending-yellow.svg)]()

---

## What Is This?

TernaryPhysics puts AI directly in the Linux kernel (via eBPF) where it can see and act on 100% of network traffic before anything else.

**No configuration. No manual tuning.**

---

## Install

### Bare Metal / VM
```bash
curl -sSL ternary.sh | bash
```

### Kubernetes
```bash
kubectl apply -f https://ternaryphysics.com/k8s.yaml
```

**What happens:**
1. System enters 30-day **shadow mode** (observe only, no actions)
2. System adapts to your infrastructure
3. After validation, can go live and start acting on traffic

**No configuration required.** Zero manual tuning.

---

## What It Does

TernaryPhysics runs AI directly in the Linux kernel (via eBPF), making decisions on every packet at line rate:

- **Load balancing** – Routes traffic to healthy backends, avoids failures
- **Threat detection** – Blocks anomalies, DDoS, intrusion attempts
- **Observability** – Intelligently filters telemetry (keep signal, drop noise)
- **Auto-scaling** – Predicts capacity needs before saturation

---

## Key Features

### Kernel-Space Neural Networks
- **Ternary weights** {-1, 0, +1} optimized for eBPF constraints
- **Sub-microsecond inference** – Decisions happen before userspace sees the packet
- **Zero GPU dependency** – Runs on any Linux kernel with BPF support

### Adaptive System
- **Hot-swap deployments** – New models replace old ones atomically, zero downtime
- **Improves over time** – System adapts to your specific environment

### Production-Grade Safety
- **Shadow mode** – 30 days of validation before acting on traffic
- **Performance gates** – Blocks regressing models from deployment
- **Memory-safe** – Zero leaks, zero cleanup failures
- **One-command rollback** – Instant revert if needed

### Enterprise-Ready
- **Air-gap support** – Works offline, no internet required
- **No telemetry** – Your data stays on your infrastructure
- **Compliance-ready** – GDPR, HIPAA, FedRAMP-compatible architecture
- **30-day free trial** – Full feature access in shadow mode

---

## How It Works

**Per-packet inference (<1μs):**
```
Packet → BPF hook → Feature extraction → Ternary NN inference → Action (route/drop/mark)
```

Inference runs at line rate. Training happens asynchronously in userspace without blocking packet processing.

---

## Use Cases

### Financial Services
Sub-millisecond routing for trading infrastructure. Every decision immutably logged for regulatory audit.

### Defense & Government
Full air-gap operation. No cloud dependency, no phone-home. Classified environments supported.

### High-Frequency Infrastructure
API gateways, payment processors, real-time systems. Microsecond decisions that keep SLOs intact under load spikes.

### Kubernetes
Deploys as a DaemonSet. Sees all pod-to-pod traffic, ingress, and service mesh without sidecars or mesh changes.

---

## Documentation

- **Website:** [ternaryphysics.com](https://ternaryphysics.com)
- **CLI Reference:** [ternaryphysics.com/docs](https://ternaryphysics.com/docs)
- **Security:** [ternaryphysics.com/security](https://ternaryphysics.com/security)

---

## License

**Source:** Proprietary
**Binaries:** Freely available via container images and install scripts

The compiled binaries and container images are freely distributed. Source code is not publicly available.

See [LICENSE](LICENSE) for details.

---

## Patent

**Patent Pending**

U.S. Provisional Patent Application filed March 2026.

---

## Security

Report vulnerabilities: [security@ternaryphysics.com](mailto:security@ternaryphysics.com)

See [SECURITY.md](SECURITY.md) for our security policy.

---

## Support

- **Community:** [GitHub Discussions](https://github.com/TernaryPhysics/ternary/discussions)
- **Bug Reports:** [GitHub Issues](https://github.com/TernaryPhysics/ternary/issues)
- **Security:** [security@ternaryphysics.com](mailto:security@ternaryphysics.com)

## Community & Governance

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Governance](GOVERNANCE.md)
- [Security Policy](SECURITY.md)
- [Support](SUPPORT.md)

---

## Why "Ternary"?

Traditional neural networks use 32-bit floats. Ternary networks use {-1, 0, +1}.

**Benefits:**
- 16x smaller models (2 bits per weight vs 32)
- No multiplication (only add/subtract)
- Perfect for kernel constraints (eBPF has strict limits)
- Fast inference (sub-microsecond)

---

## Project Status

**Active Development**

TernaryPhysics is under active development.

Have feedback or feature requests? Open an issue on [GitHub](https://github.com/TernaryPhysics/ternary/issues).

---

**Copyright © 2026 TernaryPhysics**

Patent Pending
