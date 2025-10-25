## The Grimoire - Persistent Spell Memory

## Overview

**The Grimoire** is ArcaneOS's file-based memory layer that records every spell cast across sessions. It provides persistent storage for daemon operations, enabling session continuity, historical analysis, and debugging capabilities.

## Concept

In the mystical realm of ArcaneOS, The Grimoire serves as an eternal archive - a leather-bound tome that records every incantation, every daemon summoning, and every spell result for all eternity. Unlike the ephemeral `arcane_log.txt` which tracks application events, The Grimoire maintains a structured, queryable database of spell history in JSON Lines format.

```
┌─────────────────────────────────────────────────────────┐
│                    THE GRIMOIRE                          │
│  "The Eternal Archive of Mystical Operations"          │
│                                                          │
│  📖 grimoire_spells.jsonl (Structured spell records)   │
│  📜 arcane_log.txt (Application logging)               │
│                                                          │
│  Every spell recorded with:                             │
│  • Timestamp & datetime                                 │
│  • Spell name & type                                    │
│  • Command & result                                     │
│  • Daemon involvement                                   │
│  • Success/failure status                               │
│  • Execution time metrics                               │
└─────────────────────────────────────────────────────────┘
```

## Storage Format

### JSON Lines (JSONL)

Each spell is recorded as a single JSON object on its own line:

```json
{"timestamp": 1730000000.123, "datetime": "2025-10-24T12:34:56.123000", "spell_name": "summon_claude", "spell_type": "summon", "daemon_name": "claude", "command": {"daemon_name": "claude"}, "result": {"status": "summoned", "daemon": "claude"}, "success": true, "execution_time": null}
{"timestamp": 1730000010.456, "datetime": "2025-10-24T12:35:10.456000", "spell_name": "invoke_claude", "spell_type": "invoke", "daemon_name": "claude", "command": {"daemon_name": "claude", "task": "analyze code", "parameters": {}}, "result": {"output": {...}, "success": true}, "success": true, "execution_time": 0.234}
```

### Dual Storage System

1. **grimoire_spells.jsonl** - Structured spell records (JSONL format)
   - One JSON object per line
   - Easily parseable and searchable
   - Efficient for large datasets

2. **arcane_log.txt** - Application logging (Python logging format)
   - Standard log format with timestamps
   - Includes all application events
   - Integrated spell recording messages

This dual approach provides:
- Structured data for queries and analysis
- Human-readable logs for debugging
- Complete session continuity

## API Endpoints

### 1. Record Spell

```http
POST /grimoire/record
```

Records a new spell in the eternal grimoire.

**Request:**
```json
{
  "spell_name": "summon_claude",
  "command": {"daemon_name": "claude"},
  "result": {"status": "summoned", "message": "Claude awakens!"},
  "spell_type": "summon",
  "daemon_name": "claude",
  "success": true,
  "execution_time": 0.234
}
```

**Response:**
```json
{
  "status": "recorded",
  "message": "✨ The spell 'summon_claude' has been inscribed in the eternal grimoire! ✨",
  "entry": {
    "timestamp": 1730000000.123,
    "datetime": "2025-10-24T12:34:56.123000",
    "spell_name": "summon_claude",
    "spell_type": "summon",
    "daemon_name": "claude",
    "command": {"daemon_name": "claude"},
    "result": {"status": "summoned"},
    "success": true,
    "execution_time": 0.234
  }
}
```

### 2. Recall Spells

```http
GET /grimoire/recall?limit=5&spell_type=summon&daemon_name=claude&success_only=false
```

Retrieves recent spells with optional filtering.

**Query Parameters:**
- `limit` (1-100, default: 5) - Number of spells to recall
- `spell_type` (optional) - Filter by type (summon, invoke, banish, etc.)
- `daemon_name` (optional) - Filter by daemon
- `success_only` (boolean, default: false) - Only successful spells

**Response:**
```json
{
  "status": "success",
  "message": "✨ The grimoire reveals 5 spell(s)... ✨",
  "spells": [
    {
      "timestamp": 1730000000.123,
      "datetime": "2025-10-24T12:34:56.123000",
      "spell_name": "summon_claude",
      "spell_type": "summon",
      "daemon_name": "claude",
      "command": {"daemon_name": "claude"},
      "result": {"status": "summoned"},
      "success": true,
      "execution_time": 0.234
    }
  ],
  "count": 5
}
```

### 3. Grimoire Statistics

```http
GET /grimoire/statistics
```

Reveals comprehensive statistics about all spells in the grimoire.

**Response:**
```json
{
  "status": "success",
  "message": "✨ The grimoire's secrets are laid bare... ✨",
  "statistics": {
    "total_spells": 42,
    "spell_types": {
      "summon": 15,
      "invoke": 20,
      "banish": 7
    },
    "daemon_usage": {
      "claude": 25,
      "gemini": 12,
      "liquidmetal": 5
    },
    "success_count": 40,
    "fail_count": 2,
    "success_rate": 95.24,
    "total_execution_time": 12.345,
    "average_execution_time": 0.294,
    "oldest_spell": "2025-10-20T10:00:00",
    "newest_spell": "2025-10-24T15:30:00",
    "file_size_bytes": 25600
  }
}
```

