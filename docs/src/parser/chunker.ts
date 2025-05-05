import { CodeChunk, ParsedFunction } from './types';
import { v4 as uuidv4 } from 'uuid';

export function chunkFunctions(
  functions: ParsedFunction[],
  imports: string[],
  maxLines = 300
): CodeChunk[] {
  const chunks: CodeChunk[] = [];
  let current: ParsedFunction[] = [];
  let totalLines = 0;

  for (const fn of functions) {
    const lines = fn.endLine - fn.startLine + 1;
    if (totalLines + lines > maxLines && current.length > 0) {
      chunks.push({
        id: uuidv4(),
        language: 'javascript',
        startLine: current[0].startLine,
        endLine: current[current.length - 1].endLine,
        functions: current,
        imports,
      });
      current = [];
      totalLines = 0;
    }

    current.push(fn);
    totalLines += lines;
  }

  if (current.length > 0) {
    chunks.push({
      id: uuidv4(),
      language: 'javascript',
      startLine: current[0].startLine,
      endLine: current[current.length - 1].endLine,
      functions: current,
      imports,
    });
  }

  return chunks;
}
