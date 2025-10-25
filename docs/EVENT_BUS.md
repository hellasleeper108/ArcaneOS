# ArcaneEventBus Documentation

## Overview

The **ArcaneEventBus** is a channel-based WebSocket event broadcasting system that enables real-time communication between the server and multiple clients. It provides async-safe message routing with automatic subscriber management.

## Features

- **Channel-Based Routing**: Subscribe to specific channels for targeted messages
- **WebSocket Broadcasting**: JSON message delivery to all channel subscribers
- **Async-Safe**: Built with asyncio for non-blocking operations
- **Queue Buffering**: Uses asyncio.Queue per channel for reliable delivery
- **Automatic Cleanup**: Removes disconnected subscribers automatically
- **Thread-Safe**: Protected with asyncio.Lock for concurrent access
- **No External Dependencies**: Uses only FastAPI and asyncio

## Installation

The ArcaneEventBus is part of the core ArcaneOS modules:

```python
from core.event_bus import get_event_bus, ArcaneEventBus
```

## Basic Usage

### Server-Side (Python)

```python
from core.event_bus import get_event_bus
from fastapi import WebSocket

# Get global event bus instance
bus = get_event_bus()

# Subscribe a WebSocket to a channel
await bus.subscribe("notifications", websocket)

# Emit events to all subscribers on a channel
await bus.emit("notifications", {
    "type": "alert",
    "message": "New daemon summoned!",
    "timestamp": "2025-10-24T12:00:00"
})

# Unsubscribe when done
await bus.unsubscribe("notifications", websocket)
```

### Client-Side (Python)

```python
import asyncio
import websockets
import json

async def listen_to_channel():
    uri = "ws://localhost:8000/ws/events/notifications"

    async with websockets.connect(uri) as websocket:
        # Receive welcome message
        welcome = await websocket.recv()
        print(f"Connected: {json.loads(welcome)}")

        # Listen for events
        async for message in websocket:
            event = json.loads(message)
            print(f"Received: {event}")

asyncio.run(listen_to_channel())
```

### Client-Side (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events/notifications');

ws.onopen = () => {
    console.log('Connected to channel');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'connection') {
        console.log('Welcome:', data.message);
    } else {
        console.log('Event received:', data);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected from channel');
};
```

## API Reference

### Class: ArcaneEventBus

#### `__init__()`

Initialize the ArcaneEventBus.

**Example:**
```python
from core.event_bus import ArcaneEventBus

bus = ArcaneEventBus()
```

However, you should use the singleton pattern:

```python
from core.event_bus import get_event_bus

bus = get_event_bus()
```

#### `async subscribe(channel: str, websocket: WebSocket) -> None`

Subscribe a WebSocket connection to a specific channel.

**Parameters:**
- `channel` (str): The channel name to subscribe to
- `websocket` (WebSocket): The WebSocket connection to add

**Example:**
```python
await bus.subscribe("route", websocket)
```

#### `async emit(channel: str, message: dict) -> None`

Emit a message to all subscribers on a specific channel.

**Parameters:**
- `channel` (str): The channel to broadcast on
- `message` (dict): The message dictionary to send (will be JSON-encoded)

**Example:**
```python
await bus.emit("route", {
    "event": "navigation",
    "path": "/dashboard",
    "user": "admin"
})
```

#### `async unsubscribe(channel: str, websocket: WebSocket) -> None`

Unsubscribe a WebSocket connection from a specific channel.

**Parameters:**
- `channel` (str): The channel to unsubscribe from
- `websocket` (WebSocket): The WebSocket connection to remove

**Example:**
```python
await bus.unsubscribe("route", websocket)
```

#### `get_subscriber_count(channel: str) -> int`

Get the number of active subscribers on a channel.

**Parameters:**
- `channel` (str): The channel name

**Returns:**
- `int`: Number of active subscribers

**Example:**
```python
count = bus.get_subscriber_count("notifications")
print(f"Channel has {count} subscribers")
```

#### `get_channels() -> list`

Get list of all active channels.

**Returns:**
- `list`: List of channel names

**Example:**
```python
channels = bus.get_channels()
print(f"Active channels: {channels}")
# Output: Active channels: ['route', 'notifications', 'spell']
```

### Function: get_event_bus()

Get the global ArcaneEventBus instance (singleton pattern).

**Returns:**
- `ArcaneEventBus`: The global event bus instance

**Example:**
```python
from core.event_bus import get_event_bus

bus = get_event_bus()
```

## WebSocket Endpoints

### Subscribe to Channel

**Endpoint:** `ws://localhost:8000/ws/events/{channel}`

**Description:** Connect to a specific channel and receive all events broadcast on that channel.

**Example:**
```bash
# Using websocat
websocat ws://localhost:8000/ws/events/route

# Using wscat
wscat -c ws://localhost:8000/ws/events/route
```