### 4. Purge Old Spells

```http
DELETE /grimoire/purge?days=30
```

Removes spells older than specified days, archiving them first.

**Query Parameters:**
- `days` (1-365, default: 30) - Remove spells older than this

**Response:**
```json
{
  "status": "success",
  "message": "✨ Purged 15 ancient spell(s) from the grimoire! ✨",
  "purged_count": 15,
  "archive_file": "grimoire_archive_1730000000.jsonl"
}
```

### 5. Search Spells

```http
POST /grimoire/search
```

Searches for spells containing specific text.

**Request:**
```json
{
  "query": "claude",
  "limit": 10
}
```

**Response:**
```json
{
  "status": "success",
  "message": "✨ Found 8 spell(s) matching 'claude'... ✨",
  "query": "claude",
  "spells": [...],
  "count": 8
}
```

### 6. Grimoire Info

```http
GET /grimoire/info
```

Provides information about the grimoire system.

## Automatic Integration

The Grimoire automatically records spells from daemon operations:

### Summon Operations

When a daemon is summoned:
```python
grimoire.record_spell(
    spell_name=f"summon_{daemon_name}",
    command={"daemon_name": daemon_name},
    result={"status": "summoned", "daemon": daemon_name},
    spell_type="summon",
    daemon_name=daemon_name,
    success=True
)
```

### Invoke Operations

When a daemon is invoked:
```python
grimoire.record_spell(
    spell_name=f"invoke_{daemon_name}",
    command={"daemon_name": daemon_name, "task": task, "parameters": params},
    result={"output": result, "success": success},
    spell_type="invoke",
    daemon_name=daemon_name,
    success=success,
    execution_time=exec_time
)
```

### Banish Operations

When a daemon is banished:
```python
grimoire.record_spell(
    spell_name=f"banish_{daemon_name}",
    command={"daemon_name": daemon_name},
    result={"status": "banished", "statistics": stats},
    spell_type="banish",
    daemon_name=daemon_name,
    success=True,
    execution_time=total_time
)
```

## Manual Recording

You can also manually record custom spells:

### Python

```python
from app.services.grimoire import get_grimoire

grimoire = get_grimoire()

grimoire.record_spell(
    spell_name="custom_operation",
    command={"action": "transform", "target": "data"},
    result={"status": "completed", "output": "transformed"},
    spell_type="compile",
    daemon_name=None,
    success=True,
    execution_time=1.23
)
```

### API

```bash
curl -X POST http://localhost:8000/grimoire/record \
  -H "Content-Type: application/json" \
  -d '{
    "spell_name": "custom_spell",
    "command": {"action": "test"},
    "result": {"status": "success"},
    "spell_type": "query",
    "success": true
  }'
```

## Usage Examples

### Example 1: View Recent Activity

```bash
# Last 10 spells
curl http://localhost:8000/grimoire/recall?limit=10

# Last 5 summon operations
curl http://localhost:8000/grimoire/recall?spell_type=summon&limit=5

# All Claude operations
curl "http://localhost:8000/grimoire/recall?daemon_name=claude&limit=20"

# Only successful invocations
curl "http://localhost:8000/grimoire/recall?spell_type=invoke&success_only=true"
```

### Example 2: Analyze Patterns

```python
import requests

# Get statistics
response = requests.get("http://localhost:8000/grimoire/statistics")
stats = response.json()["statistics"]

print(f"Total spells: {stats['total_spells']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Most used daemon: {max(stats['daemon_usage'], key=stats['daemon_usage'].get)}")
```

### Example 3: Search for Errors

```bash
# Find failed operations
curl -X POST http://localhost:8000/grimoire/search \
  -H "Content-Type: application/json" \
  -d '{"query": "failed", "limit": 10}'

# Search for specific task
curl -X POST http://localhost:8000/grimoire/search \
  -H "Content-Type: application/json" \
  -d '{"query": "write_haiku", "limit": 5}'
```

### Example 4: Maintenance

```bash
# Purge spells older than 7 days
curl -X DELETE "http://localhost:8000/grimoire/purge?days=7"

# Purge spells older than 90 days
curl -X DELETE "http://localhost:8000/grimoire/purge?days=90"
```

## Session Continuity

The Grimoire enables session continuity across server restarts:

### Before Restart
```bash
# User summons and uses Claude
curl -X POST http://localhost:8000/summon -d '{"daemon_name": "claude"}'
curl -X POST http://localhost:8000/invoke -d '{"daemon_name": "claude", "task": "analyze"}'
```

### After Restart
```bash
# View previous session activity
curl http://localhost:8000/grimoire/recall?limit=10

# See what daemons were active
curl http://localhost:8000/grimoire/statistics
```

The grimoire preserves:
- Which daemons were summoned
- What tasks were performed
- When operations occurred
- Success/failure rates
- Performance metrics

