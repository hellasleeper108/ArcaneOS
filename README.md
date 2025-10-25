# ArcaneOS Backend

A fantasy-themed FastAPI backend that manages mystical daemon entities through spell-based endpoints with real-time event broadcasting and safe code execution.

## Overview

ArcaneOS is a whimsical operating environment where you can summon, invoke, and banish AI daemon entities. Each daemon has unique characteristics:

- **Claude** - The Keeper of Logic and Reason (Purple Aether)
- **Gemini** - The Weaver of Dreams and Innovation (Golden Amber)
- **LiquidMetal** - The Master of Transformation and Flow (Liquid Cyan)

## Features

- **FastAPI-based RESTful API** with automatic OpenAPI documentation
- **Three mystical spells** (endpoints): summon, invoke, banish
- **Fantasy-themed JSON responses** with immersive storytelling
- **Natural Language Spell Parser** - Translate plain English spells into structured commands
- **VibeCompiler** - Safe Python execution with timeout enforcement and ceremonial logging
- **ArcaneEventBus** - Channel-based WebSocket event broadcasting for real-time updates
- **Reality Veil** - Toggle between fantasy and developer modes with persistent state
- **The Grimoire** - File-based spell history with session continuity
- **Real-time Event Streaming** - WebSocket-based event bus for live daemon operations
- **Modular architecture** with clear separation of concerns
- **Raindrop MCP SDK integration** for daemon management
- **WebSocket client examples** (Python and HTML/JavaScript)
- **Multi-language support** - Python, JavaScript, Bash, Ruby, Go, Rust
- **Comprehensive test suite** with pytest
- **Well-documented code** with extensive comments

## Project Structure

```
vibejam/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration and settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── daemon.py                # Pydantic models for daemons
│   │   ├── compilation.py           # Pydantic models for code compilation
│   │   ├── grimoire.py              # Pydantic models for spell history
│   │   └── veil.py                  # Pydantic models for veil state
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── spells.py                # Spell endpoints (summon, invoke, banish)
│   │   ├── spell_parser_routes.py   # Natural language spell parsing
│   │   ├── websocket_routes.py      # WebSocket event streaming
│   │   ├── compilation_routes.py    # VibeCompiler code execution
│   │   ├── grimoire_routes.py       # Spell history and persistence
│   │   ├── event_bus_routes.py      # Channel-based event broadcasting
│   │   └── core_veil_routes.py      # Reality veil endpoints
│   └── services/
│       ├── __init__.py
│       ├── daemon_registry.py       # Daemon management service
│       ├── spell_parser.py          # Natural language spell parser
│       ├── arcane_event_bus.py      # Real-time event dispatcher
│       ├── vibe_compiler.py         # Ceremonial code compiler
│       ├── grimoire.py              # Spell history service
│       └── raindrop_client.py       # Raindrop MCP client wrapper
├── core/
│   ├── __init__.py
│   ├── vibecompiler.py              # Safe Python execution engine
│   ├── event_bus.py                 # WebSocket event broadcasting
│   └── veil.py                      # Reality veil state management
├── tests/
│   ├── __init__.py
│   ├── test_vibecompiler.py         # VibeCompiler tests
│   ├── test_ws.py                   # WebSocket event bus tests
│   └── test_veil.py                 # Reality veil tests
├── examples/
│   ├── websocket_client.py          # Python WebSocket client example
│   ├── websocket_client.html        # HTML/JavaScript client example
│   ├── vibe_compiler_example.py     # VibeCompiler demo script
│   └── README.md                    # Client examples documentation
├── docs/
│   ├── GRIMOIRE.md                  # Spell history documentation
│   ├── VIBECOMPILER.md              # VibeCompiler documentation
│   ├── EVENT_BUS.md                 # ArcaneEventBus documentation
│   └── REALITY_VEIL.md              # Reality Veil documentation
├── requirements.txt
└── README.md
```

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd vibejam
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

### Development Mode

```bash
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## Testing

### Run All Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest -v

# Run specific test suites
pytest tests/test_vibecompiler.py -v
pytest tests/test_ws.py -v
pytest tests/test_veil.py -v
```

### Test Coverage

