# TernaryPhysics - Data Lifecycle

Complete guide to what data gets deleted, rotated, or kept forever.

## Quick Reference

| Data Type | Location | Retention | Cleanup | Recoverable |
|-----------|----------|-----------|---------|-------------|
| **Telemetry events** | RAM | 24h | Auto (every 60s) | ✗ No |
| **Flow histories** | RAM | 24h or LRU | Auto (time + LRU) | ✗ No |
| **Model versions** | Disk | 10 versions | Auto (rotation) | ✓ Last 10 |
| **Weight history** | Disk | 10 deployments | Auto (rotation) | ✓ Last 10 |
| **Test data** | Disk | Forever | Manual only | ✓ Yes |
| **BPF weights** | Kernel | Current only | Replaced | ✗ Backup first! |
| **Behavioral clusters** | RAM/Disk | 100 profiles | Auto (sliding) | ✗ No |
| **Logs** | Disk | System config | System (logrotate) | Depends |

## 1. Telemetry Events (Memory - DELETED)

**Location:** RAM only (FeatureStore)
**Retention:** 24 hours
**Cleanup:** Every 60 seconds
**Recoverable:** No - gone forever

### What Happens

```python
# Every 60 seconds
def _cleanup(self):
    cutoff_ns = time.time_ns() - retention_ns  # 24 hours ago

    # Delete old events from deques
    while self.all_events and self.all_events[0].timestamp_ns < cutoff_ns:
        self.all_events.popleft()  # DELETED, gone forever

    # Delete old samples
    while self.labeled_samples and sample_time < cutoff_ns:
        self.labeled_samples.popleft()  # DELETED

    # Delete old flow events
    for flow in self.flows.values():
        # Remove old events from each flow
        while flow.feature_events and flow.feature_events[0].timestamp_ns < cutoff_ns:
            flow.feature_events.popleft()  # DELETED
        while flow.action_events and flow.action_events[0].timestamp_ns < cutoff_ns:
            flow.action_events.popleft()   # DELETED
        while flow.outcomes and flow.outcomes[0].timestamp_ns < cutoff_ns:
            flow.outcomes.popleft()        # DELETED

    # Delete empty flows entirely
    stale_flows = [fid for fid, flow in self.flows.items()
                   if not flow.feature_events and not flow.action_events and not flow.outcomes]
    for flow_id in stale_flows:
        del self.flows[flow_id]  # DELETED
```

### Data Deleted

- `all_events`: All telemetry events > 24h old
- `labeled_samples`: All labeled samples > 24h old
- `flow.feature_events`: Per-flow feature history > 24h old
- `flow.action_events`: Per-flow action history > 24h old
- `flow.outcomes`: Per-flow outcome history > 24h old
- Empty flows: Flows with no remaining events

### Disk Storage

**NONE** - All telemetry lives only in RAM

### Why This is OK

Telemetry is exported to disk BEFORE it expires (every 6 hours during training).
The learned knowledge goes into model weights, which are permanent.

## 2. Flow Histories (Memory - LRU Eviction)

**Location:** RAM only (FeatureStore)
**Retention:** Until `max_flows` exceeded
**Cleanup:** Immediate LRU eviction
**Recoverable:** No - evicted flows are gone

### What Happens

```python
def _evict_lru_flow(self):
    """Remove least recently used flow when max_flows reached."""

    # Find oldest accessed flow
    lru_flow_id = min(self.flow_access_times, key=self.flow_access_times.get)

    # Delete entire flow history
    if lru_flow_id in self.flows:
        del self.flows[lru_flow_id]       # DELETED
    del self.flow_access_times[lru_flow_id]  # DELETED

    self.stats['flows_evicted'] += 1
```

### When Eviction Happens

```
max_flows = 1000 (default for 1GB droplet)

Flow 1 arrives   → 1 active flow
Flow 1000 arrives → 1000 active flows
Flow 1001 arrives → Evict Flow 1 (oldest), 1000 active flows
Flow 1002 arrives → Evict Flow 2, 1000 active flows
```

### Logging

```
WARNING: LRU evicted 100 flows (max=1000)
```

Logged every 100 evictions.

### Why This is Critical

**Without flow limits:**
- 10,000 flows = 3.3 GB RAM (exceeds 1GB droplet!)
- DDoS with 50k spoofed IPs = 16+ GB RAM = OOM kill

