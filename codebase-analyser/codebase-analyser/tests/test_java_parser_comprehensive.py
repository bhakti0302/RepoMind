#!/usr/bin/env python3
"""
Comprehensive test script for Java parsing functionality.
"""

import sys
import json
from pathlib import Path
from codebase_analyser import CodebaseAnalyser
from codebase_analyser.utils.ast_utils import print_ast

def test_java_parser(file_path):
    """Test Java parser on a file with detailed output."""
    print(f"Testing Java parser on {file_path}")
    
    # Create analyser with the parent directory as the repo path
    analyser = CodebaseAnalyser(file_path.parent)
    
    # Parse the Java file
    result = analyser.parse_file(file_path)
    
    if not result:
        print(f"Failed to parse {file_path}")
        return
    
    print(f"Successfully parsed Java file: {file_path}")
    
    # Basic information
    print(f"\nBasic Information:")
    print(f"  Package: {result.get('package')}")
    print(f"  Imports: {', '.join(result.get('imports', []))}")
    
    # Classes
    print(f"\nClasses ({len(result.get('classes', []))}):")
    for i, cls in enumerate(result.get('classes', [])):
        print(f"\n  Class {i+1}: {cls['name']}")
        
        # Inheritance
        if cls.get('superclass'):
            print(f"    Extends: {cls['superclass']}")
        if cls.get('interfaces'):
            print(f"    Implements: {', '.join(cls['interfaces'])}")
        
        # Fields
        print(f"\n    Fields ({len(cls.get('fields', []))}):")
        for field in cls.get('fields', []):
            print(f"      - {field['type']} {field['name']} (line {field['start_line']})")
        
        # Methods
        print(f"\n    Methods ({len(cls.get('methods', []))}):")
        for method in cls.get('methods', []):
            params = [f"{p['type']} {p['name']}" for p in method.get('parameters', [])]
            print(f"      - {method['return_type']} {method['name']}({', '.join(params)}) (lines {method['start_line']}-{method['end_line']})")
    
    # Methods outside classes
    methods = [m for m in result.get('methods', []) if not any(m in cls.get('methods', []) for cls in result.get('classes', []))]
    if methods:
        print(f"\nMethods outside classes ({len(methods)}):")
        for method in methods:
            params = [f"{p['type']} {p['name']}" for p in method.get('parameters', [])]
            print(f"  - {method['return_type']} {method['name']}({', '.join(params)}) (lines {method['start_line']}-{method['end_line']})")
    
    # AST structure
    print("\nAST Structure (first 3 levels):")
    print_ast(result['ast'].root_node, result['content'].encode('utf-8'), max_depth=3)
    
    # Save the full result to a JSON file for inspection
    output_file = file_path.with_suffix('.json')
    with open(output_file, 'w') as f:
        # Convert non-serializable objects to strings
        serializable_result = {k: (str(v) if k == 'ast' else v) for k, v in result.items()}
        json.dump(serializable_result, f, indent=2)
    
    print(f"\nFull parse result saved to {output_file}")
    print("\nJava parser test completed successfully")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_java_parser_comprehensive.py <path_to_java_file>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    if file_path.suffix.lower() != '.java':
        print(f"Not a Java file: {file_path}")
        return
    
    test_java_parser(file_path)

if __name__ == "__main__":
    main()