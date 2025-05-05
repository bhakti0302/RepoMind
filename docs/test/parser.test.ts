import fs from 'fs';
import path from 'path';
import { CodeChunk } from '../src/parser/types';

function saveChunks(chunks: CodeChunk[]) {
  const debugPath = path.join(__dirname, '../debug_chunks');
  if (!fs.existsSync(debugPath)) fs.mkdirSync(debugPath);

  chunks.forEach((chunk, i) => {
    const filename = path.join(debugPath, `chunk_${i + 1}.json`);
    fs.writeFileSync(filename, JSON.stringify(chunk, null, 2));
  });

  console.log(`🔍 Wrote ${chunks.length} chunks to debug_chunks/`);
}
