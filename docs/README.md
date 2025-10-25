# ArcaneOS Documentation

Welcome to the ArcaneOS documentation! This directory contains comprehensive guides for all ArcaneOS components.

## Documentation Index

### Getting Started

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Main README](../README.md)** - Project overview and installation

### Core Components

- **[VibeCompiler](VIBECOMPILER.md)** - Safe Python code execution with timeout enforcement
  - Safe subprocess execution
  - Timeout protection
  - Output capture (stdout/stderr)
  - Ceremonial logging
  - Built-in modules only

- **[ArcaneEventBus](EVENT_BUS.md)** - Channel-based WebSocket event broadcasting
  - Real-time message broadcasting
  - Channel-based routing
  - Async-safe operations
  - Automatic subscriber cleanup
  - Queue buffering

- **[Reality Veil](REALITY_VEIL.md)** - Fantasy/developer mode toggle
  - Global state management
  - Persistent state storage
  - Thread-safe operations
  - Mode-specific behavior
  - REST API endpoints

- **[The Grimoire](GRIMOIRE.md)** - Spell history and session continuity
  - File-based persistence
  - Dual storage (JSONL + logs)
  - Filtering and search
  - Statistics tracking
  - Automatic spell recording

## Quick Links

### API Documentation
- [Swagger UI](http://localhost:8000/grimoire) - Interactive API docs (server must be running)
- [ReDoc](http://localhost:8000/arcane-docs) - Alternative API docs (server must be running)

### Testing
```bash
# Run all tests
pytest -v

# Run component tests
pytest tests/test_vibecompiler.py -v
pytest tests/test_ws.py -v
pytest tests/test_veil.py -v
```

### Examples
- `../examples/websocket_client.py` - Python WebSocket client
- `../examples/websocket_client.html` - Browser WebSocket client
- `../examples/vibe_compiler_example.py` - VibeCompiler demo

## Component Overview

### VibeCompiler
Execute Python code safely with timeout enforcement.

**Key Features:**
- Subprocess isolation
- No shell, no network access
- Configurable timeout
- Ceremonial logging

**Usage:**
```python
from core.vibecompiler import VibeCompiler

compiler = VibeCompiler()
result = compiler.run_snippet("print('Hello!')", timeout=3)
```

**Documentation:** [VIBECOMPILER.md](VIBECOMPILER.md)

---

### ArcaneEventBus
Real-time WebSocket broadcasting with channel-based routing.

**Key Features:**
- Channel subscriptions
- JSON message broadcasting
- Automatic cleanup
- Async-safe operations

**Usage:**
```python
from core.event_bus import get_event_bus

bus = get_event_bus()
await bus.subscribe("route", websocket)
await bus.emit("route", {"event": "data"})
```

**WebSocket:** `ws://localhost:8000/ws/events/{channel}`

**Documentation:** [EVENT_BUS.md](EVENT_BUS.md)

---

### Reality Veil
Toggle between fantasy and developer modes with persistent state.

**Key Features:**
- Global state variable
- Persistent JSON storage
- Thread-safe access
- REST API

**Usage:**
```python
from core.veil import get_veil, reveal, restore

# Check mode
is_fantasy = get_veil()

# Switch modes
reveal()   # Developer mode
restore()  # Fantasy mode
```

**API:** `GET /veil`, `POST /reveal`, `POST /veil/restore`

**Documentation:** [REALITY_VEIL.md](REALITY_VEIL.md)

---

### The Grimoire
File-based spell history with session continuity.

**Key Features:**
- JSONL storage format
- Dual logging system
- Filtering and search
- Statistics tracking

**Usage:**
```python
from app.services.grimoire import get_grimoire

grimoire = get_grimoire()
grimoire.record_spell(
    spell_name="test",
    command={"action": "test"},
    result={"status": "success"}
)
```

**API:** `/grimoire/recall`, `/grimoire/statistics`, `/grimoire/search`

**Documentation:** [GRIMOIRE.md](GRIMOIRE.md)

## Architecture

### Core Layer (`../core/`)
Foundation modules with minimal dependencies:
- `vibecompiler.py` - Safe code execution
- `event_bus.py` - WebSocket broadcasting
- `veil.py` - Reality veil state

### Application Layer (`../app/`)
FastAPI application with business logic:
- `models/` - Pydantic data models
- `routers/` - API endpoint handlers
- `services/` - Business logic

### Test Layer (`../tests/`)
Comprehensive test suite:
- `test_vibecompiler.py` - VibeCompiler tests (5 tests)
- `test_ws.py` - WebSocket tests (4 tests)
- `test_veil.py` - Reality Veil tests (4 tests)

**Total:** 30+ automated tests

## API Endpoints Summary

### Core Daemon Operations
- `GET /daemons` - List all daemons
- `POST /summon` - Summon a daemon
- `POST /invoke` - Invoke a daemon
- `POST /banish` - Banish a daemon

### Spell Parser
- `POST /spell/parse` - Parse natural language spell
- `POST /spell/cast` - Parse and execute spell
- `GET /spell/examples` - List spell examples

### Grimoire
- `POST /grimoire/record` - Record a spell
- `GET /grimoire/recall` - Retrieve recent spells
- `GET /grimoire/statistics` - Get statistics
- `DELETE /grimoire/purge` - Purge old spells
- `POST /grimoire/search` - Search spells

### Reality Veil
- `GET /veil` - Get veil status
- `POST /veil` - Set veil state
- `POST /reveal` - Developer mode
- `POST /veil/restore` - Fantasy mode

### Event Bus
- `ws://localhost:8000/ws/events/{channel}` - WebSocket subscription
- `GET /channels` - List active channels

## Testing Guide

### Run All Tests
```bash
source venv/bin/activate
pytest -v
```

### Component-Specific Tests
```bash
# VibeCompiler
pytest tests/test_vibecompiler.py -v

# WebSocket Event Bus
pytest tests/test_ws.py -v

# Reality Veil
pytest tests/test_veil.py -v

# Spell Parser
pytest test_spell_parser.py -v

# Daemon Registry
pytest test_registry.py -v
```

### Acceptance Tests
```bash
pytest tests/test_vibecompiler.py::test_vibecompiler_runs \
       tests/test_vibecompiler.py::test_vibecompiler_timeout \
       tests/test_ws.py::test_ws_sequence \
       tests/test_veil.py::test_veil_toggle_persists -v
```

## Development Workflow

1. **Start Server:**
   ```bash
   python -m app.main
   ```

2. **Run Tests:**
   ```bash
   pytest -v
   ```

3. **Check API Docs:**
   ```
   http://localhost:8000/grimoire
   ```

4. **View Logs:**
   ```bash
   tail -f arcane_log.txt
   ```

5. **Clean State:**
   ```bash
   rm -f .veil_state.json grimoire_spells.jsonl
   ```

## Best Practices

### 1. Use Core Modules Directly
```python
# Good - Direct import from core
from core.vibecompiler import VibeCompiler
from core.event_bus import get_event_bus
from core.veil import get_veil

# Avoid - Don't create new instances
bus = ArcaneEventBus()  # Use get_event_bus() instead
```

### 2. Handle Async Operations
```python
# All event bus operations are async
await bus.subscribe(channel, websocket)
await bus.emit(channel, message)
await bus.unsubscribe(channel, websocket)
```

### 3. Check Veil State
```python
from core.veil import get_veil

if get_veil():
    # Fantasy mode behavior
    return "✨ Mystical response ✨"
else:
    # Developer mode behavior
    return "Technical response"
```

### 4. Record Important Operations
```python
from app.services.grimoire import get_grimoire

grimoire = get_grimoire()
grimoire.record_spell(
    spell_name="operation_name",
    command={"params": "..."},
    result={"status": "success"},
    success=True
)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Port Already in Use**
   ```bash
   lsof -i :8000
   kill -9 <PID>
   ```

3. **State File Issues**
   ```bash
   rm -f .veil_state.json
   ```

4. **WebSocket Connection Fails**
   ```bash
   curl http://localhost:8000/health
   ```

## Contributing

When adding new features:

1. Add tests in `tests/`
2. Update relevant documentation
3. Follow existing code style
4. Ensure all tests pass: `pytest -v`

## Support

- **Documentation Issues:** Check this directory
- **API Issues:** View Swagger UI at `/grimoire`
- **Test Failures:** Review test output with `pytest -v`
- **Examples:** Check `../examples/` directory

## Resources

- [Main README](../README.md) - Project overview
- [Quick Start](QUICK_START.md) - 5-minute setup guide
- [Examples Directory](../examples/) - Working code examples
- [Test Suite](../tests/) - Test implementations

---

**Last Updated:** October 2025

All documentation maintained and up-to-date with ArcaneOS v1.0.0.
