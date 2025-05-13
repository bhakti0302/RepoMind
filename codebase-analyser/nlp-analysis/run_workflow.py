#!/usr/bin/env python3

"""
Run the code synthesis workflow.

This script runs the code synthesis workflow with the specified parameters.
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

# Import the workflow
try:
    from src.code_synthesis_workflow import CodeSynthesisWorkflow
    from src.env_loader import load_env_vars
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    # Load environment variables
    load_env_vars()
    
    # Define parameters
    input_file = "/Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt"
    db_path = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb"
    output_dir = "/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output"
    
    # Initialize the workflow
    workflow = CodeSynthesisWorkflow(
        db_path=db_path,
        output_dir=output_dir
    )
    
    # Run the workflow
    result = workflow.run_workflow(
        input_file=input_file,
        rag_type="multi_hop",
        generate_code=True
    )
    
    # Check for errors
    if "error" in result:
        logger.error(f"Workflow failed: {result['error']}")
        sys.exit(1)
    
    # Print success message
    print(f"\nCode synthesis workflow completed successfully!")
    
    # Print output files
    if "instructions_file" in result:
        print(f"Instructions file: {result['instructions_file']}")
    
    if "output_file" in result:
        print(f"Generated code file: {result['output_file']}")
    
    # Print LLM error if there was one
    if "llm_error" in result:
        print(f"LLM error: {result['llm_error']}")
    
    # Close connections
    workflow.close()

if __name__ == "__main__":
    main()
