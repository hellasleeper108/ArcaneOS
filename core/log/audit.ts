import { appendFile, readFile, writeFile } from 'fs/promises';
import { resolve } from 'path';

const LOG_FILE = resolve('arcane_log.txt');
const MAX_LINES = 1000;

const formatLine = (
  action: string,
  path: string,
  status: 'approved' | 'denied' | 'error',
  details?: string,
) => {
  const timestamp = new Date().toISOString();
  const payload = {
    timestamp,
    action,
    path,
    status,
    details,
  };
  return JSON.stringify(payload);
};

const pruneLog = async () => {
  try {
    const contents = await readFile(LOG_FILE, 'utf8');
    const lines = contents.trim().split('\n');
    if (lines.length <= MAX_LINES) return;
    const pruned = lines.slice(lines.length - MAX_LINES).join('\n') + '\n';
    await writeFile(LOG_FILE, pruned, 'utf8');
  } catch {
    // ignore if file does not exist or cannot be read
  }
};

export const logAction = async (
  action: string,
  path: string,
  status: 'approved' | 'denied' | 'error',
  details?: string,
): Promise<void> => {
  try {
    await appendFile(LOG_FILE, formatLine(action, path, status, details) + '\n', 'utf8');
    await pruneLog();
  } catch (error) {
    console.error('AUDIT LOG FAIL', error);
  }
};

export default logAction;
