import fs from 'fs/promises';
import path from 'path';
import { ReadArgs, ReadResult } from '../types';
import { requestPermission } from '../../permissions/gatekeeper';

/**
 * Reads the contents of a text file
 * Requires permission for each execution
 */
export async function read(args: ReadArgs): Promise<ReadResult> {
  try {
    // Request permission
    const allowed = await requestPermission('read', args.path);
    if (!allowed) {
      return {
        success: false,
        error: 'Permission denied by user'
      };
    }

    // Resolve and validate path
    const resolvedPath = path.resolve(args.path);

    // Check if file exists
    try {
      await fs.access(resolvedPath);
    } catch {
      return {
        success: false,
        error: `File not found: ${args.path}`
      };
    }

    // Read file contents
    const content = await fs.readFile(resolvedPath, 'utf-8');

    return {
      success: true,
      content
    };

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}
