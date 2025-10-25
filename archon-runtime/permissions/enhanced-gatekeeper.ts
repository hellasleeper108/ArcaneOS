/**
 * Enhanced Permission Gatekeeper
 * Multiple UI options: CLI, Web, Auto-approve patterns
 */

import readline from 'readline';
import { PermissionRequest, PermissionResponse } from '../core/types';

// ANSI color codes for enhanced CLI
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m'
};

export type PermissionMode = 'cli' | 'web' | 'auto-approve' | 'auto-deny';

export interface GatekeeperConfig {
  mode: PermissionMode;
  autoApprovePatterns?: Array<{ action: string; resource: RegExp }>;
  autoDenyPatterns?: Array<{ action: string; resource: RegExp }>;
  webServerPort?: number;
  timeout?: number; // milliseconds
}

// Default configuration
let gatekeeperConfig: GatekeeperConfig = {
  mode: 'cli',
  timeout: 30000 // 30 seconds
};

// Permission cache
const permissionCache = new Map<string, boolean>();

// Pending web requests (for web UI mode)
const pendingRequests = new Map<string, {
  request: PermissionRequest;
  resolve: (response: PermissionResponse) => void;
}>();

/**
 * Configure the gatekeeper
 */
export function configureGatekeeper(config: Partial<GatekeeperConfig>): void {
  gatekeeperConfig = { ...gatekeeperConfig, ...config };
  console.log(`${colors.cyan}🔧 Gatekeeper configured:${colors.reset}`, gatekeeperConfig.mode);
}

/**
 * Main permission request function
 */
export async function requestPermission(
  action: string,
  resource: string,
  archon: string = 'archon'
): Promise<boolean> {
  const cacheKey = `${action}:${resource}`;

  // Check cache first
  if (permissionCache.has(cacheKey)) {
    const cached = permissionCache.get(cacheKey)!;
    console.log(`${colors.dim}📋 Using cached permission: ${cached ? 'approved' : 'denied'}${colors.reset}`);
    return cached;
  }

  const request: PermissionRequest = {
    action,
    resource,
    archon,
    timestamp: Date.now()
  };

  // Check auto-approve patterns
  if (gatekeeperConfig.autoApprovePatterns) {
    for (const pattern of gatekeeperConfig.autoApprovePatterns) {
      if (pattern.action === action && pattern.resource.test(resource)) {
        console.log(`${colors.green}✅ Auto-approved by pattern${colors.reset}`);
        permissionCache.set(cacheKey, true);
        return true;
      }
    }
  }

  // Check auto-deny patterns
  if (gatekeeperConfig.autoDenyPatterns) {
    for (const pattern of gatekeeperConfig.autoDenyPatterns) {
      if (pattern.action === action && pattern.resource.test(resource)) {
        console.log(`${colors.red}❌ Auto-denied by pattern${colors.reset}`);
        permissionCache.set(cacheKey, false);
        return false;
      }
    }
  }

  // Route to appropriate UI
  let response: PermissionResponse;

  switch (gatekeeperConfig.mode) {
    case 'cli':
      response = await promptUserCLI(request);
      break;
    case 'web':
      response = await promptUserWeb(request);
      break;
    case 'auto-approve':
      response = { granted: true };
      console.log(`${colors.yellow}⚠️  AUTO-APPROVE MODE - Permission granted${colors.reset}`);
      break;
    case 'auto-deny':
      response = { granted: false, reason: 'Auto-deny mode active' };
      console.log(`${colors.red}❌ AUTO-DENY MODE - Permission denied${colors.reset}`);
      break;
    default:
      response = await promptUserCLI(request);
  }

  // Cache the response
  if (response.granted) {
    permissionCache.set(cacheKey, true);
  }

  return response.granted;
}

/**
 * Enhanced CLI prompt with colors and better formatting
 */
