#!/usr/bin/env python3
"""
Command-line interface for processing requirements and generating code.

This script provides a command-line interface for the requirements processor,
allowing users to process requirements and generate code from the command line.
"""

import argparse
import logging
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path to allow importing from the package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from requirements_processor.processor import RequirementsProcessor
from requirements_processor.utils.file_utils import (
    ensure_dir_exists,
    write_json_file,
    read_text_file
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process requirements and generate code"
    )
    
    # Required arguments
    parser.add_argument(
        "--project-id",
        required=True,
        help="Project ID"
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--requirement-text",
        help="Requirement text"
    )
    input_group.add_argument(
        "--requirement-file",
        help="Path to requirement file"
    )
    input_group.add_argument(
        "--requirements-dir",
        help="Path to directory containing requirement files"
    )
    
    # Optional arguments
    parser.add_argument(
        "--requirement-id",
        help="Requirement ID (generated if not provided)"
    )
    parser.add_argument(
        "--language",
        default="java",
        help="Target programming language (default: java)"
    )
    parser.add_argument(
        "--file-type",
        default="class",
        help="Type of file to generate (default: class)"
    )
    parser.add_argument(
        "--db-path",
        default=".lancedb",
        help="Path to the LanceDB database (default: .lancedb)"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to save output files (default: output)"
    )
    parser.add_argument(
        "--model",
        default="nvidia/llama-3.3-nemotron-super-49b-v1:free",
        help="Name of the model to use for code generation (default: nvidia/llama-3.3-nemotron-super-49b-v1:free)"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (defaults to OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save results to files"
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output-file",
        help="Path to output file (prints to stdout if not provided)"
    )
    
    return parser.parse_args()

def process_requirements(args):
    """Process requirements based on command-line arguments."""
    # Initialize processor
    processor = RequirementsProcessor(
        db_path=args.db_path,
        output_dir=args.output_dir,
        model=args.model,
        api_key=args.api_key
    )
    
    try:
        # Determine processing mode
        if args.requirement_text:
            # Process single requirement from text
            result = processor.process_requirement(
                requirement_text=args.requirement_text,
                project_id=args.project_id,
                requirement_id=args.requirement_id,
                language=args.language,
                file_type=args.file_type,
                save_results=not args.no_save
            )
            results = {result["requirement_id"]: result}
            
        elif args.requirement_file:
            # Process single requirement from file
            result = processor.process_requirement_file(
                file_path=args.requirement_file,
                project_id=args.project_id,
                language=args.language,
                file_type=args.file_type,
                save_results=not args.no_save
            )
            results = {result["requirement_id"]: result}
            
        elif args.requirements_dir:
            # Process all requirements in directory
            results = processor.process_project_requirements(
                project_id=args.project_id,
                requirements_dir=args.requirements_dir,
                language=args.language,
                file_type=args.file_type,
                save_results=not args.no_save
            )
        
        # Format output
        if args.output_format == "text":
            output = format_text_output(results)
        else:
            output = json.dumps(results, indent=2)
        
        # Write output
        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output)
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing requirements: {e}")
        return False
    
    finally:
        # Close processor
        processor.close()

def format_text_output(results: Dict[str, Dict[str, Any]]) -> str:
    """Format results as text output.
    
    Args:
        results: Dictionary mapping requirement IDs to results
        
    Returns:
        Formatted text output
    """
    output_lines = []
    
    for requirement_id, result in results.items():
        if "error" in result:
            output_lines.append(f"Requirement: {requirement_id}")
            output_lines.append(f"Error: {result['error']}")
            output_lines.append("")
            continue
        
        output_lines.append(f"Requirement: {requirement_id}")
        output_lines.append(f"Project: {result['project_id']}")
        output_lines.append("")
        
        if "formatted_output" in result:
            output_lines.append(result["formatted_output"])
        
        if "saved_files" in result.get("generation_result", {}):
            output_lines.append("Saved Files:")
            for file_type, file_path in result["generation_result"]["saved_files"].items():
                output_lines.append(f"  {file_type}: {file_path}")
        
        output_lines.append("")
        output_lines.append("-" * 80)
        output_lines.append("")
    
    return "\n".join(output_lines)

def main():
    """Main entry point."""
    args = parse_args()
    success = process_requirements(args)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