**Welcome Message:**
```json
{
  "type": "connection",
  "message": "✨ Connected to channel 'route' ✨",
  "channel": "route",
  "subscribers": 1
}
```

### Get Active Channels

**Endpoint:** `GET /channels`

**Description:** Retrieve list of all active channels and their subscriber counts.

**Response:**
```json
{
  "status": "success",
  "message": "✨ The ethereal channels pulse with energy... ✨",
  "channels": {
    "route": 3,
    "notifications": 5,
    "spell": 2
  },
  "total_channels": 3
}
```

**Example:**
```bash
curl http://localhost:8000/channels
```

## Channel Examples

### 1. Navigation Channel

Track user navigation across the application:

```python
# Server: Emit navigation event
await bus.emit("route", {
    "event": "page_view",
    "path": "/dashboard",
    "user_id": "user123",
    "timestamp": "2025-10-24T12:00:00"
})
```

```javascript
// Client: Listen for navigation events
const ws = new WebSocket('ws://localhost:8000/ws/events/route');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === 'page_view') {
        console.log(`User navigated to ${data.path}`);
    }
};
```

### 2. Notification Channel

Send real-time notifications to users:

```python
# Server: Send notification
await bus.emit("notifications", {
    "type": "success",
    "title": "Daemon Summoned",
    "message": "Claude has been summoned successfully!",
    "timestamp": "2025-10-24T12:00:00"
})
```

```javascript
// Client: Display notifications
const ws = new WebSocket('ws://localhost:8000/ws/events/notifications');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type && data.message) {
        showNotification(data.type, data.title, data.message);
    }
};
```

### 3. Spell Channel

Broadcast spell casting events:

```python
# Server: Spell cast event
await bus.emit("spell", {
    "spell_name": "summon",
    "daemon": "claude",
    "success": True,
    "execution_time": 0.234
})
```

```python
# Client: Monitor spell activity
import asyncio
import websockets

async def monitor_spells():
    async with websockets.connect('ws://localhost:8000/ws/events/spell') as ws:
        async for message in ws:
            event = json.loads(message)
            if event.get('spell_name'):
                print(f"Spell '{event['spell_name']}' cast on {event['daemon']}")

asyncio.run(monitor_spells())
```

## Advanced Usage

### Multiple Channels

Subscribe to multiple channels simultaneously:

```python
import asyncio
import websockets
import json

async def multi_channel_listener():
    # Connect to multiple channels
    route_ws = await websockets.connect('ws://localhost:8000/ws/events/route')
    notify_ws = await websockets.connect('ws://localhost:8000/ws/events/notifications')

    async def listen_route():
        async for message in route_ws:
            event = json.loads(message)
            print(f"Route: {event}")

    async def listen_notify():
        async for message in notify_ws:
            event = json.loads(message)
            print(f"Notification: {event}")

    # Listen to both channels concurrently
    await asyncio.gather(listen_route(), listen_notify())

asyncio.run(multi_channel_listener())
```

### Broadcasting to Multiple Channels

```python
async def broadcast_to_all(event_data):
    """Broadcast event to multiple channels"""
    bus = get_event_bus()

    channels = ["route", "notifications", "spell"]

    for channel in channels:
        await bus.emit(channel, event_data)
```

### Conditional Broadcasting

```python
async def conditional_broadcast(event):
    """Only broadcast to channels with subscribers"""
    bus = get_event_bus()

    for channel in bus.get_channels():
        if bus.get_subscriber_count(channel) > 0:
            await bus.emit(channel, event)
```

### Failed Connection Handling

The event bus automatically handles failed connections:

```python
# Failed connections are automatically cleaned up
await bus.emit("route", {"test": "message"})
# If a subscriber's connection fails, they're removed automatically
```

## Integration Examples

### With FastAPI Router

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.event_bus import get_event_bus

router = APIRouter()

@router.websocket("/ws/custom/{channel}")
async def custom_channel(websocket: WebSocket, channel: str):
    bus = get_event_bus()

    await websocket.accept()
    await bus.subscribe(channel, websocket)

    try:
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
    except WebSocketDisconnect:
        pass
    finally:
        await bus.unsubscribe(channel, websocket)
```

### With Daemon Operations

```python
from core.event_bus import get_event_bus

async def summon_daemon(daemon_name: str):
    bus = get_event_bus()

    # Perform summon operation
    # ...

    # Broadcast event
    await bus.emit("daemon", {
        "operation": "summon",
        "daemon": daemon_name,
        "timestamp": datetime.utcnow().isoformat()
    })
```

### With Grimoire

```python
from core.event_bus import get_event_bus
from app.services.grimoire import get_grimoire

async def record_and_broadcast_spell(spell_data):
    grimoire = get_grimoire()
    bus = get_event_bus()

    # Record in grimoire
    entry = grimoire.record_spell(**spell_data)

    # Broadcast to subscribers
    await bus.emit("spell", {
        "event": "spell_recorded",
        "spell_name": spell_data["spell_name"],
        "timestamp": entry.datetime
    })
