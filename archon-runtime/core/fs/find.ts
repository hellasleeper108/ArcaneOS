import { glob } from 'glob';
import path from 'path';
import { FindArgs, FindResult } from '../types';
import { requestPermission } from '../../permissions/gatekeeper';

/**
 * Recursively searches for files matching a glob pattern
 * Requires permission for each execution
 */
export async function find(args: FindArgs): Promise<FindResult> {
  try {
    // Request permission
    const allowed = await requestPermission('find', args.base);
    if (!allowed) {
      return {
        success: false,
        error: 'Permission denied by user'
      };
    }

    // Resolve base path
    const basePath = path.resolve(args.base);

    // Build full pattern
    const fullPattern = path.join(basePath, args.pattern);

    // Execute glob search
    const files = await glob(fullPattern, {
      nodir: true,  // Only return files, not directories
      dot: false,   // Exclude dotfiles by default
      ignore: ['**/node_modules/**', '**/dist/**', '**/.git/**']
    });

    // Make paths relative to base for cleaner output
    const relativeFiles = files.map(f => path.relative(basePath, f));

    return {
      success: true,
      files: relativeFiles,
      count: relativeFiles.length
    };

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}
