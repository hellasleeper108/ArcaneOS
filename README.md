# ArcaneOS + Archon Tool Runtime

> A fantasy-themed FastAPI backend with permission-gated AI tool execution, mystical daemon management, and real-time event broadcasting.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**[GitHub Repository](https://github.com/hellasleeper108/ArcaneOS)** • **[Documentation](#documentation)** • **[Quick Start](#quick-start)**

---

## Overview

**ArcaneOS + Archon** is a complete AI agent infrastructure combining:

1. **ArcaneOS Backend** (Python/FastAPI) - Fantasy-themed daemon management system with natural language spell parsing, safe code execution, and real-time event broadcasting
2. **Archon Tool Runtime** (TypeScript) - Permission-gated tool execution layer with 11 core tools (fs, git, exec, http, db) and multi-mode UI (CLI, Web, Auto-approve)
3. **Frontend** (React + TailwindCSS) - Real-time UI with daemon visualization, event feeds, and permission management

**Key Features:**
- **Permission Gating** - Every AI tool operation requires user approval
- **Multi-Mode UI** - Choose CLI prompts, web browser UI, or auto-approve patterns
- **Fantasy Theme** - Mystical terminology: daemons, spells, summon/invoke/banish
- **Real-Time Events** - WebSocket-based event broadcasting across all components
- **Safe Execution** - Subprocess isolation, timeout enforcement, permission gates
- **Session Persistence** - State, history, and permissions persist across restarts
- **Raindrop MCP Integration** - Compatible with Raindrop orchestration framework

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Quick Start](#quick-start)
  - [Backend Setup](#backend-setup-python)
  - [Archon Runtime Setup](#archon-runtime-setup-typescript)
  - [Frontend Setup](#frontend-setup-react)
- [Features](#features)
  - [ArcaneOS Backend](#arcaneos-backend-features)
  - [Archon Tool Runtime](#archon-tool-runtime-features)
  - [Frontend](#frontend-features)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Documentation](#documentation)
- [Recent Updates](#recent-updates)
- [Development](#development)
- [License](#license)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      React Frontend (Port 3000)                 │
│              Real-time UI + Permission Management               │
└────────────────────────┬────────────────────────────────────────┘
                         │ WebSocket + REST
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 ArcaneOS Backend (Port 8000)                    │
│  FastAPI • Daemon Registry • Event Bus • Grimoire • VibeCompiler│
└────────────────────────┬────────────────────────────────────────┘
                         │ Raindrop MCP
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Archon Tool Runtime (TypeScript)                │
│  11 Tools • Permission Gates • CLI/Web UI • Auto-approve        │
└─────────────────────────────────────────────────────────────────┘

Three-Layer Architecture:
1. Core Layer (core/) - Minimal dependencies: event_bus, vibecompiler, veil
2. Application Layer (app/) - FastAPI routers, services, models
3. Tool Layer (archon-runtime/) - Permission-gated AI tool execution
```

---

## Quick Start

### Backend Setup (Python)

```bash
# Navigate to project directory
cd vibejam

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m app.main
# Server runs at http://localhost:8000
```

**Verify Installation:**
```bash
# API Documentation
open http://localhost:8000/grimoire      # Swagger UI
open http://localhost:8000/arcane-docs   # ReDoc

# Test endpoint
curl http://localhost:8000/daemons
```

### Archon Runtime Setup (TypeScript)

```bash
# Navigate to Archon directory
cd archon-runtime

# Install dependencies
npm install

# Build the runtime
npm run build

# Run examples
npm run demo
```

**Configure Permission Mode:**
```typescript
import { configureGatekeeper } from './permissions/enhanced-gatekeeper';

// CLI mode (default) - prompt in terminal
configureGatekeeper({ mode: 'cli' });

// Web mode - browser-based UI
configureGatekeeper({ mode: 'web', webServerPort: 3001 });

// Auto-approve mode (development only)
configureGatekeeper({ mode: 'auto-approve' });
```

### Frontend Setup (React)

```bash
# Navigate to UI directory
cd ArcaneOS/ui

# Install dependencies
npm install

# Start development server
npm start
# Frontend runs at http://localhost:3000
```

**Build for Production:**
```bash
npm run build
# Output in ArcaneOS/ui/build/
```

---

## Features

### ArcaneOS Backend Features

#### Mystical Daemons
Manage AI entities with fantasy-themed lifecycle operations:
- **Claude** - Keeper of Logic and Reason (Purple Aether)
- **Gemini** - Weaver of Dreams and Innovation (Golden Amber)
- **LiquidMetal** - Master of Transformation and Flow (Liquid Cyan)

```bash
# Summon a daemon
curl -X POST http://localhost:8000/summon \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'

# Invoke daemon with task
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude", "task": "Analyze quantum patterns"}'

# Banish daemon
curl -X POST http://localhost:8000/banish \
  -H "Content-Type: application/json" \
  -d '{"daemon_name": "claude"}'
```

#### Natural Language Spell Parser
Write spells in plain English instead of JSON:

```bash
curl -X POST http://localhost:8000/spell/cast \
  -H "Content-Type: application/json" \
  -d '{"spell_text": "summon gemini and make him write a haiku"}'
```

**Supported Patterns:**
- "summon claude"
- "invoke gemini to generate ideas"
- "banish liquidmetal"
- "show me all daemons"
- "make claude analyze the data"

See `/spell/examples` for 50+ patterns.

#### VibeCompiler - Safe Code Execution
Execute Python snippets safely with ceremonial logging:

```python
from core.vibecompiler import VibeCompiler

compiler = VibeCompiler()
result = compiler.run_snippet("print('Hello, mystical realm!')", timeout=3)
# Output: {"stdout": "Hello, mystical realm!\n", "stderr": "", "duration": 0.005}
```

**Features:**
- Subprocess isolation (no shell, no network)
- Timeout enforcement (default: 3 seconds)
- Ceremonial logging: "Runes align...", "Mana stabilizing..."
- Multi-language support: Python, JavaScript, Bash, Ruby, Go, Rust

#### WebSocket Event Bus
Channel-based real-time event broadcasting:

```python
from core.event_bus import get_event_bus

bus = get_event_bus()

# Subscribe to channel
await bus.subscribe("spell", websocket)

# Emit events
await bus.emit("spell", {"action": "summon", "daemon": "claude"})

# Unsubscribe
await bus.unsubscribe("spell", websocket)
```

**WebSocket Endpoints:**
- `ws://localhost:8000/ws/events` - Legacy daemon events
- `ws://localhost:8000/ws/events/{channel}` - Channel-based events
- `GET /channels` - List active channels

#### The Grimoire - Spell History
Persistent spell history with session continuity:

```bash
# Record spell
curl -X POST http://localhost:8000/grimoire/record \
  -d '{"spell_type": "summon", "daemon": "claude", "success": true}'

# Recall recent spells
curl http://localhost:8000/grimoire/recall?limit=10

# Search spells
curl -X POST http://localhost:8000/grimoire/search \
  -d '{"query": "claude"}'

# Get statistics
curl http://localhost:8000/grimoire/statistics
```

**Features:**
- Dual storage: `grimoire_spells.jsonl` + `arcane_log.txt`
- Filter by spell type, daemon, success status
- Full-text search
- Automatic recording of daemon operations

#### Reality Veil - Fantasy/Developer Mode
Toggle between fantasy-themed and developer modes:

```bash
# Check current mode
curl http://localhost:8000/veil
# Response: {"veil": true, "mode": "fantasy"}

# Switch to developer mode
curl -X POST http://localhost:8000/reveal

# Restore fantasy mode
curl -X POST http://localhost:8000/veil/restore
```

**Features:**
- Persistent state in `.veil_state.json`
- Global thread-safe access
- Ceremonial logging on state changes

---

### Archon Tool Runtime Features

#### 11 Permission-Gated Tools

**File System:**
- `read` - Read file contents with encoding support
- `write` - Write/create files with overwrite protection
- `edit` - Safe file editing with backup
- `find` - Recursive file/directory search with glob patterns
- `delete` - Safe deletion with confirmation

**Code & Execution:**
- `git-status` - Git repository status and changes
- `exec` - Execute shell commands with timeout and sandboxing

**Network & Data:**
- `http` - HTTP/HTTPS requests (GET, POST, PUT, DELETE)
- `db-query` - SQL database queries with prepared statements
- `db-schema` - Database schema inspection

**System:**
- `env-get` - Read environment variables

#### Multi-Mode Permission System

**CLI Mode** (Default):
```
╔════════════════════════════════════════════════════════════════╗
║                   🔒 PERMISSION REQUEST                        ║
╠════════════════════════════════════════════════════════════════╣
║ Archon:   claude-archon                                        ║
║ Action:   📖 READ                                              ║
║ Resource: /home/user/project/config.json                       ║
╚════════════════════════════════════════════════════════════════╝

Approve this operation? [y/N/a=always/n=never]:
```

**Web Mode:**
```typescript
configureGatekeeper({ mode: 'web', webServerPort: 3001 });
// Opens browser UI at http://localhost:3001/permissions
```

**Auto-Approve Patterns:**
```typescript
import { addAutoApprovePattern } from './permissions/enhanced-gatekeeper';

// Auto-approve reading package.json
addAutoApprovePattern('read', /package\.json$/);

// Auto-approve all git operations
addAutoApprovePattern('exec', /^git /);
```

#### Archon Client - Conversation Management

```typescript
import { ArchonClient } from './client/archon-client';

const archon = new ArchonClient({
  name: 'claude-archon',
  apiKey: 'your-raindrop-api-key',
  permissionMode: 'cli'
});

// Execute tools with automatic permission gating
const response = await archon.executeTools([
  { tool: 'read', arguments: { path: './config.json' } },
  { tool: 'exec', arguments: { command: 'git status' } }
]);
```

#### Raindrop MCP Integration

```typescript
import { RaindropIntegration } from './core/raindrop-integration';

const integration = new RaindropIntegration({
  sessionId: 'session-123',
  archonName: 'claude-archon'
});

await integration.registerTools();  // Register all 11 tools with Raindrop
const result = await integration.routeToolCall(toolRequest);
```

---

### Frontend Features

- **10 React Components** with TailwindCSS styling
- **Real-time Daemon Visualization** - See daemon status, invocations, metadata
- **Event Feed** - Live WebSocket event stream with animations
- **Permission UI** - Web-based permission approval interface
- **Relic System** - Interactive relics with visual effects
- **Responsive Design** - Mobile and desktop support
- **Dark Mode** - Fantasy-themed color palette

**Key Components:**
- `DaemonCard.tsx` - Daemon status visualization
- `EventFeed.tsx` - Real-time event stream
- `RelicVisuals.tsx` - Interactive relic animations
- `PermissionGate.tsx` - Web-based permission UI

---

## API Documentation

Once the server is running:

- **Swagger UI:** http://localhost:8000/grimoire
- **ReDoc:** http://localhost:8000/arcane-docs

### Core Endpoints

```
GET    /daemons                    - List all daemons
POST   /summon                     - Summon daemon
POST   /invoke                     - Invoke daemon with task
POST   /banish                     - Banish daemon

POST   /spell/parse                - Parse natural language spell
POST   /spell/cast                 - Parse and execute spell
GET    /spell/examples             - List all supported patterns

GET    /grimoire/recall            - Get spell history
POST   /grimoire/record            - Record new spell
POST   /grimoire/search            - Search spells
GET    /grimoire/statistics        - Get spell stats
DELETE /grimoire/purge             - Archive old spells

GET    /veil                       - Get reality veil state
POST   /veil                       - Set reality veil state
POST   /reveal                     - Switch to developer mode
POST   /veil/restore               - Restore fantasy mode

GET    /channels                   - List WebSocket channels
WS     /ws/events                  - Legacy event stream
WS     /ws/events/{channel}        - Channel-based events
```

---

## Testing

### Backend Tests (Python)

```bash
# Activate environment
source venv/bin/activate

# Run all tests (30 tests)
pytest -v

# Run specific test suites
pytest tests/test_vibecompiler.py -v    # Safe execution (5 tests)
pytest tests/test_ws.py -v              # WebSocket events (4 tests)
pytest tests/test_veil.py -v            # Reality veil (4 tests)
pytest test_spell_parser.py -v          # Spell parser (10 tests)
pytest test_registry.py -v              # Daemon lifecycle (7 tests)

# Run with coverage
pytest --cov=core --cov=app --cov-report=html

# Clean state before tests
rm -f .veil_state.json grimoire_spells.jsonl && pytest -v
```

### Archon Runtime Tests (TypeScript)

```bash
cd archon-runtime

# Run all tests
npm test

# Run specific test suites
npm test -- tools/fs
npm test -- permissions

# Run with coverage
npm run test:coverage
```

### Frontend Tests (React)

```bash
cd ArcaneOS/ui

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

### Integration Testing

```bash
# 1. Start backend
python -m app.main

# 2. Run WebSocket client
python examples/websocket_client.py

# 3. Trigger events
curl -X POST http://localhost:8000/summon -d '{"daemon_name": "claude"}'

# 4. Watch events in real-time!
```

---

## Documentation

### Backend Documentation (ArcaneOS)
- **[VibeCompiler](docs/VIBECOMPILER.md)** - Safe Python execution with timeout enforcement
- **[Event Bus](docs/EVENT_BUS.md)** - Channel-based WebSocket broadcasting
- **[Reality Veil](docs/REALITY_VEIL.md)** - Fantasy/developer mode toggle
- **[The Grimoire](docs/GRIMOIRE.md)** - Spell history and persistence
- **[WebSocket Clients](examples/README.md)** - Client examples (Python, JavaScript, HTML)
- **[CLAUDE.md](CLAUDE.md)** - Project overview and development guide

### Archon Runtime Documentation
- **[README](archon-runtime/README.md)** - Overview and architecture
- **[Quick Start](archon-runtime/docs/QUICKSTART.md)** - Getting started guide
- **[Integration Guide](archon-runtime/docs/INTEGRATION_GUIDE.md)** - Raindrop MCP integration
- **[System Prompt](archon-runtime/docs/SYSTEM_PROMPT.md)** - AI agent configuration
- **[Tool Manifest](archon-runtime/docs/archon_tools_manifest.md)** - Complete tool specification

### Additional Documentation
- **[CLEANUP_STATUS.md](CLEANUP_STATUS.md)** - Codebase cleanup report (217 lines removed)
- **[GITHUB_READY.md](GITHUB_READY.md)** - GitHub repository setup guide

---

## Project Structure

```
vibejam/
├── app/                                # FastAPI application layer
│   ├── main.py                         # Entry point
│   ├── config.py                       # Configuration
│   ├── models/                         # Pydantic models
│   │   ├── daemon.py                   # Daemon models
│   │   ├── compilation.py              # Code execution models
│   │   ├── grimoire.py                 # Spell history models
│   │   └── veil.py                     # Veil state models
│   ├── routers/                        # API endpoints
│   │   ├── spells.py                   # Daemon operations
│   │   ├── spell_parser_routes.py      # Natural language parser
│   │   ├── websocket_routes.py         # WebSocket events
│   │   ├── compilation_routes.py       # Code execution
│   │   ├── grimoire_routes.py          # Spell history
│   │   ├── event_bus_routes.py         # Channel events
│   │   └── veil_routes.py              # Reality veil
│   └── services/                       # Business logic
│       ├── daemon_registry.py          # Daemon management
│       ├── spell_parser.py             # NL spell parser
│       ├── arcane_event_bus.py         # Event dispatcher
│       ├── grimoire.py                 # Spell history
│       └── raindrop_client.py          # Raindrop MCP client
├── core/                               # Core layer (minimal dependencies)
│   ├── vibecompiler.py                 # Safe code execution
│   ├── event_bus.py                    # WebSocket broadcasting
│   └── veil.py                         # State management
├── ArcaneOS/                           # Enhanced ArcaneOS layer
│   ├── core/                           # Core modules
│   │   ├── archon_router.py            # Archon routing
│   │   ├── event_bus.py                # Event system
│   │   ├── grimoire.py                 # Constants
│   │   ├── safety.py                   # Safety checks
│   │   └── veil.py                     # Veil management
│   └── ui/                             # React frontend
│       ├── src/
│       │   ├── components/             # React components (10)
│       │   ├── App.tsx                 # Main app
│       │   └── index.tsx               # Entry point
│       ├── public/                     # Static assets
│       └── package.json                # Dependencies
├── archon-runtime/                     # TypeScript tool runtime
│   ├── core/
│   │   ├── types.ts                    # Core types
│   │   ├── dispatcher.ts               # Tool dispatcher
│   │   ├── raindrop-integration.ts     # MCP integration
│   │   ├── fs/                         # File system tools (5)
│   │   ├── code/                       # Code tools (2)
│   │   ├── network/                    # Network tools (2)
│   │   ├── data/                       # Data tools (2)
│   │   └── system/                     # System tools (1)
│   ├── permissions/
│   │   └── enhanced-gatekeeper.ts      # Multi-mode permissions
│   ├── client/
│   │   └── archon-client.ts            # Conversation manager
│   ├── server/
│   │   └── permission-server.ts        # Web UI server
│   └── docs/                           # Documentation (5 files)
├── tests/                              # Test suite
│   ├── test_vibecompiler.py            # VibeCompiler tests (5)
│   ├── test_ws.py                      # WebSocket tests (4)
│   ├── test_veil.py                    # Veil tests (4)
│   ├── test_spell_parser.py            # Parser tests (10)
│   └── test_registry.py                # Registry tests (7)
├── examples/                           # Client examples
│   ├── websocket_client.py             # Python WS client
│   ├── websocket_client.html           # HTML/JS client
│   └── vibe_compiler_example.py        # Compiler demo
├── docs/                               # Documentation (4 files)
│   ├── VIBECOMPILER.md
│   ├── EVENT_BUS.md
│   ├── REALITY_VEIL.md
│   └── GRIMOIRE.md
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git exclusions
├── CLAUDE.md                           # Project instructions
├── CLEANUP_STATUS.md                   # Cleanup report
├── GITHUB_READY.md                     # GitHub guide
└── README.md                           # This file
```

**File Counts:**
- Python files: ~50
- TypeScript files: ~30
- React components: ~15
- Documentation: ~25
- Test files: ~8
- **Total committed: 161 files (26,469 lines)**

---

## Recent Updates

### 2025-10-25: Major Cleanup & GitHub Push

**Codebase Cleanup (Phase 1 Complete):**
- Deleted 3 orphaned/duplicate files (189 lines removed)
- Reduced 1 file to minimal stub (28 lines saved)
- **Total: 217 lines removed** with zero functionality impact
- Created `CLEANUP_STATUS.md` documenting all changes

**GitHub Repository:**
- Initialized git repository
- Created comprehensive `.gitignore` (Python, Node.js, TypeScript, state files)
- Committed 161 files with 26,469 lines
- Pushed to [github.com/hellasleeper108/ArcaneOS](https://github.com/hellasleeper108/ArcaneOS)

**Archon Runtime:**
- Built complete TypeScript tool execution system
- Implemented 11 permission-gated tools
- Created multi-mode permission system (CLI, Web, Auto-approve)
- Integrated with Raindrop MCP framework
- Comprehensive documentation (5 docs)

**Frontend:**
- Fixed TypeScript compilation errors in `RelicVisuals.tsx`
- Built production-ready React app with TailwindCSS
- 10 components with real-time event integration

---

## Development

### Adding New Daemons

1. Add enum to `app/models/daemon.py`:
```python
class DaemonType(str, Enum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    LIQUIDMETAL = "liquidmetal"
    YOUR_NEW_DAEMON = "your_new_daemon"  # Add here
```

2. Add configuration in `app/services/daemon_registry.py`:
```python
def _initialize_daemons(self):
    self._daemons["your_new_daemon"] = Daemon(
        name="your_new_daemon",
        role=DaemonRole.YOUR_ROLE,
        color_code="#HEX",
        metadata={"element": "Fire", "domain": "Destruction"}
    )
```

3. Update fantasy messages in `app/routers/spells.py`
4. Add aliases to spell parser in `app/services/spell_parser.py`

### Adding Archon Tools

1. Create tool in `archon-runtime/core/{category}/{tool}.ts`:
```typescript
import { requestPermission } from '../../permissions/enhanced-gatekeeper';

export async function myTool(args: MyArgs): Promise<MyResult> {
  const allowed = await requestPermission('action', args.resource);
  if (!allowed) {
    return { success: false, error: 'Permission denied' };
  }
  // Tool implementation
  return { success: true, data: result };
}
```

2. Register in `archon-runtime/core/dispatcher.ts`:
```typescript
case 'my-tool':
  return await myTool(call.arguments);
```

3. Add manifest entry in `archon_tools_manifest.md`

### Environment Configuration

Create `.env` file:
```env
# Backend
DEBUG_MODE=true
HOST=0.0.0.0
PORT=8000
RAINDROP_ENABLED=true
MAX_CONCURRENT_DAEMONS=3
VOICE_CACHE_DIR=arcane_audio

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Archon
PERMISSION_MODE=cli
PERMISSION_TIMEOUT=30000
WEB_UI_PORT=3001
```

### Code Quality

```bash
# Python linting
flake8 app/ core/
black app/ core/

# TypeScript linting
cd archon-runtime && npm run lint
npm run format

# Type checking
mypy app/ core/
cd archon-runtime && npm run type-check
```

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

See [GITHUB_READY.md](GITHUB_READY.md) for repository guidelines.

---

## Technology Stack

**Backend:**
- FastAPI 0.100+ (async Python web framework)
- Pydantic (data validation)
- WebSockets (real-time events)
- Raindrop MCP SDK (AI orchestration)

**Archon Runtime:**
- TypeScript 5.0+
- Node.js (async runtime)
- Readline (CLI interactions)
- Express (web UI server)

**Frontend:**
- React 18+ (UI framework)
- TailwindCSS (styling)
- WebSocket client (real-time updates)

**Development:**
- pytest (Python testing)
- Jest (TypeScript testing)
- React Testing Library (component testing)

---

## License

This project is for educational and entertainment purposes. See [LICENSE](LICENSE) for details.

---

## Credits

Built with FastAPI, TypeScript, React, and mystical energies from the ethereal realm.

**Special thanks to:**
- FastAPI framework
- Raindrop MCP SDK
- Claude Code (for development assistance)
- The open source community

---

## Support

**Issues & Questions:**
- GitHub Issues: [github.com/hellasleeper108/ArcaneOS/issues](https://github.com/hellasleeper108/ArcaneOS/issues)
- Documentation: [See docs/](#documentation)

**Quick Links:**
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Testing Guide](#testing)
- [Development Guide](#development)

---

**May your daemons be swift, your spells be powerful, and your permissions be granted!** ✨

*Generated with Claude Code • 2025-10-25*
