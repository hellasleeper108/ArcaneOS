## 🎯 Archon Runtime Integration Guide

This guide shows you how to integrate the Archon tool-calling system into your AI application.

---

## Quick Overview

The Archon Runtime provides:
- ✅ **Permission-gated tool execution** - Every operation requires user approval
- ✅ **11 core tools** - File system, Git, HTTP, shell execution, database queries
- ✅ **Multiple UI modes** - CLI, Web UI, Auto-approve patterns
- ✅ **Raindrop MCP integration** - Session management and memory storage
- ✅ **Archon client** - Manages conversation loop with tool-calling

---

## Installation & Setup

```bash
cd archon-runtime
npm install
npm run build
```

---

## Integration Steps

### Step 1: Configure Permission Mode

Choose how users will approve tool requests:

```typescript
import { configureGatekeeper } from './archon-runtime';

// Option A: CLI mode (default) - Terminal prompts
configureGatekeeper({ mode: 'cli' });

// Option B: Web UI mode - Browser-based approval
configureGatekeeper({ mode: 'web', webServerPort: 3000 });

// Option C: Auto-approve mode (dev only)
configureGatekeeper({ mode: 'auto-approve' });

// Option D: Custom patterns
import { addAutoApprovePattern } from './archon-runtime';
addAutoApprovePattern('read', /^(src|docs)\//); // Auto-approve reading src/ and docs/
```

### Step 2: Start Web UI (Optional)

If using web mode:

```typescript
import { startWebUIServer } from './archon-runtime';

const server = startWebUIServer(3000);
console.log('Permission UI: http://localhost:3000/permissions');
```

### Step 3: Create Archon Client

```typescript
import { ArchonClient } from './archon-runtime';
import fs from 'fs';

// Load system prompt
const systemPrompt = fs.readFileSync('./SYSTEM_PROMPT.md', 'utf-8');

// Create client
const archon = new ArchonClient({
  model: 'gpt-oss:20b',
  systemPrompt,
  maxTurns: 10
});
```

### Step 4: Handle User Messages

```typescript
async function handleUserMessage(message: string) {
  try {
    // Archon automatically handles tool requests
    const response = await archon.sendMessage(message);

    console.log('Archon:', response);
  } catch (error) {
    console.error('Error:', error);
  }
}

// Example usage
await handleUserMessage("Find all TypeScript files in src/");
```

### Step 5: Optional - Add Raindrop Session Management

```typescript
import { RaindropArchonRuntime } from './archon-runtime';

// Create Raindrop-integrated runtime
const runtime = new RaindropArchonRuntime();

// Start session
const sessionId = await runtime.startSession();

// Execute tools with session tracking
const response = await runtime.executeWithSession(toolRequest, sessionId);

// Get session memory
const memory = await runtime.getSessionMemory({ key: 'archon_tools' });

// End session
await runtime.endSession(true); // true = flush to episodic storage
```

---

## Available Tools

The Archon Runtime includes 11 tools across 5 categories:

### 📁 File System (5 tools)

```typescript
// Read file
{ "name": "archon.fs.read", "args": { "path": "config.json" } }

// Write file
{ "name": "archon.fs.write", "args": { "path": "output.txt", "content": "data" } }

// Edit file (find-replace)
{ "name": "archon.fs.edit", "args": {
  "path": "app.js",
  "find": "DEBUG=false",
  "replace": "DEBUG=true"
}}

// Find files (glob)
{ "name": "archon.fs.find", "args": { "base": "src/", "pattern": "**/*.ts" } }

// Delete file/directory
{ "name": "archon.fs.delete", "args": { "path": "temp/" } }
```

### 🔧 Git (1 tool)

```typescript
// Get git status
{ "name": "archon.git.status", "args": {} }
```

### ⚡ Execution (1 tool)

```typescript
// Execute shell command (HIGH RISK)
{ "name": "archon.exec", "args": {
  "command": "npm",
  "args": ["install"],
  "cwd": "/project",
  "timeout": 60000
}}
```

