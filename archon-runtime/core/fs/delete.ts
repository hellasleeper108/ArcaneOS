import fs from 'fs-extra';
import path from 'path';
import { DeleteArgs, DeleteResult } from '../types';
import { requestPermission } from '../../permissions/gatekeeper';

/**
 * Deletes a file or directory
 * Requires permission for each execution
 * WARNING: This operation is irreversible
 */
export async function deleteResource(args: DeleteArgs): Promise<DeleteResult> {
  try {
    // Request permission
    const allowed = await requestPermission('delete', args.path);
    if (!allowed) {
      return {
        success: false,
        error: 'Permission denied by user'
      };
    }

    // Resolve path
    const resolvedPath = path.resolve(args.path);

    // Check if path exists
    const exists = await fs.pathExists(resolvedPath);
    if (!exists) {
      return {
        success: false,
        error: `Path not found: ${args.path}`
      };
    }

    // Remove file or directory
    await fs.remove(resolvedPath);

    return {
      success: true
    };

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}
