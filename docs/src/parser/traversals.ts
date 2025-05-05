import { SyntaxNode } from 'tree-sitter';
import { ParsedFunction } from './types';

export function getAllFunctions(root: SyntaxNode, code: string): ParsedFunction[] {
  const functions: ParsedFunction[] = [];

  const visit = (node: SyntaxNode, parentClass: string | null = null) => {
    if (node.type === 'function_declaration' || node.type === 'method_definition') {
      const name = node.firstChild?.text ?? 'anonymous';
      const fnCode = code.slice(node.startIndex, node.endIndex);
      functions.push({
        name: parentClass ? `${parentClass}.${name}` : name,
        startLine: node.startPosition.row + 1,
        endLine: node.endPosition.row + 1,
        code: fnCode,
      });
    } else if (node.type === 'class_declaration') {
      const className = node.childForFieldName('name')?.text ?? 'UnnamedClass';
      for (let i = 0; i < node.childCount; i++) {
        const child = node.child(i);
        if (child) visit(child, className);
      }
      return;
    }

    for (let i = 0; i < node.childCount; i++) {
      const child = node.child(i);
      if (child) visit(child, parentClass);
    }
  };

  visit(root);
  return functions;
}

export function extractImports(root: SyntaxNode, code: string): string[] {
  const imports: string[] = [];
  for (let i = 0; i < root.childCount; i++) {
    const child = root.child(i);
    if (child && (child.type === 'import_statement' || child.type === 'require_call')) {
      imports.push(code.slice(child.startIndex, child.endIndex));
    }
  }
  return imports;
}
