# ArcaneEventBus Documentation

## Overview

The **ArcaneEventBus** is a real-time event dispatcher system for ArcaneOS that enables WebSocket-based event streaming from the backend to connected clients. It provides a fantasy-themed, async event broadcasting system that notifies clients about daemon operations in real-time.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ArcaneOS Backend                         │
│                                                             │
│  ┌────────────────┐        ┌──────────────────┐           │
│  │ Daemon         │        │  ArcaneEventBus  │           │
│  │ Operations     │───────▶│  (Singleton)     │           │
│  │                │ emit   │                  │           │
│  │ - summon()     │        │  - Subscribers   │           │
│  │ - invoke()     │        │  - Event History │           │
│  │ - banish()     │        │  - Async Queues  │           │
│  │ - query()      │        └────────┬─────────┘           │
│  └────────────────┘                 │                      │
│                                     │ broadcast            │
│                    ┌────────────────▼────────────────┐     │
│                    │  WebSocket Endpoint             │     │
│                    │  /ws/events                     │     │
│                    └────────────────┬────────────────┘     │
└─────────────────────────────────────┼──────────────────────┘
                                      │
                     ┌────────────────▼────────────────┐
                     │     WebSocket Connections       │
                     │                                 │
                     │  ┌──────┐  ┌──────┐  ┌──────┐ │
                     │  │Client│  │Client│  │Client│ │
                     │  │  1   │  │  2   │  │  3   │ │
                     │  └──────┘  └──────┘  └──────┘ │
                     └─────────────────────────────────┘
```

## Core Components

### 1. ArcaneEvent

Represents a single mystical event in the system.

**Attributes:**
- `spell_name`: Type of spell (SUMMON, INVOKE, BANISH, REVEAL, PARSE)
- `daemon_name`: Name of the daemon involved (optional)
- `success`: Whether the operation succeeded
- `description`: Fantasy-themed description of the event
- `timestamp`: UTC timestamp of when the event occurred
- `metadata`: Additional event-specific data

**Example:**
```python
event = ArcaneEvent(
    spell_name=SpellType.SUMMON,
    daemon_name="claude",
    success=True,
    description="✨ The Keeper of Logic materializes from the aether! ✨",
    metadata={"model": "claude-3-5-sonnet-20241022"}
)
```

### 2. ArcaneEventBus

The central event dispatcher using a publisher-subscriber pattern.

**Key Features:**
- Singleton pattern for global access
- Async/await for non-blocking operations
- Maintains event history (last 100 events)
- Automatic cleanup of disconnected clients
- Type-safe event emission methods

**Methods:**

#### Subscription Management

```python
# Subscribe to events
queue = await event_bus.subscribe()

# Unsubscribe
await event_bus.unsubscribe(queue)

# Get subscriber count
count = event_bus.get_subscriber_count()
```

#### Event Emission

```python
# Generic event emission
await event_bus.emit(event)

# Type-specific emissions with helpers
await event_bus.emit_summon(daemon_name="claude", success=True)
await event_bus.emit_invoke(daemon_name="claude", task="analyze code", execution_time=0.5)
await event_bus.emit_banish(daemon_name="claude", invocation_count=5, total_time=2.5)
await event_bus.emit_reveal(daemon_name="claude", is_active=True)
await event_bus.emit_parse(spell_text="summon claude", success=True, parsed_action="summon")
await event_bus.emit_voice(daemon_name="claude", success=True, description="Claude speaks", metadata={"audio_path": "arcane_audio/claude_summon.mp3"})
```

#### Event History

```python
# Get recent events
recent_events = event_bus.get_recent_events(count=10)
```

### 3. WebSocket Endpoint

**Location:** `app/routers/websocket_routes.py`

**Endpoint:** `ws://localhost:8000/ws/events`

**Connection Flow:**
1. Client connects via WebSocket
2. Server sends welcome message with recent events
3. Client subscribes to event bus
4. Server streams events in real-time
5. Client receives JSON-formatted events
6. On disconnect, client is automatically unsubscribed

