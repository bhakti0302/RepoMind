#!/usr/bin/env python3
"""
Test script to verify AST utility functions.
"""

import sys
from pathlib import Path
from codebase_analyser import CodebaseAnalyser
from codebase_analyser.utils.ast_utils import (
    traverse_ast, find_nodes_by_type, find_nodes_by_text,
    find_nodes_by_type_and_text, get_node_children_by_type,
    get_node_descendants, get_node_location, print_ast
)

def test_ast_utils(file_path):
    """Test AST utility functions on a file."""
    print(f"Testing AST utilities on {file_path}")
    
    # Create analyser with the parent directory as the repo path
    analyser = CodebaseAnalyser(file_path.parent)
    
    # Parse the file
    result = analyser.parse_file(file_path)
    
    if not result:
        print(f"Failed to parse {file_path}")
        return
    
    print(f"Successfully parsed {file_path}")
    print(f"Language: {result['language']}")
    
    # Get the AST and source code
    ast = result['ast']
    source_code = result['content'].encode('utf-8')
    
    # Test 1: Count nodes by type
    print("\nTest 1: Counting nodes by type")
    node_types = {}
    
    def count_node_types(node, _):
        node_type = node.type
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    traverse_ast(ast.root_node, count_node_types)
    
    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {node_type}: {count} nodes")
    
    # Test 2: Find specific node types
    print("\nTest 2: Finding specific node types")
    if result['language'] == 'java':
        # For Java files
        node_types_to_find = ['class_declaration', 'method_declaration', 'field_declaration']
    else:
        # For other languages, use generic types
        node_types_to_find = ['function_definition', 'class_definition', 'variable_declaration']
    
    for node_type in node_types_to_find:
        nodes = find_nodes_by_type(ast.root_node, node_type)
        print(f"  Found {len(nodes)} {node_type} nodes")
        
        # Print the first few nodes
        for i, node in enumerate(nodes[:3]):
            try:
                node_text = source_code[node.start_byte:node.end_byte].decode('utf-8')
                first_line = node_text.split('\n')[0][:50]
                print(f"    Node {i+1}: {first_line}...")
            except Exception as e:
                print(f"    Node {i+1}: <Error: {e}>")
    
    # Test 3: Find nodes by text
    print("\nTest 3: Finding nodes containing specific text")
    search_text = "main"  # Common text to search for
    text_nodes = find_nodes_by_text(ast.root_node, search_text, source_code)
    print(f"  Found {len(text_nodes)} nodes containing '{search_text}'")
    
    # Test 4: Print part of the AST
    print("\nTest 4: Printing part of the AST (first 5 levels)")
    print_ast(ast.root_node, source_code, max_depth=5)
    
    print("\nAST utility tests completed successfully")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_ast_utils.py <path_to_file>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    test_ast_utils(file_path)

if __name__ == "__main__":
    main()