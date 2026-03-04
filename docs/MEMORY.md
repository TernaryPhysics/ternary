# TernaryPhysics - Memory Management

Comprehensive memory management strategy to prevent OOM kills and ensure stable operation on constrained hardware (512MB-1GB droplets).

## Memory Architecture

### Components and Limits

```
┌─────────────────────────────────────────────────────────────┐
│ FeatureStore (In-Memory Time-Series)                        │
├─────────────────────────────────────────────────────────────┤
│ all_events: deque(maxlen=1,000,000)          ~191 MB        │
│ labeled_samples: deque(maxlen=500,000)       ~143 MB        │
│ flow_histories: Dict[flow_id, FlowHistory]   ~300 MB*       │
│                                                              │
│ *With max_flows=1000, each flow ~300KB                      │
│                                                              │
│ Total Estimated Max: 634 MB (1GB droplet safe)              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ BehavioralClassifier                                         │
├─────────────────────────────────────────────────────────────┤
│ clusters: List[BehavioralProfile]            ~1 MB          │
│ (sliding window, max 100 profiles)                          │
└─────────────────────────────────────────────────────────────┘
```

## Hard Limits

### FeatureStore

| Structure | Max Size | Bytes/Item | Total Memory |
|-----------|----------|------------|--------------|
| all_events | 1,000,000 | ~200 | 191 MB |
| labeled_samples | 500,000 | ~300 | 143 MB |
| flow_histories (1k flows) | 1,000 flows | ~300 KB | 300 MB |
| **Total** | | | **634 MB** |

### Per-Flow Limits

Each FlowHistory has bounded deques:
- `feature_events: deque(maxlen=1000)` - feature vectors
- `action_events: deque(maxlen=1000)` - actions taken
- `outcomes: deque(maxlen=100)` - outcome observations

Total per flow: ~2,100 events × 150 bytes = 300 KB

## Flow Count Management

### Why Flow Limits Matter

Without flow limits, memory can grow unbounded:

| Active Flows | Flow Memory | Total Memory | Outcome |
|--------------|-------------|--------------|---------|
| 100 | 30 MB | 364 MB | ✓ Safe |
| 1,000 | 300 MB | 634 MB | ✓ Safe (1GB) |
| 5,000 | 1,502 MB | 1,836 MB | ✗ OOM on 1GB |
| 10,000 | 3,004 MB | 3,338 MB | ✗ OOM on 1GB |
| 50,000 | 15,020 MB | 15,354 MB | ✗ OOM |

**Critical**: Without `max_flows`, a DDoS attack with 10k+ unique flows causes OOM.

### LRU Eviction

When `max_flows` is reached, the least recently used flow is evicted:

```python
class FeatureStore:
    def __init__(self, max_flows: int = 1000):
        self.max_flows = max_flows
        self.flows: Dict[int, FlowHistory] = {}
        self.flow_access_times: Dict[int, int] = {}

    def add_event(self, event: TelemetryEvent):
        # Check limit before creating new flow
        if len(self.flows) >= self.max_flows:
            self._evict_lru_flow()  # Remove oldest flow

        # Update access time for LRU
        self.flow_access_times[event.flow_id] = event.timestamp_ns
```

**LRU Algorithm:**
1. Find flow with oldest `flow_access_times` entry
2. Delete flow from `self.flows`
3. Delete access time from `self.flow_access_times`
4. Increment `stats['flows_evicted']`

**Logging:**
- Warning every 100 evictions: `"LRU evicted 100 flows (max=1000)"`

## Time-Based Cleanup

### Retention Window (24 hours)

Every 60 seconds, cleanup thread removes old data:

```python
def _cleanup_loop(self):
    while True:
        time.sleep(60)
        self._cleanup()            # Remove old events
        self._check_memory_usage() # Monitor usage
```

**Cleanup Process:**
1. Remove events older than `retention_ns` (24h)
2. Remove labeled samples older than retention
3. Remove old events from per-flow histories
4. Delete flows with no remaining events
5. Clean up orphaned `flow_access_times` entries

## Memory Monitoring

### Active Monitoring

Every 60 seconds, estimate current memory usage:

```python
def _check_memory_usage(self):
    events_mb = len(self.all_events) * 200 / 1024**2
    samples_mb = len(self.labeled_samples) * 300 / 1024**2

    total_flow_events = sum(
        len(f.feature_events) + len(f.action_events) + len(f.outcomes)
        for f in self.flows.values()
    )
    flows_mb = total_flow_events * 150 / 1024**2

    total_mb = events_mb + samples_mb + flows_mb

    # Warn if > 80% of estimated max
    if usage_pct > 80:
        logging.warning(
            f"High memory usage: {total_mb:.0f} MB ({usage_pct:.0f}% of max)"
        )
```

**Warning Threshold:** 80% of estimated maximum

**Example Warning:**
```
High memory usage: 520 MB (82% of max) - events=980000, samples=450000, flows=950
```

## Configuration

### Default Settings (1GB Droplet)

