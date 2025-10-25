# Reality Veil Documentation

## Overview

The **Reality Veil** is a state management system that toggles ArcaneOS between fantasy-themed and developer modes. It provides persistent state storage, thread-safe operations, and seamless mode switching with ceremonial logging.

## Features

- **Global State Variable**: Single source of truth for mode state
- **Persistent Storage**: State saved to `.veil_state.json`
- **Automatic Loading**: State restored on server startup
- **Thread-Safe**: Protected with threading.Lock
- **Ceremonial Logging**: Fantasy-themed state change messages
- **REST API**: FastAPI endpoints for state management
- **Helper Functions**: Simple Python API for mode control

## Modes

### Fantasy Mode (Veil = True)

Fantasy mode presents the system with mystical, whimsical themes:
- Fantasy-themed response messages
- Mystical terminology (spells, daemons, summoning)
- Ceremonial language and emojis
- Immersive storytelling

### Developer Mode (Veil = False)

Developer mode shows technical, straightforward information:
- Direct, technical responses
- Standard terminology (API, processes, operations)
- Debugging-friendly output
- Performance metrics

## Installation

The Reality Veil is part of the core ArcaneOS modules:

```python
from core.veil import get_veil, set_veil, reveal, restore, get_mode
```

## Basic Usage

### Python API

```python
from core.veil import get_veil, set_veil, reveal, restore, get_mode

# Check current state
is_fantasy = get_veil()
print(f"Fantasy mode: {is_fantasy}")  # True or False

# Get mode as string
mode = get_mode()
print(f"Current mode: {mode}")  # "fantasy" or "developer"

# Switch to developer mode
reveal()

# Switch to fantasy mode
restore()

# Set explicit state
set_veil(True)   # Fantasy mode
set_veil(False)  # Developer mode

# Toggle between modes
from core.veil import toggle_veil
toggle_veil()
```

### REST API

#### Get Veil Status

```bash
curl http://localhost:8000/veil
```

**Response:**
```json
{
  "veil": true,
  "mode": "fantasy"
}
```

#### Set Veil State

```bash
curl -X POST http://localhost:8000/veil \
  -H "Content-Type: application/json" \
  -d '{"veil": false}'
```

**Response:**
```json
{
  "veil": false,
  "mode": "developer"
}
```

#### Reveal (Developer Mode)

```bash
curl -X POST http://localhost:8000/reveal
```

**Response:**
```json
{
  "veil": false,
  "mode": "developer"
}
```

#### Restore (Fantasy Mode)

```bash
curl -X POST http://localhost:8000/veil/restore
```

**Response:**
```json
{
  "veil": true,
  "mode": "fantasy"
}
```

## API Reference

### Python Functions

#### `get_veil() -> bool`

Get the current veil state.

**Returns:**
- `bool`: True if fantasy mode, False if developer mode

**Example:**
```python
if get_veil():
    print("Fantasy mode is active")
else:
    print("Developer mode is active")
```

#### `set_veil(value: bool) -> bool`

Set the veil state and persist to file.

**Parameters:**
- `value` (bool): True for fantasy mode, False for developer mode

**Returns:**
- `bool`: The new veil state

**Example:**
```python
set_veil(False)  # Switch to developer mode
```

**Logging:**
- Veil up: `"✨ Veil restored - Fantasy mode enabled"`
- Veil down: `"🔍 Veil lifted - Developer mode enabled"`

#### `toggle_veil() -> bool`

Toggle the veil state between fantasy and developer mode.

**Returns:**
- `bool`: The new veil state after toggling

**Example:**
```python
current = get_veil()  # True
new_state = toggle_veil()  # False
```

#### `reveal() -> bool`

Switch to developer mode (veil down).

**Returns:**
- `bool`: The new veil state (False)

**Example:**
```python
reveal()
print(get_mode())  # "developer"
```

#### `restore() -> bool`

Switch to fantasy mode (veil up).

**Returns:**
- `bool`: The new veil state (True)

**Example:**
```python
restore()
print(get_mode())  # "fantasy"
```

#### `get_mode() -> str`

Get the current mode as a string.

**Returns:**
- `str`: "fantasy" or "developer"

**Example:**
```python
mode = get_mode()
if mode == "fantasy":
    print("Using fantasy theme")
```

### REST Endpoints

#### `GET /veil`

Get the current veil status.

**Response Model:**
```json
{
  "veil": bool,
  "mode": str
}
```

#### `POST /veil`

Update the veil state.

**Request Model:**
```json
{
  "veil": bool
}
```

**Response Model:**
```json
{
  "veil": bool,
  "mode": str
}
```

#### `POST /reveal`

Switch to developer mode (veil down).

**Response Model:**
```json
{
  "veil": false,
  "mode": "developer"
}
```