## Event Types

### SUMMON Events

Emitted when a daemon is summoned to the material realm.

```json
{
  "spell_name": "summon",
  "daemon_name": "claude",
  "timestamp": "2025-10-24T12:34:56.789000",
  "success": true,
  "description": "✨ The runes pulse with purple energy as CLAUDE materializes from the aether! ✨",
  "metadata": {
    "model": "claude-3-5-sonnet-20241022"
  }
}
```

### INVOKE Events

Emitted when a daemon performs a task.

```json
{
  "spell_name": "invoke",
  "daemon_name": "claude",
  "timestamp": "2025-10-24T12:35:10.123000",
  "success": true,
  "description": "✨ The runes shimmer with analytical power! CLAUDE completes the task in 0.456 seconds with flawless logic. ✨",
  "metadata": {
    "task": "Write a haiku about coding",
    "execution_time": 0.456,
    "parameters": {},
    "invocation_number": 1
  }
}
```

### VOICE Events

Emitted when a daemon voice line is generated or when audio playback falls back to narration.

```json
{
  "spell_name": "voice",
  "daemon_name": "claude",
  "timestamp": "2025-10-24T12:35:42.500000",
  "success": false,
  "description": "I rise from the depths of code. [audio unavailable: network timeout]",
  "metadata": {
    "event": "summon",
    "tone": "Measured resonance with analytical undertones",
    "error": "network timeout"
  }
}
```

## Synchronization Directives

Each event's `metadata.sync` block provides real-time cues so clients can align visuals and audio within 200&nbsp;ms:

```json
"sync": {
  "deadline_ms": 200,
  "animation": "pulse",
  "particles": "fade_to_idle",
  "audio": "success",
  "invert": false
}
```

- `animation`: Suggested UI animation (`pulse`, `invert`, etc.).
- `particles`: Particle-system directive (`fade_to_idle`, `halt`).
- `audio`: Indicates whether the UI should play a success or error stinger.
- `invert`: Boolean hint to invert colors briefly on failure.
- `display_text` (optional): Failure phrase to render (e.g., “Rune destabilization detected”).
- `deadline_ms`: Target latency budget for applying all cues.

### BANISH Events

Emitted when a daemon returns to the ethereal void.

```json
{
  "spell_name": "banish",
  "daemon_name": "claude",
  "timestamp": "2025-10-24T12:40:00.000000",
  "success": true,
  "description": "✨ Purple aether swirls and dissipates... CLAUDE returns to the void after 5 task(s). ✨",
  "metadata": {
    "invocation_count": 5,
    "total_time": 2.345,
    "daemon_name": "claude",
    "is_active": false,
    "total_invocations": 5,
    "total_execution_time": 2.345,
    "average_execution_time": 0.469
  }
}
```

### REVEAL Events

Emitted during query operations (list daemons, check state, get statistics).

```json
{
  "spell_name": "reveal",
  "daemon_name": null,
  "timestamp": "2025-10-24T12:36:00.000000",
  "success": true,
  "description": "✨ The cosmic veil parts, revealing the status of all daemon entities... ✨",
  "metadata": {
    "daemon_count": 3,
    "query_type": "all"
  }
}
```

### PARSE Events

Emitted when natural language spells are parsed.

```json
{
  "spell_name": "parse",
  "daemon_name": "claude",
  "timestamp": "2025-10-24T12:37:00.000000",
  "success": true,
  "description": "✨ The ancient runes decode your incantation: 'summon claude' → Action: summon ✨",
  "metadata": {
    "spell_text": "summon claude",
    "parsed_action": "summon"
  }
}
```

## Integration Guide

### Backend Integration

The ArcaneEventBus is automatically integrated into all daemon operations. Here's how it works:

#### In daemon_registry.py

