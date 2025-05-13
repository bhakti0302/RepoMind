#!/usr/bin/env python3

"""
Test script for the NLP Analysis Pipeline.

This script provides a simple way to test the entire system end-to-end
from the command line, without requiring the VS Code extension.
"""

import os
import sys
import time
import argparse
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.code_synthesis_workflow import CodeSynthesisWorkflow
from src.env_loader import load_env_vars

def test_end_to_end(input_file, output_dir, rag_type="multi_hop", generate_code=True):
    """Run an end-to-end test of the system."""
    print(f"Testing with input file: {input_file}")
    print(f"Output directory: {output_dir}")
    print(f"RAG type: {rag_type}")
    print(f"Generate code: {generate_code}")
    
    # Load environment variables
    load_env_vars()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize workflow
    workflow = CodeSynthesisWorkflow(
        output_dir=output_dir
    )
    
    # Print LLM information
    print(f"LLM API Key: {'Set' if workflow.llm_api_key else 'Not set'}")
    print(f"LLM Model: {workflow.llm_model_name}")
    
    # Start timer
    start_time = time.time()
    
    # Run workflow
    print("\nRunning workflow...")
    result = workflow.run_workflow(
        input_file=input_file,
        rag_type=rag_type,
        generate_code=generate_code
    )
    
    # End timer
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Check for errors
    if "error" in result:
        print(f"\nError: {result['error']}")
        return False
    
    # Print success message
    print(f"\nWorkflow completed successfully in {elapsed_time:.2f} seconds!")
    
    # Check output files
    instructions_file = result.get("instructions_file")
    output_file = result.get("output_file")
    
    if instructions_file and os.path.exists(instructions_file):
        print(f"Instructions file created: {instructions_file}")
        print(f"  Size: {os.path.getsize(instructions_file)} bytes")
    else:
        print("Instructions file not created")
    
    if output_file and os.path.exists(output_file):
        print(f"Output file created: {output_file}")
        print(f"  Size: {os.path.getsize(output_file)} bytes")
        
        # Print the first few lines of the output
        print("\nFirst 10 lines of output:")
        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                print(f"  {line.rstrip()}")
        print("  ...")
    elif generate_code:
        print("Output file not created")
        return False
    
    # Check for LLM error
    if "llm_error" in result:
        print(f"\nLLM error: {result['llm_error']}")
        return False
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the NLP Analysis Pipeline")
    parser.add_argument("--input-file", required=True, help="Path to the input file")
    parser.add_argument("--output-dir", default="output", help="Path to the output directory")
    parser.add_argument("--rag-type", choices=["basic", "graph", "multi_hop"], default="multi_hop",
                        help="Type of RAG to use")
    parser.add_argument("--generate-code", action="store_true", default=True,
                        help="Whether to generate code using LLM")
    parser.add_argument("--env-file", help="Path to the .env file")
    args = parser.parse_args()
    
    # Load environment variables from specified file
    if args.env_file:
        load_env_vars(args.env_file)
    
    success = test_end_to_end(
        input_file=args.input_file,
        output_dir=args.output_dir,
        rag_type=args.rag_type,
        generate_code=args.generate_code
    )
    
    sys.exit(0 if success else 1)
