# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ArcaneOS is a fantasy-themed FastAPI backend with a two-layer architecture:
- **Core Layer** (`core/`): Foundation modules with minimal dependencies for safe code execution, WebSocket broadcasting, and state management
- **Application Layer** (`app/`): FastAPI routers, services, and models that build on core functionality

The system uses fantasy terminology consistently: "daemons" (AI models), "spells" (API operations), "summon/invoke/banish" (lifecycle operations), and "grimoire" (persistent storage).

## Development Commands

### Server Operations
```bash
# Start development server
python -m app.main

# Alternative with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest -v

# Run specific test suites
pytest tests/test_vibecompiler.py -v    # Core: Safe code execution
pytest tests/test_ws.py -v              # Core: WebSocket event bus
pytest tests/test_veil.py -v            # Core: Reality veil state
pytest test_spell_parser.py -v          # App: Natural language parser
pytest test_registry.py -v              # App: Daemon lifecycle

# Run single test
pytest tests/test_vibecompiler.py::test_vibecompiler_runs -v

# Run with output visible
pytest -v -s

# Clean state files before veil tests
rm -f .veil_state.json && pytest tests/test_veil.py -v
```

### Documentation
```bash
# Interactive API documentation (server must be running)
open http://localhost:8000/grimoire      # Swagger UI
open http://localhost:8000/arcane-docs   # ReDoc

# Component documentation in docs/
cat docs/VIBECOMPILER.md    # Safe code execution
cat docs/EVENT_BUS.md        # WebSocket broadcasting
cat docs/REALITY_VEIL.md     # Fantasy/developer mode toggle
cat docs/GRIMOIRE.md         # Spell history persistence
```

## Architecture

### Two-Layer System

**Core Layer** (`core/`): Independent, reusable components
- `vibecompiler.py`: Subprocess-based Python execution with timeout enforcement
- `event_bus.py`: Channel-based WebSocket event broadcasting
- `veil.py`: Global state management with JSON persistence

**Application Layer** (`app/`): FastAPI-specific implementation
- `routers/`: API endpoints organized by feature (spells, grimoire, websockets)
- `services/`: Business logic (daemon_registry, spell_parser, grimoire)
- `models/`: Pydantic models for request/response validation

### Singleton Pattern Usage

Use singleton getters for shared state:
```python
from core.event_bus import get_event_bus       # NOT ArcaneEventBus()
from core.veil import get_veil, set_veil       # NOT direct VEIL access
from app.services.grimoire import get_grimoire  # NOT Grimoire()
```

### Async Task Management

The daemon registry uses `_safe_create_task()` to handle async operations that may run in sync test contexts:
```python
# In daemon_registry.py
_safe_create_task(event_bus.emit_summon(...))  # Safe in tests and production
```

This pattern prevents `RuntimeError: no running event loop` in tests.

### State Persistence Files

The system creates several state files in the project root:
- `.veil_state.json`: Reality veil mode (fantasy vs developer)
- `grimoire_spells.jsonl`: Spell history in JSON Lines format
- `arcane_log.txt`: Application logging including ceremonial messages

Clean these before fresh test runs if needed.

### Natural Language Parsing

The spell parser (`app/services/spell_parser.py`) uses regex patterns to convert natural language to structured commands:
- Daemon aliases: "logic keeper" → "claude", "dream weaver" → "gemini"
- Action detection: "summon", "invoke", "banish", "show/list" → structured spell
- Confidence scoring based on pattern matches

### Daemon Lifecycle

Daemon operations flow through:
1. Router endpoint (`app/routers/spells.py`)
2. Daemon registry (`app/services/daemon_registry.py`) - manages state and MCP integration
3. Raindrop MCP client (`app/services/raindrop_client.py`) - interfaces with AI models
4. Event bus - broadcasts lifecycle events
5. Grimoire - records spell history

### WebSocket Architecture

Two event bus implementations exist:
- **Legacy** (`app/services/arcane_event_bus.py`): Queue-based, single stream for daemon operations
- **New** (`core/event_bus.py`): Channel-based, supports multiple independent channels

New code should use the core event bus for channel-based broadcasting.

## Adding New Features

### Adding a New Daemon
1. Add enum to `app/models/daemon.py`: `DaemonType` and `DaemonRole`
2. Add configuration in `daemon_registry.py`: `MODEL_MAPPINGS` and `_initialize_daemons()`
3. Update fantasy messages in `app/routers/spells.py`
4. Add aliases to spell parser patterns in `spell_parser.py`

### Adding a New Core Module
1. Create in `core/` directory with minimal dependencies
2. Export via `core/__init__.py`
3. Provide singleton getter function (e.g., `get_module_name()`)
4. Add comprehensive tests in `tests/`
5. Document in `docs/`

### Adding API Endpoints
1. Create router in `app/routers/`
2. Use Pydantic models from `app/models/`
3. Include router in `app/main.py`
4. Use fantasy-themed response messages for consistency
5. Integrate with grimoire for spell recording if applicable

## Testing Philosophy

Tests use FastAPI's TestClient for router testing and direct imports for core modules:
```python
# Router testing
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.post("/endpoint", json={...})

# Core module testing
from core.vibecompiler import VibeCompiler
compiler = VibeCompiler()
result = compiler.run_snippet("print('test')")
```

The test suite includes 30+ tests covering core functionality and integration points.

## Raindrop MCP Integration

The system is designed to integrate with Raindrop MCP SDK for AI model routing:
- `raindrop_client.py`: MCP client wrapper
- Daemon registry automatically registers daemons with MCP
- Invocations route through MCP tool system
- Mock responses used when Raindrop is unavailable

## Common Patterns

### Fantasy-Themed Responses
```python
# Consistent with existing style
{
    "status": "summoned",
    "message": "✨ The daemon CLAUDE materializes through swirling purple aether... ✨",
    "daemon": daemon_object
}
```

### Error Handling
```python
from fastapi import HTTPException

if not daemon.is_summoned:
    raise HTTPException(
        status_code=400,
        detail="The daemon slumbers in the void - summon it first!"
    )
```

### Logging with Ceremony
```python
logger.info("✨ Veil restored - Fantasy mode enabled")
logger.info("🔍 Veil lifted - Developer mode enabled")
logger.info("📖 SPELL RECORDED: summon_claude succeeded [daemon: claude]")
```

## Key Files for Understanding System

- `app/main.py`: FastAPI app setup and router registration
- `app/services/daemon_registry.py`: Core daemon lifecycle management
- `core/vibecompiler.py`: Safe execution engine
- `core/event_bus.py`: WebSocket broadcasting system
- `core/veil.py`: Mode toggle implementation
- `app/services/grimoire.py`: Spell history persistence

## Configuration

Environment variables via `.env`:
```env
DEBUG_MODE=true
HOST=0.0.0.0
PORT=8000
RAINDROP_ENABLED=true
MAX_CONCURRENT_DAEMONS=3
VOICE_CACHE_DIR=arcane_audio
```

Settings loaded through `app/config.py` using pydantic-settings.
