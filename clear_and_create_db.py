#!/usr/bin/env python3
"""
Script to clear and create a new LanceDB table.
"""

import os
import sys
import argparse
import logging
import lancedb
import numpy as np
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_and_create_table(db_path, table_name="code_chunks"):
    """Clear and create a new LanceDB table.
    
    Args:
        db_path: Path to the LanceDB database
        table_name: Name of the table to clear and create
    """
    logger.info(f"Connecting to database: {db_path}")
    db = lancedb.connect(db_path)
    
    # Check if the table exists
    if table_name in db.table_names():
        logger.info(f"Dropping existing table: {table_name}")
        db.drop_table(table_name)
    
    # Create a minimal schema for the table
    logger.info(f"Creating new table: {table_name}")
    
    # Create a sample chunk with all required fields
    sample_chunk = {
        "embedding": np.random.rand(768).astype(np.float32).tolist(),
        "node_id": "sample",
        "chunk_type": "file",
        "content": "Sample content",
        "file_path": "sample/path.java",
        "start_line": 1,
        "end_line": 10,
        "language": "java",
        "name": "Sample",
        "qualified_name": "com.example.Sample",
        "metadata": json.dumps({"level": "file"}),
        "context": json.dumps({"package": "com.example"}),
        "parent_id": "",
        "root_id": "sample",
        "depth": 0,
        "token_count": 2,
        "complexity": 1.0,
        "importance": 0.8,
        "created_at": int(datetime.now().timestamp() * 1000),
        "updated_at": int(datetime.now().timestamp() * 1000),
        "project_id": "sample",
        "children_ids": json.dumps([])
    }
    
    # Create the table with the sample chunk
    db.create_table(table_name, data=[sample_chunk])
    
    # Open the table to verify it was created
    table = db.open_table(table_name)
    
    # Print the schema
    logger.info(f"Table created with schema: {table.schema}")
    
    # Remove the sample chunk
    table.delete("node_id = 'sample'")
    
    logger.info(f"Table {table_name} cleared and created successfully")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Clear and create a new LanceDB table")
    parser.add_argument("--db-path", default="codebase-analyser/.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--table-name", default="code_chunks", help="Name of the table to clear and create")
    
    args = parser.parse_args()
    
    # Clear and create the table
    clear_and_create_table(args.db_path, args.table_name)

if __name__ == "__main__":
    main()