import { ToolRegistry } from '../core/types';
import { read } from '../core/fs/read';
import { write } from '../core/fs/write';
import { edit } from '../core/fs/edit';
import { find } from '../core/fs/find';
import { deleteResource } from '../core/fs/delete';
import { gitStatus } from '../core/git/status';
import { execute } from '../core/exec/execute';
import { httpRequest } from '../core/network/http';
import { dbQuery } from '../core/db/query';

/**
 * Central registry of all available tools
 */
export const toolRegistry: ToolRegistry = {
  // File system tools
  'archon.fs.read': read,
  'archon.fs.write': write,
  'archon.fs.edit': edit,
  'archon.fs.find': find,
  'archon.fs.delete': deleteResource,

  // Git tools
  'archon.git.status': gitStatus,

  // Execution tools
  'archon.exec': execute,

  // Network tools
  'archon.http.request': httpRequest,

  // Database tools
  'archon.db.query': dbQuery,

  // Meta tools
  'archon.tools.list': listTools,
  'archon.tools.help': getToolHelp
};

/**
 * Lists all available tools
 */
async function listTools(): Promise<{ tools: string[] }> {
  return {
    tools: Object.keys(toolRegistry)
  };
}

/**
 * Provides help documentation for a specific tool
 */
async function getToolHelp(args: { tool_id: string }): Promise<{ help: string }> {
  const helpDocs: Record<string, string> = {
    'archon.fs.read': `
archon.fs.read(path: string)
  Reads and returns the contents of a text file.

  Args:
    path - Absolute or relative file path

  Returns:
    { success: boolean, content?: string, error?: string }

  Example:
    { "name": "archon.fs.read", "args": { "path": "src/main.ts" } }
`,
    'archon.fs.write': `
archon.fs.write(path: string, content: string)
  Writes content to a file, creating it if it doesn't exist.

  Args:
    path - Target file path
    content - Full file content to write

  Returns:
    { success: boolean, bytesWritten?: number, error?: string }

  Example:
    { "name": "archon.fs.write", "args": {
      "path": "output.txt",
      "content": "Hello World"
    }}
`,
    'archon.fs.edit': `
archon.fs.edit(path: string, find: string, replace: string)
  Applies a find-and-replace patch to an existing file.

  Args:
    path - Target file path
    find - Text to find (can be multiline)
    replace - Replacement text

  Returns:
    { success: boolean, matchCount?: number, error?: string }

  Example:
    { "name": "archon.fs.edit", "args": {
      "path": "src/config.ts",
      "find": "DEBUG = false",
      "replace": "DEBUG = true"
    }}
`,
    'archon.fs.find': `
archon.fs.find(base: string, pattern: string)
  Recursively searches for files matching a glob pattern.

  Args:
    base - Starting directory
    pattern - Glob pattern (e.g., "*.ts", "**/*.tsx")

  Returns:
    { success: boolean, files?: string[], count?: number, error?: string }

  Example:
    { "name": "archon.fs.find", "args": {
      "base": "src/",
      "pattern": "**/*.ts"
    }}
`,
    'archon.fs.delete': `
archon.fs.delete(path: string)
  Deletes a file or directory (irreversible operation).

  Args:
    path - File or directory to delete

  Returns:
    { success: boolean, error?: string }

  Example:
    { "name": "archon.fs.delete", "args": { "path": "temp/cache.txt" } }
`,
    'archon.git.status': `
archon.git.status()
  Gets the current git repository status.

  Args: None

  Returns:
    { success: boolean, branch?: string, staged?: string[],
      modified?: string[], untracked?: string[], error?: string }

  Example:
    { "name": "archon.git.status", "args": {} }
`,
    'archon.exec': `
archon.exec(command: string, args?: string[], cwd?: string, timeout?: number)
  Executes a shell command (HIGH RISK - requires permission).

  Args:
    command - Command to execute
    args - Optional command arguments array
    cwd - Optional working directory
    timeout - Optional timeout in milliseconds (default: 30000)

  Returns:
    { success: boolean, stdout?: string, stderr?: string,
      exitCode?: number, error?: string }

  Example:
    { "name": "archon.exec", "args": {
      "command": "npm",
      "args": ["install"],
      "cwd": "/project"
    }}

  WARNING: This tool can execute arbitrary commands. Use with extreme caution.
`,
    'archon.http.request': `
archon.http.request(url: string, method?: string, headers?: object, body?: any, timeout?: number)
  Makes an HTTP/HTTPS request.

  Args:
    url - The URL to request
    method - HTTP method (GET, POST, PUT, DELETE, PATCH) [default: GET]
    headers - Optional headers object
    body - Optional request body (string or object)
    timeout - Optional timeout in milliseconds (default: 30000)

  Returns:
    { success: boolean, status?: number, headers?: object,
      body?: string, error?: string }

  Example:
    { "name": "archon.http.request", "args": {
      "url": "https://api.example.com/data",
      "method": "GET"
    }}
`,
    'archon.db.query': `
archon.db.query(database_id: string, query: string, parameters?: any[])
  Executes a database query via Raindrop SmartSQL.

  Args:
    database_id - The database identifier or SmartSQL name
    query - SQL query to execute
    parameters - Optional query parameters for prepared statements

  Returns:
    { success: boolean, rows?: any[], rowCount?: number, error?: string }

  Example:
    { "name": "archon.db.query", "args": {
      "database_id": "analytics-db",
      "query": "SELECT * FROM users WHERE id = ?",
      "parameters": [123]
    }}
`,
    'archon.tools.list': `
archon.tools.list()
  Lists all available tools in the registry.

  Args: None

  Returns:
    { tools: string[] }

  Example:
    { "name": "archon.tools.list", "args": {} }
`,
    'archon.tools.help': `
archon.tools.help(tool_id: string)
  Provides detailed help documentation for a specific tool.

  Args:
    tool_id - The ID of the tool to get help for

  Returns:
    { help: string }

  Example:
    { "name": "archon.tools.help", "args": { "tool_id": "archon.fs.read" } }
`
  };

  const help = helpDocs[args.tool_id] || `No documentation found for tool: ${args.tool_id}`;

  return { help };
}

/**
 * Checks if a tool exists in the registry
 */
export function toolExists(toolId: string): boolean {
  return toolId in toolRegistry;
}

/**
 * Gets a tool by ID
 */
export function getTool(toolId: string) {
  return toolRegistry[toolId];
}
