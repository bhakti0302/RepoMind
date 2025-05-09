#!/usr/bin/env python3
"""
End-to-end test for the agent workflow.

This script tests the complete agent workflow from requirements to code generation,
validation, documentation, and test generation.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from pathlib import Path

# Add parent directory to path to import codebase_analyser
sys.path.append(str(Path(__file__).parent.parent))

from codebase_analyser.agent.state import AgentState
from codebase_analyser.agent.workflow import run_agent_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Sample requirements
SAMPLE_REQUIREMENTS = [
    {
        "description": "Create a simple Java class that represents a Person with name and age properties",
        "language": "java"
    },
    {
        "description": "Create a Python function to read a CSV file and return a list of dictionaries",
        "language": "python"
    },
    {
        "description": "Create a JavaScript function to fetch data from an API and display it in a table",
        "language": "javascript"
    }
]

async def test_agent_workflow(requirements, output_dir=None, prompt_template=None):
    """
    Test the agent workflow with the given requirements.
    
    Args:
        requirements: The requirements to process
        output_dir: Directory to save output files
        prompt_template: Custom prompt template to use
    """
    logger.info(f"Testing agent workflow with requirements: {requirements['description']}")
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create initial state
    state = AgentState(
        requirements=requirements,
        prompt_template=prompt_template
    )
    
    # Run the agent workflow
    result_state = await run_agent_workflow(state)
    
    # Check if workflow completed successfully
    if result_state.errors:
        logger.error(f"Agent workflow completed with {len(result_state.errors)} errors:")
        for error in result_state.errors:
            logger.error(f"  - {error.get('stage', 'unknown')}: {error.get('message', 'No message')}")
    else:
        logger.info("Agent workflow completed successfully!")
    
    # Print workflow results
    logger.info(f"Generated code length: {len(result_state.generated_code) if result_state.generated_code else 0}")
    
    if result_state.validation_result:
        logger.info(f"Validation result: valid={result_state.validation_result.get('valid', False)}")
        
        # Print issues
        issues = result_state.validation_result.get("issues", [])
        if issues:
            logger.info(f"Found {len(issues)} issues:")
            for issue in issues[:3]:  # Print first 3 issues
                logger.info(f"  - {issue.get('severity', 'unknown')}: {issue.get('message', 'No message')}")
    
    # Save results to files if output directory is specified
    if output_dir and result_state.generated_code:
        # Determine file extension based on language
        language = requirements.get("language", "").lower()
        if language == "java":
            ext = ".java"
        elif language == "python":
            ext = ".py"
        elif language == "javascript":
            ext = ".js"
        else:
            ext = ".txt"
        
        # Save generated code
        code_file = os.path.join(output_dir, f"generated_code{ext}")
        with open(code_file, "w") as f:
            f.write(result_state.generated_code)
        logger.info(f"Generated code saved to {code_file}")
        
        # Save documentation if available
        if result_state.documentation:
            doc_file = os.path.join(output_dir, "documentation.md")
            with open(doc_file, "w") as f:
                f.write(result_state.documentation)
            logger.info(f"Documentation saved to {doc_file}")
        
        # Save tests if available
        if result_state.tests:
            test_file = os.path.join(output_dir, f"tests{ext}")
            with open(test_file, "w") as f:
                f.write(result_state.tests)
            logger.info(f"Tests saved to {test_file}")
    
    return result_state

async def main():
    """Run the agent workflow tests."""
    parser = argparse.ArgumentParser(description="Test the agent workflow")
    parser.add_argument("--requirement-index", type=int, default=0, help="Index of the sample requirement to use (0-2)")
    parser.add_argument("--output-dir", type=str, default="tests/output", help="Directory to save output files")
    parser.add_argument("--prompt-file", type=str, help="Path to a custom prompt template file")
    parser.add_argument("--custom-requirement", type=str, help="Custom requirement description")
    parser.add_argument("--language", type=str, default="java", help="Programming language for custom requirement")
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Load custom prompt template if specified
    prompt_template = None
    if args.prompt_file:
        try:
            with open(args.prompt_file, "r") as f:
                prompt_template = f.read()
            logger.info(f"Loaded custom prompt template from {args.prompt_file}")
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
    
    # Determine which requirement to use
    if args.custom_requirement:
        # Use custom requirement
        requirement = {
            "description": args.custom_requirement,
            "language": args.language
        }
        logger.info(f"Using custom requirement: {requirement['description']}")
    else:
        # Use sample requirement
        index = max(0, min(args.requirement_index, len(SAMPLE_REQUIREMENTS) - 1))
        requirement = SAMPLE_REQUIREMENTS[index]
        logger.info(f"Using sample requirement {index}: {requirement['description']}")
    
    # Run the test
    await test_agent_workflow(
        requirements=requirement,
        output_dir=str(output_dir),
        prompt_template=prompt_template
    )

if __name__ == "__main__":
    asyncio.run(main())