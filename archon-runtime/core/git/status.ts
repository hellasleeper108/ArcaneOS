import { exec } from 'child_process';
import { promisify } from 'util';
import { GitStatusArgs, GitStatusResult } from '../types';
import { requestPermission } from '../../permissions/enhanced-gatekeeper';

const execAsync = promisify(exec);

/**
 * Get git repository status
 */
export async function gitStatus(args: GitStatusArgs): Promise<GitStatusResult> {
  try {
    // Request permission
    const allowed = await requestPermission('git-status', process.cwd());
    if (!allowed) {
      return {
        success: false,
        error: 'Permission denied by user'
      };
    }

    // Get current branch
    const { stdout: branchOutput } = await execAsync('git branch --show-current');
    const branch = branchOutput.trim();

    // Get status
    const { stdout: statusOutput } = await execAsync('git status --porcelain');

    const staged: string[] = [];
    const modified: string[] = [];
    const untracked: string[] = [];

    const lines = statusOutput.split('\n').filter(line => line.trim());

    for (const line of lines) {
      const status = line.substring(0, 2);
      const file = line.substring(3);

      if (status.startsWith('A') || status.startsWith('M') || status.startsWith('D')) {
        staged.push(file);
      } else if (status.includes('M')) {
        modified.push(file);
      } else if (status.startsWith('??')) {
        untracked.push(file);
      }
    }

    return {
      success: true,
      branch,
      staged,
      modified,
      untracked
    };

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}