**With flow limits:**
- 1,000 flows = 300 MB RAM (safe for 1GB droplet)
- DDoS with 50k IPs = Still 300 MB (oldest flows evicted)
- System survives attack

## 3. Model Versions (Disk - Rotation)

**Location:** `/var/lib/ternary-physics/models/`
**Retention:** Last 10 versions
**Cleanup:** After each training run
**Recoverable:** Yes (last 10 versions)

### Directory Structure

```
/var/lib/ternary-physics/models/
├── v001_20250301_120000/  ← DELETED when v011 created
├── v002_20250301_180000/  ← DELETED when v012 created
├── ...
├── v010_20250302_060000/
├── v011_20250302_120000/  ← Latest
├── active -> v011_...     ← Symlink (PROTECTED)
└── shadow -> v010_...     ← Symlink (PROTECTED)
```

### What Happens

```python
def _cleanup_old_versions(self):
    """Remove old model versions."""
    max_versions = 10

    # Get all version directories
    versions = sorted([
        d for d in self.models_dir.iterdir()
        if d.is_dir() and d.name.startswith('v')
    ], reverse=True)

    # Keep symlink targets (active and shadow)
    keep = set()
    if self.active_link.exists():
        keep.add(self.active_link.resolve())
    if self.shadow_link.exists():
        keep.add(self.shadow_link.resolve())

    # Delete versions beyond max_versions
    for version in versions[max_versions:]:
        if version.resolve() not in keep:
            logging.info(f"Removing old version: {version.name}")
            shutil.rmtree(version)  # DELETE entire directory
```

### Each Version Contains

```
v011_20250302_120000/
├── weights.json      ← Model weights (JSON format)
├── weights.bin       ← Model weights (binary format)
├── metrics.json      ← Training metrics
└── meta.json         ← Metadata (timestamp, config)
```

All files deleted after 10 newer versions exist.

### Protection

**Active and shadow versions are NEVER deleted**, even if > 10 versions old.

### Disk Usage Timeline

```
Day 1:  100 MB  (v001)
Day 2:  200 MB  (v001-v002)
...
Day 10: 1 GB    (v001-v010)
Day 11: 1 GB    (v002-v011, v001 DELETED)
Day 12: 1 GB    (v003-v012, v002 DELETED)
...
Forever: ~1 GB  (always last 10 versions)
```

### Rollback

```bash
# List available versions
ls /var/lib/ternary-physics/models/

# Rollback to previous version
python -m bitnet.deployer.hot_swap rollback

# Rollback to specific version
python -m bitnet.deployer.hot_swap rollback --version v009_20250301_120000
```

## 4. Weight History (Disk - Rotation)

**Location:** `/var/lib/ternary-physics/weights/`
**Retention:** Last 10 deployments
**Cleanup:** After each deployment
**Recoverable:** Yes (last 10 deployments)

### Directory Structure

```
/var/lib/ternary-physics/weights/
├── v001_20250301_120000_deploy/  ← DELETED when v011 deployed
├── v002_20250301_130000_auto/    ← DELETED when v012 deployed
├── ...
├── v010_20250302_080000_deploy/
└── v011_20250302_090000_deploy/  ← Latest
```

### What Happens

```python
class WeightHistory:
    max_versions = 10

    def _cleanup_old_versions(self):
        """Remove old versions beyond max_versions."""
        versions = sorted(self.history_dir.iterdir(), reverse=True)

        # Delete old versions
        for old_version in versions[max_versions:]:
            if old_version.is_dir():
                shutil.rmtree(old_version)  # DELETE
                logging.debug(f"Removed old version: {old_version.name}")
```

### Each Deployment Contains

```
v011_20250302_090000_deploy/
├── weights.json   ← Full weight data
├── weights.bin    ← Binary weights for BPF
└── meta.json      ← Deployment metadata
```

All files deleted after 10 newer deployments.

### Deployment History

```bash
# List deployment history
python -m bitnet.deployer.hot_swap history

# Output:
Available versions (10):
  v011_20250302_090000_deploy: version=11, label=deploy
  v010_20250302_080000_auto: version=10, label=auto
  ...
```

## 5. Test Data (Disk - Manual Only)

