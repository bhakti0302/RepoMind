#!/usr/bin/env python3
"""
Test script to verify context preservation and structural integrity in code chunks.
"""

import sys
import json
from pathlib import Path
from codebase_analyser import CodebaseAnalyser

def test_context_preservation(file_path):
    """Test context preservation and structural integrity on a file."""
    print(f"Testing context preservation on {file_path}")
    
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
    
    # Get all chunks including descendants
    all_chunks = []
    for chunk in chunks:
        all_chunks.append(chunk)
        all_chunks.extend(chunk.get_descendants())
    
    print(f"Total chunks (including children): {len(all_chunks)}")
    
    # Test context preservation
    print("\n=== Context Preservation ===")
    context_preserved_count = 0
    for chunk in all_chunks:
        if chunk.context:
            context_preserved_count += 1
            print(f"\nChunk: {chunk.chunk_type} (lines {chunk.start_line}-{chunk.end_line})")
            print(f"  Name: {chunk.name}")
            print(f"  Qualified name: {chunk.qualified_name}")
            print(f"  Context:")
            for key, value in chunk.context.items():
                if isinstance(value, list):
                    print(f"    {key}: {len(value)} items")
                    if len(value) > 0:
                        print(f"      Example: {value[0]}")
                else:
                    print(f"    {key}: {value}")
    
    print(f"\nContext preserved in {context_preserved_count} out of {len(all_chunks)} chunks")
    
    # Test structural integrity
    print("\n=== Structural Integrity ===")
    valid_chunks = 0
    for chunk in all_chunks:
        is_valid = chunk.validate_structural_integrity()
        if is_valid:
            valid_chunks += 1
        else:
            print(f"\nInvalid chunk: {chunk.chunk_type} (lines {chunk.start_line}-{chunk.end_line})")
            print(f"  Name: {chunk.name}")
            print(f"  Qualified name: {chunk.qualified_name}")
    
    print(f"\nStructural integrity validated for {valid_chunks} out of {len(all_chunks)} chunks")
    
    # Test references
    print("\n=== References Between Chunks ===")
    chunks_with_references = 0
    for chunk in all_chunks:
        if chunk.references:
            chunks_with_references += 1
            print(f"\nChunk: {chunk.chunk_type} (lines {chunk.start_line}-{chunk.end_line})")
            print(f"  Name: {chunk.name}")
            print(f"  References:")
            for ref in chunk.references:
                print(f"    -> {ref.chunk_type}: {ref.name}")
    
    print(f"\nFound references in {chunks_with_references} out of {len(all_chunks)} chunks")
    
    # Test standalone content generation
    print("\n=== Standalone Content Generation ===")
    for chunk in all_chunks:
        if chunk.chunk_type in ['method_declaration', 'constructor_declaration', 'orphaned_method_declaration']:
            print(f"\nGenerating standalone content for: {chunk.name}")
            standalone = chunk.get_standalone_content()
            lines = standalone.split('\n')
            preview = '\n'.join(lines[:5] + (['...'] if len(lines) > 10 else []) + lines[-5:] if len(lines) > 10 else lines)
            print(f"  Standalone content ({len(lines)} lines):")
            print(f"```\n{preview}\n```")
    
    # Save detailed results to a JSON file
    output_file = file_path.with_suffix('.context.json')
    
    # Create a serializable representation of the chunk hierarchy with context
    def chunk_to_dict(chunk):
        chunk_dict = chunk.to_dict()
        chunk_dict['children'] = [chunk_to_dict(child) for child in chunk.children]
        chunk_dict['standalone_content'] = chunk.get_standalone_content() if chunk.chunk_type in ['method_declaration', 'constructor_declaration'] else None
        return chunk_dict
    
    with open(output_file, 'w') as f:
        json.dump([chunk_to_dict(chunk) for chunk in chunks], f, indent=2)
    
    print(f"\nDetailed results saved to {output_file}")
    print("Context preservation test completed successfully")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_context_preservation.py <path_to_file>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    test_context_preservation(file_path)

if __name__ == "__main__":
    main()
