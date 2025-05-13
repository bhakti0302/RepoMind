#!/usr/bin/env python3
"""
Script to view all entries in the LanceDB database.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the codebase-analyser directory to the path
codebase_analyser_dir = str(Path(__file__).parent.parent)
if codebase_analyser_dir not in sys.path:
    sys.path.append(codebase_analyser_dir)
    logger.info(f"Added {codebase_analyser_dir} to sys.path")

import lancedb
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 50)

def view_all_entries(db_path=None, table_name="code_chunks", limit=None, project_id=None):
    """View all entries in the specified table.
    
    Args:
        db_path: Path to the LanceDB database
        table_name: Name of the table to view
        limit: Maximum number of entries to display
        project_id: Filter by project ID
    """
    # Use the default path if not specified
    if db_path is None:
        # Try common locations
        possible_paths = [
            os.path.join(codebase_analyser_dir, ".lancedb"),
            os.path.join(os.getcwd(), ".lancedb"),
            os.path.join(os.getcwd(), "codebase-analyser", ".lancedb"),
            os.path.join(os.path.dirname(os.getcwd()), ".lancedb"),
            os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), ".lancedb")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found database at: {path}")
                db_path = path
                break
        
        if db_path is None:
            logger.error("Could not find database path")
            return
    
    logger.info(f"Connecting to database at {db_path}")
    
    try:
        # Connect to the database
        db = lancedb.connect(db_path)
        logger.info("Successfully connected to database")
        
        # Get table names
        try:
            table_names = db.table_names()
            logger.info(f"Available tables: {table_names}")
            
            if table_name not in table_names:
                logger.error(f"Table {table_name} not found")
                logger.info("Available tables:")
                for name in table_names:
                    logger.info(f"  - {name}")
                return
        except AttributeError:
            logger.warning("Could not get table names (older LanceDB version)")
            # Try to open the table directly
            try:
                db.open_table(table_name)
                logger.info(f"Table {table_name} exists")
            except Exception as e:
                logger.error(f"Table {table_name} not found: {e}")
                return
        
        # Open the table
        table = db.open_table(table_name)
        logger.info(f"Successfully opened table {table_name}")
        
        # Get the schema
        try:
            schema = table.schema
            logger.info(f"Table schema: {schema}")
        except AttributeError:
            logger.warning("Could not get schema (older LanceDB version)")
        
        # Get all rows
        df = table.to_pandas()
        logger.info(f"Retrieved {len(df)} total rows")
        
        # Filter by project_id if specified
        if project_id and 'project_id' in df.columns:
            df = df[df['project_id'] == project_id]
            logger.info(f"Filtered to {len(df)} rows for project_id {project_id}")
        
        # Exclude embedding column to make output more readable
        for col in df.columns:
            if col.lower() in ['embedding', 'vector', 'embeddings', 'embedding_vector']:
                logger.info(f"Excluding column {col} from display")
                df = df.drop(columns=[col])
        
        # Limit the number of rows if specified
        if limit is not None:
            df = df.head(limit)
            logger.info(f"Limited to {len(df)} rows")
        
        # Print the data
        print("\n" + "="*80)
        print(f"Data from table {table_name}:")
        print("="*80)
        print(df)
        print("="*80)
        
        # Print summary information
        if 'chunk_type' in df.columns:
            print("\nChunk types:")
            print(df['chunk_type'].value_counts())
        
        if 'language' in df.columns:
            print("\nLanguages:")
            print(df['language'].value_counts())
        
        if 'project_id' in df.columns:
            print("\nProjects:")
            print(df['project_id'].value_counts())
        
    except Exception as e:
        logger.error(f"Error viewing database entries: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="View all entries in the LanceDB database")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--table", default="code_chunks", help="Name of the table to view")
    parser.add_argument("--limit", type=int, help="Maximum number of entries to display")
    parser.add_argument("--project-id", help="Filter by project ID")
    
    args = parser.parse_args()
    
    view_all_entries(
        db_path=args.db_path,
        table_name=args.table,
        limit=args.limit,
        project_id=args.project_id
    )

if __name__ == "__main__":
    main()