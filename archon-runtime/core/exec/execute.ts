import { exec } from 'child_process';
import { promisify } from 'util';
import { ExecArgs, ExecResult } from '../types';
import { requestPermission } from '../../permissions/enhanced-gatekeeper';

const execAsync = promisify(exec);

/**
 * Execute a shell command
 * HIGH RISK - Requires explicit permission
 */
export async function execute(args: ExecArgs): Promise<ExecResult> {
  try {
    // Build command string
    const cmdString = args.args
      ? `${args.command} ${args.args.join(' ')}`
      : args.command;

    // Request permission with WARNING
    console.log('\n⚠️  WARNING: Shell command execution is HIGH RISK');
    console.log(`Command: ${cmdString}`);

    const allowed = await requestPermission('execute', cmdString);
    if (!allowed) {
      return {
        success: false,
        error: 'Permission denied by user'
      };
    }

    // Execute with timeout
    const timeout = args.timeout || 30000; // 30 seconds default

    const { stdout, stderr } = await execAsync(cmdString, {
      cwd: args.cwd || process.cwd(),
      timeout,
      maxBuffer: 1024 * 1024 // 1MB buffer
    });

    return {
      success: true,
      stdout: stdout.trim(),
      stderr: stderr.trim(),
      exitCode: 0
    };

  } catch (error: any) {
    return {
      success: false,
      stdout: error.stdout || '',
      stderr: error.stderr || error.message,
      exitCode: error.code || 1,
      error: error.message
    };
  }
}
