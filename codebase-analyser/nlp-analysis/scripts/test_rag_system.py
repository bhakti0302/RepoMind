#!/usr/bin/env python3

"""
Test RAG System Script.

This script tests the RAG system with a sample query without modifying the database structure.
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

# Import the vector search and multi-hop RAG
try:
    from src.vector_search import VectorSearch
    from src.multi_hop_rag import MultiHopRAG
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
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
        logger.info("Vector search test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing vector search: {e}")
        raise

def test_multi_hop_rag(
    db_path: str,
    query: str,
    output_dir: str = "./output",
    max_hops: int = 3,
    output_file: Optional[str] = None
) -> None:
    """Test the multi-hop RAG functionality.
    
    Args:
        db_path: Path to the LanceDB database
        query: Search query
        output_dir: Path to the output directory
        max_hops: Maximum number of hops
        output_file: Path to the output file
    """
    try:
        # Initialize the multi-hop RAG
        logger.info(f"Initializing multi-hop RAG with database at {db_path}")
        rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
        
        # Implement multi-hop RAG
        logger.info(f"Implementing multi-hop RAG for query: '{query}'")
        result = rag.multi_hop_rag(query=query, max_hops=max_hops)
        
        # Print the results
        print(f"\nMulti-Hop RAG Results:")
        print(f"Query: {query}")
        
        print(f"\nArchitectural Patterns:")
        for pattern in result.get('architectural_patterns', []):
            print(f"  - {pattern}")
        
        print(f"\nImplementation Details:")
        for detail in result.get('implementation_details', []):
            print(f"  - {detail}")
        
        print(f"\nRelated Components:")
        for component in result.get('related_components', []):
            print(f"  - {component}")
        
        # Print a sample of the context
        context = result.get('context', '')
        if len(context) > 200:
            context = context[:200] + "..."
        print(f"\nContext Sample:\n{context}")
        
        # Save the results to a file if specified
        if output_file:
            logger.info(f"Saving results to {output_file}")
            with open(output_file, 'w') as f:
                f.write(f"Multi-Hop RAG Results\n")
                f.write(f"====================\n\n")
                f.write(f"Query: {query}\n\n")
                
                f.write(f"Architectural Patterns:\n")
                for pattern in result.get('architectural_patterns', []):
                    f.write(f"  - {pattern}\n")
                
                f.write(f"\nImplementation Details:\n")
                for detail in result.get('implementation_details', []):
                    f.write(f"  - {detail}\n")
                
                f.write(f"\nRelated Components:\n")
                for component in result.get('related_components', []):
                    f.write(f"  - {component}\n")
                
                f.write(f"\nContext:\n{result.get('context', '')}")
        
        # Close the connection
        rag.close()
        logger.info("Multi-hop RAG test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing multi-hop RAG: {e}")
        raise

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the RAG system")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--query", default="employee management system", help="Search query")
    parser.add_argument("--output-dir", default="./output", help="Path to the output directory")
    parser.add_argument("--test-type", choices=["vector", "multi-hop", "both"], default="both", help="Type of test to run")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results to return")
    parser.add_argument("--max-hops", type=int, default=3, help="Maximum number of hops for multi-hop RAG")
    parser.add_argument("--output-file", help="Path to the output file")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run the tests
    if args.test_type in ["vector", "both"]:
        test_vector_search(
            db_path=args.db_path,
            query=args.query,
            limit=args.limit,
            output_file=os.path.join(args.output_dir, "vector_search_results.txt") if args.output_file is None else args.output_file
        )
    
    if args.test_type in ["multi-hop", "both"]:
        test_multi_hop_rag(
            db_path=args.db_path,
            query=args.query,
            output_dir=args.output_dir,
            max_hops=args.max_hops,
            output_file=os.path.join(args.output_dir, "multi_hop_rag_results.txt") if args.output_file is None else args.output_file
        )

if __name__ == "__main__":
    main()
