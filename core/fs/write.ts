import { access, constants, writeFile as fsWriteFile, appendFile as fsAppendFile } from 'fs/promises';
import { requestPermission } from '../file_guard';

const fileExists = async (path: string): Promise<boolean> => {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
};

export const writeFile = async (
  path: string,
  content: string,
  overwrite = true,
): Promise<boolean> => {
  try {
    if (!overwrite && (await fileExists(path))) {
      console.warn(`WRITE ABORT (exists): ${path}`);
      return false;
    }

    const permitted = await requestPermission('write', path);
    if (!permitted) {
      console.warn(`WRITE DENIED: ${path}`);
      return false;
    }

    await fsWriteFile(path, content, 'utf8');
    console.info(`WRITE OK: ${path}`);
    return true;
  } catch (error) {
    console.error(`WRITE FAIL: ${path}`, error);
    return false;
  }
};

export const appendFile = async (path: string, content: string): Promise<boolean> => {
  try {
    const permitted = await requestPermission('write', path);
    if (!permitted) {
      console.warn(`APPEND DENIED: ${path}`);
      return false;
    }

    await fsAppendFile(path, content, 'utf8');
    console.info(`APPEND OK: ${path}`);
    return true;
  } catch (error) {
    console.error(`APPEND FAIL: ${path}`, error);
    return false;
  }
};

export default {
  writeFile,
  appendFile,
};
