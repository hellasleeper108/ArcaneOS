/**
 * Full Integration Example
 * Demonstrates Archon tool-calling with Raindrop MCP integration
 */

import { ArchonClient } from '../core/archon/client';
import { RaindropArchonRuntime } from '../core/raindrop/integration';
import { configureGatekeeper, addAutoApprovePattern } from '../permissions/enhanced-gatekeeper';
import { startWebUIServer } from '../permissions/web-ui-server';
import { ToolRequest } from '../core/types';
import fs from 'fs';
import path from 'path';

// Load system prompt
const SYSTEM_PROMPT = fs.readFileSync(
  path.join(__dirname, '../SYSTEM_PROMPT.md'),
  'utf-8'
);

/**
 * Example 1: Basic Archon workflow with CLI permission
 */
async function example1_basicWorkflow() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 1: Basic Archon Workflow with CLI Permissions');
  console.log('='.repeat(70) + '\n');

  // Configure for CLI mode
  configureGatekeeper({ mode: 'cli' });

  // Create Archon client with system prompt
  const archon = new ArchonClient({
    model: 'gpt-oss:20b',
    systemPrompt: SYSTEM_PROMPT
  });

  // Simulate Archon conversation
  console.log('User: "List all TypeScript files in the core directory"\n');

  // Archon would return this tool request
  const toolRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Finding TypeScript files in core/ directory",
    tools: [
      {
        name: "archon.fs.find",
        args: {
          base: "core/",
          pattern: "**/*.ts"
        }
      }
    ],
    requires_permission: true
  };

  console.log('Archon tool request:');
  console.log(JSON.stringify(toolRequest, null, 2));
  console.log();

  // Send message (this would trigger tool execution)
  const response = await archon.sendMessage("List all TypeScript files in the core directory");
  console.log('\nArchon response:', response);
}

/**
 * Example 2: Raindrop MCP Integration
 */
async function example2_raindropIntegration() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 2: Raindrop MCP Integration');
  console.log('='.repeat(70) + '\n');

  // Create Raindrop runtime
  const runtime = new RaindropArchonRuntime();

  // Start a new session
  const sessionId = await runtime.startSession();
  console.log(`✅ Session started: ${sessionId}\n`);

  // Execute tools with session tracking
  const toolRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Reading package.json to understand project dependencies",
    tools: [
      {
        name: "archon.fs.read",
        args: { path: "package.json" }
      }
    ],
    requires_permission: true
  };

  const response = await runtime.executeWithSession(toolRequest, sessionId);

  if (response.success) {
    console.log('\n✅ Tools executed successfully');
    console.log('Results stored in session memory');

    // Get session memory
    const memory = await runtime.getSessionMemory({ key: 'archon_tools' });
    console.log(`\nSession has ${memory.length} memory entries`);
  }

  // End session
  await runtime.endSession(true);
  console.log('\n✅ Session ended');
}

/**
 * Example 3: Web UI Permission Mode
 */
async function example3_webUIPermissions() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 3: Web UI Permission Mode');
  console.log('='.repeat(70) + '\n');

  // Start web UI server
  const server = startWebUIServer(3000);

  // Configure for web mode
  configureGatekeeper({
    mode: 'web',
    webServerPort: 3000
  });

  console.log('Web UI is running at http://localhost:3000/permissions');
  console.log('Permission requests will appear in the browser\n');

  // Simulate a tool request
  const toolRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Checking git repository status",
    tools: [
      {
        name: "archon.git.status",
        args: {}
      }
    ],
    requires_permission: true
  };

  console.log('A permission request is now pending in the web UI');
  console.log('Open your browser to approve or deny\n');

  // In a real scenario, the web UI would handle the approval
  // For this example, we'll just keep the server running briefly
  await new Promise(resolve => setTimeout(resolve, 5000));

  // Stop server
  server.close();
  console.log('\n✅ Web UI server stopped');
}

/**
 * Example 4: Auto-Approve Patterns
 */
async function example4_autoApprove() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 4: Auto-Approve Patterns');
  console.log('='.repeat(70) + '\n');

  // Configure auto-approve patterns
  configureGatekeeper({ mode: 'cli' });

  // Auto-approve reading from specific directories
  addAutoApprovePattern('read', /^(src|core|docs)\//);

  // Auto-approve finding files
  addAutoApprovePattern('find', /.*/);

  console.log('✅ Auto-approve patterns configured:');
  console.log('  - Reading from src/, core/, docs/');
  console.log('  - Finding files (all patterns)\n');

  const toolRequests: ToolRequest[] = [
    {
      phase: "EXECUTE",
      intent: "tool_call",
      summary: "Reading from auto-approved directory",
      tools: [
        { name: "archon.fs.read", args: { path: "core/types.ts" } }
      ],
      requires_permission: true
    },
    {
      phase: "EXECUTE",
      intent: "tool_call",
      summary: "Finding files (auto-approved)",
      tools: [
        { name: "archon.fs.find", args: { base: ".", pattern: "*.md" } }
      ],
      requires_permission: true
    }
  ];

  for (const request of toolRequests) {
    console.log(`Executing: ${request.summary}`);
    // Would execute automatically without prompting
    console.log('  → Auto-approved ✅\n');
  }
}

