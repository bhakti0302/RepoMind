#!/usr/bin/env python3
"""
Script to index a Java file in LanceDB with schema compatibility.
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
import pyarrow as pa

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_table_schema(db_path, table_name):
    """Get the schema of an existing table.
    
    Args:
        db_path: Path to the LanceDB database
        table_name: Name of the table
        
    Returns:
        Dictionary mapping field names to their types
    """
    db = lancedb.connect(db_path)
    if table_name in db.table_names():
        table = db.open_table(table_name)
        schema = table.schema
        
        # Convert PyArrow schema to dictionary
        schema_dict = {}
        for field in schema:
            schema_dict[field.name] = str(field.type)
        
        return schema_dict
    
    return None

def index_java_file(file_path, db_path, project_id):
    """Index a Java file in LanceDB with schema compatibility.
    
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
    
    # Get the schema of the existing table
    table_name = "code_chunks"
    schema_dict = get_table_schema(db_path, table_name)
    
    if schema_dict:
        logger.info(f"Found existing table with schema: {schema_dict.keys()}")
    else:
        logger.error("Could not get schema from existing table")
        return
    
    # Create simple chunks from the file
    chunks = []
    
    # Current timestamp in milliseconds
    current_time = int(time.time() * 1000)
    
    # Add the whole file as a chunk
    file_node_id = f"file:{file_path.stem}"
    
    # Create methods list for children_ids
    methods = []
    
    # Find methods in the file
    import re
    method_pattern = r'(static\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
    for match in re.finditer(method_pattern, content):
        method_name = match.group(3)
        method_node_id = f"method:{file_path.stem}.{method_name}"
        methods.append(method_node_id)
    
    # Create file chunk with all required fields from schema
    file_chunk = {}
    for field_name in schema_dict.keys():
        if field_name == "embedding":
            file_chunk[field_name] = np.random.rand(768).astype(np.float32).tolist()
        elif field_name == "node_id":
            file_chunk[field_name] = file_node_id
        elif field_name == "chunk_type":
            file_chunk[field_name] = "file"
        elif field_name == "content":
            file_chunk[field_name] = content
        elif field_name == "file_path":
            file_chunk[field_name] = str(file_path)
        elif field_name == "start_line":
            file_chunk[field_name] = 1
        elif field_name == "end_line":
            file_chunk[field_name] = content.count('\n') + 1
        elif field_name == "language":
            file_chunk[field_name] = "java"
        elif field_name == "name":
            file_chunk[field_name] = file_path.stem
        elif field_name == "qualified_name":
            file_chunk[field_name] = f"com.example.{file_path.stem}"
        elif field_name == "metadata":
            file_chunk[field_name] = json.dumps({"level": "file"})
        elif field_name == "context":
            file_chunk[field_name] = json.dumps({"package": "com.example"})
        elif field_name == "parent_id":
            file_chunk[field_name] = ""
        elif field_name == "root_id":
            file_chunk[field_name] = file_node_id
        elif field_name == "depth":
            file_chunk[field_name] = 0
        elif field_name == "token_count":
            file_chunk[field_name] = len(content.split())
        elif field_name == "complexity":
            file_chunk[field_name] = 1.0
        elif field_name == "importance":
            file_chunk[field_name] = 0.8
        elif field_name == "created_at":
            file_chunk[field_name] = current_time
        elif field_name == "updated_at":
            file_chunk[field_name] = current_time
        elif field_name == "project_id":
            file_chunk[field_name] = project_id
        elif field_name == "children_ids":
            # This is the field that was missing
            file_chunk[field_name] = json.dumps(methods)
        elif field_name == "tags" or field_name == "categories":
            file_chunk[field_name] = json.dumps([])
        else:
            # For any other fields, add empty values based on type
            if "string" in schema_dict[field_name]:
                file_chunk[field_name] = ""
            elif "int" in schema_dict[field_name]:
                file_chunk[field_name] = 0
            elif "float" in schema_dict[field_name]:
                file_chunk[field_name] = 0.0
            elif "bool" in schema_dict[field_name]:
                file_chunk[field_name] = False
            elif "list" in schema_dict[field_name]:
                file_chunk[field_name] = []
            else:
                file_chunk[field_name] = None
    
    chunks.append(file_chunk)
    
    # Add each method as a chunk
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
        
        # Create method chunk with all required fields from schema
        method_chunk = {}
        for field_name in schema_dict.keys():
            if field_name == "embedding":
                method_chunk[field_name] = np.random.rand(768).astype(np.float32).tolist()
            elif field_name == "node_id":
                method_chunk[field_name] = method_node_id
            elif field_name == "chunk_type":
                method_chunk[field_name] = "method"
            elif field_name == "content":
                method_chunk[field_name] = method_content
            elif field_name == "file_path":
                method_chunk[field_name] = str(file_path)
            elif field_name == "start_line":
                method_chunk[field_name] = start_line
            elif field_name == "end_line":
                method_chunk[field_name] = end_line
            elif field_name == "language":
                method_chunk[field_name] = "java"
            elif field_name == "name":
                method_chunk[field_name] = method_name
            elif field_name == "qualified_name":
                method_chunk[field_name] = f"com.example.{file_path.stem}.{method_name}"
            elif field_name == "metadata":
                method_chunk[field_name] = json.dumps({"level": "method"})
            elif field_name == "context":
                method_chunk[field_name] = json.dumps({"package": "com.example", "class": file_path.stem})
            elif field_name == "parent_id":
                method_chunk[field_name] = file_node_id
            elif field_name == "root_id":
                method_chunk[field_name] = file_node_id
            elif field_name == "depth":
                method_chunk[field_name] = 1
            elif field_name == "token_count":
                method_chunk[field_name] = len(method_content.split())
            elif field_name == "complexity":
                method_chunk[field_name] = 1.0
            elif field_name == "importance":
                method_chunk[field_name] = 0.7
            elif field_name == "created_at":
                method_chunk[field_name] = current_time
            elif field_name == "updated_at":
                method_chunk[field_name] = current_time
            elif field_name == "project_id":
                method_chunk[field_name] = project_id
            elif field_name == "children_ids":
                # This is the field that was missing
                method_chunk[field_name] = json.dumps([])
            elif field_name == "tags" or field_name == "categories":
                method_chunk[field_name] = json.dumps([])
            else:
                # For any other fields, add empty values based on type
                if "string" in schema_dict[field_name]:
                    method_chunk[field_name] = ""
                elif "int" in schema_dict[field_name]:
                    method_chunk[field_name] = 0
                elif "float" in schema_dict[field_name]:
                    method_chunk[field_name] = 0.0
                elif "bool" in schema_dict[field_name]:
                    method_chunk[field_name] = False
                elif "list" in schema_dict[field_name]:
                    method_chunk[field_name] = []
                else:
                    method_chunk[field_name] = None
        
        chunks.append(method_chunk)
    
    logger.info(f"Created {len(chunks)} chunks")
    
    # Connect to LanceDB
    logger.info(f"Connecting to database: {db_path}")
    db = lancedb.connect(db_path)
    
    # Open the table
    table = db.open_table(table_name)
    
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
                
                # Print the schema type for each field
                for field_name in schema_dict.keys():
                    if field_name in chunk:
                        logger.error(f"  - {field_name}: {type(chunk[field_name])} (expected {schema_dict[field_name]})")
    
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