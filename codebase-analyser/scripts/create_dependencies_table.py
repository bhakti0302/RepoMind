#!/usr/bin/env python3
"""
Create Dependencies Table

This script creates a dependencies table in the database to store relationships
between code chunks. This is needed because the code_chunks table doesn't have
columns for storing relationships.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

import lancedb
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_dependencies_table(project_id, db_path=".lancedb"):
    """Create a dependencies table in the database."""
    logger.info(f"Creating dependencies table for project: {project_id}")
    
    # Connect to the database
    db = lancedb.connect(db_path)
    
    # Check if the dependencies table already exists
    if "dependencies" in db.table_names():
        logger.info("Dependencies table already exists")
        
        # Check if we need to drop the table
        table = db.open_table("dependencies")
        try:
            # Try to get dependencies for this project
            df = table.search().where(f"project_id = '{project_id}'").to_pandas()
            if len(df) > 0:
                logger.info(f"Found {len(df)} existing dependencies for project {project_id}")
                logger.info("Dropping existing dependencies table to recreate it")
                db.drop_table("dependencies")
            else:
                logger.info(f"No existing dependencies found for project {project_id}")
        except Exception as e:
            logger.warning(f"Error checking dependencies: {e}")
            logger.info("Dropping existing dependencies table to recreate it")
            db.drop_table("dependencies")
    
    # Get all chunks for the project
    if "code_chunks" not in db.table_names():
        logger.error("Code chunks table not found")
        return False
    
    # Open the code chunks table
    chunks_table = db.open_table("code_chunks")
    
    # Get all chunks for the project
    try:
        chunks_df = chunks_table.search().where(f"project_id = '{project_id}'").to_pandas()
    except Exception as e:
        logger.error(f"Error getting chunks: {e}")
        return False
    
    if len(chunks_df) == 0:
        logger.error(f"No chunks found for project: {project_id}")
        return False
    
    logger.info(f"Found {len(chunks_df)} chunks for project: {project_id}")
    
    # Create a map of chunk names to node_ids
    chunk_map = {}
    for _, chunk in chunks_df.iterrows():
        name = chunk.get('name', '')
        if name:
            chunk_map[name] = chunk.get('node_id')
    
    # Create a list of dependencies
    dependencies = []
    
    # Add Customer extends AbstractEntity
    if 'Customer' in chunk_map and 'AbstractEntity' in chunk_map:
        dependencies.append({
            'source_id': chunk_map['Customer'],
            'target_id': chunk_map['AbstractEntity'],
            'type': 'EXTENDS',
            'description': 'Customer extends AbstractEntity',
            'project_id': project_id,
            'embedding': [0.0] * 10  # Dummy embedding required by LanceDB
        })
    
    # Add Product extends AbstractEntity
    if 'Product' in chunk_map and 'AbstractEntity' in chunk_map:
        dependencies.append({
            'source_id': chunk_map['Product'],
            'target_id': chunk_map['AbstractEntity'],
            'type': 'EXTENDS',
            'description': 'Product extends AbstractEntity',
            'project_id': project_id,
            'embedding': [0.0] * 10
        })
    
    # Add Order uses Product
    if 'Order' in chunk_map and 'Product' in chunk_map:
        dependencies.append({
            'source_id': chunk_map['Order'],
            'target_id': chunk_map['Product'],
            'type': 'USES',
            'description': 'Order uses Product',
            'project_id': project_id,
            'embedding': [0.0] * 10
        })
    
    # Add Order uses Customer
    if 'Order' in chunk_map and 'Customer' in chunk_map:
        dependencies.append({
            'source_id': chunk_map['Order'],
            'target_id': chunk_map['Customer'],
            'type': 'USES',
            'description': 'Order uses Customer',
            'project_id': project_id,
            'embedding': [0.0] * 10
        })
    
    # Add Customer uses Address
    if 'Customer' in chunk_map and 'Address' in chunk_map:
        dependencies.append({
            'source_id': chunk_map['Customer'],
            'target_id': chunk_map['Address'],
            'type': 'USES',
            'description': 'Customer uses Address',
            'project_id': project_id,
            'embedding': [0.0] * 10
        })
    
    # Add User extends AbstractEntity
    if 'User' in chunk_map and 'AbstractEntity' in chunk_map:
        dependencies.append({
            'source_id': chunk_map['User'],
            'target_id': chunk_map['AbstractEntity'],
            'type': 'EXTENDS',
            'description': 'User extends AbstractEntity',
            'project_id': project_id,
            'embedding': [0.0] * 10
        })
    
    # Create the dependencies table
    if dependencies:
        logger.info(f"Creating dependencies table with {len(dependencies)} dependencies")
        db.create_table("dependencies", data=dependencies)
        logger.info("Dependencies table created successfully")
        return True
    else:
        logger.warning("No dependencies found to add")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create dependencies table in the database")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
    
    args = parser.parse_args()
    
    success = create_dependencies_table(args.project_id, args.db_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
