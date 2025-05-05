import fs from 'fs';
import path from 'path';
import { parseSourceCode } from '../src/parser/index';
import { chunkFunctions } from '../src/parser/chunker';
import { extractImports } from '../src/parser/traversals';
import { CodeChunk } from '../src/parser/types';
import * as JavaScriptModule from 'tree-sitter-javascript';
import Parser from 'tree-sitter';



// ----------- CONFIG ----------
const inputFilePath = process.argv[2];
const outputDir = path.join(__dirname, '../debug_chunks');
// -----------------------------

if (!inputFilePath) {
  console.error('❌ Please provide a file path to parse (e.g., node scripts/parse-and-chunk.js ./sample.js)');
  process.exit(1);
}

const code = fs.readFileSync(inputFilePath, 'utf-8');

// Parse + chunk pipeline
const parser = new Parser();
parser.setLanguage(JavaScriptModule as unknown as Parser.Language);const tree = parser.parse(code);
const root = tree.rootNode;

const functions = parseSourceCode(code);
const imports = extractImports(root, code);
const chunks: CodeChunk[] = chunkFunctions(functions, imports);

// Save output
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);
chunks.forEach((chunk, i) => {
  const fileName = path.join(outputDir, `chunk_${i + 1}.json`);
  fs.writeFileSync(fileName, JSON.stringify(chunk, null, 2));
});

console.log(`✅ Saved ${chunks.length} chunk(s) to debug_chunks/`);