### 🌐 Network (1 tool)

```typescript
// HTTP request
{ "name": "archon.http.request", "args": {
  "url": "https://api.example.com/data",
  "method": "GET",
  "headers": { "Authorization": "Bearer token" }
}}
```

### 🗄️ Database (1 tool)

```typescript
// SQL query via Raindrop SmartSQL
{ "name": "archon.db.query", "args": {
  "database_id": "analytics-db",
  "query": "SELECT * FROM users WHERE id = ?",
  "parameters": [123]
}}
```

### 🔍 Meta Tools (2 tools)

```typescript
// List all tools
{ "name": "archon.tools.list", "args": {} }

// Get help for a tool
{ "name": "archon.tools.help", "args": { "tool_id": "archon.fs.read" } }
```

---

## Permission Modes

### CLI Mode (Default)

Enhanced terminal UI with colors:

```
╔════════════════════════════════════════════════════════════════════╗
║                        🔒 PERMISSION REQUEST                       ║
╠════════════════════════════════════════════════════════════════════╣
║ Archon:   gpt-oss:20b                                              ║
║ Action:   📖 READ                                                   ║
║ Resource: src/config.ts                                            ║
╚════════════════════════════════════════════════════════════════════╝

Approve this operation? [y/N/a=always/n=never]:
```

Options:
- `y` - Approve once
- `a` - Approve and cache for session (always approve this action+resource)
- `n` - Deny and cache for session (never approve this action+resource)
- `N` - Deny once (default)

### Web UI Mode

Browser-based permission management:

```typescript
import { startWebUIServer, configureGatekeeper } from './archon-runtime';

configureGatekeeper({ mode: 'web', webServerPort: 3000 });
startWebUIServer(3000);

// Open http://localhost:3000/permissions
// See real-time permission requests
// Approve/deny with buttons
```

Features:
- Real-time updates
- Beautiful gradient UI
- Color-coded actions
- Request history

### Auto-Approve Patterns

For development or trusted operations:

```typescript
import { configureGatekeeper, addAutoApprovePattern } from './archon-runtime';

// Auto-approve reading specific directories
addAutoApprovePattern('read', /^(src|docs|tests)\//);

// Auto-approve all file searches
addAutoApprovePattern('find', /.*/);

// Auto-approve git operations
addAutoApprovePattern('git-status', /.*/);
```

---

## Raindrop MCP Integration

The Archon Runtime integrates seamlessly with Raindrop's workflow orchestration:

### Basic Integration

```typescript
import { RaindropArchonRuntime, ToolRequest } from './archon-runtime';

const runtime = new RaindropArchonRuntime();

// Start session
const sessionId = await runtime.startSession();

// Execute tools (automatically stores in memory)
const response = await runtime.executeWithSession(request, sessionId);

// Tool results are stored in session memory with key 'archon_tools'
```

### With Existing Session

```typescript
// Attach to existing Raindrop session
const runtime = new RaindropArchonRuntime({
  session_id: 'existing_session_123',
  timeline_id: 'timeline_456',
  current_state: 'processing'
});

// All tool executions update workflow state
const response = await runtime.executeWithSession(request);
```

### Memory Integration

Tool executions are automatically stored in working memory:

```json
{
  "type": "tool_request",
  "summary": "Reading configuration file",
  "tools": ["archon.fs.read"],
  "timestamp": "2025-10-25T10:30:00.000Z"
}
```

```json
{
  "type": "tool_response",
  "success": true,
  "results": [...],
  "timestamp": "2025-10-25T10:30:01.500Z"
}
```

Retrieve memory:

```typescript
const memory = await runtime.getSessionMemory({
  key: 'archon_tools',
  n_most_recent: 10
});
```

---

## Complete Example

Here's a full working example:

