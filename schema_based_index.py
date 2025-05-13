#!/usr/bin/env python3
"""
Schema-based script to index a Java file in LanceDB.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import lancedb
import numpy as np
import json
from datetime import datetime
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def index_java_file(file_path, db_path, project_id):
    """Index a Java file in LanceDB using the schema from the codebase.
    
    Args:
        file_path: Path to the Java file
        db_path: Path to the LanceDB database
        project_id: Project ID to associate with the file
    """
    logger.info(f"Indexing file: {file_path}")
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        logger.error(f"File does not exist: {file_path}")
        return
    
    # Read the file content
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return
    
    # Import the schema definitions
    try:
        from codebase_analyser.database.schema import SchemaDefinitions
        logger.info("Successfully imported SchemaDefinitions")
        
        # Get the schema for code chunks
        schema = SchemaDefinitions.get_minimal_code_chunks_schema()
        logger.info(f"Using minimal schema with fields: {list(schema.keys())}")
    except ImportError as e:
        logger.error(f"Error importing SchemaDefinitions: {e}")
        logger.info("Using hardcoded minimal schema")
        
        # Hardcoded minimal schema based on the codebase
        schema = {
            "embedding": "list[float32]",
            "node_id": "string",
            "chunk_type": "string",
            "content": "string",
            "file_path": "string",
            "start_line": "int32",
            "end_line": "int32",
            "language": "string",
            "name": "string",
            "qualified_name": "string",
            "metadata": "string",
            "context": "string",
            "project_id": "string"
        }
    
    # Create simple chunks from the file
    chunks = []
    
    # Current timestamp in milliseconds
    current_time = int(time.time() * 1000)
    
    # Add the whole file as a chunk
    file_node_id = f"file:{file_path.stem}"
    file_chunk = {
        'embedding': np.random.rand(768).astype(np.float32).tolist(),
        'node_id': file_node_id,
        'chunk_type': 'file',
        'content': content,
        'file_path': str(file_path),
        'start_line': 1,
        'end_line': content.count('\n') + 1,
        'language': 'java',
        'name': file_path.stem,
        'qualified_name': f"com.example.{file_path.stem}",
        'metadata': json.dumps({"level": "file"}),
        'context': json.dumps({"package": "com.example"}),
        'project_id': project_id
    }
    chunks.append(file_chunk)
    
    # Add each method as a chunk
    import re
    method_pattern = r'(static\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
    for match in re.finditer(method_pattern, content):
        method_start = match.start()
        method_name = match.group(3)
        
        # Find the method body by counting braces
        open_braces = 1
        end_pos = method_start + match.group(0).find('{') + 1
        
        while open_braces > 0 and end_pos < len(content):
            if content[end_pos] == '{':
                open_braces += 1
            elif content[end_pos] == '}':
                open_braces -= 1
            end_pos += 1
        
        method_content = content[method_start:end_pos]
        start_line = content[:method_start].count('\n') + 1
        end_line = start_line + method_content.count('\n')
        
        method_node_id = f"method:{file_path.stem}.{method_name}"
        method_chunk = {
            'embedding': np.random.rand(768).astype(np.float32).tolist(),
            'node_id': method_node_id,
            'chunk_type': 'method',
            'content': method_content,
            'file_path': str(file_path),
            'start_line': start_line,
            'end_line': end_line,
            'language': 'java',
            'name': method_name,
            'qualified_name': f"com.example.{file_path.stem}.{method_name}",
            'metadata': json.dumps({"level": "method"}),
            'context': json.dumps({"package": "com.example", "class": file_path.stem}),
            'project_id': project_id
        }
        chunks.append(method_chunk)
    
    logger.info(f"Created {len(chunks)} chunks")
    
    # Connect to LanceDB
    logger.info(f"Connecting to database: {db_path}")
    db = lancedb.connect(db_path)
    
    # Create or get the table
    table_name = "code_chunks"
    if table_name in db.table_names():
        table = db.open_table(table_name)
        logger.info(f"Opened existing table {table_name}")
    else:
        logger.info(f"Creating table {table_name}")
        table = db.create_table(table_name, data=chunks)
    
    # Add chunks to the table
    logger.info(f"Adding {len(chunks)} chunks to the database")
    try:
        table.add(chunks)
        logger.info("Successfully added chunks to the database")
    except Exception as e:
        logger.error(f"Error adding chunks to the database: {e}")
        
        # Try adding one by one to identify problematic chunks
        for i, chunk in enumerate(chunks):
            try:
                table.add([chunk])
                logger.info(f"Successfully added chunk {i+1}/{len(chunks)}")
            except Exception as e:
                logger.error(f"Error adding chunk {i+1}/{len(chunks)}: {e}")
                logger.error(f"Problematic chunk: {chunk.keys()}")
    
    logger.info("Indexing complete")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Index a Java file in LanceDB")
    parser.add_argument("--file-path", required=True, help="Path to the Java file")
    parser.add_argument("--db-path", default="codebase-analyser/.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--project-id", default="default", help="Project ID to associate with the file")
    
    args = parser.parse_args()
    
    # Convert file path to absolute path
    file_path = os.path.abspath(args.file_path)
    
    # Index the file
    index_java_file(file_path, args.db_path, args.project_id)

if __name__ == "__main__":
    main()