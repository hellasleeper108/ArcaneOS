# 🧱 Archon Tool-Calling Manifest

## Overview

The Archon Tool-Calling Manifest defines a permission-gated tool system where AI agents (Archons) must request permission before executing any operation. This architecture ensures human oversight over all file system operations and tool executions.

## Protocol Specification

### Tool Request Format

The Archon emits a JSON object to request tool execution:

```json
{
  "phase": "EXECUTE",
  "intent": "tool_call",
  "summary": "short purpose description",
  "tools": [
    {"name": "tool.id", "args": { /* arguments */ }}
  ],
  "requires_permission": true
}
```

### Execution Flow

1. **Request**: Archon emits tool request JSON
2. **Permission Gate**: Runtime shows user consent prompt
3. **Execution**: Upon approval, tools are executed
4. **Response**: Results returned in next user message
5. **Continuation**: Archon processes results and continues

## Core Tools Registry

| Tool ID | Description | Implementation | Permission Required |
|---------|-------------|----------------|---------------------|
| `archon.fs.read` | Read text file contents | `core/fs/read.ts` | Yes |
| `archon.fs.write` | Write or create file | `core/fs/write.ts` | Yes |
| `archon.fs.edit` | Apply patch/diff to file | `core/fs/edit.ts` | Yes |
| `archon.fs.find` | Recursive file search | `core/fs/find.ts` | Yes |
| `archon.fs.delete` | Delete file or directory | `core/fs/delete.ts` | Yes |
| `archon.tools.list` | Enumerate registered tools | Built-in | No |
| `archon.tools.help` | Describe tool arguments | Built-in | No |

### Tool Signatures

#### `archon.fs.read(path: string)`

Reads and returns the contents of a text file.

```typescript
interface ReadArgs {
  path: string;  // Absolute or relative file path
}

interface ReadResult {
  success: boolean;
  content?: string;
  error?: string;
}
```

#### `archon.fs.write(path: string, content: string)`

Writes content to a file, creating it if it doesn't exist.

```typescript
interface WriteArgs {
  path: string;    // Target file path
  content: string; // Full file content
}

interface WriteResult {
  success: boolean;
  bytesWritten?: number;
  error?: string;
}
```

#### `archon.fs.edit(path: string, find: string, replace: string)`

Applies a find-and-replace patch to an existing file.

```typescript
interface EditArgs {
  path: string;      // Target file path
  find: string;      // Text to find (can be multiline)
  replace: string;   // Replacement text
}

interface EditResult {
  success: boolean;
  matchCount?: number;
  error?: string;
}
```

#### `archon.fs.find(base: string, pattern: string)`

Recursively searches for files matching a pattern.

```typescript
interface FindArgs {
  base: string;    // Starting directory
  pattern: string; // Glob pattern (e.g., "*.ts", "**/*.tsx")
}

interface FindResult {
  success: boolean;
  files?: string[];
  count?: number;
  error?: string;
}
```

#### `archon.fs.delete(path: string)`

Deletes a file or directory.

```typescript
interface DeleteArgs {
  path: string; // File or directory to delete
}

interface DeleteResult {
  success: boolean;
  error?: string;
}
```

## System Prompt Integration

Add this section to the Archon's system prompt:

```
## Tool Access Protocol

You have access to a limited toolset managed by Raindrop.
You may REQUEST a tool by returning JSON with a "tools" array.

### Rules

1. You must clearly state the purpose of each tool call.
2. You must never read, write, or edit without permission.
3. When uncertain, ask: "Creator, shall I call [tool.name] with these arguments?"
4. You may chain multiple tools in one request.
5. After execution, expect results to arrive as the next message.
6. If access is denied, respond: "Access denied by creator." and continue safely.

### Example Request

{
  "phase": "EXECUTE",
  "intent": "tool_call",
  "summary": "Need to inspect core/veil.py for syntax errors",
  "tools": [
    {"name":"archon.fs.read","args":{"path":"core/veil.py"}}
  ],
  "requires_permission": true
}

### Available Tools

- archon.fs.read(path) - Read file contents
- archon.fs.write(path, content) - Write file
- archon.fs.edit(path, find, replace) - Apply patch
- archon.fs.find(base, pattern) - Search for files
- archon.fs.delete(path) - Delete file
- archon.tools.list() - List all tools
- archon.tools.help(tool_id) - Get tool documentation
```

