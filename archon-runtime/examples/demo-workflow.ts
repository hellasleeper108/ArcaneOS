/**
 * Demo Workflow
 * Demonstrates Archon tool-calling with permission gates
 */

import { executeTools, formatResponse, ToolRequest } from '../index';

/**
 * Example 1: Reading a file
 */
async function example1_readFile() {
  console.log('\n=== EXAMPLE 1: Read File ===\n');

  const request: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Reading package.json to check dependencies",
    tools: [
      {
        name: "archon.fs.read",
        args: { path: "package.json" }
      }
    ],
    requires_permission: true
  };

  const response = await executeTools(request);
  console.log(formatResponse(response));

  return response;
}

/**
 * Example 2: Finding files
 */
async function example2_findFiles() {
  console.log('\n=== EXAMPLE 2: Find Files ===\n');

  const request: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Finding all TypeScript files in core/",
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

  const response = await executeTools(request);
  console.log(formatResponse(response));

  return response;
}

/**
 * Example 3: Writing a file
 */
async function example3_writeFile() {
  console.log('\n=== EXAMPLE 3: Write File ===\n');

  const testContent = `# Test File
This file was created by the Archon Runtime demo.
Timestamp: ${new Date().toISOString()}
`;

  const request: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Creating a test file",
    tools: [
      {
        name: "archon.fs.write",
        args: {
          path: "examples/test-output.md",
          content: testContent
        }
      }
    ],
    requires_permission: true
  };

  const response = await executeTools(request);
  console.log(formatResponse(response));

  return response;
}

/**
 * Example 4: Editing a file
 */
async function example4_editFile() {
  console.log('\n=== EXAMPLE 4: Edit File ===\n');

  const request: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Updating timestamp in test file",
    tools: [
      {
        name: "archon.fs.edit",
        args: {
          path: "examples/test-output.md",
          find: "Timestamp:",
          replace: "Updated:"
        }
      }
    ],
    requires_permission: true
  };

  const response = await executeTools(request);
  console.log(formatResponse(response));

  return response;
}

/**
 * Example 5: Chaining multiple tools
 */
async function example5_chainedTools() {
  console.log('\n=== EXAMPLE 5: Chained Tools ===\n');

  const request: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Listing all tools and getting help for read",
    tools: [
      {
        name: "archon.tools.list",
        args: {}
      },
      {
        name: "archon.tools.help",
        args: { tool_id: "archon.fs.read" }
      }
    ],
    requires_permission: true
  };

  const response = await executeTools(request);
  console.log(formatResponse(response));

  return response;
}

/**
 * Example 6: Complete workflow (find → read → analyze)
 */
async function example6_completeWorkflow() {
  console.log('\n=== EXAMPLE 6: Complete Workflow ===\n');

  // Step 1: Find TypeScript files
  console.log('Step 1: Finding TypeScript files...');
  const findRequest: ToolRequest = {
    phase: "EXECUTE",
    intent: "tool_call",
    summary: "Finding TypeScript files to analyze",
    tools: [
      {
        name: "archon.fs.find",
        args: { base: "core/fs/", pattern: "*.ts" }
      }
    ],
    requires_permission: true
  };

  const findResponse = await executeTools(findRequest);

  if (!findResponse.success || !findResponse.results) {
    console.error('Failed to find files');
    return;
  }

  const files = findResponse.results[0].result.files;
  console.log(`Found ${files.length} files:`, files);

  // Step 2: Read first file
  if (files.length > 0) {
    console.log(`\nStep 2: Reading ${files[0]}...`);
    const readRequest: ToolRequest = {
      phase: "EXECUTE",
      intent: "tool_call",
      summary: `Reading ${files[0]} for analysis`,
      tools: [
        {
          name: "archon.fs.read",
          args: { path: `core/fs/${files[0]}` }
        }
      ],
      requires_permission: true
    };

    const readResponse = await executeTools(readRequest);

    if (readResponse.success && readResponse.results) {
      const content = readResponse.results[0].result.content;
      const lines = content.split('\n').length;
      console.log(`File contains ${lines} lines`);
    }
  }
}

/**
 * Main demo runner
 */
async function main() {
  console.log('🚀 Archon Runtime Demo');
  console.log('This demonstrates the permission-gated tool system');
  console.log('You will be prompted to approve each operation\n');

  try {
    // Run examples
    await example1_readFile();
    await example2_findFiles();
    await example3_writeFile();
    await example4_editFile();
    await example5_chainedTools();
    await example6_completeWorkflow();

    console.log('\n✅ All examples completed!');
  } catch (error) {
    console.error('\n❌ Error:', error);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export {
  example1_readFile,
  example2_findFiles,
  example3_writeFile,
  example4_editFile,
  example5_chainedTools,
  example6_completeWorkflow
};