/**
 * Example 5: Advanced Multi-Tool Workflow
 */
async function example5_advancedWorkflow() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 5: Advanced Multi-Tool Workflow');
  console.log('='.repeat(70) + '\n');

  // Configure for auto-approve mode for demo
  configureGatekeeper({ mode: 'auto-approve' });

  console.log('Scenario: Archon analyzes project and makes HTTP request\n');

  // Step 1: Find all package.json files
  console.log('Step 1: Finding package.json files...');
  const findRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Finding all package.json files in project",
    tools: [
      { name: "archon.fs.find", args: { base: ".", pattern: "**/package.json" } }
    ],
    requires_permission: true
  };

  // Step 2: Read first package.json
  console.log('Step 2: Reading first package.json...');
  const readRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Reading package.json to analyze dependencies",
    tools: [
      { name: "archon.fs.read", args: { path: "package.json" } }
    ],
    requires_permission: true
  };

  // Step 3: Check git status
  console.log('Step 3: Checking git repository status...');
  const gitRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Getting current git status",
    tools: [
      { name: "archon.git.status", args: {} }
    ],
    requires_permission: true
  };

  // Step 4: Make HTTP request (example)
  console.log('Step 4: Making HTTP request to check package registry...');
  const httpRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Checking latest version from npm registry",
    tools: [
      {
        name: "archon.http.request",
        args: {
          url: "https://registry.npmjs.org/typescript",
          method: "GET"
        }
      }
    ],
    requires_permission: true
  };

  console.log('\n✅ All steps completed (would execute with real tools)\n');
}

/**
 * Example 6: Database Query via Raindrop SmartSQL
 */
async function example6_databaseQuery() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 6: Database Query via Raindrop SmartSQL');
  console.log('='.repeat(70) + '\n');

  const dbRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Querying user data from analytics database",
    tools: [
      {
        name: "archon.db.query",
        args: {
          database_id: "analytics-db",
          query: "SELECT * FROM users WHERE active = ? LIMIT 10",
          parameters: [true]
        }
      }
    ],
    requires_permission: true
  };

  console.log('Database query request:');
  console.log(JSON.stringify(dbRequest, null, 2));
  console.log('\nNote: SmartSQL integration pending - see core/db/query.ts\n');
}

/**
 * Example 7: Shell Command Execution
 */
async function example7_shellExecution() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 7: Shell Command Execution (HIGH RISK)');
  console.log('='.repeat(70) + '\n');

  const execRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Running npm install to update dependencies",
    tools: [
      {
        name: "archon.exec",
        args: {
          command: "npm",
          args: ["install"],
          cwd: process.cwd(),
          timeout: 60000
        }
      }
    ],
    requires_permission: true
  };

  console.log('⚠️  WARNING: Shell execution requires explicit permission');
  console.log('Execution request:');
  console.log(JSON.stringify(execRequest, null, 2));
  console.log('\nThis would prompt user for approval with HIGH RISK warning\n');
}

/**
 * Main runner
 */
async function main() {
  console.log('\n' + '█'.repeat(70));
  console.log('  ARCHON RUNTIME - FULL INTEGRATION EXAMPLES');
  console.log('█'.repeat(70));

  const examples = [
    { name: 'Basic Workflow', fn: example1_basicWorkflow },
    { name: 'Raindrop Integration', fn: example2_raindropIntegration },
    { name: 'Web UI Permissions', fn: example3_webUIPermissions },
    { name: 'Auto-Approve Patterns', fn: example4_autoApprove },
    { name: 'Advanced Workflow', fn: example5_advancedWorkflow },
    { name: 'Database Query', fn: example6_databaseQuery },
    { name: 'Shell Execution', fn: example7_shellExecution }
  ];

  console.log('\nAvailable examples:');
  examples.forEach((ex, i) => {
    console.log(`  ${i + 1}. ${ex.name}`);
  });

  // Run all examples (or select specific ones)
  const runAll = process.argv.includes('--all');
  const exampleNum = process.argv[2] ? parseInt(process.argv[2]) : null;

  if (exampleNum && exampleNum >= 1 && exampleNum <= examples.length) {
    await examples[exampleNum - 1].fn();
  } else if (runAll) {
    for (const example of examples) {
      await example.fn();
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  } else {
    console.log('\nUsage:');
    console.log('  npx ts-node examples/full-integration.ts <number>  - Run specific example');
    console.log('  npx ts-node examples/full-integration.ts --all      - Run all examples');
  }

  console.log('\n' + '█'.repeat(70));
  console.log('  EXAMPLES COMPLETE');
  console.log('█'.repeat(70) + '\n');
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export {
  example1_basicWorkflow,
  example2_raindropIntegration,
  example3_webUIPermissions,
  example4_autoApprove,
  example5_advancedWorkflow,
  example6_databaseQuery,
  example7_shellExecution
};
