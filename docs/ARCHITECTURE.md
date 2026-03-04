# Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         KERNEL SPACE                            │
│                                                                 │
│  ┌─────────┐    ┌─────────┐                                    │
│  │   XDP   │    │   TC    │                                    │
│  │ ingress │    │ egress  │                                    │
│  └────┬────┘    └────┬────┘                                    │
│       │              │                                          │
│       └──────┬───────┘                                          │
│              │                                                  │
│              ▼                                                  │
│      ┌───────────────┐      ┌───────────────┐                  │
│      │   observer    │ ───► │  telemetry    │ ─► ringbuf      │
│      │   .bpf.c      │      │  emit.h       │                  │
│      └───────┬───────┘      └───────────────┘                  │
│              │                                                  │
│              ▼                                                  │
│      ┌───────────────┐      ┌───────────────┐                  │
│      │   inference   │ ◄─── │  model_map    │ ◄─ hot-swap     │
│      │   engine.h    │      │               │                  │
│      └───────┬───────┘      └───────────────┘                  │
│              │                                                  │
│              ▼                                                  │
│      ┌───────────────┐                                         │
│      │    action     │  pass / drop / redirect / sample       │
│      │  primitives.h │                                         │
│      └───────────────┘                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           ↕ ringbuf
┌─────────────────────────────────────────────────────────────────┐
│                        USER SPACE                               │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │  Collector  │──►│   Trainer   │──►│  Deployer   │          │
│  │  (ringbuf)  │   │  (ternary)  │   │  (hot-swap) │          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
│         │                 ▲                 │                   │
│         │                 │                 │                   │
│         ▼                 │                 ▼                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │   Feature   │──►│   Labeler   │   │   Shadow    │          │
│  │    Store    │   │  (outcomes) │   │  Validator  │          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
│                                                                 │
│              Feedback Loop Controller                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Packet arrives** (XDP ingress or TC egress)
2. **Extract features** from packet headers
3. **Run inference** (ternary neural network)
4. **Take action** (pass, drop, redirect, sample)
5. **Emit telemetry** to ringbuf
6. **Userspace observes** outcomes
7. **Labels generated** from ground truth
8. **Model retrained** on labeled data
9. **Hot-swap deployed** to kernel
10. **Repeat forever**

## Components

### Kernel Space (core/)

| Component | File | Purpose |
|-----------|------|---------|
| Types | `types.h` | packet_obs, flow_obs, action, model_weights |
| Observer | `observer.bpf.c` | XDP/TC entry points |
| Inference | `inference/engine.h` | Variable-architecture ternary NN |
| Telemetry | `telemetry/*.h` | Ringbuf maps and emission |
| Actions | `actions/primitives.h` | Action execution |

### User Space (bitnet/)

| Component | Directory | Purpose |
|-----------|-----------|---------|
| Collector | `collector/` | Ringbuf consumer, feature store |
| Trainer | `trainer/` | Ternary model training with STE |
| Deployer | `deployer/` | BPF loading, hot-swap, rollback |
| Feedback | `feedback/` | Autonomous learning loop |
| Discovery | `discovery/` | Feature ranking, domain detection |

### Domain Detection

The system automatically determines what domain it's operating in based on behavior:

| Action | Category |
|--------|----------|
| DROP | Threat-Response |
| REDIRECT | Traffic-Steering |
| SAMPLE | Data-Collection |
| TAG | Traffic-Marking |
| PASS | Passthrough |

Roles emerge from outcomes (e.g., `blocked` → `Blocker`). Result: `Threat-Response: Blocker`.

## Model Architecture

Variable architecture defined by config:

```
n_features (1-8) → n_hidden (1-8) → n_outputs (1-4)
```

Weights are ternary {-1, 0, +1}:
- +1: add feature to sum
- -1: subtract feature from sum
- 0: skip (no operation)

No multiplication required. Just add, subtract, and ReLU.

## Telemetry

Events flow from kernel to userspace via BPF ringbuf:

```c
struct telemetry_event {
    __u64 timestamp_ns;
    __u64 flow_id;
    __u8  type;         // packet, flow, action, outcome
    __u8  action_type;
    __u8  outcome_type;
    __u8  n_features;
    __s32 score;
    __s32 features[8];
};
```

## Why Ternary?

1. **No floating point** - BPF doesn't support it
2. **Simple operations** - multiply becomes add/subtract/skip
3. **Small model** - fits in BPF instruction limit
4. **Fast** - <100 integer operations per inference
5. **CPU-only** - no GPU required for training or inference
