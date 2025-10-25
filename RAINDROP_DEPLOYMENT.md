# ArcaneOS Raindrop Deployment Guide

## Overview

This guide explains how to deploy the ArcaneOS backend to the Raindrop platform with full MCP integration for daemon management and AI model routing.

## Prerequisites

- Raindrop CLI installed and authenticated
- Python 3.11+ environment
- All dependencies installed (`pip install -r requirements.txt`)

## Project Structure

```
vibejam/
├── app/                          # FastAPI application
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Configuration
│   ├── models/daemon.py          # Daemon models
│   ├── routers/spells.py         # API endpoints
│   └── services/
│       ├── daemon_registry.py     # Enhanced registry with MCP
│       └── raindrop_client.py     # Raindrop MCP client wrapper
├── raindrop.manifest             # Raindrop deployment configuration
├── requirements.txt              # Python dependencies
└── package.json                  # Node.js/Raindrop framework deps
```

## Raindrop Manifest Configuration

The `raindrop.manifest` file defines how ArcaneOS deploys to Raindrop:

```hcl
application "arcaneos" {
  service "api" {
    # Service configuration
  }
}
```

## Deployment Steps

### 1. Initialize Raindrop Project

```bash
raindrop build init .
```

This creates:
- `raindrop.manifest` - Deployment configuration
- `package.json` - Node.js dependencies for Raindrop framework
- `src/_app/` - Raindrop framework files (TypeScript)

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Raindrop framework dependencies
npm install
```

### 3. Configure Environment Variables

Create `.env` file:

```env
APP_NAME=ArcaneOS
APP_VERSION=1.0.0
DEBUG_MODE=false
RAINDROP_ENABLED=true
MAX_CONCURRENT_DAEMONS=3
```

### 4. Validate Configuration

```bash
raindrop build validate
```

### 5. Deploy to Raindrop

```bash
raindrop build deploy
```

## Raindrop MCP Integration

### Architecture

The ArcaneOS backend integrates with Raindrop's MCP (Model Context Protocol) for intelligent daemon routing:

```
Client Request → FastAPI → DaemonRegistry → RaindropMCPClient → AI Models
```

### Daemon-to-Model Mapping

| Daemon | Model | Provider |
|--------|-------|----------|
| Claude | claude-3-5-sonnet-20241022 | Anthropic |
| Gemini | gemini-2.0-flash-exp | Google |
| LiquidMetal | liquidmetal-adaptive-v1 | Raindrop Custom |

### MCP Client Configuration

The `RaindropMCPClient` in `app/services/raindrop_client.py` handles:

1. **Tool Registration**: Each daemon is registered as an MCP tool
2. **Model Routing**: Invocations route to appropriate AI models
3. **Result Tracking**: Execution time and metadata tracking

## API Endpoints

Once deployed, ArcaneOS exposes the following endpoints:

### Core Spells

- `POST /summon` - Summon a daemon (auto-registers with MCP)
- `POST /invoke` - Invoke daemon through MCP
- `POST /banish` - Banish daemon with statistics

### Query Endpoints

- `GET /daemons` - List all daemons
- `GET /daemons/active` - List active daemons
- `GET /statistics` - Registry statistics
- `GET /daemon/{name}/state` - Daemon state details

### Documentation

- `GET /grimoire` - Swagger UI
- `GET /arcane-docs` - ReDoc documentation
- `GET /health` - Health check

## Production Configuration

### Scaling

Configure in `raindrop.manifest`:

```hcl
service "api" {
  scaling {
    min_instances = 1
    max_instances = 5
    target_cpu = 70
  }
}
```

### Monitoring

Raindrop provides built-in monitoring:

```bash
# View logs
raindrop logs tail arcaneos

# Check status
raindrop build status arcaneos
```

### Environment Management

Use Raindrop's environment management:

```bash
# Set environment variable
raindrop build env set APP_NAME=ArcaneOS

# Get environment variable
raindrop build env get APP_NAME
```

## Testing Deployment

### 1. Local Testing

```bash
# Start locally
source venv/bin/activate
python -m app.main

# Test endpoints
curl http://localhost:8000/health
```

### 2. Deploy to Raindrop

```bash
raindrop build deploy
```

### 3. Test Deployed Service

```bash
# Get deployment URL
raindrop build status arcaneos

# Test health endpoint
curl https://your-app.raindrop.run/health

# Summon daemon
curl -X POST https://your-app.raindrop.run/summon \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'
```

## MCP Integration Details

### Real Raindrop SDK Integration

To use the actual Raindrop MCP SDK (when available), update `app/services/raindrop_client.py`:

```python
# Replace mock implementation with:
from raindrop_mcp import RaindropClient

class RaindropMCPClient:
    def __init__(self, api_key=None, timeout=30):
        self.client = RaindropClient(
            api_key=api_key or os.getenv("RAINDROP_API_KEY"),
            timeout=timeout
        )

    def invoke_tool(self, tool_name, task, parameters=None):
        # Use real SDK
        return self.client.invoke(
            tool=tool_name,
            prompt=task,
            params=parameters
        )
```

### Model Configuration

Models are configured in `daemon_registry.py`:

```python
MODEL_MAPPINGS = {
    DaemonType.CLAUDE: {
        "model": "claude-3-5-sonnet-20241022",
        "provider": ModelProvider.ANTHROPIC,
        "capabilities": ["reasoning", "analysis", "code_generation"]
    },
    # ... other daemons
}
```

## Troubleshooting

### Common Issues

**1. TypeScript Errors**

If you see TypeScript errors during validation, they're from the Raindrop framework boilerplate. The Python app doesn't need them:

```bash
# Remove TypeScript src if not needed
rm -rf src/
```

**2. Module Not Found**

Ensure all Python dependencies are installed:

```bash
pip install -r requirements.txt
```

**3. Raindrop Auth Issues**

Re-authenticate:

```bash
raindrop auth login
```

**4. Deployment Fails**

Check logs:

```bash
raindrop logs tail arcaneos
```

## Advanced Features

### Custom Daemon Registration

You can register custom daemons programmatically:

```python
from app.services.daemon_registry import daemon_registry
from app.models.daemon import DaemonType

daemon_registry.register_daemon(
    name=DaemonType.CLAUDE,
    model="claude-3-opus-20240229",  # Custom model
    role="Deep Analysis Specialist",
    capabilities=["deep_reasoning", "research"]
)
```

### Monitoring Daemon Performance

```python
# Get statistics
stats = daemon_registry.get_registry_statistics()

print(f"Total invocations: {stats['total_invocations']}")
print(f"Active daemons: {stats['active_daemons']}")
```

## Security Considerations

1. **API Keys**: Store in Raindrop environment variables
2. **Authentication**: Add authentication middleware for production
3. **Rate Limiting**: Configure in `raindrop.manifest`
4. **CORS**: Configure allowed origins in `app/main.py`

## Next Steps

1. Deploy to Raindrop production environment
2. Configure custom domain
3. Set up monitoring and alerts
4. Implement authentication
5. Add rate limiting
6. Configure auto-scaling

## Support

- Raindrop Documentation: https://docs.raindrop.run
- ArcaneOS Repository: See README.md and REGISTRY_GUIDE.md
- Report Issues: Contact your Raindrop administrator

---

The mystical realm of ArcaneOS awaits deployment to the Raindrop cloud!
