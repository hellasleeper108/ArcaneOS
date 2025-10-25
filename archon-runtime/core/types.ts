/**
 * Core type definitions for Archon tool system
 */

// Tool request from Archon
export interface ToolRequest {
  phase: "EXECUTE";
  intent: "tool_call";
  summary: string;
  tools: ToolCall[];
  requires_permission: boolean;
}

// Individual tool call
export interface ToolCall {
  name: string;
  args: Record<string, any>;
}

// Tool execution result
export interface ToolResult {
  tool: string;
  result: any;
}

// Response to Archon
export interface ToolResponse {
  success: boolean;
  results?: ToolResult[];
  message?: string;
  denied?: boolean;
  error?: boolean;
}

// Permission request
export interface PermissionRequest {
  action: string;
  resource: string;
  archon?: string;
  timestamp?: number;
}

// Permission response
export interface PermissionResponse {
  granted: boolean;
  reason?: string;
}

// Tool module interface
export type ToolModule = (args: any) => Promise<any>;

// Tool registry
export type ToolRegistry = Record<string, ToolModule>;

// File system tool arguments and results

export interface ReadArgs {
  path: string;
}

export interface ReadResult {
  success: boolean;
  content?: string;
  error?: string;
}

export interface WriteArgs {
  path: string;
  content: string;
}

export interface WriteResult {
  success: boolean;
  bytesWritten?: number;
  error?: string;
}

export interface EditArgs {
  path: string;
  find: string;
  replace: string;
}

export interface EditResult {
  success: boolean;
  matchCount?: number;
  error?: string;
}

export interface FindArgs {
  base: string;
  pattern: string;
}

export interface FindResult {
  success: boolean;
  files?: string[];
  count?: number;
  error?: string;
}

export interface DeleteArgs {
  path: string;
}

export interface DeleteResult {
  success: boolean;
  error?: string;
}

// Git tool arguments and results

export interface GitStatusArgs {}

export interface GitStatusResult {
  success: boolean;
  branch?: string;
  staged?: string[];
  modified?: string[];
  untracked?: string[];
  error?: string;
}

export interface GitCommitArgs {
  message: string;
  files?: string[];
}

export interface GitCommitResult {
  success: boolean;
  hash?: string;
  message?: string;
  error?: string;
}

export interface GitLogArgs {
  limit?: number;
}

export interface GitLogResult {
  success: boolean;
  commits?: Array<{
    hash: string;
    author: string;
    date: string;
    message: string;
  }>;
  error?: string;
}

// Exec tool arguments and results

export interface ExecArgs {
  command: string;
  args?: string[];
  cwd?: string;
  timeout?: number;
}

export interface ExecResult {
  success: boolean;
  stdout?: string;
  stderr?: string;
  exitCode?: number;
  error?: string;
}

// Network tool arguments and results

export interface HttpRequestArgs {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: string | object;
  timeout?: number;
}

export interface HttpRequestResult {
  success: boolean;
  status?: number;
  headers?: Record<string, string>;
  body?: string;
  error?: string;
}

// Database tool arguments and results

export interface DbQueryArgs {
  database_id: string;
  query: string;
  parameters?: any[];
}

export interface DbQueryResult {
  success: boolean;
  rows?: any[];
  rowCount?: number;
  error?: string;
}
