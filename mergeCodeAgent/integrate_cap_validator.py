#!/usr/bin/env python3
"""
Script to integrate the CAP SAP Java validator with the merge code agent workflow.

This script scans a directory for Java files and applies CAP SAP Java
validation and fixes to ensure compliance.
"""

import os
import sys
import argparse
from typing import List, Tuple, Optional
import glob

# Add the path to the current directory to ensure we can import our local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from java_cap_validator import validate_java_file

def find_java_files(directory: str) -> List[str]:
    """
    Find all Java files in a directory and its subdirectories.
    
    Args:
        directory: Path to the directory to search
        
    Returns:
        List of paths to Java files
    """
    java_files = []
    
    # Use glob to find all Java files
    for root, _, _ in os.walk(directory):
        java_files.extend(glob.glob(os.path.join(root, "*.java")))
    
    return java_files

def validate_and_fix_files(directory: str, files: Optional[List[str]] = None) -> Tuple[int, int]:
    """
    Validate and fix CAP SAP Java compliance for all Java files in the directory.
    
    Args:
        directory: Path to the project directory
        files: Optional list of specific files to validate
        
    Returns:
        Tuple of (total files, fixed files)
    """
    if files is None:
        files = find_java_files(directory)
    else:
        # Filter to only include Java files
        files = [f for f in files if f.endswith(".java")]
    
    total_files = len(files)
    fixed_files = 0
    
    print(f"Found {total_files} Java files to validate")
    
    for file_path in files:
        print(f"Validating {file_path}...")
        success, error_msg = validate_java_file(file_path, directory)
        
        if success:
            fixed_files += 1
        else:
            print(f"  Error: {error_msg}")
    
    return total_files, fixed_files

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate and fix CAP SAP Java compliance")
    parser.add_argument("--directory", "-d", default=".", help="Project directory (default: current directory)")
    parser.add_argument("--files", "-f", nargs="+", help="Specific files to validate")
    
    args = parser.parse_args()
    
    print(f"CAP SAP Java Validator")
    print(f"=====================")
    print(f"Project directory: {args.directory}")
    
    total_files, fixed_files = validate_and_fix_files(args.directory, args.files)
    
    print(f"\nSummary:")
    print(f"Total files: {total_files}")
    print(f"Fixed files: {fixed_files}")
    
    if total_files > 0:
        success_rate = (fixed_files / total_files) * 100
        print(f"Success rate: {success_rate:.2f}%")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 