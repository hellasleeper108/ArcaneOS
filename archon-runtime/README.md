# Archon Runtime

> Permission-gated tool execution system for AI agents

## Overview

Archon Runtime provides a secure, permission-gated interface for AI agents to perform file system operations. Every operation requires explicit user approval, ensuring human oversight over all automated actions.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      ARCHON AI                          │
│  (Requests tools via JSON, never executes directly)     │
└─────────────────────┬───────────────────────────────────┘
                      │ Tool Request (JSON)
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    DISPATCHER                           │
│  • Validates requests                                   │
│  • Routes to tools                                      │
│  • Logs execution                                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               PERMISSION GATEKEEPER                     │
│  • Prompts user for consent                             │
│  • Manages permission cache                             │
│  • Returns approve/deny                                 │
└─────────────────────┬───────────────────────────────────┘
                      │ If approved
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   TOOL MODULES                          │
│  • archon.fs.read      • archon.fs.find                 │
│  • archon.fs.write     • archon.fs.delete               │
│  • archon.fs.edit      • archon.tools.*                 │
└─────────────────────┬───────────────────────────────────┘
                      │ Results
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    USER / ARCHON                        │
│  (Receives results, Archon continues workflow)          │
└─────────────────────────────────────────────────────────┘
```

## Installation

```bash
cd archon-runtime
npm install
npm run build
```

## Usage

### Basic Example

```typescript
import { executeTools, ToolRequest } from './archon-runtime';

// Archon submits this request
const request: ToolRequest = {
  phase: "EXECUTE",
  intent: "tool_call",
  summary: "Read configuration file",
  tools: [
    {
      name: "archon.fs.read",
      args: { path: "config/settings.json" }
    }
  ],
  requires_permission: true
};

// Runtime executes (with user permission)
const response = await executeTools(request);

if (response.success) {
  console.log("Results:", response.results);
} else {
  console.error("Error:", response.message);
}
```

### Permission Flow

```typescript
import { requestPermission } from './archon-runtime';

// Called internally by each tool
const allowed = await requestPermission('read', 'src/main.ts', 'archon-gpt');

if (!allowed) {
  return { success: false, error: 'Permission denied' };
}

// Proceed with operation...
```

### Complete Integration Example

```typescript
import { executeTools, formatResponse } from './archon-runtime';

async function runArchonWorkflow() {
  // Step 1: Archon wants to find TypeScript files
  const findRequest = {
    phase: "EXECUTE" as const,
    intent: "tool_call" as const,
    summary: "Finding all TypeScript files in src/",
    tools: [
      {
        name: "archon.fs.find",
        args: { base: "src/", pattern: "**/*.ts" }
      }
    ],
    requires_permission: true
  };

  const findResponse = await executeTools(findRequest);
  console.log(formatResponse(findResponse));

  if (!findResponse.success || !findResponse.results) {
    return;
  }

  // Extract file list from results
  const files = findResponse.results[0].result.files;

  // Step 2: Read the first file
  if (files && files.length > 0) {
    const readRequest = {
      phase: "EXECUTE" as const,
      intent: "tool_call" as const,
      summary: `Reading ${files[0]}`,
      tools: [
        {
          name: "archon.fs.read",
          args: { path: `src/${files[0]}` }
        }
      ],
      requires_permission: true
    };

    const readResponse = await executeTools(readRequest);
    console.log(formatResponse(readResponse));
  }
}

runArchonWorkflow();
```

## Available Tools

| Tool | Description | Permission Required |
|------|-------------|---------------------|
| `archon.fs.read` | Read file contents | Yes |
| `archon.fs.write` | Create/overwrite file | Yes |
| `archon.fs.edit` | Apply find-replace patch | Yes |
| `archon.fs.find` | Search for files (glob) | Yes |
| `archon.fs.delete` | Delete file/directory | Yes |
| `archon.tools.list` | List available tools | No |
| `archon.tools.help` | Get tool documentation | No |

See [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md) for detailed tool documentation.

## Security Features

### 1. Permission Gating
Every file operation prompts the user:

```
============================================================
🔒 PERMISSION REQUEST
============================================================
Archon: gpt-oss:20b
Action: READ
Resource: src/config.ts
============================================================
Approve this operation? [y/N]:
```

### 2. Path Validation
All paths are resolved and validated to prevent directory traversal attacks.

### 3. Execution Logging
All tool executions are logged with timestamps:

```typescript
import { getExecutionLog } from './archon-runtime';

const log = getExecutionLog();
console.log(log);
```

### 4. Permission Caching
Once approved, permissions are cached for the session:

```typescript
import { clearPermissionCache, setAutoApprove } from './archon-runtime';

// Clear cache to require fresh permissions
clearPermissionCache();

// Auto-approve specific operations (use with caution!)
setAutoApprove('read', 'src/config.ts');
```

## Integration with Raindrop

The Archon Runtime is designed to integrate seamlessly with Raindrop's orchestration layer:

```typescript
import { executeTools } from './archon-runtime';
import { updateState, putMemory } from 'raindrop-mcp';

