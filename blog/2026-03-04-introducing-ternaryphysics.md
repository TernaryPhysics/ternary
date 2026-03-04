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

## How It Works

**Decision path** (per packet, <1μs):
```
Packet → BPF hook → Feature extraction → Ternary NN → Action
```

**Learning path** (continuous background):
```
Outcomes → Ground truth → Training → Validation → Hot-swap deploy
```

The system learns from what actually happens. A connection that gets reset? That's a label. A request that times out? Label. A backend that goes unhealthy? Label.

No manual labeling. No human in the loop. The network teaches the model what matters.

## What It Does

- **Load balancing** - Routes to healthy backends, avoids failures before they cascade
- **Threat detection** - Blocks anomalies at line rate
- **Observability** - Filters telemetry intelligently (keep signal, drop noise)
- **Auto-scaling** - Predicts capacity needs before saturation

## Production Results

We've been running this in production:

- 42+ hours continuous operation
- 22 model versions deployed automatically
- Zero-downtime hot-swaps
- No memory leaks, no cleanup failures

The system trains itself. New model every few hours. Each one slightly better than the last.

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

The system starts in shadow mode—30 days of observation before taking any action. Watch it learn. See what it finds. Then decide if you want to let it act.

## Get Involved

- [GitHub](https://github.com/TernaryPhysics/ternary)
- [Documentation](https://ternaryphysics.com/docs)
- [Discussions](https://github.com/TernaryPhysics/ternary/discussions)

We're looking for contributors who understand eBPF, ML systems, or both. The intersection is small but growing. If you've ever wanted to hack on AI at the lowest level of the stack, this is your chance.

---

*TernaryPhysics: The decision happens at the moment the packet exists.*
