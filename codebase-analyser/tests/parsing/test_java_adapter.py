#!/usr/bin/env python3
"""
Test script for the Java parser adapter.
"""

import os
import sys
import json
from pathlib import Path

from codebase_analyser.parsing.java_parser_adapter import JavaParserAdapter
from codebase_analyser.chunking.code_chunk import CodeChunk


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_java_adapter.py <java_file>")
        return 1

    file_path = sys.argv[1]
    
    # Parse the file
    result = JavaParserAdapter.parse_file(file_path)
    if not result:
        print(f"Error: Failed to parse {file_path}")
        return 1
    
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
        for imp in result['imports']:
            print(f"  - {imp['name']}")
    else:
        print("Imports: None")
    
    # Print class information
    if result.get('classes'):
        print(f"Classes: {len(result['classes'])}")
        for cls in result['classes']:
            print(f"  - {cls['name']}")
            
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
                    params = ", ".join([f"{p.get('type', '')} {p.get('name', '')}" for p in method.get('parameters', [])])
                    print(f"      - {method['name']}({params}): {method.get('return_type', 'void')}")
            
            # Print fields
            if cls.get('fields'):
                print(f"    Fields: {len(cls['fields'])}")
                for field in cls['fields']:
                    print(f"      - {field['name']}: {field.get('type', '')}")
    else:
        print("Classes: None")
    
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
    else:
        print("Dependencies: None")
    
    # Convert to CodeChunk objects
    chunks = []
    chunk_map = {}
    
    # First pass: create all chunks
    for chunk_data in result['chunks']:
        # Create the chunk
        chunk = CodeChunk(
            node_id=chunk_data['node_id'],
            chunk_type=chunk_data['chunk_type'],
            content=chunk_data['content'],
            file_path=chunk_data['file_path'],
            start_line=chunk_data['start_line'],
            end_line=chunk_data['end_line'],
            language=chunk_data['language'],
            name=chunk_data.get('name'),
            qualified_name=chunk_data.get('qualified_name')
        )
        
        # Add metadata and context
        if 'metadata' in chunk_data:
            chunk.metadata = chunk_data['metadata']
        if 'context' in chunk_data:
            chunk.context = chunk_data['context']
        
        # Store in map and list
        chunk_map[chunk.node_id] = chunk
        chunks.append(chunk)
    
    # Second pass: establish parent-child relationships
    for chunk_data in result['chunks']:
        if 'parent_id' in chunk_data and chunk_data['parent_id']:
            child = chunk_map.get(chunk_data['node_id'])
            parent = chunk_map.get(chunk_data['parent_id'])
            if child and parent:
                parent.add_child(child)
    
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
    
    return 0


if __name__ == "__main__":
    main()
