#!/usr/bin/env python3

"""
Test script for the RAG system.

This script tests the RAG system with a sample query to verify if it's working correctly.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the components
try:
    from src.vector_search import VectorSearch
    from src.multi_hop_rag import MultiHopRAG
    from src.env_loader import load_env_vars
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def test_vector_search(db_path, query="employee management system", limit=5):
    """Test the vector search functionality.
    
    Args:
        db_path: Path to the LanceDB database
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        List of search results
    """
    logger.info(f"Testing vector search with query: '{query}'")
    
    # Initialize vector search
    vector_search = VectorSearch(db_path=db_path)
    logger.info(f"Initialized vector search with database at {db_path}")
    
    # Search for code chunks
    search_results = vector_search.search(query=query, limit=limit)
    logger.info(f"Found {len(search_results)} results for query: '{query}'")
    
    # Print the results
    print(f"\nVector Search Results:")
    print(f"Query: {query}")
    print(f"Number of results: {len(search_results)}")
    
    for i, result in enumerate(search_results):
        print(f"\nResult {i+1}:")
        print(f"  Score: {result.get('score', 'N/A')}")
        print(f"  File: {result.get('file_path', 'N/A')}")
        print(f"  Type: {result.get('type', 'N/A')}")
        
        # Print a sample of the content
        content = result.get('content', '')
        if len(content) > 100:
            content = content[:100] + "..."
        print(f"  Content: {content}")
    
    # Close the connection
    vector_search.close()
    logger.info("Closed vector search connection")
    
    return search_results

def test_multi_hop_rag(db_path, output_dir, query="employee management system"):
    """Test the multi-hop RAG functionality.
    
    Args:
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
        query: Search query
        
    Returns:
        Dictionary containing multi-hop RAG results
    """
    logger.info(f"Testing multi-hop RAG with query: '{query}'")
    
    # Initialize multi-hop RAG
    rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
    logger.info(f"Initialized multi-hop RAG with database at {db_path}")
    
    # Implement multi-hop RAG
    result = rag.multi_hop_rag(query=query)
    logger.info(f"Implemented multi-hop RAG for query: '{query}'")
    
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
    
    # Save the results to a file
    output_file = os.path.join(output_dir, "multi-hop-test-output.txt")
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
    
    logger.info(f"Saved results to {output_file}")
    
    # Close the connection
    rag.close()
    logger.info("Closed RAG connection")
    
    return result

def main():
    """Main function."""
    # Load environment variables
    load_env_vars()
    
    # Get database path from environment or use default
    db_path = os.environ.get("DB_PATH", "../.lancedb")
    
    # Make sure the database path is absolute
    db_path = os.path.abspath(db_path)
    
    # Get output directory from environment or use default
    output_dir = os.environ.get("OUTPUT_DIR", "./output")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Test vector search
    print("\n=== Testing Vector Search ===\n")
    vector_search_results = test_vector_search(db_path)
    
    # Test multi-hop RAG
    print("\n=== Testing Multi-Hop RAG ===\n")
    multi_hop_rag_results = test_multi_hop_rag(db_path, output_dir)
    
    # Print summary
    print("\n=== Test Summary ===\n")
    print(f"Vector Search: Found {len(vector_search_results)} results")
    print(f"Multi-Hop RAG: Found {len(multi_hop_rag_results.get('architectural_patterns', []))} architectural patterns, {len(multi_hop_rag_results.get('implementation_details', []))} implementation details, and {len(multi_hop_rag_results.get('related_components', []))} related components")
    
    # Check if the tests were successful
    if vector_search_results and multi_hop_rag_results:
        print("\nRAG system is working correctly!")
        return True
    else:
        print("\nRAG system is not working correctly.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
