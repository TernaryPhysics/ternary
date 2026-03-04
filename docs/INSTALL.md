# Installation Guide

## Requirements

| Requirement | Minimum |
|-------------|---------|
| Linux Kernel | 6.1+ |
| CPU | x86_64 or arm64 |
| Memory | 2GB RAM |
| Clang/LLVM | 16+ (for BPF compilation) |
| Python | 3.10+ (for training pipeline) |

## Quick Install

### Bare Metal / VM

```bash
curl -sSL https://install.ternaryphysics.com | sh
```

### Kubernetes

```bash
kubectl apply -f https://install.ternaryphysics.com/k8s.yaml
```

## Manual Installation

### 1. Clone the Repository

```bash
git clone https://github.com/TernaryPhysics/ternary.git
cd ternary
```

### 2. Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y clang llvm libbpf-dev bpftool linux-headers-$(uname -r)
```

**Fedora/RHEL:**
```bash
sudo dnf install -y clang llvm libbpf-devel bpftool kernel-devel
```

**Arch:**
```bash
sudo pacman -S clang llvm libbpf bpf linux-headers
```

### 3. Build BPF Programs

```bash
make -C core build
```

### 4. Install Python Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Load BPF Programs

```bash
sudo ./ternaryphysics load
```

## Verify Installation

```bash
# Check BPF programs are loaded
sudo bpftool prog list | grep ternary

# Check service status
sudo systemctl status ternaryphysics

# View logs
sudo journalctl -u ternaryphysics -f
```

## What Happens After Install

1. **Shadow Mode (14 days)** - System observes traffic without taking action
2. **Learning** - Models train automatically from observed outcomes
3. **Validation** - Performance gates ensure models improve before deployment
4. **Live** - After validation, system can act on traffic (requires explicit opt-in)

## Configuration

TernaryPhysics runs with zero configuration by default. Optional settings:

```bash
# View current config
ternaryphysics config show

# Set shadow mode duration (default: 14 days)
ternaryphysics config set shadow_duration 7d

# Enable specific actions
ternaryphysics config set actions.load_balance true
ternaryphysics config set actions.threat_block true
```

## Uninstall

```bash
# Stop and remove
sudo ternaryphysics unload
sudo rm -rf /opt/ternaryphysics

# Remove systemd service
sudo systemctl disable ternaryphysics
sudo rm /etc/systemd/system/ternaryphysics.service
sudo systemctl daemon-reload
```

## Troubleshooting

### BPF verification fails

Ensure kernel version is 6.1+:
```bash
uname -r
```

### Permission denied

BPF operations require root:
```bash
sudo ternaryphysics load
```

### Missing libbpf

Install libbpf development headers for your distribution (see Dependencies above).

## Next Steps

- [CLI Reference](https://ternaryphysics.com/docs/cli)
- [Architecture Overview](https://ternaryphysics.com/docs/architecture)
- [Contributing](../CONTRIBUTING.md)
