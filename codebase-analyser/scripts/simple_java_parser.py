#!/usr/bin/env python3
"""
Simple Java parser using Tree-sitter.
"""

import os
import sys
from pathlib import Path
from tree_sitter import Language, Parser

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python simple_java_parser.py <java_file>")
        return 1

    file_path = sys.argv[1]
    
    # Initialize parser
    parser = Parser()
    
    # Load Java language
    language_path = os.path.join(os.path.dirname(__file__), "build", "languages.so")
    if not os.path.exists(language_path):
        print(f"Error: Language library not found at {language_path}")
        return 1
    
    try:
        language = Language(language_path, "java")
        parser.set_language(language)
    except Exception as e:
        print(f"Error loading Java language: {e}")
        return 1
    
    # Parse the file
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        
        tree = parser.parse(content)
        
        # Print the AST
        print(f"AST for {file_path}:")
        print_node(tree.root_node, content, 0)
        
        # Find class declarations
        print("\nClass declarations:")
        find_nodes_by_type(tree.root_node, "class_declaration", content)
        
        return 0
    except Exception as e:
        print(f"Error parsing file: {e}")
        return 1

def print_node(node, content, level):
    """Print a node and its children."""
    indent = "  " * level
    node_text = content[node.start_byte:node.end_byte].decode("utf-8")
    if len(node_text) > 50:
        node_text = node_text[:47] + "..."
    print(f"{indent}{node.type}: {node_text}")
    
    for child in node.children:
        print_node(child, content, level + 1)

def find_nodes_by_type(node, type_name, content):
    """Find nodes by type."""
    if node.type == type_name:
        node_text = content[node.start_byte:node.end_byte].decode("utf-8")
        print(f"Found {type_name}: {node_text[:50]}...")
        
        # Find class name
        for child in node.children:
            if child.type == "identifier":
                class_name = content[child.start_byte:child.end_byte].decode("utf-8")
                print(f"  Class name: {class_name}")
    
    for child in node.children:
        find_nodes_by_type(child, type_name, content)

if __name__ == "__main__":
    sys.exit(main())
