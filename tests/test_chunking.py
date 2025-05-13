#!/usr/bin/env python3
"""
Test script to verify code chunking functionality.
"""

import sys
import json
from pathlib import Path
from codebase_analyser import CodebaseAnalyser

def test_chunking(file_path):
    """Test code chunking on a file."""
    print(f"Testing code chunking on {file_path}")
    
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
    
    print(f"\nCreated {len(chunks)} chunks:")
    
    # Print information about each chunk
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}: {chunk.chunk_type}")
        print(f"  Lines: {chunk.start_line}-{chunk.end_line} ({chunk.end_line - chunk.start_line + 1} lines)")
        print(f"  File: {chunk.file_path}")
        
        # Print metadata
        if chunk.metadata:
            print("  Metadata:")
            for key, value in chunk.metadata.items():
                if key == "context" and value:
                    context_preview = value[:50] + "..." if len(value) > 50 else value
                    print(f"    {key}: {context_preview}")
                elif isinstance(value, list) and value:
                    print(f"    {key}: {len(value)} items")
                else:
                    print(f"    {key}: {value}")
        
        # Print content preview
        content_lines = chunk.content.split('\n')
        preview_lines = 3
        if len(content_lines) > preview_lines * 2:
            content_preview = '\n'.join(content_lines[:preview_lines] + ['...'] + content_lines[-preview_lines:])
        else:
            content_preview = chunk.content
        
        print(f"  Content Preview:")
        for line in content_preview.split('\n')[:10]:  # Limit to 10 lines max
            print(f"    {line}")
    
    # Save chunks to a JSON file for inspection
    output_file = file_path.with_suffix('.chunks.json')
    with open(output_file, 'w') as f:
        json.dump([chunk.to_dict() for chunk in chunks], f, indent=2)
    
    print(f"\nChunks saved to {output_file}")
    print("Chunking test completed successfully")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_chunking.py <path_to_file>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    test_chunking(file_path)

if __name__ == "__main__":
    main()
