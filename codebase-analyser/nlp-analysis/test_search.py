#!/usr/bin/env python3

"""
Test script for the modified vector search functionality.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the vector search module
from src.vector_search import VectorSearch

def test_search(db_path, query, project_id=None, limit=10):
    """Test the vector search functionality.
    
    Args:
        db_path: Path to the LanceDB database
        query: Search query
        project_id: Project ID to filter results
        limit: Maximum number of results to return
    """
    try:
        # Initialize vector search
        search = VectorSearch(db_path=db_path)
        logger.info(f"Initialized vector search with database at {db_path}")
        
        # Search for code chunks
        results = search.search(
            query=query,
            project_id=project_id,
            limit=limit
        )
        
        # Print results
        print(f"\nFound {len(results)} results for query: {query}")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Score: {result.get('score', 0):.4f}")
            print(f"  Node ID: {result.get('node_id', 'Unknown')}")
            print(f"  Name: {result.get('name', 'Unknown')}")
            print(f"  Type: {result.get('chunk_type', 'Unknown')}")
            print(f"  File: {result.get('file_path', 'Unknown')}")
            print(f"  Lines: {result.get('start_line', 0)}-{result.get('end_line', 0)}")
            
            # Print a snippet of the content
            content = result.get('content', '')
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"  Content: {content}")
        
        # Close the connection
        search.close()
        
        return results
    
    except Exception as e:
        logger.error(f"Error testing search: {e}")
        return []

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test vector search")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--project-id", help="Project ID to filter results")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
    args = parser.parse_args()
    
    # Test search
    test_search(
        db_path=args.db_path,
        query=args.query,
        project_id=args.project_id,
        limit=args.limit
    )

if __name__ == "__main__":
    main()
