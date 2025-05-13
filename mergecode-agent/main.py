#!/usr/bin/env python3
"""
Main entry point for the Merge Code Agent.

This module handles command-line arguments and initializes the orchestrator.
"""

import argparse
import os
import sys
import pathlib
from typing import Optional
from dotenv import load_dotenv

from merge_code_agent.orchestrator import Orchestrator

# Load environment variables from .env file
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


def validate_paths(instructions_path: str, codebase_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate the input paths.

    Args:
        instructions_path: Path to the instructions file
        codebase_path: Path to the codebase directory

    Returns:
        A tuple of (is_valid, error_message)
    """
    # Check if instructions file exists
    if not os.path.isfile(instructions_path):
        return False, f"Instructions file not found: {instructions_path}"

    # Check if codebase directory exists
    if not os.path.isdir(codebase_path):
        return False, f"Codebase directory not found: {codebase_path}"

    return True, None


def main():
    """Main entry point for the Merge Code Agent."""
    parser = argparse.ArgumentParser(
        description="Merge Code Agent - LLM-Driven Codebase Modification Tool"
    )
    parser.add_argument(
        "instructions",
        help="Path to the instructions file (llm-instructions.txt)"
    )
    parser.add_argument(
        "codebase",
        help="Path to the codebase directory to be modified"
    )

    args = parser.parse_args()

    # Validate input paths
    is_valid, error_message = validate_paths(args.instructions, args.codebase)
    if not is_valid:
        print(f"Error: {error_message}", file=sys.stderr)
        sys.exit(1)

    # Initialize the orchestrator
    orchestrator = Orchestrator(
        instructions_path=args.instructions,
        codebase_path=args.codebase
    )

    # Run the orchestrator
    try:
        orchestrator.run()
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
