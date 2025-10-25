/**
 * Archon Runtime
 * Main entry point for the permission-gated tool execution system
 */

// Core dispatcher
export { executeTools, getExecutionLog, clearExecutionLog, formatResponse } from './core/raindrop/dispatcher';

// Permission management
export {
  requestPermission as requestPermissionLegacy,
  clearPermissionCache as clearPermissionCacheLegacy,
  setAutoApprove as setAutoApproveLegacy
} from './permissions/gatekeeper';

// Enhanced permission management
export {
  requestPermission,
  clearPermissionCache,
  configureGatekeeper,
  addAutoApprovePattern,
  addAutoDenyPattern,
  getPendingRequests,
  resolveWebRequest
} from './permissions/enhanced-gatekeeper';

// Web UI server
export { startWebUIServer, stopWebUIServer } from './permissions/web-ui-server';

// Tool registry
export { toolRegistry, toolExists, getTool } from './tools/registry';

// Archon client
export { ArchonClient } from './core/archon/client';
export type { ArchonMessage, ArchonConfig, ArchonResponse } from './core/archon/client';

// Raindrop integration
export { RaindropArchonRuntime, createRaindropRuntime } from './core/raindrop/integration';

// Types
export type {
  ToolRequest,
  ToolResponse,
  ToolResult,
  ToolCall,
  PermissionRequest,
  PermissionResponse,
  ToolModule,
  ToolRegistry,
  // File system types
  ReadArgs,
  ReadResult,
  WriteArgs,
  WriteResult,
  EditArgs,
  EditResult,
  FindArgs,
  FindResult,
  DeleteArgs,
  DeleteResult,
  // Git types
  GitStatusArgs,
  GitStatusResult,
  GitCommitArgs,
  GitCommitResult,
  GitLogArgs,
  GitLogResult,
  // Exec types
  ExecArgs,
  ExecResult,
  // Network types
  HttpRequestArgs,
  HttpRequestResult,
  // Database types
  DbQueryArgs,
  DbQueryResult
} from './core/types';
