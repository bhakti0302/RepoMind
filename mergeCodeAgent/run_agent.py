#!/usr/bin/env python3
"""
Script to run the Merge Code Agent with LLM-based file modification.

Features:
- LLM-powered file creation and modification
- Path normalization to prevent duplication issues
- Automatic Java file formatting
- CAP SAP Java validation and automatic fixes
"""

import os
import sys
import json
import pathlib
import re

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_node import LLMNode
from filesystem_node import FilesystemNode
from path_utils import normalize_path

def main():
    """Run the Merge Code Agent with LLM-based file modification."""
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python run_agent.py <instructions_file> <codebase_path>")
        return 1

    # Get paths from command line arguments
    instructions_path = sys.argv[1]
    codebase_path = sys.argv[2]

    # Normalize the codebase path to avoid path issues
    codebase_path = os.path.normpath(os.path.abspath(codebase_path))
    print(f"Using normalized codebase path: {codebase_path}")

    # Ensure the instructions file exists
    if not os.path.exists(instructions_path):
        print(f"Error: Instructions file not found: {instructions_path}")
        return 1

    # Ensure the codebase directory exists
    if not os.path.exists(codebase_path):
        print(f"Creating codebase directory: {codebase_path}")
        os.makedirs(codebase_path, exist_ok=True)

    # Initialize the LLM node
    try:
        llm_node = LLMNode()
    except ValueError as e:
        print(f"Error initializing LLM node: {str(e)}")
        print("Make sure you have set the OPENAI_API_KEY environment variable.")
        return 1

    # Initialize the filesystem node with the LLM node
    fs_node = FilesystemNode(codebase_path, llm_node)

    # Read and process the instructions
    print(f"Reading instructions from: {instructions_path}")
    actions = llm_node.process_instructions(instructions_path)

    # Process each action
    for i, action in enumerate(actions, 1):
        print(f"\nProcessing action {i}/{len(actions)}:")
        print(f"Action type: {action.get('action')}")
        
        # Normalize file paths in the action
        if 'file_path' in action and action['file_path']:
            file_path = action['file_path']
            print(f"Original file path: {file_path}")
            
            # Apply our improved path normalization
            action['file_path'] = normalize_path(file_path, codebase_path)
                
            print(f"Normalized file path: {action['file_path']}")
        
        print(f"File path: {action.get('file_path')}")

        # Get user approval
        approval = input("\nDo you want to execute this action? (y/n): ")
        if approval.lower() != 'y':
            print("Action not approved. Skipping.")
            continue

        # Execute the action
        print("\nExecuting action...")
        success, error = fs_node.execute_action(action)

        if success:
            print("Action executed successfully!")
        else:
            print(f"Error: {error}")

    print("\nAll actions processed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
