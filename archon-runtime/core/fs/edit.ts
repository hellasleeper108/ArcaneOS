import fs from 'fs/promises';
import path from 'path';
import { EditArgs, EditResult } from '../types';
import { requestPermission } from '../../permissions/gatekeeper';

/**
 * Applies a find-and-replace patch to an existing file
 * Requires permission for each execution
 */
export async function edit(args: EditArgs): Promise<EditResult> {
  try {
    // Request permission
    const allowed = await requestPermission('edit', args.path);
    if (!allowed) {
      return {
        success: false,
        error: 'Permission denied by user'
      };
    }

    // Resolve path
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

    // Read current content
    const content = await fs.readFile(resolvedPath, 'utf-8');

    // Count matches
    const regex = new RegExp(escapeRegex(args.find), 'g');
    const matches = content.match(regex);
    const matchCount = matches ? matches.length : 0;

    if (matchCount === 0) {
      return {
        success: false,
        error: 'No matches found for the specified text'
      };
    }

    // Apply replacement
    const newContent = content.replace(regex, args.replace);

    // Write back
    await fs.writeFile(resolvedPath, newContent, 'utf-8');

    return {
      success: true,
      matchCount
    };

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Escapes special regex characters in a string
 */
function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