## Integration with Logging

The Grimoire integrates seamlessly with Python's logging system:

### Application Logs (arcane_log.txt)
```
2025-10-24 12:34:56,789 - INFO - 📖 SPELL RECORDED: summon_claude succeeded [daemon: claude]
2025-10-24 12:35:10,123 - INFO - 📖 SPELL RECORDED: invoke_claude succeeded [daemon: claude] [time: 0.234s]
2025-10-24 12:36:00,456 - INFO - 📖 SPELL RECORDED: banish_claude succeeded [daemon: claude] [time: 1.234s]
```

### Spell Records (grimoire_spells.jsonl)
```json
{"timestamp": 1730000096.789, "spell_name": "summon_claude", ...}
{"timestamp": 1730000110.123, "spell_name": "invoke_claude", ...}
{"timestamp": 1730000160.456, "spell_name": "banish_claude", ...}
```

This dual approach provides:
- **Structured data** for queries (JSONL)
- **Human-readable logs** for debugging (text logs)
- **Complete history** for analysis

## Best Practices

### 1. Regular Purging

```bash
# Weekly cron job to purge old spells
0 0 * * 0 curl -X DELETE "http://localhost:8000/grimoire/purge?days=30"
```

### 2. Monitoring Success Rates

```python
# Check success rate daily
stats = requests.get("http://localhost:8000/grimoire/statistics").json()
success_rate = stats["statistics"]["success_rate"]

if success_rate < 90:
    alert("Low success rate detected!")
```

### 3. Search Before Debug

```bash
# Before filing a bug, search for similar errors
curl -X POST http://localhost:8000/grimoire/search \
  -d '{"query": "error_message", "limit": 20"}'
```

### 4. Archive Important Sessions

```bash
# Manually archive before purging
cp grimoire_spells.jsonl grimoire_backup_$(date +%Y%m%d).jsonl
curl -X DELETE "http://localhost:8000/grimoire/purge?days=7"
```

## Advanced Usage

### Custom Spell Types

```python
from app.services.grimoire import get_grimoire

grimoire = get_grimoire()

# Record a code compilation
grimoire.record_spell(
    spell_name="compile_python_ritual",
    command={"language": "python", "code": "print('Hello')"},
    result={"output": "Hello\\n", "success": True},
    spell_type="compile",
    daemon_name=None,
    success=True,
    execution_time=0.123
)
```

### Batch Analysis

```python
import json

# Read all spells
with open("grimoire_spells.jsonl", "r") as f:
    spells = [json.loads(line) for line in f]

# Analyze performance by daemon
from collections import defaultdict
daemon_times = defaultdict(list)

for spell in spells:
    if spell.get("execution_time") and spell.get("daemon_name"):
        daemon_times[spell["daemon_name"]].append(spell["execution_time"])

# Calculate averages
for daemon, times in daemon_times.items():
    avg_time = sum(times) / len(times)
    print(f"{daemon}: {avg_time:.3f}s average")
```

## File Locations

- **Spell Records:** `grimoire_spells.jsonl` (in project root)
- **Application Logs:** `arcane_log.txt` (in project root)
- **Archives:** `grimoire_archive_<timestamp>.jsonl` (created during purge)

## Troubleshooting

### Grimoire Not Recording

**Problem:** Spells aren't being recorded

**Solution:**
1. Check file permissions: `ls -la grimoire_spells.jsonl`
2. Check logs: `tail -f arcane_log.txt | grep SPELL`
3. Verify integration is active in daemon operations

### File Too Large

**Problem:** `grimoire_spells.jsonl` is too large

**Solution:**
```bash
# Purge old entries
curl -X DELETE "http://localhost:8000/grimoire/purge?days=7"

# Or manually archive and start fresh
mv grimoire_spells.jsonl grimoire_backup.jsonl
touch grimoire_spells.jsonl
```

### Malformed Entries

**Problem:** Errors when reading grimoire

**Solution:**
The grimoire automatically skips malformed entries. To clean them:
```bash
# Validate and clean
python -c "
import json
with open('grimoire_spells.jsonl', 'r') as f:
    valid = [line for line in f if json.loads(line.strip())]
with open('grimoire_cleaned.jsonl', 'w') as f:
    f.writelines(valid)
"
mv grimoire_cleaned.jsonl grimoire_spells.jsonl
```

## Future Enhancements

- [ ] Database backend option (SQLite/PostgreSQL)
- [ ] Real-time spell streaming via WebSocket
- [ ] Spell replay functionality
- [ ] Performance analytics dashboard
- [ ] Export to CSV/Excel
- [ ] Integration with monitoring tools (Prometheus, Grafana)
- [ ] Spell tagging and categorization
- [ ] Spell chaining and dependency tracking

## Related Documentation

- [Daemon Registry](./DAEMON_REGISTRY.md) - Where spells are automatically recorded
- [API Documentation](http://localhost:8000/grimoire) - Interactive API docs
- [Main README](../README.md) - Project overview
