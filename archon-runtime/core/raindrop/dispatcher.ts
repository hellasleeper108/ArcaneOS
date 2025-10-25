import {
  ToolRequest,
  ToolResponse,
  ToolResult,
  ToolCall
} from '../types';
import { toolRegistry, toolExists } from '../../tools/registry';

/**
 * Raindrop Dispatcher
 * Orchestrates tool execution with permission gating and error handling
 */

interface ExecutionLog {
  timestamp: number;
  request: ToolRequest;
  response: ToolResponse;
}

// Execution audit trail
const executionLog: ExecutionLog[] = [];

/**
 * Main dispatcher function
 * Processes tool requests from Archon and returns results
 */
export async function executeTools(request: ToolRequest): Promise<ToolResponse> {
  const startTime = Date.now();

  console.log('\n' + '▼'.repeat(60));
  console.log('🧠 ARCHON TOOL REQUEST');
  console.log('▼'.repeat(60));
  console.log(`Summary: ${request.summary}`);
  console.log(`Tools requested: ${request.tools.length}`);
  console.log('▼'.repeat(60) + '\n');

  // Validate request structure
  if (!request.tools || !Array.isArray(request.tools) || request.tools.length === 0) {
    const response: ToolResponse = {
      success: false,
      error: true,
      message: 'Invalid request: tools array is empty or missing'
    };
    logExecution(request, response);
    return response;
  }

  const results: ToolResult[] = [];

  // Execute each tool in sequence
  for (const toolCall of request.tools) {
    console.log(`\n🔧 Executing: ${toolCall.name}`);

    // Check if tool exists
    if (!toolExists(toolCall.name)) {
      const response: ToolResponse = {
        success: false,
        error: true,
        message: `Unknown tool: ${toolCall.name}`
      };
      logExecution(request, response);
      return response;
    }

    // Get tool module
    const toolModule = toolRegistry[toolCall.name];

    try {
      // Execute tool (permission checking happens inside each tool)
      const result = await toolModule(toolCall.args);

      // Check if permission was denied
      if (result.success === false && result.error?.includes('Permission denied')) {
        const response: ToolResponse = {
          success: false,
          denied: true,
          message: `Permission denied for ${toolCall.name}`
        };
        logExecution(request, response);
        return response;
      }

      // Check if tool execution failed
      if (result.success === false) {
        const response: ToolResponse = {
          success: false,
          error: true,
          message: `Tool execution failed: ${result.error || 'Unknown error'}`
        };
        logExecution(request, response);
        return response;
      }

      // Add successful result
      results.push({
        tool: toolCall.name,
        result
      });

      console.log(`✅ Success: ${toolCall.name}`);

    } catch (error) {
      const response: ToolResponse = {
        success: false,
        error: true,
        message: `Tool execution threw exception: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
      logExecution(request, response);
      return response;
    }
  }

  // All tools executed successfully
  const response: ToolResponse = {
    success: true,
    results
  };

  const duration = Date.now() - startTime;
  console.log(`\n${'▲'.repeat(60)}`);
  console.log(`✅ ALL TOOLS EXECUTED SUCCESSFULLY (${duration}ms)`);
  console.log('▲'.repeat(60) + '\n');

  logExecution(request, response);
  return response;
}

/**
 * Logs execution to audit trail
 */
function logExecution(request: ToolRequest, response: ToolResponse): void {
  executionLog.push({
    timestamp: Date.now(),
    request,
    response
  });

  // Keep only last 100 executions
  if (executionLog.length > 100) {
    executionLog.shift();
  }
}

/**
 * Gets the execution audit trail
 */
export function getExecutionLog(): ExecutionLog[] {
  return [...executionLog];
}

/**
 * Clears the execution audit trail
 */
export function clearExecutionLog(): void {
  executionLog.length = 0;
}

/**
 * Formats tool response for display to user
 */
export function formatResponse(response: ToolResponse): string {
  if (!response.success) {
    if (response.denied) {
      return `❌ Access denied: ${response.message}`;
    }
    return `❌ Error: ${response.message}`;
  }

  if (!response.results || response.results.length === 0) {
    return '✅ Tools executed successfully (no results)';
  }

  let output = '✅ Tools executed successfully:\n\n';

  for (const result of response.results) {
    output += `📦 ${result.tool}:\n`;
    output += JSON.stringify(result.result, null, 2) + '\n\n';
  }

  return output;
}