## Runtime Implementation

### Dispatcher Architecture

The dispatcher (`core/raindrop/dispatcher.ts`) orchestrates tool execution:

```typescript
export async function executeTools(request: ToolRequest): Promise<ToolResponse> {
  const results: ToolResult[] = [];

  for (const toolCall of request.tools) {
    // Check permission for each tool
    const allowed = await requestPermission("execute", toolCall.name);

    if (!allowed) {
      return {
        success: false,
        message: `Permission denied for ${toolCall.name}`,
        denied: true
      };
    }

    // Resolve and execute tool
    const toolModule = toolRegistry[toolCall.name];
    if (!toolModule) {
      return {
        success: false,
        message: `Unknown tool: ${toolCall.name}`,
        error: true
      };
    }

    const result = await toolModule(toolCall.args);
    results.push({ tool: toolCall.name, result });
  }

  return { success: true, results };
}
```

### Permission System

Each tool invokes `requestPermission()` internally:

```typescript
async function requestPermission(action: string, resource: string): Promise<boolean> {
  // Display consent UI to user
  const approved = await showPermissionDialog({
    action,
    resource,
    archon: "gpt-oss:20b"
  });

  return approved;
}
```

## Testing

### Test Prompt

```
User: "Read the contents of core/vibecompiler.py"

Expected Archon Response:
{
  "phase": "EXECUTE",
  "intent": "tool_call",
  "summary": "Requesting permission to read the specified file.",
  "tools": [
    {
      "name": "archon.fs.read",
      "args": {"path": "core/vibecompiler.py"}
    }
  ],
  "requires_permission": true
}

Runtime Action:
→ Prompt: "The Archon requests permission to read core/vibecompiler.py. Approve?"
→ User approves
→ Execute tool
→ Return results to Archon
→ Archon processes and responds
```

### Multi-Tool Request

```
User: "Find all TypeScript files in src/ and read the first one"

Expected Archon Response:
{
  "phase": "EXECUTE",
  "intent": "tool_call",
  "summary": "Search for TypeScript files, then read the first result",
  "tools": [
    {
      "name": "archon.fs.find",
      "args": {"base": "src/", "pattern": "**/*.ts"}
    }
  ],
  "requires_permission": true
}

After receiving results:
{
  "phase": "EXECUTE",
  "intent": "tool_call",
  "summary": "Reading the first TypeScript file found",
  "tools": [
    {
      "name": "archon.fs.read",
      "args": {"path": "src/components/Button.ts"}
    }
  ],
  "requires_permission": true
}
```

## Security Considerations

1. **Permission Required**: All file operations require explicit user consent
2. **Path Validation**: Tools validate paths to prevent directory traversal
3. **Sandboxing**: Operations are confined to the project directory
4. **Audit Trail**: All tool executions are logged with timestamps
5. **Rate Limiting**: Prevent excessive tool calls within time windows
6. **Content Validation**: File writes are scanned for malicious content

## Integration with Raindrop

The Archon tool system integrates with Raindrop's orchestration layer:

1. **Session Management**: Tools operate within session context
2. **Memory Integration**: Tool results stored in working memory
3. **State Transitions**: Tool success/failure triggers workflow updates
4. **Artifact Tracking**: File modifications recorded as artifacts

## Future Extensions

- `archon.git.*` - Git operations (status, commit, push)
- `archon.exec.*` - Execute shell commands (high permission)
- `archon.network.*` - HTTP requests (permission-gated)
- `archon.db.*` - Database queries (SmartSQL integration)
- `archon.ai.*` - Invoke other AI models (Claude, GPT, etc.)
