#!/usr/bin/env python3
"""
Test script to verify hierarchical code chunking functionality.
"""

import sys
import json
from pathlib import Path
from codebase_analyser import CodebaseAnalyser

def print_chunk_hierarchy(chunk, indent=0):
    """Print a chunk and its children with indentation to show hierarchy."""
    indent_str = "  " * indent
    print(f"{indent_str}Chunk: {chunk.chunk_type} (lines {chunk.start_line}-{chunk.end_line}, {chunk.end_line - chunk.start_line + 1} lines)")
    print(f"{indent_str}  Level: {chunk.metadata.get('level', 'unknown')}")
    print(f"{indent_str}  Node type: {chunk.metadata.get('node_type', 'unknown')}")
    
    # Print a preview of the content
    content_lines = chunk.content.split('\n')
    if len(content_lines) > 4:
        content_preview = '\n'.join(content_lines[:2] + ['...'] + content_lines[-2:])
    else:
        content_preview = chunk.content
    
    print(f"{indent_str}  Content preview:")
    for line in content_preview.split('\n')[:4]:  # Limit to 4 lines max
        print(f"{indent_str}    {line}")
    
    # Print children
    if chunk.children:
        print(f"{indent_str}  Children: {len(chunk.children)}")
        for child in chunk.children:
            print_chunk_hierarchy(child, indent + 1)
    else:
        print(f"{indent_str}  Children: None")
    
    print()  # Empty line for readability

def test_hierarchical_chunking(file_path):
    """Test hierarchical code chunking on a file."""
    print(f"Testing hierarchical code chunking on {file_path}")
    
    # Create analyser with the parent directory as the repo path
    analyser = CodebaseAnalyser(file_path.parent)
    
    # Parse the file
    result = analyser.parse_file(file_path)
    
    if not result:
        print(f"Failed to parse {file_path}")
        return
    
    print(f"Successfully parsed {file_path}")
    print(f"Language: {result['language']}")
    
    # Get chunks for the file
    chunks = analyser.get_chunks(result)
    
    print(f"\nCreated {len(chunks)} top-level chunks")
    
    # Print the chunk hierarchy
    for chunk in chunks:
        print_chunk_hierarchy(chunk)
    
    # Count total chunks (including children)
    total_chunks = 0
    for chunk in chunks:
        total_chunks += 1 + len(chunk.get_descendants())
    
    print(f"Total chunks (including children): {total_chunks}")
    
    # Save chunks to a JSON file for inspection
    output_file = file_path.with_suffix('.hierarchy.json')
    
    # Create a serializable representation of the chunk hierarchy
    def chunk_to_dict(chunk):
        chunk_dict = chunk.to_dict()
        chunk_dict['children'] = [chunk_to_dict(child) for child in chunk.children]
        return chunk_dict
    
    with open(output_file, 'w') as f:
        json.dump([chunk_to_dict(chunk) for chunk in chunks], f, indent=2)
    
    print(f"\nChunk hierarchy saved to {output_file}")
    print("Hierarchical chunking test completed successfully")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_hierarchical_chunking.py <path_to_file>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    test_hierarchical_chunking(file_path)

if __name__ == "__main__":
    main()