async function raindropWorkflow(sessionId: string, timelineId: string) {
  // Archon requests tools
  const request = {
    phase: "EXECUTE" as const,
    intent: "tool_call" as const,
    summary: "Reading project configuration",
    tools: [
      { name: "archon.fs.read", args: { path: "raindrop.config.json" } }
    ],
    requires_permission: true
  };

  // Execute with permission
  const response = await executeTools(request);

  // Store in Raindrop memory
  if (response.success) {
    await putMemory({
      session_id: sessionId,
      content: `Tool results: ${JSON.stringify(response.results)}`
    });

    // Update workflow state
    await updateState({
      session_id: sessionId,
      timeline_id: timelineId,
      status: "complete",
      artifacts: { toolResults: response.results }
    });
  }
}
```

## Testing

### Manual Testing

```bash
# Build the project
npm run build

# Run test script
node examples/test-workflow.js
```

### Unit Tests

```bash
npm test
```

### Test with Mock Archon

```typescript
import { executeTools } from './archon-runtime';

// Simulate Archon request
const mockRequest = {
  phase: "EXECUTE" as const,
  intent: "tool_call" as const,
  summary: "Test file operations",
  tools: [
    { name: "archon.tools.list", args: {} },
    { name: "archon.tools.help", args: { tool_id: "archon.fs.read" } }
  ],
  requires_permission: true
};

executeTools(mockRequest).then(response => {
  console.log(JSON.stringify(response, null, 2));
});
```

## Configuration

### Environment Variables

```bash
# Enable debug mode
export ARCHON_DEBUG=true

# Set permission timeout (ms)
export ARCHON_PERMISSION_TIMEOUT=30000

# Auto-approve mode (DANGEROUS - dev only)
export ARCHON_AUTO_APPROVE=false
```

### Custom Permission Handler

Replace the default CLI prompt with a custom UI:

```typescript
// permissions/gatekeeper.ts
export async function requestPermission(
  action: string,
  resource: string,
  archon: string
): Promise<boolean> {
  // Custom implementation (e.g., web UI, Slack bot, etc.)
  return await myCustomPermissionUI({ action, resource, archon });
}
```

## Project Structure

```
archon-runtime/
├── core/
│   ├── types.ts              # TypeScript type definitions
│   ├── fs/                   # File system tools
│   │   ├── read.ts
│   │   ├── write.ts
│   │   ├── edit.ts
│   │   ├── find.ts
│   │   └── delete.ts
│   └── raindrop/
│       └── dispatcher.ts     # Main orchestration layer
├── tools/
│   └── registry.ts           # Tool registration and lookup
├── permissions/
│   └── gatekeeper.ts         # Permission management
├── index.ts                  # Main entry point
├── package.json
├── tsconfig.json
├── SYSTEM_PROMPT.md          # Archon integration guide
└── README.md                 # This file
```

## Extending with New Tools

### 1. Define Tool Interface

```typescript
// core/types.ts
export interface MyToolArgs {
  param1: string;
  param2: number;
}

export interface MyToolResult {
  success: boolean;
  data?: any;
  error?: string;
}
```

### 2. Implement Tool Module

```typescript
// core/mytool/execute.ts
import { requestPermission } from '../../permissions/gatekeeper';

export async function myTool(args: MyToolArgs): Promise<MyToolResult> {
  const allowed = await requestPermission('mytool', args.param1);
  if (!allowed) {
    return { success: false, error: 'Permission denied' };
  }

  // Tool implementation...
  return { success: true, data: result };
}
```

### 3. Register Tool

```typescript
// tools/registry.ts
import { myTool } from '../core/mytool/execute';

export const toolRegistry: ToolRegistry = {
  // ... existing tools
  'archon.mytool': myTool
};
```

### 4. Add Help Documentation

```typescript
// tools/registry.ts - helpDocs
'archon.mytool': `
archon.mytool(param1: string, param2: number)
  Description of what this tool does.

  Args:
    param1 - Description
    param2 - Description

  Returns:
    { success: boolean, data?: any, error?: string }
`
```

## Roadmap

- [ ] Git operations (`archon.git.*`)
- [ ] Shell command execution (`archon.exec.*`)
- [ ] HTTP requests (`archon.network.*`)
- [ ] Database queries (`archon.db.*`)
- [ ] AI model invocation (`archon.ai.*`)
- [ ] Web UI for permission management
- [ ] Integration tests with gpt-oss:20b
- [ ] Performance metrics and rate limiting

## Contributing

Contributions are welcome! Please follow these guidelines:

1. All tools must implement permission gating
2. Include comprehensive error handling
3. Add help documentation to registry
4. Write tests for new functionality
5. Update SYSTEM_PROMPT.md with new tools

## License

MIT

## Related Documentation

- [archon_tools_manifest.md](../archon_tools_manifest.md) - Complete protocol specification
- [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md) - Integration guide for Archon AI
- [Raindrop MCP Documentation](https://raindrop.dev/docs)

## Support

For issues and feature requests, please file an issue on GitHub.

---

**Built for secure, permission-gated AI tool execution** 🔒🤖
