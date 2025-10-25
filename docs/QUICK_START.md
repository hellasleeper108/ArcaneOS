# ArcaneOS Quick Start Guide

Get up and running with ArcaneOS in 5 minutes!

## Installation

```bash
# 1. Navigate to project
cd vibejam

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Start the Server

```bash
# Start development server
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

## Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Summon a daemon
curl -X POST http://localhost:8000/summon \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'

# View API docs
open http://localhost:8000/grimoire
```

## Core Components Quick Reference

### 1. VibeCompiler - Safe Code Execution

```python
from core.vibecompiler import VibeCompiler

compiler = VibeCompiler()
result = compiler.run_snippet("print('Hello!')", timeout=3)
# Returns: {"stdout": "Hello!\n", "stderr": "", "duration": 0.005}
```

**Key Features:**
- Safe subprocess execution (no shell, no network)
- Timeout enforcement (default 3s)
- Stdout/stderr capture

**Docs:** [VIBECOMPILER.md](VIBECOMPILER.md)

### 2. ArcaneEventBus - WebSocket Broadcasting

```python
from core.event_bus import get_event_bus

bus = get_event_bus()

# Subscribe to channel
await bus.subscribe("notifications", websocket)

# Broadcast event
await bus.emit("notifications", {"message": "Hello!"})
```

**WebSocket Endpoint:**
```
ws://localhost:8000/ws/events/{channel}
```

**Docs:** [EVENT_BUS.md](EVENT_BUS.md)

### 3. Reality Veil - Mode Toggle

```python
from core.veil import get_veil, reveal, restore

# Check mode
is_fantasy = get_veil()  # True/False

# Switch modes
reveal()   # Developer mode
restore()  # Fantasy mode
```

**API Endpoints:**
```bash
GET  /veil            # Get current state
POST /reveal          # Developer mode
POST /veil/restore    # Fantasy mode
```

**Docs:** [REALITY_VEIL.md](REALITY_VEIL.md)

### 4. The Grimoire - Spell History

```python
from app.services.grimoire import get_grimoire

grimoire = get_grimoire()

# Record spell
grimoire.record_spell(
    spell_name="test_spell",
    command={"action": "test"},
    result={"status": "success"}
)

# Recall recent spells
spells = grimoire.recall_spells(limit=10)
```

**API Endpoints:**
```bash
GET  /grimoire/recall       # Get recent spells
GET  /grimoire/statistics   # Get stats
POST /grimoire/search       # Search spells
```

**Docs:** [GRIMOIRE.md](GRIMOIRE.md)

## Testing

```bash
# Run all tests
pytest -v

# Run specific component tests
pytest tests/test_vibecompiler.py -v
pytest tests/test_ws.py -v
pytest tests/test_veil.py -v

# Run acceptance tests only
pytest tests/test_vibecompiler.py::test_vibecompiler_runs \
       tests/test_vibecompiler.py::test_vibecompiler_timeout \
       tests/test_ws.py::test_ws_sequence \
       tests/test_veil.py::test_veil_toggle_persists -v
```

## Common Operations

### Summon a Daemon

```bash
curl -X POST http://localhost:8000/summon \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'
```

### Invoke a Daemon

```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "daemon_name": "claude",
    "task": "Write a haiku"
  }'
```

### Natural Language Spell

```bash
curl -X POST http://localhost:8000/spell/cast \
  -H "Content-Type: application/json" \
  -d '{"spell_text": "summon gemini and make it analyze data"}'
```

### WebSocket Connection

**Python:**
```python
import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8000/ws/events/route"
    async with websockets.connect(uri) as ws:
        async for message in ws:
            print(message)

asyncio.run(listen())
```

**JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events/route');
ws.onmessage = (event) => console.log(event.data);
```

### Toggle Reality Veil

```bash
# Switch to developer mode
curl -X POST http://localhost:8000/reveal

# Switch to fantasy mode
curl -X POST http://localhost:8000/veil/restore

# Check current mode
curl http://localhost:8000/veil
```

### View Spell History

```bash
# Recent spells
curl http://localhost:8000/grimoire/recall?limit=10

# Statistics
curl http://localhost:8000/grimoire/statistics

# Search
curl -X POST http://localhost:8000/grimoire/search \
  -H "Content-Type: application/json" \
  -d '{"query": "claude", "limit": 5}'
```

## Project Structure

```
vibejam/
├── core/                    # Core modules
│   ├── vibecompiler.py     # Safe code execution
│   ├── event_bus.py        # WebSocket broadcasting
│   └── veil.py             # Reality veil
├── app/                     # FastAPI application
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   └── models/             # Pydantic models
├── tests/                   # Test suite
│   ├── test_vibecompiler.py
│   ├── test_ws.py
│   └── test_veil.py
└── docs/                    # Documentation
    ├── VIBECOMPILER.md
    ├── EVENT_BUS.md
    ├── REALITY_VEIL.md
    └── GRIMOIRE.md
```

## API Documentation

Once server is running:
- **Swagger UI:** http://localhost:8000/grimoire
- **ReDoc:** http://localhost:8000/arcane-docs

## Environment Variables

Create `.env` file:

```env
DEBUG_MODE=true
HOST=0.0.0.0
PORT=8000
RAINDROP_ENABLED=true
MAX_CONCURRENT_DAEMONS=3
VOICE_CACHE_DIR=arcane_audio
```

## Troubleshooting

### Port Already in Use

```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Module Import Errors

```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Failing

```bash
# Clean state files
rm -f .veil_state.json

# Run tests fresh
pytest -v
```

### WebSocket Connection Issues

```bash
# Check server is running
curl http://localhost:8000/health

# Test WebSocket endpoint
websocat ws://localhost:8000/ws/events/test
```

## Next Steps

1. **Read the Documentation:**
   - [VibeCompiler](VIBECOMPILER.md) - Safe code execution
   - [Event Bus](EVENT_BUS.md) - WebSocket broadcasting
   - [Reality Veil](REALITY_VEIL.md) - Mode toggling
   - [Grimoire](GRIMOIRE.md) - Spell history

2. **Explore Examples:**
   - Check `examples/` directory for client code
   - Try WebSocket clients (Python and HTML)

3. **Run Tests:**
   - Execute test suite: `pytest -v`
   - Review test files to understand usage

4. **Customize:**
   - Add new daemons
   - Create custom spell types
   - Build your own WebSocket channels

## Helpful Commands

```bash
# Start server
python -m app.main

# Run all tests
pytest -v

# Run specific test
pytest tests/test_ws.py::test_ws_sequence -v

# Check test coverage
pytest --cov=core --cov=app -v

# Clean state files
rm -f .veil_state.json grimoire_spells.jsonl

# View logs
tail -f arcane_log.txt

# Interactive API testing
open http://localhost:8000/grimoire
```

## Support

- **Documentation:** `docs/` directory
- **Examples:** `examples/` directory
- **Tests:** `tests/` directory
- **Issues:** Check test output for errors

## Summary

You now have:
- ✅ ArcaneOS server running
- ✅ Safe code execution (VibeCompiler)
- ✅ WebSocket event broadcasting (ArcaneEventBus)
- ✅ Fantasy/Developer mode toggle (Reality Veil)
- ✅ Spell history persistence (Grimoire)
- ✅ Comprehensive test suite
- ✅ Full documentation

**Happy spell casting!** ✨

---

For detailed documentation, see the main [README](../README.md) and component-specific docs in `docs/`.
