#!/bin/bash
#
# TernaryPhysics Installer
#
# AI at the kernel boundary. The decision happens at the moment the packet exists.
#
# Usage:
#   curl -sSL ternary.sh | sh
#   curl -sSL ternary.sh | sh -s -- --interface eth0
#
# Options:
#   --interface IFACE   Network interface to attach (default: auto-detect)
#   --data-dir DIR      Data directory (default: /var/lib/ternary-physics)
#   --no-start          Install but don't start services
#   --uninstall         Remove TernaryPhysics
#
set -e

VERSION="0.1.0"
RELEASE_URL="https://github.com/TernaryPhysics/ternary/releases/download/v${VERSION}/ternary-${VERSION}-linux-amd64.tar.gz"
INSTALL_DIR="/opt/ternary-physics"
DATA_DIR="/var/lib/ternary-physics"
BPF_PIN_PATH="/sys/fs/bpf/ternary-physics"
INTERFACE=""
NO_START=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[ternary]${NC} $*"; }
warn() { echo -e "${YELLOW}[ternary]${NC} $*"; }
error() { echo -e "${RED}[ternary]${NC} $*" >&2; }
banner() {
    echo -e "${BLUE}"
    cat << 'EOF'
  _____                                ____  _               _
 |_   _|__ _ __ _ __   __ _ _ __ _   _|  _ \| |__  _   _ ___(_) ___ ___
   | |/ _ \ '__| '_ \ / _` | '__| | | | |_) | '_ \| | | / __| |/ __/ __|
   | |  __/ |  | | | | (_| | |  | |_| |  __/| | | | |_| \__ \ | (__\__ \
   |_|\___|_|  |_| |_|\__,_|_|   \__, |_|   |_| |_|\__, |___/_|\___|___/
                                 |___/             |___/
EOF
    echo -e "${NC}"
    echo "  AI at the kernel boundary. Version $VERSION"
    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --interface)
            INTERFACE="$2"
            shift 2
            ;;
        --data-dir)
            DATA_DIR="$2"
            shift 2
            ;;
        --no-start)
            NO_START=1
            shift
            ;;
        --uninstall)
            # Uninstall mode
            log "Uninstalling TernaryPhysics..."
            systemctl stop ternary-observer 2>/dev/null || true
            systemctl stop ternary-ai 2>/dev/null || true
            systemctl disable ternary-observer 2>/dev/null || true
            systemctl disable ternary-ai 2>/dev/null || true
            rm -f /etc/systemd/system/ternary-*.service
            systemctl daemon-reload
            rm -rf "$BPF_PIN_PATH"
            rm -rf "$INSTALL_DIR"
            log "Uninstalled. Data preserved at $DATA_DIR"
            log "To remove data: rm -rf $DATA_DIR"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

banner

# Check requirements
check_requirements() {
    log "Checking requirements..."

    # Must be Linux
    if [[ "$(uname)" != "Linux" ]]; then
        error "TernaryPhysics requires Linux (BPF)"
        exit 1
    fi

    # Must be root
    if [[ $EUID -ne 0 ]]; then
        error "Please run as root: sudo sh -c '\$(curl -sSL ternary.sh)'"
        exit 1
    fi

    # Check kernel version (need 5.8+ for ringbuf)
    KERNEL_VERSION=$(uname -r | cut -d. -f1-2)
    KERNEL_MAJOR=$(echo $KERNEL_VERSION | cut -d. -f1)
    KERNEL_MINOR=$(echo $KERNEL_VERSION | cut -d. -f2)
    if [[ $KERNEL_MAJOR -lt 5 ]] || [[ $KERNEL_MAJOR -eq 5 && $KERNEL_MINOR -lt 8 ]]; then
        error "Kernel 5.8+ required for BPF ringbuf (found: $(uname -r))"
        exit 1
    fi
    log "  Kernel: $(uname -r) ✓"

    # Check BTF support
    if [[ ! -f /sys/kernel/btf/vmlinux ]]; then
        error "Kernel BTF not found. Enable CONFIG_DEBUG_INFO_BTF=y"
        exit 1
    fi
    log "  BTF: enabled ✓"

    # Check for required tools (no build tools needed - using pre-built binaries)
    for cmd in bpftool python3 curl; do
        if ! command -v $cmd &>/dev/null; then
            error "Required tool not found: $cmd"
            case $cmd in
                bpftool)
                    error "Install with: apt install linux-tools-common linux-tools-\$(uname -r)"
                    ;;
                *)
                    error "Install with: apt install $cmd"
                    ;;
            esac
            exit 1
        fi
    done
    log "  Tools: bpftool, python3, curl ✓"
}

# Auto-detect network interface
detect_interface() {
    if [[ -n "$INTERFACE" ]]; then
        if ! ip link show "$INTERFACE" &>/dev/null; then
            error "Interface not found: $INTERFACE"
            exit 1
        fi
        return
    fi

    # Find default route interface
    INTERFACE=$(ip route | grep default | head -1 | awk '{print $5}')
    if [[ -z "$INTERFACE" ]]; then
        # Fallback: first non-lo interface
        INTERFACE=$(ip link show | grep -E '^[0-9]+:' | grep -v lo: | head -1 | cut -d: -f2 | tr -d ' ')
    fi

    if [[ -z "$INTERFACE" ]]; then
        error "Could not detect network interface. Use --interface IFACE"
        exit 1
    fi

    log "  Interface: $INTERFACE (auto-detected)"
}

# Download and install
install_ternary() {
    log "Installing TernaryPhysics..."

    # Download release
    log "  Downloading v${VERSION}..."
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"

    if ! curl -sSL "$RELEASE_URL" -o ternary.tar.gz; then
        error "Failed to download release from $RELEASE_URL"
        exit 1
    fi

    # Extract
    log "  Extracting..."
    tar -xzf ternary.tar.gz --strip-components=1
    rm -f ternary.tar.gz

    # Create data directory
    mkdir -p "$DATA_DIR"/{models,metrics,samples}

    # Install Python dependencies
    log "  Installing Python dependencies..."
    pip3 install numpy 2>/dev/null || python3 -m pip install numpy 2>/dev/null || true

    log "  Installation complete ✓"
}

# Setup BPF maps
setup_bpf() {
    log "Setting up BPF..."

    # Create pin directory
    mkdir -p "$BPF_PIN_PATH"

    # Detach any existing XDP program (all modes)
    ip link set dev "$INTERFACE" xdpgeneric off 2>/dev/null || true
    ip link set dev "$INTERFACE" xdpdrv off 2>/dev/null || true
    ip link set dev "$INTERFACE" xdp off 2>/dev/null || true

    # Clean up old pins
    rm -f "$BPF_PIN_PATH"/* 2>/dev/null || true

    # Load all BPF programs with pinned maps
    log "  Loading observer on $INTERFACE..."
    bpftool prog loadall "$INSTALL_DIR/bpf/observer.o" "$BPF_PIN_PATH" \
        pinmaps "$BPF_PIN_PATH"

    # Attach XDP to interface
    ip link set dev "$INTERFACE" xdpgeneric pinned "$BPF_PIN_PATH/xdp_observer" 2>/dev/null || \
        bpftool net attach xdpgeneric pinned "$BPF_PIN_PATH/xdp_observer" dev "$INTERFACE"

    # Enable telemetry
    bpftool map update pinned "$BPF_PIN_PATH/telemetry_cfg" \
        key 0 0 0 0 \
        value 1 0 0 0  1 0 0 0  1 0 0 0  1 0 0 0  1 0 0 0  1 0 0 0

    log "  Observer attached to $INTERFACE ✓"
}

# Install systemd services
install_services() {
    log "Installing systemd services..."

    # Observer service (BPF loader)
    cat > /etc/systemd/system/ternary-observer.service << EOF
[Unit]
Description=TernaryPhysics BPF Observer
After=network.target
Wants=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
Environment=INSTALL_DIR=$INSTALL_DIR
Environment=BPF_PIN_PATH=$BPF_PIN_PATH
ExecStart=/bin/bash -c 'mkdir -p $BPF_PIN_PATH && rm -f $BPF_PIN_PATH/* 2>/dev/null || true && ip link set dev $INTERFACE xdp off 2>/dev/null || true && bpftool prog loadall $INSTALL_DIR/bpf/observer.o $BPF_PIN_PATH pinmaps $BPF_PIN_PATH && ip link set dev $INTERFACE xdpgeneric pinned $BPF_PIN_PATH/xdp_observer'
ExecStop=/bin/bash -c 'ip link set dev $INTERFACE xdp off; rm -rf $BPF_PIN_PATH'

[Install]
WantedBy=multi-user.target
EOF

    # AI service (feedback loop)
    cat > /etc/systemd/system/ternary-ai.service << EOF
[Unit]
Description=TernaryPhysics AI Feedback Loop
After=ternary-observer.service
Requires=ternary-observer.service

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/scripts/run_feedback_loop.py \\
    --bpf \\
    --data-dir $DATA_DIR \\
    --map-path $BPF_PIN_PATH \\
    --duration 8760h
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload

    log "  Services installed ✓"
}

# Start services
start_services() {
    if [[ $NO_START -eq 1 ]]; then
        log "Skipping service start (--no-start)"
        return
    fi

    log "Starting services..."
    systemctl enable ternary-observer
    systemctl enable ternary-ai
    systemctl start ternary-observer
    systemctl start ternary-ai

    log "  Services started ✓"
}

# Print status
print_status() {
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  TernaryPhysics installed successfully!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Installation:  $INSTALL_DIR"
    echo "  Data:          $DATA_DIR"
    echo "  Interface:     $INTERFACE"
    echo "  BPF maps:      $BPF_PIN_PATH"
    echo ""
    echo "  The system is now observing in SHADOW mode."
    echo "  It will learn from outcomes and improve over time."
    echo ""
    echo "  Commands:"
    echo "    systemctl status ternary-ai      # Check AI status"
    echo "    journalctl -fu ternary-ai        # View AI logs"
    echo "    cat $DATA_DIR/run_summary.json   # View metrics"
    echo ""
    echo "  To uninstall:"
    echo "    curl -sSL ternary.sh | sh -s -- --uninstall"
    echo ""
}

# Main
main() {
    check_requirements
    detect_interface
    install_ternary
    setup_bpf
    install_services
    start_services
    print_status
}

main
