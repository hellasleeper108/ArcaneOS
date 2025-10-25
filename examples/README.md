# ArcaneOS WebSocket Client Examples

This directory contains example clients for connecting to the ArcaneOS event stream via WebSocket.

## Available Examples

### 1. Python WebSocket Client

**File:** `websocket_client.py`

A terminal-based Python client that connects to the ArcaneOS event stream and displays events in real-time with colored output and detailed information.

**Requirements:**
```bash
pip install websockets
```

**Usage:**
```bash
# Make sure the ArcaneOS backend is running on http://localhost:8000
python examples/websocket_client.py
```

**Features:**
- Real-time event streaming
- Colored terminal output
- Detailed event metadata display
- Graceful error handling
- Keyboard interrupt support (Ctrl+C)

### 2. HTML/JavaScript WebSocket Client

**File:** `websocket_client.html`

A browser-based client with a beautiful, fantasy-themed UI for monitoring ArcaneOS events in real-time.

**Usage:**
```bash
# Option 1: Open directly in browser
open examples/websocket_client.html

# Option 2: Serve via Python HTTP server
cd examples
python -m http.server 8080
# Then visit: http://localhost:8080/websocket_client.html
```

**Features:**
- Beautiful fantasy-themed UI
- Real-time event display with animations
- Color-coded events by type
- Auto-scrolling event feed
- Connection status indicator
- Clear events button
- No dependencies required (pure HTML/CSS/JS)

## WebSocket Endpoint

Both clients connect to:
```
ws://localhost:8000/ws/events
```

## Event Format

Events are sent as JSON with the following structure:

```json
{
  "spell_name": "summon|invoke|banish|reveal|parse",
  "daemon_name": "claude|gemini|liquidmetal",
  "timestamp": "2025-10-24T12:34:56.789000",
  "success": true,
  "description": "✨ Fantasy-themed event description ✨",
  "metadata": {
    "task": "Optional task description",
    "execution_time": 0.123,
    "parameters": {},
    "invocation_number": 1
  }
}
```

## Testing the Event Stream

### 1. Start the Backend

```bash
cd /home/hella/projects/vibejam
uvicorn app.main:app --reload
```

### 2. Connect a Client

In another terminal:

```bash
# Python client
python examples/websocket_client.py

# OR open the HTML client in a browser
open examples/websocket_client.html
```

### 3. Trigger Events

In a third terminal, use curl to interact with the API:

```bash
# Summon a daemon
curl -X POST http://localhost:8000/summon \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'

# Invoke a daemon
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude", "task": "Write a haiku about coding"}'

# Query daemons
curl http://localhost:8000/daemons

# Banish a daemon
curl -X POST http://localhost:8000/banish \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'
```

You should see events appear in real-time in your connected WebSocket client!

## Event Types

| Spell Type | Icon | Description |
|-----------|------|-------------|
| `summon` | 🔮 | Daemon is summoned to the material realm |
| `invoke` | ⚡ | Daemon performs a task |
| `banish` | 🌙 | Daemon returns to the ethereal void |
| `reveal` | 📜 | Query operations (list, state check) |
| `parse` | 📖 | Natural language spell parsing |

## Troubleshooting

### Connection Refused

Make sure the ArcaneOS backend is running:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### CORS Issues (HTML Client)

If you're having CORS issues with the HTML client, serve it via HTTP:
```bash
cd examples
python -m http.server 8080
```

### WebSocket Connection Failed

Verify the backend is accessible:
```bash
curl http://localhost:8000/health
```

## Creating Your Own Client

### JavaScript/TypeScript

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events');

ws.onopen = () => {
  console.log('Connected to ArcaneOS!');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event received:', data);
};
```

### Python

```python
import asyncio
import websockets
import json

async def listen():
    async with websockets.connect('ws://localhost:8000/ws/events') as ws:
        async for message in ws:
            event = json.loads(message)
            print(f"Event: {event}")

asyncio.run(listen())
```

## Next Steps

- Integrate the WebSocket client into a React/Vue/Svelte frontend
- Add filtering options for specific event types
- Create rune animations triggered by events
- Store event history in local storage
- Add event replay functionality