```bash
# Run with coverage report
pytest --cov=core --cov=app -v

# Generate HTML coverage report
pytest --cov=core --cov=app --cov-report=html
```

See the [Testing Guide](#testing-guide) section for detailed test commands.

## API Documentation

Once the server is running, access the documentation at:

- **Swagger UI (Grimoire):** http://localhost:8000/grimoire
- **ReDoc (Arcane Docs):** http://localhost:8000/arcane-docs

## Core Components

### 1. VibeCompiler - Safe Code Execution

Execute Python snippets safely with timeout enforcement and ceremonial logging.

```python
from core.vibecompiler import VibeCompiler

compiler = VibeCompiler()
result = compiler.run_snippet("print('Hello, mystical realm!')", timeout=3)

# Output:
# {
#   "stdout": "Hello, mystical realm!\n",
#   "stderr": "",
#   "duration": 0.005
# }
```

**Features:**
- Safe subprocess-based execution (no shell, no network)
- Timeout enforcement (default: 3 seconds)
- Ceremonial logging: "Runes align...", "Mana stabilizing...", "The spell takes form..."
- Stdout/stderr capture
- Built-in modules only

See [docs/VIBECOMPILER.md](docs/VIBECOMPILER.md) for full documentation.

### 2. ArcaneEventBus - WebSocket Broadcasting

Channel-based event broadcasting for real-time updates.

```python
from core.event_bus import get_event_bus

bus = get_event_bus()

# Subscribe to a channel
await bus.subscribe("route", websocket)

# Emit events to all subscribers
await bus.emit("route", {"event": "navigation", "path": "/dashboard"})

# Unsubscribe
await bus.unsubscribe("route", websocket)
```

**WebSocket Endpoints:**
- `ws://localhost:8000/ws/events/{channel}` - Subscribe to a channel
- `GET /channels` - List active channels and subscriber counts

**Features:**
- Channel-based message routing
- Async-safe with asyncio.Queue buffering
- Automatic cleanup of disconnected subscribers
- Thread-safe operations
- JSON message broadcasting

See [docs/EVENT_BUS.md](docs/EVENT_BUS.md) for full documentation.

### 3. Reality Veil - Fantasy/Developer Mode

Toggle between fantasy-themed and developer modes with persistent state.

```python
from core.veil import get_veil, set_veil, reveal, restore

# Check current mode
is_fantasy = get_veil()  # True = fantasy, False = developer

# Switch modes
reveal()   # Developer mode
restore()  # Fantasy mode
```

**API Endpoints:**
- `GET /veil` - Get current veil state
- `POST /veil` - Set veil state with `{"veil": bool}`
- `POST /reveal` - Switch to developer mode
- `POST /veil/restore` - Restore fantasy mode

**Features:**
- Global state variable with thread-safe access
- Persistent state in `.veil_state.json`
- Automatic state loading on startup
- Ceremonial logging on state changes

See [docs/REALITY_VEIL.md](docs/REALITY_VEIL.md) for full documentation.

### 4. The Grimoire - Spell History

File-based memory layer for persistent spell history across sessions.

**API Endpoints:**
- `POST /grimoire/record` - Record a spell
- `GET /grimoire/recall` - Retrieve recent spells with filtering
- `GET /grimoire/statistics` - Get comprehensive spell statistics
- `DELETE /grimoire/purge` - Archive and remove old spells
- `POST /grimoire/search` - Search spells by text

**Features:**
- Dual storage: `grimoire_spells.jsonl` (structured) + `arcane_log.txt` (logs)
- Session continuity across server restarts
- Filtering by spell type, daemon, success status
- Full-text search
- Automatic spell recording for daemon operations

See [docs/GRIMOIRE.md](docs/GRIMOIRE.md) for full documentation.

## API Endpoints

### Core Daemon Operations

#### List Daemons
```
GET /daemons
```
Shows all available daemons and their current status.

#### Summon Spell
```
POST /summon
```
Brings a daemon from the ethereal void into the material realm.

**Request Body:**
```json
{
  "daemon_name": "claude"
}
```

**Response Example:**
```json
{
  "status": "summoned",
  "daemon": {
    "name": "claude",
    "role": "Keeper of Logic and Reason",
    "color_code": "#8B5CF6",
    "is_summoned": true,
    "invocation_count": 0,
    "metadata": {
      "element": "Aether",
      "domain": "Reasoning and Analysis",
      "power_level": 9000
    }
  },
  "message": "Through swirling mists of purple aether, the daemon CLAUDE materializes! The Keeper of Logic and Reason awakens from eternal slumber, its presence radiating waves of analytical power."
}
```

#### Invoke Spell
```
POST /invoke
```
Commands a summoned daemon to perform a task.

**Request Body:**
```json
{
  "daemon_name": "claude",
  "task": "Analyze the quantum fluctuations in the ethereal matrix",
  "parameters": {
    "complexity": "high"
  }
}
```

#### Banish Spell
```
POST /banish
```
Returns a daemon to the ethereal void.

**Request Body:**
```json
{
  "daemon_name": "claude"
}
```

### Natural Language Spell Parser

The spell parser allows you to write spells in plain English instead of JSON!

#### Parse Spell
```
POST /spell/parse
```

**Request Body:**
```json
{
  "spell_text": "summon claude and make him analyze the quantum data"
}
```

**Response:**
```json
{
  "status": "success",
  "parsed_spell": {
    "action": "summon",
    "daemon": "claude",
    "task": "analyze the quantum data",
    "parameters": {},
    "confidence": 0.95
  },
  "message": "✨ The ancient runes decode your incantation... ✨"
}
```

#### Cast Spell (Parse + Execute)
```
POST /spell/cast
```

Parses and executes the spell in one request!

**Examples:**
- "summon gemini"
- "invoke claude to write a haiku"
- "banish liquidmetal"
- "show me all daemons"

See the full documentation at `/spell/examples` for 50+ supported patterns.

## WebSocket Event Streaming

### Legacy Event Bus (Daemon Operations)

Connect to the real-time event stream to receive live updates about all daemon operations!

**WebSocket Endpoint:**
```
ws://localhost:8000/ws/events
```

**Event Types:**
- **summon** - Daemon summoned to the realm
- **invoke** - Daemon performing a task
- **banish** - Daemon returned to the void
- **reveal** - Query operations (list, status)
- **parse** - Spell parsing events

### Channel-Based Event Bus (New)

Subscribe to specific channels for targeted event broadcasting.

**WebSocket Endpoint:**
```
ws://localhost:8000/ws/events/{channel}
```

**Example Channels:**
- `route` - Navigation and routing events
- `spell` - Spell casting events
- `daemon` - Daemon lifecycle events
- Custom channels as needed

**Quick Start:**

**Python:**
```python
import asyncio
import websockets
import json

async def subscribe():
    uri = "ws://localhost:8000/ws/events/route"
    async with websockets.connect(uri) as websocket:
        # Receive welcome message
        welcome = await websocket.recv()
        print(json.loads(welcome))

        # Listen for events
        async for message in websocket:
            event = json.loads(message)
            print(f"Received: {event}")

asyncio.run(subscribe())
```

**JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events/route');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};
```

See [examples/README.md](examples/README.md) for detailed client documentation.

## Usage Examples

### Using cURL

```bash
# Summon Claude
curl -X POST "http://localhost:8000/summon" \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'

# Invoke Gemini
curl -X POST "http://localhost:8000/invoke" \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "gemini", "task": "Generate creative solutions"}'

