#!/usr/bin/env python3
"""
Test script for agent nodes functionality.

This script tests the LLM and validation nodes in the agent graph.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Add parent directory to path to import codebase_analyser
sys.path.append(str(Path(__file__).parent.parent))

from codebase_analyser.agent.state import AgentState
from codebase_analyser.agent.nodes.llm_nodes import (
    generate_code, 
    validate_code as llm_validate_code,
    generate_documentation,
    generate_tests
)
from codebase_analyser.agent.nodes.validation_nodes import validate_code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_generate_code():
    """Test code generation functionality."""
    logger.info("Testing code generation...")
    
    # Create a sample state
    state = AgentState(
        requirements={
            "description": "Create a simple Java class that represents a Person with name and age properties",
            "language": "java"
        },
        processed_requirements={
            "language": "java",
            "entities": {
                "classes": ["Person"],
                "properties": ["name", "age"]
            },
            "intent": "create_class"
        },
        combined_context="Create a Person class with name and age properties."
    )
    
    # Generate code
    result = await generate_code(state)
    
    # Check if code was generated
    if "generated_code" in result:
        logger.info("Code generation successful!")
        logger.info(f"Generated code length: {len(result['generated_code'])}")
        
        # Print the first few lines of the generated code
        code_preview = "\n".join(result["generated_code"].split("\n")[:10])
        logger.info(f"Code preview:\n{code_preview}")
        
        # Save the generated code to a file
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "generated_person.java", "w") as f:
            f.write(result["generated_code"])
        
        logger.info(f"Generated code saved to {output_dir / 'generated_person.java'}")
        
        # Update state with generated code
        state.generated_code = result["generated_code"]
        
        return state
    else:
        logger.error("Code generation failed!")
        logger.error(f"Result: {result}")
        return None

async def test_validate_code(state):
    """Test code validation functionality."""
    if not state or not state.generated_code:
        logger.error("No state or generated code to validate!")
        return
    
    logger.info("Testing code validation...")
    
    # Validate code using LLM
    logger.info("Validating code using LLM...")
    llm_result = await llm_validate_code(state)
    
    if "validation_result" in llm_result:
        logger.info("LLM validation successful!")
        logger.info(f"Validation result: {llm_result['validation_result']}")
    else:
        logger.error("LLM validation failed!")
        logger.error(f"Result: {llm_result}")
    
    # Validate code using comprehensive validation
    logger.info("Validating code using comprehensive validation...")
    validation_result = await validate_code(state)
    
    if "validation_result" in validation_result:
        logger.info("Comprehensive validation successful!")
        logger.info(f"Validation result: valid={validation_result['validation_result'].get('valid', False)}")
        
        # Print issues
        issues = validation_result["validation_result"].get("issues", [])
        if issues:
            logger.info(f"Found {len(issues)} issues:")
            for issue in issues[:5]:  # Print first 5 issues
                logger.info(f"  - {issue.get('severity', 'unknown')}: {issue.get('message', 'No message')}")
        else:
            logger.info("No issues found!")
    else:
        logger.error("Comprehensive validation failed!")
        logger.error(f"Result: {validation_result}")
    
    return validation_result

async def test_generate_documentation(state):
    """Test documentation generation functionality."""
    if not state or not state.generated_code:
        logger.error("No state or generated code to document!")
        return
    
    logger.info("Testing documentation generation...")
    
    # Generate documentation
    result = await generate_documentation(state)
    
    # Check if documentation was generated
    if "documentation" in result:
        logger.info("Documentation generation successful!")
        logger.info(f"Documentation length: {len(result['documentation'])}")
        
        # Print the first few lines of the documentation
        doc_preview = "\n".join(result["documentation"].split("\n")[:10])
        logger.info(f"Documentation preview:\n{doc_preview}")
        
        # Save the documentation to a file
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "person_documentation.md", "w") as f:
            f.write(result["documentation"])
        
        logger.info(f"Documentation saved to {output_dir / 'person_documentation.md'}")
    else:
        logger.error("Documentation generation failed!")
        logger.error(f"Result: {result}")

async def test_generate_tests(state):
    """Test test generation functionality."""
    if not state or not state.generated_code:
        logger.error("No state or generated code to test!")
        return
    
    logger.info("Testing test generation...")
    
    # Generate tests
    result = await generate_tests(state)
    
    # Check if tests were generated
    if "tests" in result:
        logger.info("Test generation successful!")
        logger.info(f"Tests length: {len(result['tests'])}")
        
        # Print the first few lines of the tests
        tests_preview = "\n".join(result["tests"].split("\n")[:10])
        logger.info(f"Tests preview:\n{tests_preview}")
        
        # Save the tests to a file
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "person_tests.java", "w") as f:
            f.write(result["tests"])
        
        logger.info(f"Tests saved to {output_dir / 'person_tests.java'}")
    else:
        logger.error("Test generation failed!")
        logger.error(f"Result: {result}")

async def main():
    """Run all tests."""
    logger.info("Starting agent nodes tests...")
    
    # Test code generation
    state = await test_generate_code()
    
    if state:
        # Test code validation
        await test_validate_code(state)
        
        # Test documentation generation
        await test_generate_documentation(state)
        
        # Test test generation
        await test_generate_tests(state)
    
    logger.info("Agent nodes tests completed!")

if __name__ == "__main__":
    asyncio.run(main())