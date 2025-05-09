#!/usr/bin/env python3
"""
Test script for Java chunking.
"""

import os
import sys
from pathlib import Path

from codebase_analyser.chunking.code_chunk import CodeChunk
from codebase_analyser.chunking.chunker import CodeChunker

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_java_chunking.py <java_file>")
        return 1

    file_path = sys.argv[1]
    
    # Read the file
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1
    
    # Create a file-level chunk
    file_chunk = CodeChunk(
        node_id=f"file:{file_path}",
        chunk_type="file",
        content=content,
        file_path=file_path,
        start_line=1,
        end_line=content.count('\n') + 1,
        language="java",
        name=Path(file_path).stem
    )
    
    # Create class chunks
    class_chunks = extract_classes(content, file_path, file_chunk)
    
    # Print chunks
    print(f"File chunk: {file_chunk.node_id}")
    print(f"Class chunks: {len(class_chunks)}")
    for chunk in class_chunks:
        print(f"  - {chunk.node_id}: {chunk.name}")
        
        # Print methods
        method_chunks = extract_methods(chunk.content, file_path, chunk)
        print(f"    Methods: {len(method_chunks)}")
        for method in method_chunks:
            print(f"      - {method.node_id}: {method.name}")
    
    return 0

def extract_classes(content, file_path, parent_chunk):
    """Extract class chunks from Java content."""
    chunks = []
    
    # Simple regex-based approach
    import re
    
    # Find class declarations
    class_pattern = r'public\s+class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*\{'
    class_matches = re.finditer(class_pattern, content)
    
    for match in class_matches:
        class_name = match.group(1)
        superclass = match.group(2)
        interfaces = match.group(3)
        
        # Find the class body
        start_pos = match.start()
        
        # Find the matching closing brace
        open_braces = 1
        end_pos = start_pos + match.group(0).find('{') + 1
        
        while open_braces > 0 and end_pos < len(content):
            if content[end_pos] == '{':
                open_braces += 1
            elif content[end_pos] == '}':
                open_braces -= 1
            end_pos += 1
        
        # Extract the class content
        class_content = content[start_pos:end_pos]
        
        # Count lines
        start_line = content[:start_pos].count('\n') + 1
        end_line = content[:end_pos].count('\n') + 1
        
        # Create context
        context = {}
        if superclass:
            context['extends'] = superclass
        if interfaces:
            context['implements'] = [i.strip() for i in interfaces.split(',')]
        
        # Create the chunk
        chunk = CodeChunk(
            node_id=f"class:{class_name}",
            chunk_type="class_declaration",
            content=class_content,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            language="java",
            name=class_name,
            qualified_name=class_name
        )
        
        # Add context
        chunk.context = context
        
        # Add as child of parent
        parent_chunk.add_child(chunk)
        
        chunks.append(chunk)
    
    return chunks

def extract_methods(content, file_path, parent_chunk):
    """Extract method chunks from Java content."""
    chunks = []
    
    # Simple regex-based approach
    import re
    
    # Find method declarations
    method_pattern = r'(public|private|protected)?\s+(?:static\s+)?(?:final\s+)?(?:(\w+(?:<[\w\s,]+>)?)\s+)?(\w+)\s*\((.*?)\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
    method_matches = re.finditer(method_pattern, content)
    
    for match in method_matches:
        visibility = match.group(1) or "default"
        return_type = match.group(2) or "void"
        method_name = match.group(3)
        parameters = match.group(4)
        
        # Find the method body
        start_pos = match.start()
        
        # Find the matching closing brace
        open_braces = 1
        end_pos = start_pos + match.group(0).find('{') + 1
        
        while open_braces > 0 and end_pos < len(content):
            if content[end_pos] == '{':
                open_braces += 1
            elif content[end_pos] == '}':
                open_braces -= 1
            end_pos += 1
        
        # Extract the method content
        method_content = content[start_pos:end_pos]
        
        # Count lines
        start_line = content[:start_pos].count('\n') + 1
        end_line = content[:end_pos].count('\n') + 1
        
        # Create metadata
        metadata = {
            'visibility': visibility,
            'return_type': return_type,
            'parameters': parameters
        }
        
        # Create the chunk
        chunk = CodeChunk(
            node_id=f"method:{parent_chunk.name}.{method_name}",
            chunk_type="method_declaration",
            content=method_content,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            language="java",
            name=method_name,
            qualified_name=f"{parent_chunk.name}.{method_name}"
        )
        
        # Add metadata
        chunk.metadata = metadata
        
        # Add as child of parent
        parent_chunk.add_child(chunk)
        
        chunks.append(chunk)
    
    return chunks

if __name__ == "__main__":
    sys.exit(main())
