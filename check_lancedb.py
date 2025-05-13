#!/usr/bin/env python3
"""
Script to check LanceDB data.
"""

from codebase_analyser.database.unified_storage import UnifiedStorage

def main():
    # Initialize the database connection
    db = UnifiedStorage(db_path=".lancedb")
    
    # Search for code chunks by project ID
    results = db.search_code_chunks(
        query="class",  # Search query
        limit=10,       # Maximum number of results
        filters={"project_id": "src"}  # Filter by project ID
    )
    
    print(f"Found {len(results)} results for 'class' in project 'src'")
    
    # Print details of each result
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"  Name: {result.get('name', 'Unknown')}")
        print(f"  Type: {result.get('chunk_type', 'Unknown')}")
        print(f"  File: {result.get('file_path', 'Unknown')}")
        print(f"  Lines: {result.get('start_line', 0)}-{result.get('end_line', 0)}")

if __name__ == "__main__":
    main()