#!/usr/bin/env python3

"""
Run just the multi-hop RAG component.

This script runs just the multi-hop RAG component without the LLM code generation.
"""

import os
import sys
import logging

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the multi-hop RAG
try:
    from src.multi_hop_rag import MultiHopRAG
    from src.env_loader import load_env_vars
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def run_multihop_rag(
    input_file: str,
    db_path: str,
    output_dir: str
):
    """Run just the multi-hop RAG component.

    Args:
        input_file: Path to the input file
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Read the input file
        logger.info(f"Reading input file: {input_file}")
        with open(input_file, 'r') as f:
            content = f.read()

        # Use the entire content as the query
        query = content.replace('\n', ' ').strip()
        logger.info(f"Generated query: {query}")

        # Run multi-hop RAG
        logger.info("Running multi-hop RAG")
        rag = MultiHopRAG(db_path=db_path, output_dir=output_dir)
        rag_result = rag.multi_hop_rag(query=query)
        logger.info(f"Completed multi-hop RAG")

        # Clean up
        rag.close()

        # Print the output file path
        output_file = os.path.join(output_dir, "output-multi-hop.txt")
        if os.path.exists(output_file):
            print(f"\nMulti-hop RAG output saved to: {output_file}")

        logger.info("Multi-hop RAG completed successfully")

    except Exception as e:
        logger.error(f"Error running multi-hop RAG: {e}")
        sys.exit(1)

def main():
    # Load environment variables
    load_env_vars()

    # Define parameters
    input_file = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    db_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
    output_dir = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"

    # Run multi-hop RAG
    run_multihop_rag(
        input_file=input_file,
        db_path=db_path,
        output_dir=output_dir
    )

    print("\nMulti-hop RAG completed successfully!")

if __name__ == "__main__":
    main()