#### `POST /veil/restore`

Restore fantasy mode (veil up).

**Response Model:**
```json
{
  "veil": true,
  "mode": "fantasy"
}
```

## Persistence

### State File Format

The veil state is stored in `.veil_state.json`:

```json
{
  "veil": true,
  "mode": "fantasy"
}
```

**File Location:** Project root directory

### Automatic Loading

State is automatically loaded when the `core.veil` module is imported:

```python
# State loaded from .veil_state.json on import
from core.veil import get_veil

# If file doesn't exist, defaults to True (fantasy mode)
current_state = get_veil()
```

### Manual State File Manipulation

```bash
# View current state
cat .veil_state.json

# Manually set state (for testing)
echo '{"veil": false, "mode": "developer"}' > .veil_state.json

# Remove state file (will reset to default on next load)
rm .veil_state.json
```

## Examples

### Example 1: Conditional Responses

```python
from core.veil import get_veil

def get_response_message(operation: str):
    if get_veil():
        # Fantasy mode
        return f"✨ The mystical {operation} ritual completes! ✨"
    else:
        # Developer mode
        return f"Operation '{operation}' completed successfully"

message = get_response_message("summon")
print(message)
```

### Example 2: Toggle for Testing

```python
from core.veil import get_veil, reveal, restore

# Save current state
original_state = get_veil()

# Run tests in developer mode
reveal()
run_tests()

# Restore original state
if original_state:
    restore()
else:
    reveal()
```

### Example 3: Mode-Specific Behavior

```python
from core.veil import get_mode

def format_daemon_name(name: str) -> str:
    mode = get_mode()

    if mode == "fantasy":
        return f"✨ {name.upper()} ✨"
    else:
        return name.lower()

print(format_daemon_name("Claude"))
# Fantasy: "✨ CLAUDE ✨"
# Developer: "claude"
```

### Example 4: API Integration

```python
import requests

BASE_URL = "http://localhost:8000"

# Check current mode
response = requests.get(f"{BASE_URL}/veil")
state = response.json()
print(f"Current mode: {state['mode']}")

# Toggle to developer mode for debugging
if state['veil']:
    requests.post(f"{BASE_URL}/reveal")
    print("Switched to developer mode")

# Perform debugging operations
# ...

# Restore fantasy mode
requests.post(f"{BASE_URL}/veil/restore")
print("Restored fantasy mode")
```

### Example 5: Context Manager

```python
from contextlib import contextmanager
from core.veil import get_veil, reveal, restore

@contextmanager
def developer_mode():
    """Temporarily switch to developer mode"""
    original = get_veil()

    reveal()
    try:
        yield
    finally:
        if original:
            restore()

# Use in context
with developer_mode():
    # Code runs in developer mode
    print("Debug mode active")
# Automatically restored after context
```

## Integration Examples

### With Event Bus

```python
from core.veil import get_veil, set_veil
from core.event_bus import get_event_bus

async def toggle_and_broadcast():
    bus = get_event_bus()

    # Toggle veil
    old_state = get_veil()
    new_state = set_veil(not old_state)

    # Broadcast change
    await bus.emit("system", {
        "event": "veil_changed",
        "old_mode": "fantasy" if old_state else "developer",
        "new_mode": "fantasy" if new_state else "developer"
    })
```

### With Grimoire

```python
from core.veil import get_veil, reveal
from app.services.grimoire import get_grimoire

def record_veil_change():
    grimoire = get_grimoire()

    # Change state
    reveal()

    # Record in grimoire
    grimoire.record_spell(
        spell_name="veil_revelation",
        command={"action": "reveal"},
        result={"mode": "developer"},
        spell_type="query",
        success=True
    )
```

### With Daemon Responses

```python
from core.veil import get_mode

def format_daemon_message(daemon: str, operation: str) -> str:
    mode = get_mode()

    if mode == "fantasy":
        return f"✨ The daemon {daemon.upper()} performs the {operation} ritual! ✨"
    else:
        return f"Daemon '{daemon}' executed '{operation}' operation"

message = format_daemon_message("claude", "summon")
```

## Testing

The Reality Veil includes comprehensive tests:

```bash
# Run all veil tests
pytest tests/test_veil.py -v

# Run specific tests
pytest tests/test_veil.py::test_veil_toggle_persists -v
pytest tests/test_veil.py::test_veil_state_reload -v

# Clean state before testing
rm -f .veil_state.json && pytest tests/test_veil.py -v
```

### Test Coverage

1. **test_veil_toggle_persists** - State persistence validation
2. **test_veil_state_reload** - File format and reloading
3. **test_veil_post_endpoint** - POST /veil endpoint
4. **test_veil_endpoints_all** - All endpoints validation