```

## Testing

The ArcaneEventBus includes comprehensive tests:

```bash
# Run all event bus tests
pytest tests/test_ws.py -v

# Run specific tests
pytest tests/test_ws.py::test_ws_sequence -v
pytest tests/test_ws.py::test_ws_multiple_subscribers -v
pytest tests/test_ws.py::test_ws_channel_isolation -v
```

### Test Coverage

1. **test_ws_sequence** - Subscribe, emit, receive validation
2. **test_ws_multiple_subscribers** - Multiple clients on same channel
3. **test_ws_channel_isolation** - Channel message isolation
4. **test_ws_unsubscribe_on_disconnect** - Cleanup validation

### Manual Testing

```bash
# Terminal 1: Start server
python -m app.main

# Terminal 2: Subscribe to channel
websocat ws://localhost:8000/ws/events/test

# Terminal 3: Emit test event
python -c "
import asyncio
from core.event_bus import get_event_bus

async def test():
    bus = get_event_bus()
    await bus.emit('test', {'message': 'Hello!'})

asyncio.run(test())
"
```

## Best Practices

### 1. Use Descriptive Channel Names

```python
# Good
await bus.emit("user_authentication", event)
await bus.emit("spell_casting", event)
await bus.emit("daemon_lifecycle", event)

# Avoid
await bus.emit("ch1", event)
await bus.emit("events", event)
```

### 2. Include Timestamps

```python
from datetime import datetime

await bus.emit("notifications", {
    "message": "Event occurred",
    "timestamp": datetime.utcnow().isoformat()
})
```

### 3. Handle Disconnections Gracefully

```python
@router.websocket("/ws/events/{channel}")
async def channel_endpoint(websocket: WebSocket, channel: str):
    bus = get_event_bus()
    await websocket.accept()
    await bus.subscribe(channel, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Cleanup happens automatically
        pass
    finally:
        await bus.unsubscribe(channel, websocket)
```

### 4. Validate Message Structure

```python
def validate_event(event: dict) -> bool:
    """Ensure event has required fields"""
    required = ['type', 'timestamp']
    return all(key in event for key in required)

async def safe_emit(channel: str, event: dict):
    if validate_event(event):
        await bus.emit(channel, event)
    else:
        logger.warning(f"Invalid event structure: {event}")
```

## Troubleshooting

### Issue: Messages Not Received

**Problem:** Client not receiving messages.

**Solutions:**
1. Check channel name matches exactly
2. Verify WebSocket connection is established
3. Check that events are being emitted to correct channel

```python
# Debug: Check active channels
bus = get_event_bus()
print(f"Active channels: {bus.get_channels()}")
print(f"Subscribers on 'test': {bus.get_subscriber_count('test')}")
```

### Issue: Multiple Messages

**Problem:** Receiving duplicate messages.

**Solution:** Ensure only one WebSocket connection per client:

```javascript
// Close existing connection before creating new one
if (ws) {
    ws.close();
}
ws = new WebSocket('ws://localhost:8000/ws/events/route');
```

### Issue: Memory Leak

**Problem:** Channels not being cleaned up.

**Solution:** The event bus automatically cleans up empty channels. Ensure `unsubscribe()` is called:

```python
try:
    while True:
        await websocket.receive_text()
except WebSocketDisconnect:
    pass
finally:
    await bus.unsubscribe(channel, websocket)  # Always unsubscribe
```

## Performance Considerations

### 1. Channel Organization

Group related events into channels:

```python
# Good - Organized by domain
channels = {
    "user": ["login", "logout", "profile_update"],
    "daemon": ["summon", "invoke", "banish"],
    "system": ["startup", "shutdown", "error"]
}

# Broadcast to specific channel
await bus.emit("user", {"event": "login", ...})
```

### 2. Message Size

Keep messages reasonably sized:

```python
# Good - Essential data only
await bus.emit("notifications", {
    "type": "info",
    "message": "Task complete",
    "task_id": "12345"
})

# Avoid - Large payloads
await bus.emit("notifications", {
    "type": "info",
    "entire_database_dump": {...}  # Too large
})
```

### 3. Subscriber Limits

Monitor subscriber counts:

```python
MAX_SUBSCRIBERS = 100

async def safe_subscribe(channel: str, websocket: WebSocket):
    bus = get_event_bus()

    if bus.get_subscriber_count(channel) >= MAX_SUBSCRIBERS:
        await websocket.close()
        return

    await bus.subscribe(channel, websocket)
```

## See Also

- [ArcaneOS README](../README.md) - Main project documentation
- [VibeCompiler](VIBECOMPILER.md) - Safe code execution
- [Reality Veil](REALITY_VEIL.md) - Fantasy/developer mode toggle
- [The Grimoire](GRIMOIRE.md) - Spell history documentation

---

**Note:** The ArcaneEventBus provides real-time, channel-based communication with automatic resource management and error handling.
