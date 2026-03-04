# Introducing TernaryPhysics: AI in the Kernel

Today we're open-sourcing TernaryPhysics, a system that runs neural networks directly in the Linux kernel via eBPF.

## The Problem

Modern infrastructure generates millions of packets per second. By the time those packets reach userspace, get processed by your application, and trigger a decision, it's too late. The latency is measured in milliseconds. The damage is done.

We asked: what if the AI was already there, at the exact moment the packet exists?

## What We Built

TernaryPhysics puts neural network inference directly in eBPF. Every packet gets scored in sub-microsecond time, before userspace ever sees it.

The key insight: ternary neural networks. Instead of 32-bit floating point weights, we use just three values: -1, 0, +1. This means:

- No floating point math (eBPF doesn't allow it anyway)
- 16x smaller models
- Inference is just addition and subtraction
- Fast enough to run on every packet at line rate

## What It Does

- **Load balancing** - Routes to healthy backends, avoids failures before they cascade
- **Threat detection** - Blocks anomalies at line rate
- **Observability** - Filters telemetry intelligently (keep signal, drop noise)
- **Auto-scaling** - Predicts capacity needs before saturation

## Why Open Source

Kernel-space AI is too important to be proprietary. The attack surface is too large. The stakes are too high.

We're releasing under dual license:
- GPL-2.0 for kernel/BPF code (required by Linux)
- Apache-2.0 for userspace components

Patent pending on the core innovations, but the code is free to use, modify, and deploy.

## Try It

```bash
curl -sSL https://install.ternaryphysics.com | sh
```

The system starts in shadow mode—30 days of observation before taking any action. Watch it work. Then decide if you want to let it act.

## Get Involved

- [GitHub](https://github.com/TernaryPhysics/ternary)
- [Documentation](https://ternaryphysics.com/docs)
- [Discussions](https://github.com/TernaryPhysics/ternary/discussions)

We're looking for contributors who understand eBPF, ML systems, or both. If you've ever wanted to hack on AI at the lowest level of the stack, this is your chance.

---

*TernaryPhysics: The decision happens at the moment the packet exists.*