### Manual Testing

```bash
# Check current state
curl http://localhost:8000/veil

# Toggle to developer mode
curl -X POST http://localhost:8000/reveal

# Check state file
cat .veil_state.json

# Restore fantasy mode
curl -X POST http://localhost:8000/veil/restore

# Verify in logs
tail -f arcane_log.txt | grep -i veil
```

## Best Practices

### 1. Check Mode Before Formatting

```python
from core.veil import get_mode

def format_response(data: dict) -> dict:
    mode = get_mode()

    if mode == "fantasy":
        data["message"] = f"✨ {data['message']} ✨"
        data["theme"] = "mystical"
    else:
        data["debug"] = True
        data["theme"] = "technical"

    return data
```

### 2. Log State Changes

```python
import logging
from core.veil import set_veil

logger = logging.getLogger(__name__)

def change_mode(to_fantasy: bool):
    logger.info(f"Changing mode to {'fantasy' if to_fantasy else 'developer'}")
    set_veil(to_fantasy)
    logger.info("Mode change complete")
```

### 3. Provide User Feedback

```python
from core.veil import get_veil, reveal, restore

def toggle_with_feedback():
    was_fantasy = get_veil()

    if was_fantasy:
        reveal()
        return "Switched to developer mode - technical view enabled"
    else:
        restore()
        return "Switched to fantasy mode - mystical view enabled"
```

### 4. Respect User Preferences

```python
from core.veil import get_veil

def should_show_fantasy_ui() -> bool:
    """Check if fantasy UI should be displayed"""
    return get_veil()

# In your UI code
if should_show_fantasy_ui():
    render_fantasy_theme()
else:
    render_technical_theme()
```

## Troubleshooting

### Issue: State Not Persisting

**Problem:** Veil state resets after server restart.

**Solution:** Check file permissions and location:

```bash
# Check if file exists
ls -la .veil_state.json

# Check file contents
cat .veil_state.json

# Check write permissions
touch .veil_state.json
```

### Issue: State File Corrupted

**Problem:** JSON decode error on startup.

**Solution:** Reset state file:

```bash
# Remove corrupted file
rm .veil_state.json

# Restart server (will create new file with defaults)
python -m app.main
```

### Issue: Changes Not Reflected

**Problem:** Mode doesn't change after API call.

**Solution:** Verify module singleton is being used:

```python
# Correct - Uses singleton
from core.veil import get_event_bus
bus = get_event_bus()

# Incorrect - Creates new instance
from core.veil import ArcaneEventBus
bus = ArcaneEventBus()  # Don't do this
```

## Advanced Usage

### Custom Persistence Location

Modify `core/veil.py` to use custom location:

```python
# In core/veil.py
from pathlib import Path

# Custom location
STATE_FILE = Path("/var/lib/arcaneos/.veil_state.json")
```

### Environment-Based Default

Set default based on environment:

```python
import os
from core.veil import set_veil

# In startup code
if os.getenv("ENVIRONMENT") == "production":
    set_veil(True)  # Fantasy mode in production
else:
    set_veil(False)  # Developer mode for development
```

### Conditional Features

Enable/disable features based on mode:

```python
from core.veil import get_mode

FEATURES = {
    "fantasy": {
        "animations": True,
        "sound_effects": True,
        "verbose_logging": False
    },
    "developer": {
        "animations": False,
        "sound_effects": False,
        "verbose_logging": True
    }
}

def is_feature_enabled(feature: str) -> bool:
    mode = get_mode()
    return FEATURES[mode].get(feature, False)

if is_feature_enabled("animations"):
    play_animation()
```

## Security Considerations

### 1. Access Control

Consider restricting veil changes in production:

```python
from fastapi import HTTPException, Depends
from core.veil import set_veil

def require_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")

@router.post("/veil")
async def update_veil(
    request: VeilUpdateRequest,
    user: User = Depends(require_admin)
):
    set_veil(request.veil)
    return {"success": True}
```

### 2. Audit Logging

Log all veil changes:

```python
from core.veil import set_veil
import logging

audit_logger = logging.getLogger("audit")

def audited_veil_change(new_state: bool, user_id: str):
    audit_logger.info(
        f"User {user_id} changed veil to {new_state}"
    )
    set_veil(new_state)
```

## See Also

- [ArcaneOS README](../README.md) - Main project documentation
- [VibeCompiler](VIBECOMPILER.md) - Safe code execution
- [Event Bus](EVENT_BUS.md) - WebSocket event broadcasting
- [The Grimoire](GRIMOIRE.md) - Spell history documentation

---

**Note:** The Reality Veil provides seamless mode switching with persistent state, enabling both fantasy-themed and technical interfaces from the same API.
