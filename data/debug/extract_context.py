#!/usr/bin/env python3
"""
Script to extract context from LanceDB for debugging.
"""

import os
import sys
import json
import logging
import lancedb
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def extract_context(db_path, project_id, output_file):
    """Extract context from LanceDB for debugging.
    
    Args:
        db_path: Path to the LanceDB database
        project_id: Project ID to filter by
        output_file: Path to save the extracted context
    """
    logger.info(f"Connecting to database: {db_path}")
    db = lancedb.connect(db_path)
    
    # Check if the code_chunks table exists
    if "code_chunks" not in db.table_names():
        logger.error("Code chunks table does not exist")
        return False
    
    # Open the table
    table = db.open_table("code_chunks")
    
    # Get all chunks for the project
    logger.info(f"Extracting chunks for project: {project_id}")
    try:
        df = table.to_pandas()
        project_chunks = df[df["project_id"] == project_id]
        
        logger.info(f"Found {len(project_chunks)} chunks for project '{project_id}'")
        
        # Convert to list of dictionaries
        chunks = []
        for _, row in project_chunks.iterrows():
            chunk = row.to_dict()
            
            # Convert numpy arrays to lists
            for key, value in chunk.items():
                if hasattr(value, 'tolist'):
                    chunk[key] = value.tolist()
            
            chunks.append(chunk)
        
        # Save to file
        logger.info(f"Saving context to: {output_file}")
        with open(output_file, 'w') as f:
            json.dump(chunks, f, indent=2)
        
        # Print summary
        print(f"Extracted {len(chunks)} chunks for project '{project_id}'")
        print(f"Context saved to: {output_file}")
        
        # Print chunk types
        chunk_types = {}
        for chunk in chunks:
            chunk_type = chunk.get('chunk_type', 'unknown')
            if chunk_type not in chunk_types:
                chunk_types[chunk_type] = 0
            chunk_types[chunk_type] += 1
        
        print("\nChunk types:")
        for chunk_type, count in chunk_types.items():
            print(f"  - {chunk_type}: {count}")
        
        # Print file paths
        file_paths = set()
        for chunk in chunks:
            file_path = chunk.get('file_path', '')
            if file_path:
                file_paths.add(file_path)
        
        print("\nFile paths:")
        for file_path in file_paths:
            print(f"  - {file_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error extracting context: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract context from LanceDB for debugging")
    parser.add_argument("--db-path", required=True, help="Path to the LanceDB database")
    parser.add_argument("--project-id", required=True, help="Project ID to filter by")
    parser.add_argument("--output-file", required=True, help="Path to save the extracted context")
    
    args = parser.parse_args()
    
    # Extract context
    success = extract_context(args.db_path, args.project_id, args.output_file)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