**Location:** `/tmp/ternary-*` or custom directories
**Retention:** Forever (until manually deleted)
**Cleanup:** Manual only
**Recoverable:** Yes

### Files Created

```
/tmp/ternary-production-test/
├── samples.jsonl          (228 MB for 1M samples)
├── training_data.json     (44 MB)
├── decisions.json         (15 MB)
├── scheduler_state.json   (5 KB)
├── summary.json           (2 KB)
└── versions/
    ├── v001_20250301_120000/
    ├── v002_20250301_130000/
    └── ...
```

### Cleanup

```bash
# YOU must delete manually
rm -rf /tmp/ternary-production-test/*
```

### Disk Usage Risk

**Without cleanup:**
```
Day 1:  300 MB  (1 test run)
Day 7:  2 GB    (7 test runs)
Day 30: 9 GB    (30 test runs)
```

**Recommendation:** Delete after each test run or use unique temp directories.

## 6. BPF Weights (Kernel - Replaced)

**Location:** `/sys/fs/bpf/ternary-physics/model_map`
**Retention:** Current weights only
**Cleanup:** Atomic replacement
**Recoverable:** No (unless backed up first!)

### What Happens

```python
# Hot-swap deployment
bpftool map update pinned model_map key 0 value <NEW_WEIGHTS>

# Old weights → GONE instantly
# New weights → LIVE instantly
# Atomic operation (kernel sees old or new, never partial)
```

### History

**NONE** - Only current weights exist in kernel

### Backup Before Deploy

```bash
# ALWAYS backup before deploying
python -m bitnet.deployer.hot_swap backup --output /tmp/weights_backup.bin

# Then deploy
python -m bitnet.deployer.hot_swap deploy --weights new_weights.json

# Rollback if needed
python -m bitnet.deployer.hot_swap deploy --binary /tmp/weights_backup.bin
```

### Recovery

**Without backup:** No way to recover old weights
**With backup:** Can restore from backup file

## 7. Behavioral Clusters (Memory - Sliding Window)

**Location:** RAM + `/var/lib/ternary-physics/discovery/behavioral_clusters.json`
**Retention:** Last 100 profiles
**Cleanup:** Automatic sliding window
**Recoverable:** No

### What Happens

```python
class BehavioralClassifier:
    def _update_clusters(self, profile):
        self.clusters.append(profile)

        # Keep only recent profiles (sliding window)
        if len(self.clusters) > 100:
            self.clusters = self.clusters[-100:]  # DROP oldest 100+
```

### File Storage

```
/var/lib/ternary-physics/discovery/
└── behavioral_clusters.json  ← Overwritten every time
```

Only stores count, not full profiles:
```json
{
  "clusters": 95,
  "updated": true
}
```

## 8. Logs (Disk - System Managed)

**Location:** Depends on deployment
**Retention:** System configuration
**Cleanup:** logrotate or journald
**Recoverable:** Depends on system config

### Where Logs Go

**Systemd:**
```bash
journalctl -u ternary-physics
journalctl -u bitnet-ai
```

**Syslog:**
```bash
tail -f /var/log/syslog
```

**Docker:**
```bash
docker logs container_id
```

### Rotation

**NOT managed by application**

Configure via system:
- logrotate: `/etc/logrotate.d/ternary-physics`
- journald: `/etc/systemd/journald.conf`

## Backup Strategies

### Critical Data to Backup

```bash
# Model versions
tar czf models_backup.tar.gz /var/lib/ternary-physics/models/

# Weight history
tar czf weights_backup.tar.gz /var/lib/ternary-physics/weights/

# BPF weights (before deploy!)
bpftool map dump pinned /sys/fs/bpf/ternary-physics/model_map > weights.dump
```

### What NOT to Backup

- Telemetry events (will be gone in 24h anyway)
- Flow histories (will be gone in 24h or LRU anyway)
- Test data (can regenerate)
- Temporary files

### Backup Schedule

```bash
# Daily backup (cron)
0 0 * * * /usr/local/bin/backup-ternary-physics.sh

# Script:
#!/bin/bash
tar czf /backup/ternary-physics-$(date +%Y%m%d).tar.gz \
    /var/lib/ternary-physics/models/ \
    /var/lib/ternary-physics/weights/

# Keep last 7 days
find /backup -name "ternary-physics-*.tar.gz" -mtime +7 -delete
```

