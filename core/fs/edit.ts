import { readFile as fsReadFile, writeFile as fsWriteFile } from 'fs/promises';
import { createInterface } from 'readline/promises';
import { stdin as input, stdout as output } from 'process';
import { requestPermission } from '../file_guard';

export interface PatchInstruction {
  find: string;
  replace: string;
}

export const applyPatch = async (path: string, patch: PatchInstruction): Promise<boolean> => {
  try {
    const permitted = await requestPermission('edit', path);
    if (!permitted) {
      console.warn(`EDIT DENIED: ${path}`);
      return false;
    }

    const original = await fsReadFile(path, 'utf8');
    const index = original.indexOf(patch.find);
    if (index === -1) {
      console.warn(`EDIT ABORT: Pattern not found in ${path}`);
      return false;
    }

    const newContent =
      original.slice(0, index) + patch.replace + original.slice(index + patch.find.length);

    console.log('--- old');
    console.log(patch.find);
    console.log('+++ new');
    console.log(patch.replace);

    const rl = createInterface({ input, output });
    try {
      const answer = await rl.question('Apply change? [y/n] ');
      if (answer.trim().toLowerCase() !== 'y') {
        console.info(`EDIT ABORTED BY USER: ${path}`);
        return false;
      }
    } finally {
      rl.close();
    }

    await fsWriteFile(path, newContent, 'utf8');
    console.info(`EDIT OK: ${path}`);
    return true;
  } catch (error) {
    console.error(`EDIT FAIL: ${path}`, error);
    return false;
  }
};

export default applyPatch;
