import Parser, { Language as TreeSitterLanguage } from 'tree-sitter';
import JavaScript = require('tree-sitter-javascript');
import { getAllFunctions } from './traversals';

const parser = new Parser();
parser.setLanguage(JavaScript as unknown as TreeSitterLanguage);

export function parseSourceCode(code: string) {
  const tree = parser.parse(code);
  const root = tree.rootNode;
  return getAllFunctions(root, code);
}
