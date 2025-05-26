#!/usr/bin/env python3

import re
import sys

def fix_java_file(file_path):
    """
    Fix a Java file by removing duplicate methods and ensuring proper formatting.
    
    Args:
        file_path: Path to the Java file
    """
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the class declaration
    class_match = re.search(r'public\s+class\s+(\w+)', content)
    if not class_match:
        print(f"No class declaration found in {file_path}")
        return
    
    class_name = class_match.group(1)
    print(f"Found class: {class_name}")
    
    # Split the content into lines
    lines = content.splitlines()
    
    # Find all method declarations
    method_lines = {}
    method_bodies = {}
    current_method = None
    brace_count = 0
    
    for i, line in enumerate(lines):
        # Check if this line starts a method
        method_match = re.search(r'(public|private|protected)(?:\s+\w+)*\s+(\w+)\s*\([^)]*\)\s*{', line)
        if method_match and not current_method:
            method_name = method_match.group(2)
            current_method = method_name
            method_lines[method_name] = i
            method_bodies[method_name] = [line]
            brace_count = 1
            continue
        
        # If we're inside a method, track braces
        if current_method:
            brace_count += line.count('{')
            brace_count -= line.count('}')
            method_bodies[current_method].append(line)
            
            # If we've reached the end of the method, reset flags
            if brace_count <= 0:
                current_method = None
    
    # Find duplicate methods
    method_names = list(method_lines.keys())
    duplicate_methods = []
    
    for i, method_name in enumerate(method_names):
        for j in range(i + 1, len(method_names)):
            if method_name == method_names[j]:
                duplicate_methods.append(method_name)
    
    # Keep only the last occurrence of each duplicate method
    for method_name in duplicate_methods:
        indices = [i for i, name in enumerate(method_names) if name == method_name]
        for i in indices[:-1]:
            del method_lines[method_names[i]]
            del method_bodies[method_names[i]]
    
    # Rebuild the file
    new_content = []
    in_method = False
    skip_lines = set()
    
    for i, line in enumerate(lines):
        # Skip lines that are part of methods we're removing
        if i in skip_lines:
            continue
        
        # Check if this line starts a method
        method_match = re.search(r'(public|private|protected)(?:\s+\w+)*\s+(\w+)\s*\([^)]*\)\s*{', line)
        if method_match:
            method_name = method_match.group(2)
            
            # If this is a duplicate method and not the last occurrence, skip it
            if method_name in duplicate_methods and i != method_lines[method_name]:
                # Find the end of the method
                brace_count = 1
                for j in range(i + 1, len(lines)):
                    brace_count += lines[j].count('{')
                    brace_count -= lines[j].count('}')
                    skip_lines.add(j)
                    if brace_count <= 0:
                        break
                continue
        
        new_content.append(line)
    
    # Write the fixed content back to the file
    with open(file_path, 'w') as f:
        f.write('\n'.join(new_content))
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_java_file.py <file_path>")
        sys.exit(1)
    
    fix_java_file(sys.argv[1])
