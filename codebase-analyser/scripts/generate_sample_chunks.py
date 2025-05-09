#!/usr/bin/env python3
"""
Script to generate sample code chunks for testing.
"""

import os
import json
import argparse
from pathlib import Path


def generate_sample_chunks(output_file):
    """Generate sample code chunks for testing.
    
    Args:
        output_file: Path to the output JSON file
    """
    print(f"Generating sample code chunks...")
    
    # Sample code chunks in different languages
    chunks = [
        {
            "node_id": "file:sample1.java",
            "chunk_type": "file",
            "content": """
            package com.example;
            
            public class HelloWorld {
                public static void main(String[] args) {
                    System.out.println("Hello, World!");
                }
            }
            """,
            "file_path": "sample1.java",
            "start_line": 1,
            "end_line": 7,
            "language": "java",
            "name": "HelloWorld.java",
            "qualified_name": "com.example.HelloWorld.java",
            "metadata": {
                "is_valid": True,
                "has_errors": False,
                "dependencies": [
                    {
                        "source_id": "file:sample1.java",
                        "target_id": "class:HelloWorld",
                        "type": "CONTAINS",
                        "strength": 1.0,
                        "is_direct": True,
                        "is_required": True,
                        "description": "File contains class"
                    }
                ]
            },
            "context": {
                "package": "com.example",
                "imports": []
            }
        },
        {
            "node_id": "class:HelloWorld",
            "chunk_type": "class_declaration",
            "content": """
            public class HelloWorld {
                public static void main(String[] args) {
                    System.out.println("Hello, World!");
                }
            }
            """,
            "file_path": "sample1.java",
            "start_line": 3,
            "end_line": 7,
            "language": "java",
            "name": "HelloWorld",
            "qualified_name": "com.example.HelloWorld",
            "metadata": {
                "is_valid": True,
                "has_errors": False,
                "dependencies": [
                    {
                        "source_id": "class:HelloWorld",
                        "target_id": "method:HelloWorld.main",
                        "type": "CONTAINS",
                        "strength": 1.0,
                        "is_direct": True,
                        "is_required": True,
                        "description": "Class contains method"
                    }
                ]
            },
            "context": {
                "package": "com.example",
                "imports": []
            }
        },
        {
            "node_id": "method:HelloWorld.main",
            "chunk_type": "method_declaration",
            "content": """
            public static void main(String[] args) {
                System.out.println("Hello, World!");
            }
            """,
            "file_path": "sample1.java",
            "start_line": 4,
            "end_line": 6,
            "language": "java",
            "name": "main",
            "qualified_name": "com.example.HelloWorld.main",
            "metadata": {
                "is_valid": True,
                "has_errors": False,
                "dependencies": []
            },
            "context": {
                "package": "com.example",
                "imports": [],
                "class": "HelloWorld"
            }
        },
        {
            "node_id": "file:sample2.py",
            "chunk_type": "file",
            "content": """
            def hello_world():
                print("Hello, World!")
                
            if __name__ == "__main__":
                hello_world()
            """,
            "file_path": "sample2.py",
            "start_line": 1,
            "end_line": 5,
            "language": "python",
            "name": "sample2.py",
            "qualified_name": "sample2.py",
            "metadata": {
                "is_valid": True,
                "has_errors": False,
                "dependencies": [
                    {
                        "source_id": "file:sample2.py",
                        "target_id": "function:hello_world",
                        "type": "CONTAINS",
                        "strength": 1.0,
                        "is_direct": True,
                        "is_required": True,
                        "description": "File contains function"
                    }
                ]
            },
            "context": {
                "imports": []
            }
        },
        {
            "node_id": "function:hello_world",
            "chunk_type": "function_declaration",
            "content": """
            def hello_world():
                print("Hello, World!")
            """,
            "file_path": "sample2.py",
            "start_line": 1,
            "end_line": 2,
            "language": "python",
            "name": "hello_world",
            "qualified_name": "hello_world",
            "metadata": {
                "is_valid": True,
                "has_errors": False,
                "dependencies": []
            },
            "context": {
                "imports": []
            }
        },
        {
            "node_id": "file:sample3.js",
            "chunk_type": "file",
            "content": """
            function helloWorld() {
                console.log("Hello, World!");
            }
            
            helloWorld();
            """,
            "file_path": "sample3.js",
            "start_line": 1,
            "end_line": 5,
            "language": "javascript",
            "name": "sample3.js",
            "qualified_name": "sample3.js",
            "metadata": {
                "is_valid": True,
                "has_errors": False,
                "dependencies": [
                    {
                        "source_id": "file:sample3.js",
                        "target_id": "function:helloWorld",
                        "type": "CONTAINS",
                        "strength": 1.0,
                        "is_direct": True,
                        "is_required": True,
                        "description": "File contains function"
                    }
                ]
            },
            "context": {
                "imports": []
            }
        },
        {
            "node_id": "function:helloWorld",
            "chunk_type": "function_declaration",
            "content": """
            function helloWorld() {
                console.log("Hello, World!");
            }
            """,
            "file_path": "sample3.js",
            "start_line": 1,
            "end_line": 3,
            "language": "javascript",
            "name": "helloWorld",
            "qualified_name": "helloWorld",
            "metadata": {
                "is_valid": True,
                "has_errors": False,
                "dependencies": []
            },
            "context": {
                "imports": []
            }
        }
    ]
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Write the chunks to the output file
    with open(output_file, 'w') as f:
        json.dump(chunks, f, indent=2)
    
    print(f"Generated {len(chunks)} sample chunks and saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate sample code chunks for testing")
    parser.add_argument("--output", default="samples/sample_chunks.json", help="Path to the output JSON file")
    
    args = parser.parse_args()
    
    generate_sample_chunks(args.output)


if __name__ == "__main__":
    main()