```typescript
import {
  ArchonClient,
  RaindropArchonRuntime,
  configureGatekeeper,
  startWebUIServer
} from './archon-runtime';
import fs from 'fs';

async function main() {
  // 1. Configure permissions
  configureGatekeeper({ mode: 'web', webServerPort: 3000 });
  const server = startWebUIServer(3000);

  // 2. Load system prompt
  const systemPrompt = fs.readFileSync('./SYSTEM_PROMPT.md', 'utf-8');

  // 3. Create Archon client
  const archon = new ArchonClient({
    model: 'gpt-oss:20b',
    systemPrompt,
    maxTurns: 10
  });

  // 4. Create Raindrop runtime
  const runtime = new RaindropArchonRuntime();
  const sessionId = await runtime.startSession();

  // 5. Handle user input
  const userMessage = "Find all TypeScript files and show me the first one";

  console.log('User:', userMessage);
  const response = await archon.sendMessage(userMessage);
  console.log('Archon:', response);

  // 6. Get session memory
  const memory = await runtime.getSessionMemory({ key: 'archon_tools' });
  console.log(`Session has ${memory.length} tool executions`);

  // 7. Cleanup
  await runtime.endSession(true);
  server.close();
}

main();
```

---

## Security Best Practices

1. **Never use auto-approve in production** - Always require user permission
2. **Validate tool arguments** - Check paths, URLs, commands before execution
3. **Use timeouts** - All async operations have default 30s timeout
4. **Audit trail** - All executions are logged via `getExecutionLog()`
5. **Path validation** - File system tools validate paths to prevent traversal
6. **High-risk warnings** - Shell execution shows explicit warnings

---

## Customization

### Adding New Tools

1. Create tool module:

```typescript
// core/custom/myTool.ts
import { requestPermission } from '../../permissions/enhanced-gatekeeper';

export async function myTool(args: MyArgs): Promise<MyResult> {
  const allowed = await requestPermission('my-action', args.resource);
  if (!allowed) {
    return { success: false, error: 'Permission denied' };
  }

  // Tool implementation
  return { success: true, data: result };
}
```

2. Register in `tools/registry.ts`:

```typescript
import { myTool } from '../core/custom/myTool';

export const toolRegistry: ToolRegistry = {
  // ... existing tools
  'archon.custom.myTool': myTool
};
```

3. Add help documentation:

```typescript
const helpDocs: Record<string, string> = {
  // ... existing docs
  'archon.custom.myTool': `
archon.custom.myTool(args...)
  Description of your tool.

  Args: ...
  Returns: ...
  Example: ...
`
};
```

### Custom Permission UI

Replace the gatekeeper with your own:

```typescript
// permissions/custom-gatekeeper.ts
export async function requestPermission(
  action: string,
  resource: string
): Promise<boolean> {
  // Your custom implementation
  // Could be: Slack bot, Discord bot, mobile app, etc.
  return await myCustomApprovalSystem({ action, resource });
}
```

---

## Troubleshooting

### "Unknown tool" error

Make sure you're using the exact tool name:
- ✅ `archon.fs.read`
- ❌ `read` or `fs.read`

### Permission denied

User denied permission or auto-deny pattern matched. Clear cache:

```typescript
import { clearPermissionCache } from './archon-runtime';
clearPermissionCache();
```

### TypeScript errors

Rebuild the project:

```bash
npm run build
```

### Web UI not loading

Check if port is available and server started:

```typescript
const server = startWebUIServer(3000);
console.log('Server:', server.listening); // should be true
```

---

## Next Steps

1. ✅ Read [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md) - Full system prompt for Archon
2. ✅ Run examples: `npx ts-node examples/full-integration.ts --all`
3. ✅ Explore [archon_tools_manifest.md](../archon_tools_manifest.md) - Protocol spec
4. ✅ Customize permissions in `permissions/enhanced-gatekeeper.ts`
5. ✅ Add custom tools in `core/` directory

---

## Support

- Documentation: See README.md and QUICKSTART.md
- Examples: Check `examples/` directory
- Issues: File on GitHub

---

**Built with security and user control in mind** 🔒✨
