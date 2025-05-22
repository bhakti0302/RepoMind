#!/usr/bin/env python3
"""
Comprehensive Visualization Script

This script runs all available visualization scripts to generate a complete
set of visualizations for a codebase.

Usage:
    python visualize_all_relationships.py --repo-path /path/to/repo --output-dir /path/to/output --project-id my_project

This script is designed to be called from the VS Code extension to generate
all visualization types in one go.
"""

import os
import sys
import json
import argparse
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate all visualizations for a codebase")
    
    parser.add_argument("--repo-path", required=True, help="Path to the repository to analyze")
    parser.add_argument("--output-dir", required=True, help="Directory to save visualization outputs")
    parser.add_argument("--project-id", required=True, help="Project ID for visualization")
    parser.add_argument("--db-path", help="Path to the database file")
    parser.add_argument("--timestamp", help="Timestamp to use for filenames")
    
    return parser.parse_args()

def run_script(script_path, args_dict):
    """Run a Python script with the given arguments."""
    cmd = [sys.executable, script_path]
    
    for key, value in args_dict.items():
        if value is not None:
            cmd.extend([f"--{key.replace('_', '-')}", str(value)])
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Script output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Script failed with error: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def generate_all_visualizations(args):
    """Generate all visualizations for the given repository."""
    # Get the current directory (where this script is located)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate timestamp if not provided
    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Set up database path if not provided
    db_path = args.db_path
    if not db_path:
        db_path = os.path.join(os.path.dirname(script_dir), ".lancedb")
    
    # Dictionary to store visualization paths
    visualization_paths = {
        "multi_file_relationships": os.path.join(args.output_dir, f"{args.project_id}_multi_file_relationships_{timestamp}.png"),
        "relationship_types": os.path.join(args.output_dir, f"{args.project_id}_relationship_types_{timestamp}.png"),
        "code_relationships": os.path.join(args.output_dir, f"{args.project_id}_code_relationships_{timestamp}.png"),
        "complex_relationships": os.path.join(args.output_dir, f"{args.project_id}_complex_relationships_{timestamp}.png"),
        "uml_diagram": os.path.join(args.output_dir, f"{args.project_id}_uml_diagram_{timestamp}.png")
    }
    
    # Add testshreya visualization if applicable
    if "testshreya" in args.project_id.lower():
        visualization_paths["testshreya"] = os.path.join(args.output_dir, f"{args.project_id}_testshreya_{timestamp}.png")
    
    # 1. Generate colored relationship diagrams
    logger.info("Generating colored relationship diagrams")
    colored_script = os.path.join(script_dir, "generate_colored_diagrams.py")
    
    # Run generate_multi_file_relationships
    multi_file_args = {
        "output_file": visualization_paths["multi_file_relationships"],
        "db_path": db_path,
        "project_id": args.project_id
    }
    run_script(colored_script, {"generate_multi_file": True, **multi_file_args})
    
    # Run generate_relationship_types
    relationship_types_args = {
        "output_file": visualization_paths["relationship_types"],
        "db_path": db_path,
        "project_id": args.project_id
    }
    run_script(colored_script, {"generate_relationship_types": True, **relationship_types_args})
    
    # 2. Generate UML diagrams
    logger.info("Generating UML diagrams")
    uml_script = os.path.join(script_dir, "generate_uml_diagrams.py")
    uml_args = {
        "output_dir": args.output_dir,
        "db_path": db_path,
        "project_id": args.project_id
    }
    run_script(uml_script, uml_args)
    
    # 3. Generate code relationship visualizations
    logger.info("Generating code relationship visualizations")
    code_rel_script = os.path.join(script_dir, "visualize_code_relationships.py")
    code_rel_args = {
        "repo_path": args.repo_path,
        "output_file": visualization_paths["code_relationships"],
        "db_path": db_path,
        "project_id": args.project_id
    }
    run_script(code_rel_script, code_rel_args)
    
    # 4. Generate complex relationship visualizations
    logger.info("Generating complex relationship visualizations")
    complex_rel_script = os.path.join(script_dir, "visualize_complex_relationships.py")
    complex_rel_args = {
        "output_file": visualization_paths["complex_relationships"],
        "db_path": db_path,
        "project_id": args.project_id
    }
    run_script(complex_rel_script, complex_rel_args)
    
    # 5. Generate testshreya visualizations if applicable
    if "testshreya" in args.project_id.lower():
        logger.info("Generating TestShreya visualizations")
        testshreya_script = os.path.join(script_dir, "visualize_testshreya.py")
        testshreya_args = {
            "output_file": visualization_paths["testshreya"],
            "db_path": db_path
        }
        run_script(testshreya_script, testshreya_args)
    
    # Return the paths to the generated visualizations
    logger.info(f"All visualizations generated successfully in {args.output_dir}")
    
    # Print the paths as JSON for the VS Code extension to parse
    print(json.dumps(visualization_paths))
    
    return True

def main():
    """Main entry point."""
    args = parse_args()
    success = generate_all_visualizations(args)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
