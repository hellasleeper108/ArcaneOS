import readline from 'readline';
import { PermissionRequest, PermissionResponse } from '../core/types';

/**
 * Permission gatekeeper for tool execution
 * Prompts the user for consent before allowing operations
 */

// Permission cache for session-based auto-approvals
const permissionCache = new Map<string, boolean>();

/**
 * Requests permission from the user to execute a tool
 */
export async function requestPermission(
  action: string,
  resource: string,
  archon: string = 'archon'
): Promise<boolean> {
  const cacheKey = `${action}:${resource}`;

  // Check cache first
  if (permissionCache.has(cacheKey)) {
    return permissionCache.get(cacheKey)!;
  }

  const request: PermissionRequest = {
    action,
    resource,
    archon,
    timestamp: Date.now()
  };

  const response = await promptUser(request);

  // Cache the response for this session
  if (response.granted) {
    permissionCache.set(cacheKey, true);
  }

  return response.granted;
}

/**
 * Prompts the user via CLI for permission
 */
async function promptUser(request: PermissionRequest): Promise<PermissionResponse> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('\n' + '='.repeat(60));
    console.log('🔒 PERMISSION REQUEST');
    console.log('='.repeat(60));
    console.log(`Archon: ${request.archon}`);
    console.log(`Action: ${request.action.toUpperCase()}`);
    console.log(`Resource: ${request.resource}`);
    console.log('='.repeat(60));

    rl.question('Approve this operation? [y/N]: ', (answer) => {
      rl.close();

      const approved = answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes';

      if (approved) {
        console.log('✅ Permission granted\n');
        resolve({ granted: true });
      } else {
        console.log('❌ Permission denied\n');
        resolve({ granted: false, reason: 'User denied permission' });
      }
    });
  });
}

/**
 * Clears the permission cache
 */
export function clearPermissionCache(): void {
  permissionCache.clear();
}

/**
 * Sets auto-approve for specific patterns (use with caution)
 */
export function setAutoApprove(action: string, resource: string): void {
  const cacheKey = `${action}:${resource}`;
  permissionCache.set(cacheKey, true);
}
