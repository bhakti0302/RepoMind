#!/usr/bin/env python3
"""
Test script to verify that the _create_file method works with both strings and lists.
"""

import os
import shutil
from filesystem_node import FilesystemNode

def main():
    """Run the test."""
    # Create a test directory
    test_dir = "test_output"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Create a filesystem node
    fs_node = FilesystemNode(test_dir)
    
    # Test with a string
    print("Testing with a string...")
    success, error = fs_node._create_file("test_string.txt", "This is a test string.")
    if success:
        print("Success!")
    else:
        print(f"Error: {error}")
    
    # Test with a list
    print("\nTesting with a list...")
    success, error = fs_node._create_file("test_list.txt", ["This is line 1.", "This is line 2.", "This is line 3."])
    if success:
        print("Success!")
    else:
        print(f"Error: {error}")
    
    # Verify the files
    print("\nVerifying files...")
    with open(os.path.join(test_dir, "test_string.txt"), 'r') as f:
        print(f"test_string.txt: {f.read()}")
    
    with open(os.path.join(test_dir, "test_list.txt"), 'r') as f:
        print(f"test_list.txt: {f.read()}")
    
    # Clean up
    shutil.rmtree(test_dir)
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()
