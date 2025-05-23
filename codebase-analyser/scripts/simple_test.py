#!/usr/bin/env python3
"""
Simple test script for Java parsing.
"""

import os
import sys
import re
from pathlib import Path

class SimpleCodeChunk:
    """Simple code chunk class."""
    
    def __init__(self, chunk_type, name, content, file_path, start_line, end_line):
        self.chunk_type = chunk_type
        self.name = name
        self.content = content
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.children = []
    
    def add_child(self, child):
        """Add a child chunk."""
        self.children.append(child)

def extract_classes(content, file_path):
    """Extract classes from Java content."""
    chunks = []
    
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
        
        # Create the chunk
        chunk = SimpleCodeChunk(
            chunk_type="class",
            name=class_name,
            content=class_content,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line
        )
        
        # Extract methods
        methods = extract_methods(class_content, file_path, class_name)
        for method in methods:
            chunk.add_child(method)
        
        chunks.append(chunk)
    
    return chunks

def extract_methods(content, file_path, class_name):
    """Extract methods from Java content."""
    chunks = []
    
    # Find method declarations
    method_pattern = r'(public|private|protected)?\s+(?:static\s+)?(?:final\s+)?(?:(\w+(?:<[\w\s,]+>)?)\s+)?(\w+)\s*\((.*?)\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
    method_matches = re.finditer(method_pattern, content)
    
    for match in method_matches:
        visibility = match.group(1) or "default"
        return_type = match.group(2) or "void"
        method_name = match.group(3)
        parameters = match.group(4)
        
        # Skip if this is a constructor with the same name as the class
        if method_name == class_name and not return_type:
            continue
        
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
        
        # Create the chunk
        chunk = SimpleCodeChunk(
            chunk_type="method",
            name=method_name,
            content=method_content,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line
        )
        
        chunks.append(chunk)
    
    return chunks

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python simple_test.py <java_file>")
        return 1
    
    file_path = sys.argv[1]
    
    # Read the file
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1
    
    # Extract classes
    classes = extract_classes(content, file_path)
    
    # Print results
    print(f"Found {len(classes)} classes:")
    for cls in classes:
        print(f"  - {cls.name} (lines {cls.start_line}-{cls.end_line})")
        print(f"    Methods: {len(cls.children)}")
        for method in cls.children:
            print(f"      - {method.name} (lines {method.start_line}-{method.end_line})")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
