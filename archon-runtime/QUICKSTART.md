# Archon Runtime - Quick Start Guide

Get started with the Archon tool-calling system in 5 minutes.

## Installation

```bash
cd archon-runtime
npm install
npm run build
```

## Step 1: Understanding the Flow

```
Archon AI → Requests Tools (JSON) → Dispatcher → Permission Gate → Tools → Results → Archon
```

**Key Point**: The Archon never executes tools directly. It only *requests* them.

## Step 2: Configure Your Archon

Add this to your Archon's system prompt:

```
You have access to file system tools. Request them by returning JSON:

{
  "phase": "EXECUTE",
  "intent": "tool_call",
  "summary": "what you need to do",
  "tools": [
    {"name": "archon.fs.read", "args": {"path": "file.txt"}}
  ],
  "requires_permission": true
}

Available tools:
- archon.fs.read(path)
- archon.fs.write(path, content)
- archon.fs.edit(path, find, replace)
- archon.fs.find(base, pattern)
- archon.fs.delete(path)
```

See [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md) for the full prompt.

## Step 3: Test with Demo

```bash
# Build first
npm run build

# Run demo (requires ts-node)
npx ts-node examples/demo-workflow.ts
```

You'll see prompts like:

```
============================================================
🔒 PERMISSION REQUEST
============================================================
Archon: archon
Action: READ
Resource: package.json
============================================================
Approve this operation? [y/N]:
```

Type `y` and press Enter to approve.

## Step 4: Basic Usage

```typescript
import { executeTools, ToolRequest } from './archon-runtime';

// This is what your Archon would send
const request: ToolRequest = {
  phase: "EXECUTE",
  intent: "tool_call",
  summary: "Reading configuration",
  tools: [
    { name: "archon.fs.read", args: { path: "config.json" } }
  ],
  requires_permission: true
};

// Your runtime executes it
const response = await executeTools(request);

if (response.success) {
  console.log("Content:", response.results[0].result.content);
} else {
  console.log("Error:", response.message);
}
```

## Step 5: Integrate with Your Archon

### For gpt-oss:20b

1. Add system prompt from Step 2
2. When Archon returns JSON with `"intent": "tool_call"`, extract it
3. Pass to `executeTools()`
4. Return results to Archon in next message

### Example Integration

```typescript
async function archonLoop(userMessage: string) {
  // 1. Send message to Archon
  const archonResponse = await callArchon(userMessage);

  // 2. Check if Archon wants tools
  if (isToolRequest(archonResponse)) {
    const request = JSON.parse(archonResponse);

    // 3. Execute with permission
    const toolResults = await executeTools(request);

    // 4. Send results back to Archon
    const finalResponse = await callArchon(
      `Tool results: ${JSON.stringify(toolResults)}`
    );

    return finalResponse;
  }

  return archonResponse;
}
```

## Common Patterns

### Pattern 1: Search then Read

```typescript
// Archon Step 1: Find files
{
  "tools": [
    {"name": "archon.fs.find", "args": {"base": "src/", "pattern": "*.ts"}}
  ]
}

// Archon Step 2: Read first result
{
  "tools": [
    {"name": "archon.fs.read", "args": {"path": "src/main.ts"}}
  ]
}
```

### Pattern 2: Read, Modify, Write

```typescript
// Step 1: Read
{"name": "archon.fs.read", "args": {"path": "config.ts"}}

// Step 2: Edit
{"name": "archon.fs.edit", "args": {
  "path": "config.ts",
  "find": "debug: false",
  "replace": "debug: true"
}}
```

### Pattern 3: Batch Operations

```typescript
{
  "tools": [
    {"name": "archon.tools.list", "args": {}},
    {"name": "archon.fs.find", "args": {"base": ".", "pattern": "*.json"}}
  ]
}
```

## Security Notes

⚠️ **Every operation requires permission**

- User must approve each tool call
- Paths are validated to prevent directory traversal
- All executions are logged
- Permission cache prevents repeated prompts in same session

## Troubleshooting

### "Unknown tool" error

Make sure you're using the exact tool name:
- ✅ `archon.fs.read`
- ❌ `read`
- ❌ `fs.read`

### Permission denied

The user typed 'n' or the permission cache blocked it. Use:

```typescript
import { clearPermissionCache } from './archon-runtime';
clearPermissionCache();
```

### Type errors

Make sure you built the project:

```bash
npm run build
```

## Next Steps

1. Read [README.md](./README.md) for architecture details
2. Review [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md) for complete prompt
3. Check [archon_tools_manifest.md](../archon_tools_manifest.md) for protocol spec
4. Customize [permissions/gatekeeper.ts](./permissions/gatekeeper.ts) for your UI

## Example: Complete Session

```typescript
// User: "Find all TypeScript files and show me the first one"

// Archon emits:
{
  "phase": "EXECUTE",
  "intent": "tool_call",
  "summary": "Searching for TypeScript files",
  "tools": [
    {"name": "archon.fs.find", "args": {"base": "src/", "pattern": "**/*.ts"}}
  ],
  "requires_permission": true
}

// Runtime executes → User approves → Results:
{
  "success": true,
  "results": [{
    "tool": "archon.fs.find",
    "result": {
      "success": true,
      "files": ["main.ts", "utils.ts"],
      "count": 2
    }
  }]
}

// Archon receives results, emits:
{
  "phase": "EXECUTE",
  "intent": "tool_call",
  "summary": "Reading main.ts as requested",
  "tools": [
    {"name": "archon.fs.read", "args": {"path": "src/main.ts"}}
  ],
  "requires_permission": true
}

// Runtime executes → User approves → Results:
{
  "success": true,
  "results": [{
    "tool": "archon.fs.read",
    "result": {
      "success": true,
      "content": "... file contents ..."
    }
  }]
}

// Archon responds to user:
// "I found 2 TypeScript files. Here's the content of main.ts: ..."
```

## Questions?

Check the documentation:
- [README.md](./README.md) - Full documentation
- [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md) - Integration guide
- [archon_tools_manifest.md](../archon_tools_manifest.md) - Protocol specification

---

**Ready to build secure AI agents!** 🚀🔒
