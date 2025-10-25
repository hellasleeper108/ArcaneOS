import fs from 'fs/promises';
import path from 'path';
import { WriteArgs, WriteResult } from '../types';
import { requestPermission } from '../../permissions/gatekeeper';

/**
 * Writes content to a file, creating it if it doesn't exist
 * Requires permission for each execution
 */
export async function write(args: WriteArgs): Promise<WriteResult> {
  try {
    // Request permission
    const allowed = await requestPermission('write', args.path);
    if (!allowed) {
      return {
        success: false,
        error: 'Permission denied by user'
      };
    }

    // Resolve path
    const resolvedPath = path.resolve(args.path);

    // Ensure directory exists
    const dir = path.dirname(resolvedPath);
    await fs.mkdir(dir, { recursive: true });

    // Write file
    await fs.writeFile(resolvedPath, args.content, 'utf-8');

    // Get byte count
    const stats = await fs.stat(resolvedPath);

    return {
      success: true,
      bytesWritten: stats.size
    };

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}
