import { requestPermission } from '../file_guard';
import readFileFn from '../fs/read';
import { writeFile as writeFileFn, appendFile as appendFileFn } from '../fs/write';
import editFileFn, { PatchInstruction } from '../fs/edit';
import findFilesFn from '../fs/find';
import deleteFileFn from '../fs/delete';

type ToolResponse<T = unknown> = {
  success: boolean;
  message: string;
  data?: T;
};

export const readFileTool = async (path: string): Promise<ToolResponse<string | null>> => {
  const permitted = await requestPermission('read', path);
  if (!permitted) {
    return { success: false, message: `Read permission denied for ${path}` };
  }

  const content = await readFileFn(path);
  if (content === null) {
    return { success: false, message: `Failed to read file ${path}` };
  }
  return { success: true, message: `Read ${path}`, data: content };
};

export const writeFileTool = async (
  path: string,
  content: string,
  overwrite = true,
): Promise<ToolResponse> => {
  const permitted = await requestPermission('write', path);
  if (!permitted) {
    return { success: false, message: `Write permission denied for ${path}` };
  }

  const ok = await writeFileFn(path, content, overwrite);
  return ok
    ? { success: true, message: `Wrote to ${path}` }
    : { success: false, message: `Failed to write ${path}` };
};

export const appendFileTool = async (path: string, content: string): Promise<ToolResponse> => {
  const permitted = await requestPermission('write', path);
  if (!permitted) {
    return { success: false, message: `Append permission denied for ${path}` };
  }

  const ok = await appendFileFn(path, content);
  return ok
    ? { success: true, message: `Appended to ${path}` }
    : { success: false, message: `Failed to append ${path}` };
};

export const editFileTool = async (
  path: string,
  patch: PatchInstruction,
): Promise<ToolResponse> => {
  const permitted = await requestPermission('edit', path);
  if (!permitted) {
    return { success: false, message: `Edit permission denied for ${path}` };
  }

  const ok = await editFileFn(path, patch);
  return ok
    ? { success: true, message: `Edited ${path}` }
    : { success: false, message: `Failed to apply patch to ${path}` };
};

export const findFilesTool = async (
  basePath: string,
  pattern: string | RegExp,
): Promise<ToolResponse<string[]>> => {
  const permitted = await requestPermission('find', basePath);
  if (!permitted) {
    return { success: false, message: `Find permission denied for ${basePath}` };
  }

  const matches = await findFilesFn(basePath, pattern);
  return {
    success: true,
    message: `Found ${matches.length} matches in ${basePath}`,
    data: matches,
  };
};

export const deleteFileTool = async (path: string): Promise<ToolResponse> => {
  const permitted = await requestPermission('delete', path);
  if (!permitted) {
    return { success: false, message: `Delete permission denied for ${path}` };
  }

  const ok = await deleteFileFn(path);
  return ok
    ? { success: true, message: `Deleted ${path}` }
    : { success: false, message: `Failed to delete ${path}` };
};

export const archonFsTools = {
  'archon.fs.read': readFileTool,
  'archon.fs.write': writeFileTool,
  'archon.fs.append': appendFileTool,
  'archon.fs.edit': editFileTool,
  'archon.fs.find': findFilesTool,
  'archon.fs.delete': deleteFileTool,
};

export default archonFsTools;
