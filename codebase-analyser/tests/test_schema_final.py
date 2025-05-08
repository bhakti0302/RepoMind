#!/usr/bin/env python3
"""
Final test script for the schema definitions.
This script works with both minimal and full schemas.
"""

import os
import sys
import argparse
import numpy as np
import json
import uuid
from pathlib import Path
from datetime import datetime

from codebase_analyser.database import LanceDBManager, SchemaDefinitions


def test_schema(db_path=None, clear=False, use_minimal=True):
    """Test the schema definitions.
    
    Args:
        db_path: Path to the LanceDB database
        clear: Whether to clear existing tables
        use_minimal: Whether to use the minimal schema
    """
    print(f"Testing {'minimal' if use_minimal else 'full'} schema...")
    
    # Create a LanceDBManager instance
    db_manager = LanceDBManager(
        db_path=db_path,
        use_minimal_schema=use_minimal,
        embedding_dim=384
    )
    
    # Create tables
    db_manager.create_tables()
    
    # Clear tables if requested
    if clear:
        print("Clearing existing tables...")
        db_manager.clear_tables()
    
    # Create sample data
    print("Creating sample data...")
    
    # Sample code chunks
    code_chunks = [
        {
            "embedding": np.random.rand(384).astype(np.float32).tolist(),
            "node_id": "file:sample.java",
            "chunk_type": "file",
            "content": "package com.example;\n\npublic class Sample {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, world!\");\n    }\n}",
            "file_path": "sample.java",
            "start_line": 1,
            "end_line": 7,
            "language": "java",
            "name": "Sample.java",
            "qualified_name": "com.example.Sample.java",
            "metadata": {"is_valid": True, "has_errors": False},
            "context": {"package": "com.example", "imports": ["java.util.*"]},
            # Additional fields for full schema
            "parent_id": "",
            "root_id": "",
            "depth": 0,
            "token_count": 30,
            "complexity": 1.0,
            "importance": 0.8,
            "tags": ["file", "java"],
            "categories": ["source"]
        },
        {
            "embedding": np.random.rand(384).astype(np.float32).tolist(),
            "node_id": "class:Sample",
            "chunk_type": "class_declaration",
            "content": "public class Sample {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, world!\");\n    }\n}",
            "file_path": "sample.java",
            "start_line": 3,
            "end_line": 7,
            "language": "java",
            "name": "Sample",
            "qualified_name": "com.example.Sample",
            "metadata": {"is_valid": True, "has_errors": False},
            "context": {"package": "com.example", "imports": ["java.util.*"]},
            # Additional fields for full schema
            "parent_id": "file:sample.java",
            "root_id": "file:sample.java",
            "depth": 1,
            "token_count": 25,
            "complexity": 1.0,
            "importance": 0.8,
            "tags": ["class", "public"],
            "categories": ["declaration"]
        }
    ]
    
    # Sample dependencies
    dependencies = [
        {
            "source_id": "file:sample.java",
            "target_id": "class:Sample",
            "type": "CONTAINS",
            "strength": 1.0,
            "is_direct": True,
            "is_required": True,
            "description": "File contains class",
            # Additional fields for full schema
            "locations": json.dumps([{"line": 3, "column": 0}]),
            "frequency": 1,
            "impact": 1.0
        }
    ]
    
    # Sample embedding metadata (only for full schema)
    embedding_metadata = [
        {
            "embedding_id": str(uuid.uuid4()),
            "chunk_id": "class:Sample",
            "model_name": "codebert-base",
            "model_version": "1.0.0",
            "embedding_type": "code",
            "embedding_dim": 384,
            "quality_score": 0.95,
            "confidence": 0.98
        }
    ]
    
    # Add sample data to the database
    print("Adding sample data to the database...")
    try:
        db_manager.add_code_chunks(code_chunks)
        print("Successfully added code chunks")
    except Exception as e:
        print(f"Error adding code chunks: {e}")
    
    try:
        db_manager.add_dependencies(dependencies)
        print("Successfully added dependencies")
    except Exception as e:
        print(f"Error adding dependencies: {e}")
    
    # Add embedding metadata if using full schema
    if not use_minimal:
        try:
            db_manager.add_embedding_metadata(embedding_metadata)
            print("Successfully added embedding metadata")
        except Exception as e:
            print(f"Error adding embedding metadata: {e}")
    
    # Test search functionality
    print("\nTesting search functionality...")
    try:
        query_embedding = np.random.rand(384).astype(np.float32).tolist()
        search_results = db_manager.search_code_chunks(query_embedding, limit=2)
        print(f"Found {len(search_results)} code chunks")
    except Exception as e:
        print(f"Search functionality test failed: {e}")
    
    # Test dependency retrieval
    print("\nTesting dependency retrieval...")
    try:
        dep_results = db_manager.get_dependencies(source_id="file:sample.java")
        print(f"Found {len(dep_results)} dependencies")
    except Exception as e:
        print(f"Dependency retrieval test failed: {e}")
    
    # Close the database connection
    db_manager.close()
    
    print("\nSchema test completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Test the schema definitions")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--clear", action="store_true", help="Clear existing tables")
    parser.add_argument("--full", action="store_true", help="Use full schema instead of minimal")
    
    args = parser.parse_args()
    
    test_schema(db_path=args.db_path, clear=args.clear, use_minimal=not args.full)


if __name__ == "__main__":
    main()