# Banish LiquidMetal
curl -X POST "http://localhost:8000/banish" \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "liquidmetal"}'

# List all daemons
curl -X GET "http://localhost:8000/daemons"

# Toggle reality veil
curl -X POST "http://localhost:8000/reveal"
curl -X POST "http://localhost:8000/veil/restore"

# Get spell history
curl -X GET "http://localhost:8000/grimoire/recall?limit=10"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Summon Claude
response = requests.post(
    f"{BASE_URL}/summon",
    json={"daemon_name": "claude"}
)
print(response.json())

# Invoke Claude
response = requests.post(
    f"{BASE_URL}/invoke",
    json={
        "daemon_name": "claude",
        "task": "Analyze this mystical pattern"
    }
)
print(response.json())

# Check reality veil
response = requests.get(f"{BASE_URL}/veil")
print(response.json())  # {"veil": true, "mode": "fantasy"}

# View recent spells from grimoire
response = requests.get(f"{BASE_URL}/grimoire/recall?limit=5")
print(response.json())
```

## Testing Guide

### Quick Test Commands

```bash
# Activate environment
source venv/bin/activate

# Run all tests
pytest -v

# Run specific test files
pytest tests/test_vibecompiler.py -v
pytest tests/test_ws.py -v
pytest tests/test_veil.py -v
pytest test_spell_parser.py -v
pytest test_registry.py -v

