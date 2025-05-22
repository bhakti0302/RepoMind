#!/usr/bin/env python3

"""
Process Business Requirements Script.

This script processes business requirements files and generates code using multi-hop RAG.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the business requirements processor
try:
    from src.business_requirements_processor import BusinessRequirementsProcessor
    from src.env_loader import load_env_vars
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def process_business_requirements(
    file_path: str,
    project_id: str = None,
    db_path: str = "../.lancedb",
    output_dir: str = "./output",
    data_dir: str = "../data",
    rag_type: str = "multi_hop",
    generate_code: bool = True
) -> bool:
    """Process business requirements and generate code.
    
    Args:
        file_path: Path to the business requirements file
        project_id: Project ID
        db_path: Path to the LanceDB database
        output_dir: Path to the output directory
        data_dir: Path to the data directory
        rag_type: Type of RAG to use
        generate_code: Whether to generate code using LLM
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing business requirements file: {file_path}")
        
        # Initialize the processor
        processor = BusinessRequirementsProcessor(
            db_path=db_path,
            output_dir=output_dir,
            data_dir=data_dir
        )
        
        # Process the requirements file
        processed_requirements = processor.process_requirements_file(
            file_path=file_path,
            project_id=project_id,
            save_to_data_dir=True
        )
        
        if "error" in processed_requirements:
            logger.error(f"Error processing requirements: {processed_requirements['error']}")
            return False
        
        # Generate code from requirements
        if generate_code:
            result = processor.generate_code_from_requirements(
                processed_requirements=processed_requirements,
                rag_type=rag_type,
                generate_code=generate_code
            )
            
            if "error" in result:
                logger.error(f"Error generating code: {result['error']}")
                return False
            
            logger.info("Code generation completed successfully")
            
            # Print the output file paths
            if "instructions_file" in result:
                print(f"Instructions file: {result['instructions_file']}")
            if "output_file" in result:
                print(f"Generated code file: {result['output_file']}")
        
        # Close all connections
        processor.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing business requirements: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process business requirements and generate code")
    parser.add_argument("--file", required=True, help="Path to the business requirements file")
    parser.add_argument("--project-id", help="Project ID")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--output-dir", help="Path to the output directory")
    parser.add_argument("--data-dir", help="Path to the data directory")
    parser.add_argument("--rag-type", choices=["basic", "graph", "multi_hop"], default="multi_hop", help="Type of RAG to use")
    parser.add_argument("--generate-code", action="store_true", default=True, help="Whether to generate code using LLM")
    parser.add_argument("--env-file", help="Path to the .env file")
    args = parser.parse_args()
    
    # Load environment variables
    if args.env_file:
        load_env_vars(args.env_file)
    else:
        load_env_vars()
    
    # Get values from environment variables if not provided
    db_path = args.db_path or os.environ.get("DB_PATH", "../.lancedb")
    output_dir = args.output_dir or os.environ.get("OUTPUT_DIR", "./output")
    data_dir = args.data_dir or os.environ.get("DATA_DIR", "../data")
    
    # Process the business requirements
    success = process_business_requirements(
        file_path=args.file,
        project_id=args.project_id,
        db_path=db_path,
        output_dir=output_dir,
        data_dir=data_dir,
        rag_type=args.rag_type,
        generate_code=args.generate_code
    )
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
