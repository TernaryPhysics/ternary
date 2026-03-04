# HackerNews Launch Post

## Title Options (pick one)

1. **TernaryPhysics: Neural networks running in eBPF, making decisions on every packet**
2. **Show HN: We put AI in the Linux kernel (eBPF + ternary neural networks)**
3. **Show HN: Sub-microsecond ML inference in eBPF for packet-level decisions**

---

## First Comment

Hey HN, I built TernaryPhysics to answer a question: what if ML inference happened at the exact moment a packet exists, before userspace ever sees it?

**The hack:** Ternary neural networks with weights of just {-1, 0, +1}. No floating point (eBPF won't allow it anyway), no multiplication—just addition and subtraction. Turns out you can fit useful models in the BPF verifier's constraints.

**What it does:**
- Scores every packet in <1μs
- Learns from network outcomes (timeouts, resets, failures become labels)
- Trains new models automatically, hot-swaps them with zero downtime
- No manual configuration or labeling

**Production stats:** 42+ hours continuous, 22 model versions auto-deployed, zero memory leaks.

**Why open source:** Kernel-space AI is too security-critical to be a black box. Dual licensed GPL-2.0 (kernel) + Apache-2.0 (userspace). Patent pending but code is free.

Install starts in shadow mode (observe-only for 14 days):
```
curl -sSL https://install.ternaryphysics.com | sh
```

GitHub: https://github.com/TernaryPhysics/ternary

Happy to answer questions about eBPF constraints, ternary quantization, the feedback loop, or anything else.

---

## Anticipated Questions & Answers

**Q: How do you handle the BPF verifier?**
A: Carefully. Fixed loop bounds, no unbounded memory access, stack under 512 bytes. The ternary weights help—no floating point, simple arithmetic. We've hit verifier limits a few times and had to restructure, but modern kernels (6.1+) are reasonable.

**Q: What's the accuracy vs full-precision models?**
A: Depends on the task. For packet classification (anomaly detection, load balancing hints), ternary models get within 2-5% of float32 accuracy. The speed tradeoff is worth it when you're running inference millions of times per second.

**Q: Why not XDP?**
A: We support both XDP and TC hooks. XDP is faster but more limited. TC gives you more context. The architecture works with either.

**Q: What about adversarial attacks?**
A: Real concern. The models see raw packet features, so adversarial crafting is possible. Mitigations: ensemble models, rate limiting on action changes, shadow mode validation. It's an active research area for us.

**Q: How is this different from Cilium/Katran/other eBPF projects?**
A: Those are excellent projects with hand-coded BPF logic. We're adding learned models that adapt to your specific traffic patterns. Complementary, not competitive—you could run both.
