#!/usr/bin/env python3
"""
Script to manually update the project_id of specific entries in the LanceDB database.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

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

def find_database_path() -> Optional[str]:
    """Find the LanceDB database path."""
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
            return path
    
    logger.error("Could not find database path")
    return None

def list_entries(db_path: str, table_name: str, filter_project_id: Optional[str] = None, 
                 limit: Optional[int] = None) -> pd.DataFrame:
    """List entries in the specified table.
    
    Args:
        db_path: Path to the LanceDB database
        table_name: Name of the table to view
        filter_project_id: Filter by project ID
        limit: Maximum number of entries to display
        
    Returns:
        DataFrame containing the entries
    """
    logger.info(f"Connecting to database at {db_path}")
    
    try:
        # Connect to the database
        db = lancedb.connect(db_path)
        logger.info("Successfully connected to database")
        
        # Open the table
        table = db.open_table(table_name)
        logger.info(f"Successfully opened table {table_name}")
        
        # Get all rows
        df = table.to_pandas()
        logger.info(f"Retrieved {len(df)} total rows")
        
        # Filter by project_id if specified
        if filter_project_id and 'project_id' in df.columns:
            df = df[df['project_id'] == filter_project_id]
            logger.info(f"Filtered to {len(df)} rows for project_id {filter_project_id}")
        
        # Exclude embedding column to make output more readable
        for col in df.columns:
            if col.lower() in ['embedding', 'vector', 'embeddings', 'embedding_vector']:
                logger.info(f"Excluding column {col} from display")
                df = df.drop(columns=[col])
        
        # Limit the number of rows if specified
        if limit is not None:
            df = df.head(limit)
            logger.info(f"Limited to {len(df)} rows")
        
        return df
    
    except Exception as e:
        logger.error(f"Error listing entries: {e}")
        return pd.DataFrame()

def update_project_id(db_path: str, table_name: str, node_ids: List[str], new_project_id: str) -> bool:
    """Update the project_id of specific entries.
    
    Args:
        db_path: Path to the LanceDB database
        table_name: Name of the table
        node_ids: List of node_ids to update
        new_project_id: New project_id to set
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Updating project_id to '{new_project_id}' for {len(node_ids)} entries")
    
    try:
        # Connect to the database
        db = lancedb.connect(db_path)
        logger.info("Successfully connected to database")
        
        # Open the table
        table = db.open_table(table_name)
        logger.info(f"Successfully opened table {table_name}")
        
        # Get all rows
        df = table.to_pandas()
        logger.info(f"Retrieved {len(df)} total rows")
        
        # Find the rows to update
        rows_to_update = df[df['node_id'].isin(node_ids)]
        logger.info(f"Found {len(rows_to_update)} rows to update")
        
        if len(rows_to_update) == 0:
            logger.warning("No rows found with the specified node_ids")
            return False
        
        # Update the project_id
        for node_id in node_ids:
            try:
                # Update the row
                table.update(
                    where=f"node_id = '{node_id}'",
                    values={"project_id": new_project_id}
                )
                logger.info(f"Updated project_id for node_id: {node_id}")
            except Exception as e:
                logger.error(f"Error updating node_id {node_id}: {e}")
        
        logger.info(f"Successfully updated project_id for {len(node_ids)} entries")
        return True
    
    except Exception as e:
        logger.error(f"Error updating project_id: {e}")
        return False

def interactive_update(db_path: str, table_name: str, old_project_id: Optional[str] = None, 
                       new_project_id: Optional[str] = None) -> None:
    """Interactively update project_ids.
    
    Args:
        db_path: Path to the LanceDB database
        table_name: Name of the table
        old_project_id: Current project_id to filter by
        new_project_id: New project_id to set
    """
    # List entries
    df = list_entries(db_path, table_name, filter_project_id=old_project_id)
    
    if len(df) == 0:
        logger.error("No entries found")
        return
    
    # Display entries
    print("\n" + "="*80)
    print(f"Entries in table {table_name}:")
    print("="*80)
    
    # Add an index column for selection
    df_with_index = df.reset_index()
    print(df_with_index[['index', 'node_id', 'project_id', 'name', 'chunk_type']])
    print("="*80)
    
    # Get the new project_id if not provided
    if new_project_id is None:
        new_project_id = input("Enter the new project_id: ")
    
    # Get the indices to update
    indices_input = input("Enter the indices to update (comma-separated, or 'all' for all entries): ")
    
    if indices_input.lower() == 'all':
        # Update all entries
        node_ids = df['node_id'].tolist()
    else:
        # Parse indices
        try:
            indices = [int(idx.strip()) for idx in indices_input.split(',')]
            node_ids = df_with_index.loc[indices, 'node_id'].tolist()
        except Exception as e:
            logger.error(f"Error parsing indices: {e}")
            return
    
    # Confirm the update
    print(f"\nYou are about to update {len(node_ids)} entries to project_id '{new_project_id}'")
    confirm = input("Proceed? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Update cancelled")
        return
    
    # Update the project_id
    success = update_project_id(db_path, table_name, node_ids, new_project_id)
    
    if success:
        print(f"Successfully updated {len(node_ids)} entries to project_id '{new_project_id}'")
    else:
        print("Update failed")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update project_id of entries in the LanceDB database")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--table", default="code_chunks", help="Name of the table")
    parser.add_argument("--old-project-id", help="Current project_id to filter by")
    parser.add_argument("--new-project-id", help="New project_id to set")
    parser.add_argument("--node-ids", help="Comma-separated list of node_ids to update")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    # Find the database path if not provided
    db_path = args.db_path or find_database_path()
    if db_path is None:
        return
    
    if args.interactive:
        # Interactive mode
        interactive_update(db_path, args.table, args.old_project_id, args.new_project_id)
    elif args.node_ids and args.new_project_id:
        # Update specific node_ids
        node_ids = [node_id.strip() for node_id in args.node_ids.split(',')]
        update_project_id(db_path, args.table, node_ids, args.new_project_id)
    else:
        # Display usage
        parser.print_help()

if __name__ == "__main__":
    main()