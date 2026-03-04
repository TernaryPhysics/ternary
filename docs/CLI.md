# CLI Reference

TernaryPhysics command-line interface.

## Overview

```bash
ternaryphysics [options] <command> [args]
```

**Global Options:**
| Option | Description |
|--------|-------------|
| `--data-dir` | Data directory (default: `/var/lib/ternary-physics`) |
| `--map-path` | BPF map path (default: `/sys/fs/bpf/ternary-physics`) |
| `--log-path` | Log directory (default: `/var/log/ternary-physics`) |
| `-v, --verbose` | Verbose output |

## Commands

### status

Show system status.

```bash
ternaryphysics status
```

**Output:**
```
TernaryPhysics
AI at the kernel boundary

System Status
----------------------------------------
  System:         running
  Mode:           shadow (observing only)

  Active model:   v35
  Accuracy:       100.0%
  Total models:   35

  Samples:        500,000
  Auto-trains:    13
  Auto-deploys:   13
```

### models

List all model versions.

```bash
ternaryphysics models
```

**Output:**
```
Model Versions
----------------------------------------------------------------------
  Ver    Type             Accuracy   Samples
  -----  --------------   --------   ----------
   v35   Learning...       100.0%       500,000
   v34   Learning...       100.0%       462,864
  *v6    Learning...       100.0%       500,000
   ...

  * = active model
```

Show details for a specific model:

```bash
ternaryphysics models show 35
```

### live

Control live mode vs shadow mode.

```bash
# Show current state
ternaryphysics live

# Enable live actions (model will act on traffic)
ternaryphysics live on

# Disable live actions (shadow mode - observe only)
ternaryphysics live off
```

**Shadow mode**: Model observes and logs what it would do, but takes no action. This is the default for the first 30 days.

**Live mode**: Model takes action on traffic (drop, redirect, etc.).

### config

Show current configuration.

```bash
ternaryphysics config
```

**Output:**
```
Configuration
--------------------------------------------------
  Paths:
    Data directory:   /var/lib/ternary-physics
    BPF maps:         /sys/fs/bpf/ternary-physics
    Log directory:    /var/log/ternary-physics

  Training:
    Auto-train:       enabled
    Min samples:      1,000
    Train interval:   1h

  Safety:
    Shadow period:    30d
    Auto-rollback:    True
    Min accuracy:     90%

  Data Retention:
    Samples:          30d
    Audit log:        1y
    Model versions:   forever
```

### audit

Audit and compliance commands.

```bash
# Show audit summary
ternaryphysics audit

# Show recent audit events
ternaryphysics audit log

# Filter by event type
ternaryphysics audit log --type deployment
ternaryphysics audit log --type rollback
ternaryphysics audit log --type config_change

# Export for compliance (JSON or CSV)
ternaryphysics audit export --format json --output audit.json
ternaryphysics audit export --format csv --output audit.csv
```

**Audit events tracked:**
- Model deployments
- Rollbacks
- Configuration changes
- Live mode toggles
- Training runs

### rollback

Emergency rollback to previous model.

```bash
ternaryphysics rollback
```

This immediately reverts to the previous model version. Use when:
- Current model is misbehaving
- Unexpected behavior after deployment
- Need to quickly revert a change

The rollback is atomic and takes effect immediately.

## Examples

### Daily Operations

```bash
# Check system health
ternaryphysics status

# View recent models
ternaryphysics models

# Check if in shadow or live mode
ternaryphysics live
```

### After Shadow Period (30 days)

```bash
# Verify accuracy is good
ternaryphysics status

# Enable live mode
ternaryphysics live on

# Monitor for issues
ternaryphysics audit log
```

### Emergency Response

```bash
# Something wrong? Rollback immediately
ternaryphysics rollback

# Check status
ternaryphysics status

# Disable live mode if needed
ternaryphysics live off
```

### Compliance Export

```bash
# Export full audit log for compliance review
ternaryphysics audit export --format json --output /tmp/audit.json

# Export as CSV for spreadsheet analysis
ternaryphysics audit export --format csv --output /tmp/audit.csv
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | BPF maps not found |
| 4 | Permission denied |

## Files

| Path | Description |
|------|-------------|
| `/var/lib/ternary-physics/` | Data directory |
| `/var/lib/ternary-physics/models/` | Model versions |
| `/var/lib/ternary-physics/audit/` | Audit logs |
| `/sys/fs/bpf/ternary-physics/` | BPF maps |
| `/var/log/ternary-physics/` | Application logs |

## See Also

- [Installation Guide](INSTALL.md)
- [Quickstart](QUICKSTART.md)
- [Architecture](ARCHITECTURE.md)
