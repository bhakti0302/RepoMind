#!/usr/bin/env python3
"""
Script to view sample data from the database.
"""

from codebase_analyser.database import open_db_connection, close_db_connection
import json

def view_sample_data():
    """View sample data from the database."""
    # Open a database connection
    db_manager = open_db_connection()
    
    try:
        # Get the code chunks
        chunks = db_manager.tables["code_chunks"].to_pandas()
        
        # Print the number of chunks
        print(f"Number of code chunks: {len(chunks)}")
        
        # Print a sample chunk
        if len(chunks) > 0:
            sample_chunk = chunks.iloc[0]
            print("\nSample code chunk:")
            print(f"  node_id: {sample_chunk['node_id']}")
            print(f"  chunk_type: {sample_chunk['chunk_type']}")
            print(f"  name: {sample_chunk['name']}")
            print(f"  language: {sample_chunk['language']}")
            print(f"  file_path: {sample_chunk['file_path']}")
            print(f"  start_line: {sample_chunk['start_line']}")
            print(f"  end_line: {sample_chunk['end_line']}")
            
            # Parse and print metadata
            if sample_chunk['metadata']:
                try:
                    metadata = json.loads(sample_chunk['metadata'])
                    print("\n  metadata:")
                    for key, value in metadata.items():
                        print(f"    {key}: {value}")
                except json.JSONDecodeError:
                    print(f"  metadata: {sample_chunk['metadata']}")
            
            # Parse and print context
            if sample_chunk['context']:
                try:
                    context = json.loads(sample_chunk['context'])
                    print("\n  context:")
                    for key, value in context.items():
                        print(f"    {key}: {value}")
                except json.JSONDecodeError:
                    print(f"  context: {sample_chunk['context']}")
            
            # Print the content (truncated)
            content = sample_chunk['content']
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"\n  content: {content}")
        
        # Get the dependencies
        dependencies = db_manager.tables["dependencies"].to_pandas()
        
        # Print the number of dependencies
        print(f"\nNumber of dependencies: {len(dependencies)}")
        
        # Print a sample dependency
        if len(dependencies) > 0:
            sample_dep = dependencies.iloc[0]
            print("\nSample dependency:")
            print(f"  source_id: {sample_dep['source_id']}")
            print(f"  target_id: {sample_dep['target_id']}")
            print(f"  type: {sample_dep['type']}")
            print(f"  strength: {sample_dep['strength']}")
            print(f"  is_direct: {sample_dep['is_direct']}")
            print(f"  is_required: {sample_dep['is_required']}")
            print(f"  description: {sample_dep['description']}")
    
    finally:
        # Close the database connection
        close_db_connection(db_manager)

if __name__ == "__main__":
    view_sample_data()
