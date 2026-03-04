# Quickstart

Get TernaryPhysics running in under 5 minutes.

## Install

```bash
curl -sSL https://install.ternaryphysics.com | sh
```

## Verify

```bash
sudo ternaryphysics status
```

Expected output:
```
TernaryPhysics v0.1.0
Mode: shadow
Uptime: 2m 34s
Packets observed: 1,234,567
Models loaded: 1
Next training: 4h 23m
```

## Watch It Learn

```bash
# Live packet observations
sudo ternaryphysics watch

# Training progress
sudo ternaryphysics training status

# Model performance
sudo ternaryphysics models list
```

## Timeline

| Day | What Happens |
|-----|--------------|
| 0 | Install, enter shadow mode |
| 1-7 | System learns normal traffic patterns |
| 7-14 | Models train and validate |
| 14+ | Ready to go live (manual opt-in) |

## Go Live

After shadow mode completes:

```bash
# Review what the system learned
sudo ternaryphysics report

# Enable live mode
sudo ternaryphysics live --enable
```

## Commands

| Command | Description |
|---------|-------------|
| `status` | Current state and stats |
| `watch` | Live packet stream |
| `training status` | Training progress |
| `models list` | Deployed models |
| `report` | Summary of learned behaviors |
| `live --enable` | Exit shadow mode |
| `rollback` | Revert to previous model |

## Need Help?

- [Full Installation Guide](INSTALL.md)
- [GitHub Discussions](https://github.com/TernaryPhysics/ternary/discussions)
- [Bug Reports](https://github.com/TernaryPhysics/ternary/issues)
