#!/usr/bin/env python3
"""
Script to generate LLM instructions file from requirements and context.

Usage:
    python -m cli.generate_instructions --requirements "Create a Java class..." --context "Existing code..." --output llm_instructions.txt
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codebase_analyser.agent.nodes.code_generation import generate_llm_instructions, generate_instructions_with_code
from codebase_analyser.agent.state import AgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main_async():
    """Async main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate LLM instructions file')
    parser.add_argument('--requirements', type=str, required=True, 
                        help='Requirements text or path to a JSON file containing requirements')
    parser.add_argument('--context', type=str, default='',
                        help='Context text or path to a file containing context')
    parser.add_argument('--language', type=str, default='java',
                        help='Programming language for the generated code')
    parser.add_argument('--output', type=str, default='llm_instructions.txt',
                        help='Path to save the generated instructions')
    parser.add_argument('--include-code', action='store_true',
                        help='Generate code and include it in the instructions')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load requirements
    requirements = args.requirements
    if os.path.exists(requirements) and requirements.endswith('.json'):
        try:
            with open(requirements, 'r') as f:
                requirements = json.load(f)
            logger.info(f"Loaded requirements from {requirements}")
        except Exception as e:
            logger.error(f"Error loading requirements file: {str(e)}")
            sys.exit(1)
    
    # Load context
    context = args.context
    if os.path.exists(context) and not context.endswith('.json'):
        try:
            with open(context, 'r') as f:
                context = f.read()
            logger.info(f"Loaded context from {context}")
        except Exception as e:
            logger.error(f"Error loading context file: {str(e)}")
            sys.exit(1)
    
    # Create agent state
    state = AgentState(
        requirements=requirements,
        processed_requirements={
            "intent": "code_generation",
            "language": args.language,
            "original_text": requirements if isinstance(requirements, str) else json.dumps(requirements)
        },
        combined_context=context
    )
    
    # Generate the instructions file
    logger.info("Generating instructions file...")
    
    if args.include_code:
        result = await generate_instructions_with_code(state, output_file=args.output)
    else:
        result = await generate_llm_instructions(state, output_file=args.output)
    
    if "instructions_file" in result and result["instructions_file"]:
        logger.info(f"Instructions file generated at: {result['instructions_file']}")
    else:
        logger.error("Failed to generate instructions file")
        if "errors" in result:
            for error in result["errors"]:
                logger.error(f"Error in {error['stage']}: {error['message']}")
        sys.exit(1)

def main():
    """Main function."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
