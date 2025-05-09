#!/usr/bin/env python3
"""
Test script to verify Java parsing functionality.
"""

import sys
import json
from pathlib import Path
from codebase_analyser import CodebaseAnalyser

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_java_parser.py <path_to_java_file>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    if file_path.suffix.lower() != '.java':
        print(f"Not a Java file: {file_path}")
        return
    
    # Create analyser with the parent directory as the repo path
    analyser = CodebaseAnalyser(file_path.parent)
    
    # Parse the Java file
    result = analyser.parse_file(file_path)
    
    if result:
        print(f"Successfully parsed Java file: {file_path}")
        print(f"Package: {result.get('package')}")
        print(f"Imports: {', '.join(result.get('imports', []))}")
        
        print("\nClasses:")
        for cls in result.get('classes', []):
            print(f"  - {cls['name']}")
            if cls.get('superclass'):
                print(f"    Extends: {cls['superclass']}")
            if cls.get('interfaces'):
                print(f"    Implements: {', '.join(cls['interfaces'])}")
            
            print(f"    Fields: {len(cls.get('fields', []))}")
            for field in cls.get('fields', []):
                print(f"      - {field['type']} {field['name']}")
            
            print(f"    Methods: {len(cls.get('methods', []))}")
            for method in cls.get('methods', []):
                params = [f"{p['type']} {p['name']}" for p in method.get('parameters', [])]
                print(f"      - {method['return_type']} {method['name']}({', '.join(params)})")
        
        # Save the full result to a JSON file for inspection
        output_file = file_path.with_suffix('.json')
        with open(output_file, 'w') as f:
            # Convert non-serializable objects to strings
            serializable_result = {k: (str(v) if k == 'ast' else v) for k, v in result.items()}
            json.dump(serializable_result, f, indent=2)
        
        print(f"\nFull parse result saved to {output_file}")
    else:
        print(f"Failed to parse {file_path}")

if __name__ == "__main__":
    main()