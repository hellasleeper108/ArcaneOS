import { readFile as fsReadFile } from 'fs/promises';
import { requestPermission } from '../file_guard';

export const readFile = async (path: string): Promise<string | null> => {
  try {
    const permitted = await requestPermission('read', path);
    if (!permitted) {
      console.warn(`READ DENIED: ${path}`);
      return null;
    }

    return await fsReadFile(path, 'utf8');
  } catch (error) {
    console.error(`READ ERROR: ${path}`, error);
    return null;
  }
};

export default readFile;
