# TernaryPhysics

**AI at the kernel boundary. The decision happens at the moment the packet exists.**

Autonomous neural networks running in eBPF, making microsecond decisions on every packet at line rate.

[![License](https://img.shields.io/badge/License-Dual%20(GPL--2.0%20%2B%20Apache--2.0)-blue.svg)](LICENSE)
[![Patent](https://img.shields.io/badge/Patent-Pending-yellow.svg)]()

---

## What Is This?

TernaryPhysics puts AI directly in the Linux kernel (via eBPF) where it can see and act on 100% of network traffic before anything else. It learns from real outcomes, trains models automatically, and deploys them with zero downtime.

**No configuration. No manual tuning. No human in the loop.**

---

## Install

### Bare Metal / VM
```bash
curl -sSL install.ternaryphysics.com | sh
```

### Kubernetes
```bash
kubectl apply -f install.ternaryphysics.com/k8s.yaml
```

**What happens:**
1. System enters 14-day **shadow mode** (observe only, no actions)
2. Learns your infrastructure's normal behavior
3. Trains models automatically from observed outcomes
4. After validation, can go live and start acting on traffic

**No configuration required.** Zero manual tuning.

---

## What It Does

TernaryPhysics runs AI directly in the Linux kernel (via eBPF), making decisions on every packet at line rate:

- **Load balancing** – Routes traffic to healthy backends, avoids failures
- **Threat detection** – Blocks anomalies, DDoS, intrusion attempts
- **Observability** – Intelligently filters telemetry (keep signal, drop noise)
- **Auto-scaling** – Predicts capacity needs before saturation
- **Continuous learning** – Improves autonomously from real outcomes

### The Flywheel

```
Packet arrives → AI scores → Action taken → Outcome observed → Label generated → Model retrains → Better decisions
```

**No human in the loop.** The system learns from what actually happens, not what you tell it.

---

## Key Features

### 🧠 Kernel-Space Neural Networks
- **Ternary weights** {-1, 0, +1} optimized for eBPF constraints
- **Sub-microsecond inference** – Decisions happen before userspace sees the packet
- **Zero GPU dependency** – Runs on any Linux kernel with BPF support

### 🔄 Continuous Learning
- **Outcome-based training** – Ground truth from network behavior, not manual labels
- **Hot-swap deployments** – New models replace old ones atomically, zero downtime
- **Feature discovery** – System discovers new signals automatically, generates BPF code

### 🛡️ Production-Grade Safety
- **Shadow mode** – 14 days of validation before acting on traffic
- **Performance gates** – Blocks regressing models from deployment
- **Memory-safe** – 20 deployments, zero leaks, zero cleanup failures
- **One-command rollback** – Instant revert if needed

### 🏢 Enterprise-Ready
- **Air-gap support** – Works offline, no internet required
- **No telemetry** – Your data stays on your infrastructure
- **Compliance-ready** – GDPR, HIPAA, FedRAMP-compatible architecture
- **14-day free trial** – Full feature access in shadow mode

---

## How It Works

### Two Paths, One System

**Decision Path (per packet, <1μs):**
```
Packet → BPF hook → Feature extraction → Ternary NN inference → Action (route/drop/mark)
```

**Learning Path (continuous background):**
```
Outcomes → Ground truth labeling → Model training → Validation → Hot-swap deployment
```

The decision path and learning path never block each other. Inference runs at line rate while training happens asynchronously in userspace.

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
- **Whitepaper:** [ternaryphysics.com/whitepaper](https://ternaryphysics.com/whitepaper)
- **CLI Reference:** [ternaryphysics.com/docs](https://ternaryphysics.com/docs)
- **Security:** [ternaryphysics.com/security](https://ternaryphysics.com/security)

---

## License

TernaryPhysics uses a **dual-license model**:

- **GPL-2.0** for BPF/kernel code (required by Linux kernel)
- **Apache-2.0** for userspace code (tooling, training, deployment)

See [LICENSE](LICENSE) for details.

### Open Source

TernaryPhysics is **free and open source** under dual license (GPL-2.0 for kernel code, Apache-2.0 for userspace).

You can:
- ✅ Use it freely in production
- ✅ Modify and redistribute
- ✅ Contribute improvements back
- ✅ Use commercially with proper attribution

See [LICENSE](LICENSE) for full details.

---

## Patent

**Patent Pending**

U.S. Provisional Patent Application filed March 2026 covering:
1. Kernel-space ternary neural network inference
2. Continuous learning feedback loop from network outcomes
3. Automatic feature discovery with BPF code generation
4. Shadow validation and hot-swap deployment
5. Memory-safe model lifecycle management

---

## Security

We welcome security researchers to help make TernaryPhysics safer.

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

**The physics:** Ternary weights create decision boundaries that are simpler, faster, and provably safe to run in kernel space.

---

## Project Status

**Active Development** 🚧

TernaryPhysics is under active development and has been successfully tested in production environments. We're preparing for broader community adoption.

**Contributions welcome!** See [CONTRIBUTING.md](CONTRIBUTING.md) to get involved.

---

**Copyright © 2026 TernaryPhysics**

Open Source · Patent Pending · Autonomous Infrastructure Intelligence
