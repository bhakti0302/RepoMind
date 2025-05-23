#!/usr/bin/env python3

"""
Run the pipeline with logging.

This script runs the pipeline with logging, creating a new log file for each run.
"""

import os
import sys
import subprocess
import datetime
import argparse

# Import the run_with_logs function
from run_with_logs import run_with_logs

def run_pipeline(input_file=None, db_path=None, output_dir=None, logs_dir=None):
    """Run the pipeline with logging.
    
    Args:
        input_file: Path to the input file
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
        logs_dir: Directory to store logs
    
    Returns:
        Exit code of the pipeline
    """
    # Define default paths
    if input_file is None:
        input_file = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    
    if db_path is None:
        db_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
    
    if output_dir is None:
        output_dir = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"
    
    if logs_dir is None:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level and then to the logs directory
        logs_dir = os.path.join(os.path.dirname(script_dir), "logs")
    
    # Create the logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Set the Python path to include the current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Change to the nlp-analysis directory
    os.chdir(script_dir)
    
    # Step 1: Install the spaCy model with logging
    print("Installing spaCy model...")
    exit_code = run_with_logs(["python3", "install_spacy_model.py"], logs_dir)
    if exit_code != 0:
        print(f"Error installing spaCy model. Exit code: {exit_code}")
        return exit_code
    
    # Step 2: Run the multi-hop RAG with logging
    print("Running multi-hop RAG...")
    exit_code = run_with_logs(["python3", "run_rag_to_llm.py"], logs_dir)
    if exit_code != 0:
        print(f"Error running multi-hop RAG. Exit code: {exit_code}")
        return exit_code
    
    print("Pipeline completed successfully!")
    print(f"Check the output files in {output_dir}")
    print(f"Check the logs in {logs_dir}")
    
    return 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run the pipeline with logging.")
    parser.add_argument("--input-file", help="Path to the input file")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", help="Path to the output directory")
    parser.add_argument("--logs-dir", help="Directory to store logs")
    args = parser.parse_args()
    
    # Run the pipeline with logging
    exit_code = run_pipeline(
        input_file=args.input_file,
        db_path=args.db_path,
        output_dir=args.output_dir,
        logs_dir=args.logs_dir
    )
    
    # Exit with the same code as the pipeline
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
