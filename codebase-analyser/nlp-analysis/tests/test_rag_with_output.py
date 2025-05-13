# Create a modified test_rag.py script
#!/usr/bin/env python3

"""
Test script for the RAG implementation with output to file.
"""

import sys
import os
import logging
import argparse
import json

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

def test_rag(db_path, query, output_dir=None, output_file=None):
    """Test the RAG implementation.
    
    Args:
        db_path: Path to the LanceDB database
        query: Search query
        output_dir: Path to the output directory
        output_file: Path to the output file
    """
    try:
        # Initialize the multi-hop RAG
        rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
        logger.info(f"Initialized multi-hop RAG with database at {db_path}")

        # Implement multi-hop RAG
        result = rag.multi_hop_rag(query=query)
        logger.info(f"Implemented multi-hop RAG for query: '{query}'")

        # Prepare output
        output = []
        output.append(f"Multi-Hop RAG Test Results")
        output.append(f"=========================\n")
        output.append(f"Query: {query}\n")
        
        # Add architectural patterns
        output.append(f"Architectural Patterns:")
        for pattern in result.get('architectural_patterns', []):
            output.append(f"  - {pattern}")
        output.append("")
        
        # Add implementation details
        output.append(f"Implementation Details:")
        for detail in result.get('implementation_details', []):
            output.append(f"  - {detail}")
        output.append("")
        
        # Add related components
        output.append(f"Related Components:")
        for component in result.get('related_components', []):
            output.append(f"  - {component}")
        output.append("")
        
        # Add context sample
        context = result.get('context', '')
        context_sample = context[:500] + "..." if len(context) > 500 else context
        output.append(f"Context Sample:")
        output.append(context_sample)
        output.append("")
        
        # Add token count
        output.append(f"Total Tokens: {result.get('total_tokens', 0)}")
        
        # Print the results to console
        for line in output:
            print(line)
        
        # Save to output file if specified
        if output_file:
            with open(output_file, 'w') as f:
                for line in output:
                    f.write(line + "\n")
            logger.info(f"Saved test results to {output_file}")

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
    parser.add_argument("--output-file", default="multi-hop-test-output.txt", help="Path to the output file")
    args = parser.parse_args()

    test_rag(
        db_path=args.db_path, 
        query=args.query, 
        output_dir=args.output_dir,
        output_file=args.output_file
    )


# Make the script executable
#chmod +x test_rag_with_output.py

# Run the modified test script
#python3 test_rag_with_output.py --db-path "../.lancedb" --query "book author availability" --output-dir "../output" --output-file "multi-hop-test-output.txt"