```python
# Recommended for 1GB RAM
store = FeatureStore(
    retention_hours=24,
    max_flows=1000
)
# Max memory: ~634 MB
```

### 512MB Droplet

```python
# Tighter limits for 512MB RAM
store = FeatureStore(
    retention_hours=12,  # Shorter retention
    max_flows=500        # Fewer concurrent flows
)
# Max memory: ~467 MB
```

### High-Traffic Environment

```python
# 4GB+ server with high traffic
store = FeatureStore(
    retention_hours=72,   # 3 day retention
    max_flows=10000       # 10k concurrent flows
)
# Max memory: ~3,338 MB
```

## Graceful Degradation

### What Happens Under Pressure

**When max_flows reached:**
- Oldest flows evicted (LRU)
- New flows can still be tracked
- No crashes, no data corruption
- Warning logged every 100 evictions

**When deque maxlen reached:**
- Oldest events automatically dropped
- Fixed-size circular buffer behavior
- No memory growth beyond limit

**When retention expires:**
- Old data cleaned up every 60s
- Stale flows removed
- Memory freed automatically

## Monitoring & Alerts

### Stats Tracking

```python
store.stats = {
    'events_received': 1234567,      # Total events processed
    'flows_active': 850,              # Current flow count
    'flows_evicted': 150,             # LRU evictions
    'memory_warnings': 5,             # High usage warnings
}
```

### Health Checks

```bash
# Check current memory usage
curl localhost:8080/health | jq '.memory'

# Example response:
{
  "events_count": 980000,
  "samples_count": 450000,
  "flows_active": 950,
  "flows_evicted": 50,
  "estimated_mb": 520,
  "max_mb": 634,
  "usage_pct": 82.0
}
```

## Testing

### Resource Limit Tests

```bash
python -m bitnet.testing.resource_limits --all
```

**Flow Limit Test:**
- Creates store with `max_flows=100`
- Adds events for 200 flows
- Verifies exactly 100 active, 100 evicted
- Confirms LRU eviction working

**Memory Pressure Test:**
- Processes 1M decisions in memory
- Verifies graceful handling
- Tracks memory before/after
- Confirms garbage collection works

## Troubleshooting

### High Memory Warnings

```
WARNING: High memory usage: 520 MB (82% of max)
```

**Actions:**
1. Check `flows_active` - is it near `max_flows`?
2. Check `flows_evicted` - high eviction rate indicates too many unique flows
3. Consider lowering `max_flows` or `retention_hours`
4. Check for memory leaks in long-running process

### Frequent LRU Evictions

```
WARNING: LRU evicted 1000 flows (max=1000)
```

**Causes:**
- High cardinality traffic (many unique flows)
- DDoS attack with spoofed source IPs
- Load balancer spreading across many backends

**Actions:**
- This is expected behavior, not an error
- System is protecting itself from OOM
- Consider increasing `max_flows` if sufficient RAM
- Consider flow aggregation strategies

### OOM Kills (Despite Limits)

If process is still killed despite limits:

1. **Check actual memory usage:**
   ```bash
   ps aux | grep feature_store
   ```

2. **Verify limits are set:**
   ```python
   print(f"max_flows: {store.max_flows}")
   print(f"events maxlen: {store.all_events.maxlen}")
   ```

3. **Check for other memory consumers:**
   - Model training processes
   - Data generators
   - Cached data outside FeatureStore

4. **Enable swap (temporary fix):**
   ```bash
   fallocate -l 1G /swapfile
   chmod 600 /swapfile
   mkswap /swapfile
   swapon /swapfile
   ```

## Best Practices

### Sizing Guidelines

**For production:**
1. Max memory should be < 70% of available RAM
2. Leave 30% for OS, other processes, buffers
3. Monitor `memory_warnings` - should be rare
4. Tune `max_flows` based on traffic patterns

**Examples:**
- 512MB droplet → `max_flows=500`, `retention=12h`
- 1GB droplet → `max_flows=1000`, `retention=24h`
- 2GB droplet → `max_flows=2500`, `retention=48h`
- 4GB+ server → `max_flows=10000`, `retention=72h`

### Development vs Production

**Development (generous limits):**
```python
FeatureStore(retention_hours=1, max_flows=100)
```

**Production (realistic limits):**
```python
FeatureStore(retention_hours=24, max_flows=1000)
```

### Monitoring Recommendations

1. **Track `flows_evicted/min`** - should be low in normal traffic
2. **Track `memory_warnings/hour`** - should be zero
3. **Alert on > 90% memory usage** - indicates misconfiguration
4. **Log all LRU evictions** - helps detect attacks

## Future Improvements

### Planned

1. **Adaptive limits** - adjust `max_flows` based on available memory
2. **Flow aggregation** - combine similar flows to reduce cardinality
3. **Disk spillover** - write old flows to disk instead of evicting
4. **Compression** - compress old events before deletion

### Under Consideration

1. **Memory-mapped files** - for labeled_samples persistence
2. **External storage** - Redis/SQLite for overflow
3. **Distributed mode** - shard flows across multiple instances
