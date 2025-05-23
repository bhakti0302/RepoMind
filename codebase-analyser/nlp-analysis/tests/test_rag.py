"""
Test script for the RAG implementation.
"""

import sys
import os
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the multi-hop RAG
from src.multi_hop_rag import MultiHopRAG

def test_rag(db_path, query, output_dir=None):
    """Test the RAG implementation.
    
    Args:
        db_path: Path to the LanceDB database
        query: Search query
        output_dir: Path to the output directory
    """
    try:
        # Initialize the multi-hop RAG
        rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
        logger.info(f"Initialized multi-hop RAG with database at {db_path}")

        # Implement multi-hop RAG
        result = rag.multi_hop_rag(query=query)
        logger.info(f"Implemented multi-hop RAG for query: '{query}'")

        # Print the results
        print(f"\nMulti-Hop RAG Summary:")
        print(f"Query: {query}")
        print(f"Found {len(result.get('architectural_patterns', []))} architectural patterns")
        print(f"Found {len(result.get('implementation_details', []))} implementation details")
        print(f"Found {len(result.get('related_components', []))} related components")
        print(f"Context length: {result.get('total_tokens', 0)} tokens")

        # Print a sample of the context
        context = result.get('context', '')
        if len(context) > 200:
            context = context[:200] + "..."
        print(f"\nContext Sample:\n{context}")

        # Close the connection
        rag.close()
        logger.info("Closed RAG connection")

        return result
    
    except Exception as e:
        logger.error(f"Error testing RAG: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test RAG implementation")
    parser.add_argument("--db-path", default="../.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--query", default="Display books by author with availability status", help="Search query")
    parser.add_argument("--output-dir", default="../output", help="Path to the output directory")
    args = parser.parse_args()

    test_rag(db_path=args.db_path, query=args.query, output_dir=args.output_dir)