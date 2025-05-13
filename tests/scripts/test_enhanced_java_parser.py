#!/usr/bin/env python3
"""
Test script for the enhanced Java parser.
"""

import os
import sys
import argparse
from pathlib import Path

from codebase_analyser.analyser import CodebaseAnalyser
from codebase_analyser.parsing.enhanced_java_parser import EnhancedJavaParser


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Test the enhanced Java parser")
    parser.add_argument("file_path", help="Path to a Java file to parse")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def test_enhanced_java_parser(file_path, verbose=False):
    """Test the enhanced Java parser on a Java file."""
    # Initialize the analyzer
    analyzer = CodebaseAnalyser(Path("."))
    
    # Make sure the enhanced Java parser is initialized
    if not analyzer.enhanced_java_parser:
        print("Error: Enhanced Java parser not initialized")
        return False
    
    # Parse the file
    print(f"Parsing file: {file_path}")
    result = analyzer.enhanced_java_parser.parse_file(file_path)
    
    if not result:
        print(f"Error: Failed to parse {file_path}")
        return False
    
    # Print basic information
    print(f"File: {result['path']}")
    print(f"Language: {result['language']}")
    
    # Print package information
    if result.get('package'):
        print(f"Package: {result['package']['name']}")
    else:
        print("Package: None")
    
    # Print import information
    if result.get('imports'):
        print(f"Imports: {len(result['imports'])}")
        if verbose:
            for imp in result['imports']:
                print(f"  - {imp['name']}")
    else:
        print("Imports: None")
    
    # Print class information
    if result.get('classes'):
        print(f"Classes: {len(result['classes'])}")
        for cls in result['classes']:
            print(f"  - {cls['name']}")
            
            if verbose:
                # Print superclass
                if cls.get('superclass'):
                    print(f"    Extends: {cls['superclass']}")
                
                # Print interfaces
                if cls.get('interfaces'):
                    print(f"    Implements: {', '.join(cls['interfaces'])}")
                
                # Print methods
                if cls.get('methods'):
                    print(f"    Methods: {len(cls['methods'])}")
                    for method in cls['methods']:
                        print(f"      - {method['name']}")
                
                # Print fields
                if cls.get('fields'):
                    print(f"    Fields: {len(cls['fields'])}")
                    for field in cls['fields']:
                        print(f"      - {field['name']}: {field['type']}")
    else:
        print("Classes: None")
    
    # Print interface information
    if result.get('interfaces'):
        print(f"Interfaces: {len(result['interfaces'])}")
        for interface in result['interfaces']:
            print(f"  - {interface['name']}")
            
            if verbose:
                # Print methods
                if interface.get('methods'):
                    print(f"    Methods: {len(interface['methods'])}")
                    for method in interface['methods']:
                        print(f"      - {method['name']}")
    else:
        print("Interfaces: None")
    
    # Print chunk information
    if result.get('chunks'):
        print(f"Chunks: {len(result['chunks'])}")
        
        # Count chunks by type
        chunk_types = {}
        for chunk in result['chunks']:
            chunk_type = chunk['chunk_type']
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        for chunk_type, count in chunk_types.items():
            print(f"  - {chunk_type}: {count}")
    else:
        print("Chunks: None")
    
    # Print dependency information
    if result.get('dependencies'):
        print(f"Dependencies: {len(result['dependencies'])}")
        
        # Count dependencies by type
        dep_types = {}
        for dep in result['dependencies']:
            dep_type = dep['type']
            dep_types[dep_type] = dep_types.get(dep_type, 0) + 1
        
        for dep_type, count in dep_types.items():
            print(f"  - {dep_type}: {count}")
            
        if verbose:
            for dep in result['dependencies']:
                print(f"  - {dep['source_id']} -> {dep['target_id']} ({dep['type']})")
                print(f"    {dep['description']}")
    else:
        print("Dependencies: None")
    
    # Convert to CodeChunk objects
    chunks = analyzer.get_chunks(result)
    print(f"CodeChunk objects: {len(chunks)}")
    
    # Count chunks by type
    chunk_types = {}
    for chunk in chunks:
        chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1
    
    for chunk_type, count in chunk_types.items():
        print(f"  - {chunk_type}: {count}")
    
    # Count parent-child relationships
    parent_child_count = 0
    for chunk in chunks:
        parent_child_count += len(chunk.children)
    
    print(f"Parent-child relationships: {parent_child_count}")
    
    # Count reference relationships
    reference_count = 0
    for chunk in chunks:
        reference_count += len(chunk.references)
    
    print(f"Reference relationships: {reference_count}")
    
    return True


def main():
    """Main entry point."""
    args = parse_args()
    success = test_enhanced_java_parser(args.file_path, args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
