#!/usr/bin/env python3

"""
Merge Code Agent - Main Entry Point

This script serves as the main entry point for the Merge Code Agent.
It reads instructions from a file and executes them to modify code.
"""

import sys
import os
from llm_node import LLMNode
from filesystem_node import FilesystemNode

def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python run_agent.py <instructions_file> <target_project>")
        sys.exit(1)

    instructions_file = sys.argv[1]
    target_project = sys.argv[2]

    # Validate inputs
    if not os.path.exists(instructions_file):
        print(f"Error: Instructions file not found: {instructions_file}")
        sys.exit(1)

    if not os.path.exists(target_project):
        print(f"Creating target project directory: {target_project}")
        os.makedirs(target_project)

    try:
        # Initialize the LLM node
        llm_node = LLMNode()

        # Read and parse instructions
        print(f"Reading instructions from: {instructions_file}")
        instructions = llm_node.read_instructions(instructions_file)
        actions = llm_node.parse_instructions(instructions)

        # Initialize the filesystem node with the LLM node
        fs_node = FilesystemNode(target_project, llm_node)

        # Execute the actions
        print("\nExecuting actions:")
        print("=" * 80)
        for i, action in enumerate(actions, 1):
            print(f"\nAction {i}/{len(actions)}:")
            print(f"Type: {action.get('action', 'unknown')}")
            print(f"File: {action.get('file_path', 'N/A')}")
            
            # Get user approval
            response = input("\nDo you want to execute this action? (y/n): ").lower()
            if response != 'y':
                print("Skipping action...")
                continue

            # Execute the action
            try:
                fs_node.execute_action(action)
                print("Action executed successfully!")
            except Exception as e:
                print(f"Error executing action: {str(e)}")
                response = input("Do you want to continue with remaining actions? (y/n): ").lower()
                if response != 'y':
                    print("Stopping execution...")
                    break

        print("\nAll actions completed!")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 