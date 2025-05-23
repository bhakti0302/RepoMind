#!/usr/bin/env python3
"""
Test script for analyzing a complex Java project.

This script demonstrates the complete codebase analysis pipeline
by analyzing a complex Java project with multiple classes and dependencies.
"""

import os
import sys
import logging
import argparse
import time
from pathlib import Path

# Add parent directory to path to import run_codebase_analysis
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from run_codebase_analysis import analyze_codebase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the codebase analysis on a complex Java project")
    
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
    parser.add_argument("--clear-db", action="store_true", help="Clear the database before processing")
    parser.add_argument("--output-dir", default="samples", help="Directory to save visualization outputs")
    parser.add_argument("--no-visualize", action="store_true", help="Skip visualization")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    start_time = time.time()
    
    # Create a mock args object for analyze_codebase
    class MockArgs:
        repo_path = os.path.join(os.path.dirname(__file__), "samples", "complex_java_project")
        db_path = args.db_path
        clear_db = args.clear_db
        minimal_schema = True
        embedding_model = "microsoft/codebert-base"
        embedding_batch_size = 8
        embedding_cache_dir = ".cache"
        mock_embeddings = True
        visualize = not args.no_visualize
        output_dir = args.output_dir
        graph_format = "png"
        project_id = "complex-java-project"
        max_files = None
        skip_large_files = False
    
    mock_args = MockArgs()
    
    # Run the analysis
    logger.info(f"Starting analysis of complex Java project at {mock_args.repo_path}")
    success = analyze_codebase(mock_args)
    
    if success:
        elapsed_time = time.time() - start_time
        logger.info(f"Analysis completed successfully in {elapsed_time:.2f} seconds")
        
        # Check the results
        db_path = os.path.abspath(mock_args.db_path)
        logger.info(f"Database stored at: {db_path}")
        
        if mock_args.visualize:
            visualization_path = os.path.join(mock_args.output_dir, "dependency_graph.png")
            logger.info(f"Visualization saved at: {visualization_path}")
    else:
        logger.error("Analysis failed")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
