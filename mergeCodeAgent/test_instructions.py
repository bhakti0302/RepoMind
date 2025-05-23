"""
Test script for running instructions through the Merge Code Agent.
"""

import os
import sys
import re
from llm_node import LLMNode
from filesystem_node import FilesystemNode

def main():
    # Get the instructions file path from command line argument or use default
    instructions_file = sys.argv[1] if len(sys.argv) > 1 else "examples/simple-instructions.txt"
    
    # Initialize the nodes
    llm_node = LLMNode()
    filesystem_node = FilesystemNode("/Users/sakshi/Documents/EmployeeManagementSystem", llm_node)
    
    # Read the instructions file
    with open(instructions_file, 'r') as f:
        instructions = f.read()
    
    print(f"\nProcessing instructions file: {os.path.abspath(instructions_file)}")
    print("=" * 80)
    
    # Analyze the instructions and divide into logical blocks
    print("Analyzing full instructions and dividing into logical blocks...")
    blocks = llm_node.interpret_full_instructions(instructions)
    
    # Process each block
    for i, block in enumerate(blocks, 1):
        print(f"\nProcessing block {i}:")
        print("-" * 40)
        print(block)
        print("-" * 40)
        
        # Analyze the block to determine the action
        action = llm_node.analyze_instruction_block(block)
        print(f"\nAction: {action}")
        
        # Execute the action
        success, error = filesystem_node.execute_action(action)
        if not success:
            print(f"Error executing action: {error}")
            continue
        
        print(f"Successfully executed action for block {i}")

if __name__ == "__main__":
    main() 