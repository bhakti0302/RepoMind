#!/usr/bin/env python3
"""
Script to check LanceDB data.
"""

import lancedb
import pandas as pd
# Count chunks for your specific project
def main():
    # Connect directly to LanceDB
    db = lancedb.connect(".lancedb")
    
    try:
        # Open the code_chunks table
        table = db.open_table("code_chunks")
        
        # Convert to pandas DataFrame
        df = table.to_arrow().to_pandas()
        
        # Filter by project_id
        project_df = df[df['project_id'] == 'src']
        
        print(f"Found {len(project_df)} chunks for project 'src'")
        
        # Print some basic stats
        print("\nChunk types:")
        print(project_df['chunk_type'].value_counts())
        
        print("\nLanguages:")
        print(project_df['language'].value_counts())
        
        # Print details of a few chunks
        print("\nSample chunks:")
        for i, row in project_df.head(5).iterrows():
            print(f"\nChunk {i+1}:")
            print(f"  Name: {row.get('name', 'Unknown')}")
            print(f"  Type: {row.get('chunk_type', 'Unknown')}")
            print(f"  File: {row.get('file_path', 'Unknown')}")
            print(f"  Lines: {row.get('start_line', 0)}-{row.get('end_line', 0)}")
            
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    main()