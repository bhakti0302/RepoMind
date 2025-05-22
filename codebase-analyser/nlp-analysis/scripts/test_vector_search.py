#!/usr/bin/env python3

"""
Test Vector Search Script.

This script tests the vector search functionality with the new vector column.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the vector search
try:
    from src.vector_search import VectorSearch
except ImportError as e:
    logger.error(f"Error importing vector search: {e}")
    sys.exit(1)

def test_vector_search(
    db_path: str,
    query: str,
    limit: int = 5,
    output_file: Optional[str] = None
) -> None:
    """Test the vector search functionality.
    
    Args:
        db_path: Path to the LanceDB database
        query: Search query
        limit: Maximum number of results to return
        output_file: Path to the output file
    """
    try:
        # Initialize the vector search
        logger.info(f"Initializing vector search with database at {db_path}")
        vector_search = VectorSearch(db_path=db_path)
        
        # Search for code chunks
        logger.info(f"Searching for: '{query}'")
        results = vector_search.search(query=query, limit=limit)
        
        # Print the results
        print(f"\nVector Search Results:")
        print(f"Query: {query}")
        print(f"Number of results: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"  Score: {result.get('score', 'N/A')}")
            print(f"  File: {result.get('file_path', 'N/A')}")
            print(f"  Type: {result.get('chunk_type', 'N/A')}")
            
            # Print a snippet of the content
            content = result.get('content', '')
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"  Content: {content}")
        
        # Save the results to a file if specified
        if output_file:
            logger.info(f"Saving results to {output_file}")
            with open(output_file, 'w') as f:
                f.write(f"Vector Search Results\n")
                f.write(f"====================\n\n")
                f.write(f"Query: {query}\n")
                f.write(f"Number of results: {len(results)}\n\n")
                
                for i, result in enumerate(results):
                    f.write(f"Result {i+1}:\n")
                    f.write(f"  Score: {result.get('score', 'N/A')}\n")
                    f.write(f"  File: {result.get('file_path', 'N/A')}\n")
                    f.write(f"  Type: {result.get('chunk_type', 'N/A')}\n")
                    
                    # Write a snippet of the content
                    content = result.get('content', '')
                    if len(content) > 100:
                        content = content[:100] + "..."
                    f.write(f"  Content: {content}\n\n")
        
        # Close the connection
        vector_search.close()
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing vector search: {e}")
        raise

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the vector search functionality")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results to return")
    parser.add_argument("--output-file", help="Path to the output file")
    args = parser.parse_args()
    
    # Test the vector search
    test_vector_search(
        db_path=args.db_path,
        query=args.query,
        limit=args.limit,
        output_file=args.output_file
    )

if __name__ == "__main__":
    main()
