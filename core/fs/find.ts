import { readdir, stat } from 'fs/promises';
import { join, resolve } from 'path';
import { performance } from 'perf_hooks';
import { requestPermission } from '../file_guard';

const MAX_DEPTH = 4;

const matchesPattern = (name: string, pattern: string | RegExp): boolean => {
  if (pattern instanceof RegExp) return pattern.test(name);
  if (pattern.includes('*') || pattern.includes('?')) {
    const escaped = pattern
      .replace(/[.+^${}()|[\]\\]/g, '\\$&')
      .replace(/\\\*/g, '.*')
      .replace(/\\\?/g, '.');
    const regex = new RegExp(`^${escaped}$`);
    return regex.test(name);
  }
  return name.includes(pattern);
};

const walk = async (
  base: string,
  pattern: string | RegExp,
  depth: number,
  results: string[],
) => {
  if (depth > MAX_DEPTH) return;
  let entries: string[];
  try {
    entries = await readdir(base);
  } catch (error) {
    return;
  }

  for (const entry of entries) {
    const fullPath = join(base, entry);
    let stats;
    try {
      stats = await stat(fullPath);
    } catch (error) {
      continue;
    }
    if (stats.isDirectory()) {
      await walk(fullPath, pattern, depth + 1, results);
    } else if (stats.isFile() && matchesPattern(entry, pattern)) {
      results.push(resolve(fullPath));
    }
  }
};

export const findFiles = async (
  basePath: string,
  pattern: string | RegExp,
): Promise<string[]> => {
  const permitted = await requestPermission('find', basePath);
  if (!permitted) {
    console.warn(`FIND DENIED: ${basePath}`);
    return [];
  }

  const start = performance.now();
  const results: string[] = [];
  await walk(resolve(basePath), pattern, 0, results);
  const duration = (performance.now() - start).toFixed(1);
  console.info(`FIND OK: ${results.length} matches in ${duration}ms`);
  return results;
};

export default findFiles;