## Rollback Procedures

### Model Rollback

```bash
# Rollback to previous model version
cd /var/lib/ternary-physics/models
ln -sf v010_20250302_060000 active

# Hot-swap to kernel
python -m bitnet.deployer.hot_swap deploy --weights active/weights.json
```

### Weight Rollback

```bash
# Using weight history
python -m bitnet.deployer.hot_swap rollback

# Using backup
python -m bitnet.deployer.hot_swap deploy --binary /tmp/weights_backup.bin
```

### Cannot Rollback

- Telemetry events (deleted from RAM)
- Flow histories (evicted via LRU)
- BPF weights (unless backed up first)

## Monitoring Cleanup Operations

### Check Cleanup Status

```python
# FeatureStore stats
store.stats = {
    'events_received': 1234567,
    'flows_active': 850,
    'flows_evicted': 150,      # LRU evictions
    'memory_warnings': 0,       # High usage warnings
}
```

### Logs to Watch

```
# Normal cleanup
INFO: Removing old version: v001_20250301_120000

# LRU eviction
WARNING: LRU evicted 100 flows (max=1000)

# Memory pressure
WARNING: High memory usage: 520 MB (82% of max)

# Disk space
WARNING: Low disk space: 500 MB free (need 1000 MB)
```

## Disk Usage Projections

### Steady State (with cleanup)

```
Component          Size        Notes
─────────────────────────────────────────
Models (10 ver)    ~1 GB       Plateaus after 10 versions
Weights (10 dep)   ~100 MB     Plateaus after 10 deployments
Logs (system)      Varies      Managed by system
Test data          Varies      Manual cleanup required
─────────────────────────────────────────
Total steady       ~1.1 GB     Does NOT grow unbounded
```

### Without Cleanup (hypothetical)

```
Day 1:   100 MB
Day 10:  1 GB
Day 30:  3 GB
Day 90:  9 GB
Day 365: 36 GB   ← Unbounded growth!
```

**With cleanup, disk usage plateaus at ~1 GB.**

## Configuration

### Adjust Retention

```python
# Shorter retention (512MB droplet)
store = FeatureStore(
    retention_hours=12,  # 12h instead of 24h
    max_flows=500        # 500 instead of 1000
)

# Longer retention (4GB server)
store = FeatureStore(
    retention_hours=72,  # 3 days
    max_flows=10000      # 10k flows
)
```

### Adjust Version Limits

```python
# Keep more versions
trainer = ContinuousTrainer(
    max_versions=20  # 20 instead of 10
)

# Keep fewer versions (save disk)
trainer = ContinuousTrainer(
    max_versions=5   # 5 instead of 10
)
```

## Best Practices

1. **Backup before deploy** - Always backup BPF weights before hot-swap
2. **Monitor disk usage** - Set alerts at 80% capacity
3. **Monitor flow evictions** - High eviction rate indicates attack or misconfiguration
4. **Test rollback** - Periodically test rollback procedures
5. **Clean test data** - Delete test data after test runs
6. **Configure log rotation** - Set appropriate log retention via system
7. **Document custom configs** - If you change default retention/limits

## Troubleshooting

### Disk Full

```bash
# Check disk usage
df -h /var/lib/ternary-physics

# Find large directories
du -sh /var/lib/ternary-physics/*

# Reduce max_versions if needed
# Edit continuous trainer config
```

### High Memory Usage

```bash
# Check FeatureStore stats
# If flows_evicted is high, consider increasing max_flows
# Or reduce retention_hours

# Check memory
free -m
```

### Lost Data

**Telemetry events:** Cannot recover (deleted after 24h)
**Flow histories:** Cannot recover (LRU evicted)
**Model versions:** Recover from disk if < 10 versions old
**BPF weights:** Recover from backup (if you made one!)

## Summary

**Automatic cleanup:**
- ✓ Telemetry (24h, every 60s)
- ✓ Flow LRU (when max_flows exceeded)
- ✓ Model versions (10 version rotation)
- ✓ Weight history (10 deployment rotation)

**Manual cleanup required:**
- Test data
- Old backups
- Experiment outputs

**Disk usage plateaus** at ~1 GB with default settings.

**The AI's intelligence** lives in model weights (permanent), not telemetry (temporary).