async function promptUserCLI(request: PermissionRequest): Promise<PermissionResponse> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    // Get action color
    const actionColor = getActionColor(request.action);
    const actionIcon = getActionIcon(request.action);

    console.log('\n' + colors.bright + colors.cyan + '╔' + '═'.repeat(68) + '╗' + colors.reset);
    console.log(colors.bright + colors.cyan + '║' + colors.reset +
                ' '.repeat(23) + colors.bright + '🔒 PERMISSION REQUEST' + ' '.repeat(24) +
                colors.bright + colors.cyan + '║' + colors.reset);
    console.log(colors.bright + colors.cyan + '╠' + '═'.repeat(68) + '╣' + colors.reset);

    console.log(colors.cyan + '║' + colors.reset +
                colors.dim + ' Archon:   ' + colors.reset +
                colors.bright + (request.archon || 'archon').padEnd(56) +
                colors.cyan + '║' + colors.reset);

    console.log(colors.cyan + '║' + colors.reset +
                colors.dim + ' Action:   ' + colors.reset +
                actionIcon + ' ' + actionColor + request.action.toUpperCase().padEnd(54) + colors.reset +
                colors.cyan + '║' + colors.reset);

    console.log(colors.cyan + '║' + colors.reset +
                colors.dim + ' Resource: ' + colors.reset +
                colors.yellow + request.resource.padEnd(56) + colors.reset +
                colors.cyan + '║' + colors.reset);

    console.log(colors.bright + colors.cyan + '╚' + '═'.repeat(68) + '╝' + colors.reset);

    const question = `\n${colors.bright}Approve this operation?${colors.reset} ` +
                     `[${colors.green}y${colors.reset}/${colors.red}N${colors.reset}/${colors.yellow}a${colors.reset}=always/${colors.magenta}n${colors.reset}=never]: `;

    // Set timeout
    const timeout = setTimeout(() => {
      rl.close();
      console.log(`\n${colors.red}⏱️  Permission request timed out - denied${colors.reset}\n`);
      resolve({ granted: false, reason: 'Timeout' });
    }, gatekeeperConfig.timeout!);

    rl.question(question, (answer) => {
      clearTimeout(timeout);
      rl.close();

      const normalized = answer.toLowerCase().trim();

      if (normalized === 'y' || normalized === 'yes') {
        console.log(`${colors.green}✅ Permission granted${colors.reset}\n`);
        resolve({ granted: true });
      } else if (normalized === 'a' || normalized === 'always') {
        console.log(`${colors.green}✅ Permission granted (cached for session)${colors.reset}\n`);
        permissionCache.set(`${request.action}:${request.resource}`, true);
        resolve({ granted: true });
      } else if (normalized === 'n' || normalized === 'never') {
        console.log(`${colors.red}❌ Permission denied (cached for session)${colors.reset}\n`);
        permissionCache.set(`${request.action}:${request.resource}`, false);
        resolve({ granted: false, reason: 'User denied permanently' });
      } else {
        console.log(`${colors.red}❌ Permission denied${colors.reset}\n`);
        resolve({ granted: false, reason: 'User denied permission' });
      }
    });
  });
}

/**
 * Web-based permission prompt
 * Opens a local web server for permission management
 */
async function promptUserWeb(request: PermissionRequest): Promise<PermissionResponse> {
  return new Promise((resolve) => {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(7)}`;

    pendingRequests.set(requestId, { request, resolve });

    console.log(`\n${colors.cyan}🌐 Permission request pending in web UI${colors.reset}`);
    console.log(`${colors.dim}Request ID: ${requestId}${colors.reset}`);
    console.log(`${colors.yellow}Open: http://localhost:${gatekeeperConfig.webServerPort || 3000}/permissions${colors.reset}\n`);

    // Set timeout
    setTimeout(() => {
      if (pendingRequests.has(requestId)) {
        pendingRequests.delete(requestId);
        console.log(`${colors.red}⏱️  Web permission request timed out - denied${colors.reset}\n`);
        resolve({ granted: false, reason: 'Timeout' });
      }
    }, gatekeeperConfig.timeout!);
  });
}

/**
 * Get color for action type
 */
function getActionColor(action: string): string {
  switch (action.toLowerCase()) {
    case 'read':
      return colors.blue;
    case 'write':
      return colors.green;
    case 'edit':
      return colors.yellow;
    case 'delete':
      return colors.red;
    case 'find':
      return colors.cyan;
    case 'execute':
    case 'exec':
      return colors.magenta;
    default:
      return colors.white;
  }
}

/**
 * Get icon for action type
 */
function getActionIcon(action: string): string {
  switch (action.toLowerCase()) {
    case 'read':
      return '📖';
    case 'write':
      return '✍️';
    case 'edit':
      return '📝';
    case 'delete':
      return '🗑️';
    case 'find':
      return '🔍';
    case 'execute':
    case 'exec':
      return '⚡';
    default:
      return '🔧';
  }
}

/**
 * Clear permission cache
 */
export function clearPermissionCache(): void {
  permissionCache.clear();
  console.log(`${colors.yellow}🧹 Permission cache cleared${colors.reset}`);
}

/**
 * Set auto-approve pattern
 */
export function addAutoApprovePattern(action: string, resourcePattern: RegExp): void {
  if (!gatekeeperConfig.autoApprovePatterns) {
    gatekeeperConfig.autoApprovePatterns = [];
  }
  gatekeeperConfig.autoApprovePatterns.push({ action, resource: resourcePattern });
  console.log(`${colors.green}✅ Auto-approve pattern added: ${action} ${resourcePattern}${colors.reset}`);
}

/**
 * Set auto-deny pattern
 */
export function addAutoDenyPattern(action: string, resourcePattern: RegExp): void {
  if (!gatekeeperConfig.autoDenyPatterns) {
    gatekeeperConfig.autoDenyPatterns = [];
  }
  gatekeeperConfig.autoDenyPatterns.push({ action, resource: resourcePattern });
  console.log(`${colors.red}❌ Auto-deny pattern added: ${action} ${resourcePattern}${colors.reset}`);
}

/**
 * Get pending web requests (for web UI)
 */
export function getPendingRequests() {
  return Array.from(pendingRequests.entries()).map(([id, data]) => ({
    id,
    ...data.request
  }));
}

/**
 * Resolve a web request (for web UI)
 */
export function resolveWebRequest(requestId: string, granted: boolean): boolean {
  const pending = pendingRequests.get(requestId);
  if (!pending) {
    return false;
  }

  pending.resolve({ granted, reason: granted ? undefined : 'User denied via web UI' });
  pendingRequests.delete(requestId);
  return true;
}
