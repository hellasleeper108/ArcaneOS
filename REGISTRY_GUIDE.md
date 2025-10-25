# ArcaneOS Enhanced Daemon Registry Guide

## Overview

The Enhanced Daemon Registry integrates with Raindrop MCP SDK to provide robust daemon lifecycle management, state tracking, and model routing capabilities.

## Table of Contents

1. [Core Features](#core-features)
2. [DaemonRegistry API](#daemonregistry-api)
3. [Raindrop MCP Integration](#raindrop-mcp-integration)
4. [State Tracking](#state-tracking)
5. [HTTP API Endpoints](#http-api-endpoints)
6. [Usage Examples](#usage-examples)

## Core Features

### Enhanced Daemon Management

- **Automatic MCP Registration**: Daemons are automatically registered with Raindrop MCP upon summoning
- **Model Routing**: Each daemon routes to a specific AI model through MCP
- **State Tracking**: Comprehensive tracking of invocation history, execution times, and statistics
- **Clean Banishment**: Proper cleanup including MCP unregistration

### Model Mappings

| Daemon | Model | Provider | Capabilities |
|--------|-------|----------|-------------|
| Claude | claude-3-5-sonnet-20241022 | Anthropic | reasoning, analysis, code_generation, logic |
| Gemini | gemini-2.0-flash-exp | Google | creativity, multimodal, vision, innovation |
| LiquidMetal | liquidmetal-adaptive-v1 | Custom | transformation, adaptation, flow, custom_tasks |

## DaemonRegistry API

### Core Methods

#### `register_daemon(name, model, role, color_code=None, capabilities=None)`

Register a daemon with the Raindrop MCP interface.

```python
from app.services.daemon_registry import daemon_registry
from app.models.daemon import DaemonType

daemon = daemon_registry.register_daemon(
    name=DaemonType.CLAUDE,
    model="claude-3-5-sonnet-20241022",
    role="Master of Logic",
    capabilities=["reasoning", "analysis"]
)
```

**Parameters:**
- `name` (DaemonType): The daemon's true name
- `model` (str): AI model identifier
- `role` (str): The mystical role
- `color_code` (str, optional): Hex color code
- `capabilities` (List[str], optional): List of capabilities

**Returns:** Daemon entity

**Raises:** HTTPException if daemon doesn't exist or registration fails

---

#### `summon(daemon_name)`

Summon a daemon into the material realm and auto-register with MCP.

```python
daemon = daemon_registry.summon(DaemonType.CLAUDE)
```

**Parameters:**
- `daemon_name` (DaemonType): Daemon to summon

**Returns:** Summoned daemon entity

**Auto-registers** the daemon with MCP using default model configuration.

---

#### `invoke_daemon(name, task, parameters=None)`

Invoke a daemon's power through Raindrop MCP interface.

```python
result = daemon_registry.invoke_daemon(
    name=DaemonType.CLAUDE,
    task="Analyze this algorithm",
    parameters={"depth": "comprehensive"}
)
```

**Parameters:**
- `name` (DaemonType): Daemon to invoke
- `task` (str): Task description
- `parameters` (Dict, optional): Additional parameters

**Returns:** Dictionary with:
- `daemon`: Updated daemon entity
- `result`: MCP invocation result
- `execution_time`: Time taken (seconds)
- `success`: Boolean success status
- `metadata`: Additional metadata
- `invocation_number`: Current invocation count

---

#### `banish_daemon(name)`

Banish daemon with MCP cleanup and statistics.

```python
result = daemon_registry.banish_daemon(DaemonType.CLAUDE)
```

**Returns:** Dictionary with:
- `daemon`: Banished daemon entity
- `statistics`: Complete service statistics
- `message`: Banishment confirmation

---

### Query Methods

#### `get_daemon(daemon_name)`
Retrieve daemon information.

#### `get_daemon_state(daemon_name)`
Get detailed state including invocation history.

#### `get_all_daemons()`
Retrieve all daemons.

#### `get_active_daemons()`
Get only currently summoned daemons.

#### `get_registry_statistics()`
Comprehensive registry-wide statistics.

## Raindrop MCP Integration

### Architecture

```
Client Request
    ↓
DaemonRegistry.invoke_daemon()
    ↓
RaindropMCPClient.invoke_tool()
    ↓
Model Provider (Anthropic/Google/Custom)
    ↓
Response with MCPToolResult
```

### RaindropMCPClient

The `RaindropMCPClient` wrapper handles:

- Tool registration with model routing
- Invocation routing to appropriate models
- Result encapsulation with timing
- Error handling and retries

```python
from app.services.raindrop_client import get_mcp_client, ModelProvider

client = get_mcp_client()

# Register a tool
client.register_tool(
    tool_name="claude",
    model="claude-3-5-sonnet-20241022",
    provider=ModelProvider.ANTHROPIC,
    capabilities=["reasoning", "analysis"]
)

# Invoke
result = client.invoke_tool(
    tool_name="claude",
    task="Analyze data",
    parameters={"format": "detailed"}
)
```

### MCPToolResult

Encapsulates invocation results:

```python
class MCPToolResult:
    success: bool          # Whether invocation succeeded
    result: Any           # The actual result data
    execution_time: float # Execution time in seconds
    metadata: Dict        # Additional metadata
    timestamp: datetime   # When invocation occurred
```

## State Tracking

### DaemonState Class

Each daemon has an associated `DaemonState` that tracks:

- **Summoned timestamp**: When daemon was summoned
- **Last invocation timestamp**: Most recent invocation
- **Invocation history**: List of all invocations with details
- **Total execution time**: Cumulative execution time
- **MCP registration status**: Whether registered with MCP

### Statistics

Get detailed statistics:

```python
state = daemon_registry.get_daemon_state(DaemonType.CLAUDE)
stats = state.get_statistics()

# Returns:
{
    "daemon_name": "claude",
    "is_active": True,
    "summoned_at": "2025-10-24T10:30:00",
    "last_invoked_at": "2025-10-24T10:35:00",
    "total_invocations": 5,
    "total_execution_time": 2.456,
    "average_execution_time": 0.491,
    "mcp_registered": True
}
```

## HTTP API Endpoints

### Core Spell Endpoints

#### POST `/summon`
Summon a daemon with MCP registration.

```bash
curl -X POST http://localhost:8000/summon \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'
```

#### POST `/invoke`
Invoke daemon through MCP.

```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "daemon_name": "claude",
    "task": "Analyze this code",
    "parameters": {"depth": "high"}
  }'
```

#### POST `/banish`
Banish daemon with statistics.

```bash
curl -X POST http://localhost:8000/banish \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'
```

### Query Endpoints

#### GET `/daemons`
List all daemons.

#### GET `/daemons/active`
List only active (summoned) daemons.

#### GET `/statistics`
Get comprehensive registry statistics.

```bash
curl http://localhost:8000/statistics
```

Returns:
```json
{
  "status": "divination_complete",
  "statistics": {
    "total_daemons": 3,
    "active_daemons": 2,
    "dormant_daemons": 1,
    "total_invocations": 15,
    "mcp_registered_daemons": 2,
    "daemon_statistics": {
      "claude": {...},
      "gemini": {...},
      "liquidmetal": {...}
    }
  }
}
```

#### GET `/daemon/{daemon_name}/state`
Get detailed state for specific daemon.

```bash
curl http://localhost:8000/daemon/claude/state
```

## Usage Examples

### Example 1: Basic Workflow

```python
from app.services.daemon_registry import daemon_registry
from app.models.daemon import DaemonType

# 1. Summon
daemon = daemon_registry.summon(DaemonType.CLAUDE)

# 2. Invoke
result = daemon_registry.invoke_daemon(
    name=DaemonType.CLAUDE,
    task="Explain quantum computing",
    parameters={"audience": "beginners"}
)

print(f"Execution time: {result['execution_time']}s")
print(f"Result: {result['result']}")

# 3. Banish
banish_result = daemon_registry.banish_daemon(DaemonType.CLAUDE)
print(f"Statistics: {banish_result['statistics']}")
```

### Example 2: Multiple Daemons

```python
# Summon multiple daemons
daemons = [DaemonType.CLAUDE, DaemonType.GEMINI, DaemonType.LIQUIDMETAL]

for daemon_type in daemons:
    daemon_registry.summon(daemon_type)

# Check active daemons
active = daemon_registry.get_active_daemons()
print(f"{len(active)} daemons active")

# Invoke each with specialized task
daemon_registry.invoke_daemon(DaemonType.CLAUDE, "Analyze algorithm")
daemon_registry.invoke_daemon(DaemonType.GEMINI, "Design UI")
daemon_registry.invoke_daemon(DaemonType.LIQUIDMETAL, "Transform data")

# Get statistics
stats = daemon_registry.get_registry_statistics()
print(stats)
```

### Example 3: Custom Model Registration

```python
# Register with custom model
daemon = daemon_registry.register_daemon(
    name=DaemonType.CLAUDE,
    model="claude-3-opus-20240229",
    role="Deep Analysis Specialist",
    capabilities=["deep_reasoning", "research", "analysis"]
)

# Summon (will use custom registration)
daemon_registry.summon(DaemonType.CLAUDE)
```

### Example 4: Performance Tracking

```python
# Summon daemon
daemon_registry.summon(DaemonType.GEMINI)

# Multiple invocations
for i in range(10):
    daemon_registry.invoke_daemon(
        DaemonType.GEMINI,
        f"Creative task {i}"
    )

# Get performance statistics
state = daemon_registry.get_daemon_state(DaemonType.GEMINI)
stats = state.get_statistics()

print(f"Average execution time: {stats['average_execution_time']}s")
print(f"Total time: {stats['total_execution_time']}s")

# View history
for invocation in state.invocation_history[-5:]:
    print(f"Task: {invocation['task']}")
    print(f"Time: {invocation['execution_time']}s")
```

## Running Examples

### Python Examples

```bash
# Run comprehensive Python examples
python examples/daemon_usage_example.py
```

### HTTP API Examples

```bash
# Start the server
python -m app.main

# In another terminal, run HTTP examples
python examples/http_api_example.py
```

## Best Practices

1. **Always summon before invoking**: Daemons must be summoned before use
2. **Banish when done**: Free resources by banishing unused daemons
3. **Monitor statistics**: Use state tracking to optimize performance
4. **Handle errors**: Wrap operations in try-except blocks
5. **Use appropriate models**: Choose the right daemon for each task type

## Error Handling

Common errors and how to handle them:

```python
from fastapi import HTTPException

try:
    result = daemon_registry.invoke_daemon(
        DaemonType.CLAUDE,
        "My task"
    )
except HTTPException as e:
    if e.status_code == 400:
        # Daemon not summoned
        daemon_registry.summon(DaemonType.CLAUDE)
    elif e.status_code == 404:
        # Daemon doesn't exist
        print("Invalid daemon name")
    elif e.status_code == 500:
        # MCP or invocation error
        print(f"Invocation failed: {e.detail}")
```

## Production Considerations

For production deployment:

1. **Replace mock MCP client**: Integrate actual Raindrop MCP SDK
2. **Add authentication**: Secure API endpoints
3. **Implement rate limiting**: Prevent abuse
4. **Add persistent storage**: Store invocation history
5. **Enable monitoring**: Track performance metrics
6. **Configure logging**: Use structured logging
7. **Set up error reporting**: Monitor failures

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Raindrop MCP SDK](https://github.com/raindrop-mcp) (Replace with actual link)
- Main README: `README.md`
- API Documentation: http://localhost:8000/grimoire