```python
from app.services.arcane_event_bus import get_event_bus
import asyncio

def summon(self, daemon_name: DaemonType) -> Daemon:
    # ... summoning logic ...

    # Emit summon event (runs in background)
    event_bus = get_event_bus()
    asyncio.create_task(event_bus.emit_summon(
        daemon_name=daemon_name.value,
        success=True,
        metadata={"model": model_config.get("model")}
    ))

    return daemon
```

#### In spell routers

```python
from app.services.arcane_event_bus import get_event_bus
import asyncio

@router.get("/daemons")
async def list_daemons():
    all_daemons = daemon_registry.get_all_daemons()

    # Emit reveal event
    event_bus = get_event_bus()
    asyncio.create_task(event_bus.emit_reveal(
        daemon_name=None,
        is_active=False,
        metadata={"daemon_count": len(all_daemons)}
    ))

    return {"daemons": all_daemons}
```

### Frontend Integration

#### JavaScript/TypeScript

```javascript
// Connect to event stream
const ws = new WebSocket('ws://localhost:8000/ws/events');

// Handle connection
ws.onopen = () => {
  console.log('✨ Connected to ArcaneOS Event Stream');
};

// Listen for events
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  // Handle connection message
  if (data.type === 'connection') {
    console.log(data.message);
    console.log(`Active subscribers: ${data.subscriber_count}`);
    return;
  }

  // Handle spell events
  switch (data.spell_name) {
    case 'summon':
      showSummonAnimation(data);
      break;
    case 'invoke':
      showInvokeAnimation(data);
      break;
    case 'banish':
      showBanishAnimation(data);
      break;
    case 'reveal':
      updateDaemonList(data);
      break;
    case 'parse':
      showParseResult(data);
      break;
  }
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Handle disconnection
ws.onclose = () => {
  console.log('Disconnected from event stream');
};
```

#### Python

```python
import asyncio
import websockets
import json

async def listen_to_events():
    uri = "ws://localhost:8000/ws/events"

    async with websockets.connect(uri) as websocket:
        print("✨ Connected to ArcaneOS")

        async for message in websocket:
            event = json.loads(message)

            # Handle events
            if event.get('type') == 'connection':
                print(f"📡 {event['message']}")
                continue

            spell = event['spell_name']
            daemon = event.get('daemon_name', 'N/A')
            print(f"[{spell.upper()}] {daemon}: {event['description']}")

asyncio.run(listen_to_events())
```

## Usage Examples

### Example 1: Real-time Daemon Monitoring

Create a dashboard that shows all active daemons and their operations:

```javascript
const activeDaemons = new Map();

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.spell_name) {
    case 'summon':
      activeDaemons.set(data.daemon_name, {
        status: 'active',
        invocations: 0
      });
      updateDashboard();
      break;

    case 'invoke':
      const daemon = activeDaemons.get(data.daemon_name);
      if (daemon) {
        daemon.invocations++;
        updateDashboard();
      }
      break;

    case 'banish':
      activeDaemons.delete(data.daemon_name);
      updateDashboard();
      break;
  }
};
```

### Example 2: Rune Animation System

Trigger visual effects based on spell events:

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.spell_name === 'summon') {
    const color = getDaemonColor(data.daemon_name);
    animateRuneCircle(color, 'summon');
  } else if (data.spell_name === 'invoke') {
    animateEnergyBurst(data.daemon_name);
    showTaskProgress(data.metadata.task);
  }
};

function getDaemonColor(daemon) {
  const colors = {
    'claude': '#8B5CF6',  // Purple
    'gemini': '#F59E0B',  // Amber
    'liquidmetal': '#06B6D4'  // Cyan
  };
  return colors[daemon] || '#FFFFFF';
}
```

### Example 3: Event History and Replay

Store and replay event history:

```javascript
const eventHistory = [];
const maxHistory = 100;

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  // Store in history
  eventHistory.unshift(data);
  if (eventHistory.length > maxHistory) {
    eventHistory.pop();
  }

  // Save to localStorage
  localStorage.setItem('arcaneHistory', JSON.stringify(eventHistory));

  displayEvent(data);
};

