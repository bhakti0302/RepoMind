#!/usr/bin/env python3
"""
Run All Visualizations Script

This script runs all available visualization scripts for a given project.
It's designed to be called from the VS Code extension to generate all
visualization types in one go.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run all visualization scripts for a project")
    
    parser.add_argument("--project-id", required=True, help="Project ID for visualization")
    parser.add_argument("--db-path", required=True, help="Path to the database file")
    parser.add_argument("--output-dir", help="Directory to save visualization outputs")
    
    return parser.parse_args()

def run_all_visualizations(project_id, db_path, output_dir=None):
    """Run all visualization scripts for the given project."""
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Set up output directory
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                 'data', 'visualizations', project_id)
    
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Generating all visualizations for project: {project_id}")
    logger.info(f"Output directory: {output_dir}")
    
    # 1. Generate UML diagrams
    logger.info("Generating UML diagrams")
    try:
        from scripts.generate_uml_diagrams import generate_uml_diagrams
        generate_uml_diagrams(project_id, output_dir, db_path)
        logger.info("UML diagrams generated successfully")
    except Exception as e:
        logger.error(f"Error generating UML diagrams: {e}")
    
    # 2. Generate colored relationship diagrams
    logger.info("Generating colored relationship diagrams")
    try:
        from scripts.generate_colored_diagrams import generate_multi_file_relationships, generate_relationship_types
        
        multi_file_path = os.path.join(output_dir, f"{project_id}_multi_file_relationships_{timestamp}.png")
        relationship_types_path = os.path.join(output_dir, f"{project_id}_relationship_types_{timestamp}.png")
        
        generate_multi_file_relationships(multi_file_path)
        generate_relationship_types(relationship_types_path)
        
        logger.info("Colored relationship diagrams generated successfully")
    except Exception as e:
        logger.error(f"Error generating colored relationship diagrams: {e}")
    
    # 3. Generate code relationship visualizations
    logger.info("Generating code relationship visualizations")
    try:
        from scripts.visualize_code_relationships import visualize_code_relationships
        
        code_rel_path = os.path.join(output_dir, f"{project_id}_code_relationships_{timestamp}.png")
        visualize_code_relationships(db_path, project_id, code_rel_path)
        
        logger.info("Code relationship visualization generated successfully")
    except Exception as e:
        logger.error(f"Error generating code relationship visualization: {e}")
    
    # 4. Generate complex relationship visualizations
    logger.info("Generating complex relationship visualizations")
    try:
        from scripts.visualize_complex_relationships import visualize_complex_relationships
        
        complex_rel_path = os.path.join(output_dir, f"{project_id}_complex_relationships_{timestamp}.png")
        visualize_complex_relationships(db_path, project_id, complex_rel_path)
        
        logger.info("Complex relationship visualization generated successfully")
    except Exception as e:
        logger.error(f"Error generating complex relationship visualization: {e}")
    
    # 5. Generate testshreya visualizations if applicable
    if "testshreya" in project_id.lower():
        logger.info("Generating TestShreya visualizations")
        try:
            from scripts.visualize_testshreya import visualize_testshreya_project
            
            testshreya_path = os.path.join(output_dir, f"{project_id}_testshreya_{timestamp}.png")
            visualize_testshreya_project(db_path, testshreya_path)
            
            logger.info("TestShreya visualization generated successfully")
        except Exception as e:
            logger.error(f"Error generating TestShreya visualization: {e}")
    
    logger.info(f"All visualizations generated successfully in {output_dir}")
    return True

def main():
    """Main entry point."""
    args = parse_args()
    success = run_all_visualizations(args.project_id, args.db_path, args.output_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
