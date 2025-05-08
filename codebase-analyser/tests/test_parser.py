#!/usr/bin/env python3
"""
Simple test script to verify Tree-sitter installation and basic parsing.
"""

import sys
from pathlib import Path
from codebase_analyser import CodebaseAnalyser

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_parser.py <path_to_file>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    # Create analyser with the parent directory as the repo path
    analyser = CodebaseAnalyser(file_path.parent)
    
    # Parse the file
    result = analyser.parse_file(file_path)
    
    if result:
        print(f"Successfully parsed {file_path}")
        print(f"Language: {result['language']}")
        print(f"AST root node: {result['ast'].root_node.type}")
        print(f"Number of children: {len(result['ast'].root_node.children)}")
    else:
        print(f"Failed to parse {file_path}")

if __name__ == "__main__":
    main()