# Run acceptance tests only
pytest tests/test_vibecompiler.py::test_vibecompiler_runs \
       tests/test_vibecompiler.py::test_vibecompiler_timeout \
       tests/test_ws.py::test_ws_sequence \
       tests/test_veil.py::test_veil_toggle_persists -v

# Run with output
pytest -v -s

# Clean state and run veil tests
rm -f .veil_state.json && pytest tests/test_veil.py -v
```

### Test Suite Summary

- **VibeCompiler Tests** (5 tests): Safe execution, timeout enforcement, output capture
- **WebSocket Event Bus Tests** (4 tests): Channel subscription, broadcasting, isolation
- **Reality Veil Tests** (4 tests): State persistence, toggle, API endpoints
- **Spell Parser Tests** (10 tests): Natural language parsing, confidence scoring
- **Registry Tests** (7 tests): Daemon lifecycle, state tracking, error handling

**Total:** 30 automated tests

### WebSocket Testing

1. Start the server
2. Run the Python WebSocket client: `python examples/websocket_client.py`
3. In another terminal, trigger some events:
```bash
curl -X POST http://localhost:8000/summon -H "Content-Type: application/json" -d '{"daemon_name": "claude"}'
```
4. Watch events appear in real-time!

## Development

### Adding New Daemons

1. Add the daemon type to `DaemonType` enum in `app/models/daemon.py`
2. Add the role to `DaemonRole` enum
3. Add daemon configuration in `_initialize_daemons()` in `app/services/daemon_registry.py`
4. Update fantasy messages in `app/routers/spells.py`

### Environment Variables

Create a `.env` file to override default settings:

```env
DEBUG_MODE=true
HOST=0.0.0.0
PORT=8000
RAINDROP_ENABLED=true
MAX_CONCURRENT_DAEMONS=3
VOICE_CACHE_DIR=arcane_audio
```

## Documentation

- **[VibeCompiler](docs/VIBECOMPILER.md)** - Safe Python execution with timeout enforcement
- **[ArcaneEventBus](docs/EVENT_BUS.md)** - Channel-based WebSocket event broadcasting
- **[Reality Veil](docs/REALITY_VEIL.md)** - Fantasy/developer mode toggle with persistence
- **[The Grimoire](docs/GRIMOIRE.md)** - Spell history and session continuity
- **[WebSocket Clients](examples/README.md)** - Client examples and usage guide
- **[Swagger UI](http://localhost:8000/grimoire)** - Interactive API documentation (when server is running)
- **[ReDoc](http://localhost:8000/arcane-docs)** - Alternative API documentation (when server is running)

## Architecture

### Core Layer (`core/`)

Foundation modules with minimal dependencies:
- **vibecompiler.py** - Safe code execution engine
- **event_bus.py** - WebSocket event broadcasting
- **veil.py** - Reality veil state management

### Application Layer (`app/`)

FastAPI application with business logic:
- **models/** - Pydantic data models
- **routers/** - API endpoint handlers
- **services/** - Business logic and integrations

### Design Principles

- **Separation of Concerns** - Core logic separated from API layer
- **Async-First** - All I/O operations use async/await
- **Type Safety** - Pydantic models for validation
- **Testability** - Comprehensive test suite with pytest
- **Persistence** - File-based state for session continuity
- **Security** - Safe code execution with sandboxing and timeouts

## Raindrop MCP SDK Integration

The project is designed to integrate with the Raindrop MCP SDK for tool invocation and daemon registration. See `app/config.py` for integration notes and examples.

Key integration points:
- Daemon registration with metadata
- Tool invocation routing
- Async task execution
- Response handling

## License

This project is for educational and entertainment purposes.

## Credits

Built with FastAPI, Pydantic, and mystical energies from the ethereal realm.

---

May your daemons be swift, your spells be powerful, and your code execute safely!
