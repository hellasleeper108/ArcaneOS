import { rm } from 'fs/promises';
import { createInterface } from 'readline/promises';
import { stdin as input, stdout as output } from 'process';
import { requestPermission } from '../file_guard';

const promptConfirm = async (message: string): Promise<boolean> => {
  const rl = createInterface({ input, output });
  try {
    const answer = await rl.question(`${message} `);
    return answer.trim().toLowerCase() === 'y';
  } finally {
    rl.close();
  }
};

export const deleteFile = async (path: string): Promise<boolean> => {
  try {
    const permitted = await requestPermission('delete', path);
    if (!permitted) {
      console.warn(`DELETE DENIED: ${path}`);
      return false;
    }

    const firstConfirm = await promptConfirm(`Delete ${path}? [y/n]`);
    if (!firstConfirm) {
      console.info(`DELETE ABORTED FIRST PROMPT: ${path}`);
      return false;
    }

    const secondConfirm = await promptConfirm('This action cannot be undone. Confirm delete? [y/n]');
    if (!secondConfirm) {
      console.info(`DELETE ABORTED SECOND PROMPT: ${path}`);
      return false;
    }

    await rm(path, { force: false, recursive: false });
    console.info(`DELETE OK: ${path}`);
    return true;
  } catch (error) {
    console.error(`DELETE FAIL: ${path}`, error);
    return false;
  }
};

export default deleteFile;