// Replay events
function replayHistory() {
  eventHistory.forEach((event, index) => {
    setTimeout(() => {
      displayEvent(event);
    }, index * 500);  // 500ms between events
  });
}
```

## API Reference

### REST Endpoints

#### Get Recent Events
```
GET /events/recent?count=10
```

Returns recent events from history without maintaining a WebSocket connection.

**Response:**
```json
{
  "status": "success",
  "message": "✨ The chronicles reveal the last 10 mystical occurrences... ✨",
  "count": 10,
  "events": [...]
}
```

#### Get Event Statistics
```
GET /events/stats
```

Returns statistics about the event bus.

**Response:**
```json
{
  "status": "success",
  "message": "✨ The ethereal network thrums with energy... ✨",
  "subscribers": 3,
  "history_size": 45,
  "active": true
}
```

### WebSocket Protocol

#### Connection Message

Upon connection, the server sends:

```json
{
  "type": "connection",
  "message": "✨ Welcome to the ArcaneOS event stream! ✨",
  "subscriber_count": 1,
  "recent_events": [...]
}
```

#### Event Messages

All subsequent messages are spell events in the format described above.

## Performance Considerations

### Event History

- Maximum 100 events stored in memory
- Oldest events automatically removed
- Access via `get_recent_events(count)`

### Subscriber Management

- Automatic cleanup of dead connections
- Async operations for non-blocking broadcast
- No limit on subscriber count (but consider server resources)

### Background Tasks

Events are emitted using `asyncio.create_task()` to avoid blocking:

```python
asyncio.create_task(event_bus.emit_summon(...))
```

This ensures daemon operations complete immediately while events are processed in the background.

## Testing

### Manual Testing

1. Start the backend:
```bash
uvicorn app.main:app --reload
```

2. Connect a WebSocket client:
```bash
python examples/websocket_client.py
```

3. Trigger events via API:
```bash
curl -X POST http://localhost:8000/summon \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'
```

### Automated Testing

```python
import pytest
import asyncio
from app.services.arcane_event_bus import get_event_bus, SpellType

@pytest.mark.asyncio
async def test_event_emission():
    event_bus = get_event_bus()

    # Subscribe
    queue = await event_bus.subscribe()

    # Emit event
    await event_bus.emit_summon(
        daemon_name="claude",
        success=True
    )

    # Receive event
    event = await asyncio.wait_for(queue.get(), timeout=1.0)

    assert event.spell_name == SpellType.SUMMON
    assert event.daemon_name == "claude"
    assert event.success == True

    # Cleanup
    await event_bus.unsubscribe(queue)
```

## Troubleshooting

### Events Not Appearing

**Problem:** WebSocket client not receiving events

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check WebSocket connection: Look for connection message
3. Ensure operations trigger events: Check logs for "Event emitted" messages

### Connection Drops

**Problem:** WebSocket connection intermittently drops

**Solutions:**
1. Add reconnection logic to client
2. Implement heartbeat/ping mechanism
3. Check network stability
4. Monitor server logs for errors

### High Memory Usage

**Problem:** Event bus consuming too much memory

**Solutions:**
1. Reduce event history size (default: 100)
2. Clean up event metadata
3. Limit subscriber count
4. Implement event compression for large payloads

## Future Enhancements

- [ ] Event filtering by type or daemon
- [ ] Event replay functionality
- [ ] Persistent event storage (database)
- [ ] Event compression for bandwidth optimization
- [ ] Authentication for WebSocket connections
- [ ] Rate limiting for event broadcasts
- [ ] Event acknowledgment system
- [ ] Multi-room support (separate event streams)

## Related Documentation

- [WebSocket Client Examples](../examples/README.md)
- [Daemon Registry](./DAEMON_REGISTRY.md)
- [API Documentation](./API.md)
- [Spell Parser](./SPELL_PARSER.md)
