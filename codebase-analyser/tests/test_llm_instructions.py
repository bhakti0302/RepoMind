"""
Test the generation of LLM instructions file.

This test verifies that the system can generate proper instruction files
for LLMs based on processed requirements and context.
"""

import pytest
import os
import sys
import tempfile
import logging
from typing import Dict, Any

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions to test
from codebase_analyser.agent.nodes.code_generation import generate_llm_instructions
from codebase_analyser.agent.state import AgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test requirements
TEST_REQUIREMENTS = [
    "Create a Java class to export data to CSV files",
    "Implement a REST API endpoint for user authentication using Spring Boot"
]

# Test contexts
TEST_CONTEXTS = [
    "Existing code includes DataProcessor class with methods for data transformation.",
    "The system uses Spring Boot 2.5 with Spring Security for authentication."
]

@pytest.mark.asyncio
async def test_generate_llm_instructions():
    """Test the generation of LLM instructions file."""
    for req, context in zip(TEST_REQUIREMENTS, TEST_CONTEXTS):
        logger.info(f"Testing instruction generation for: {req}")
        
        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "llm-instructions.txt")
            
            # Create an agent state with the requirement and context
            state = AgentState(
                requirements=req,
                processed_requirements={
                    "intent": "code_generation",
                    "language": "java",
                    "original_text": req
                },
                combined_context=context
            )
            
            # Generate the instructions file
            result = await generate_llm_instructions(state, output_file=output_file)
            
            # Verify the result
            assert "instructions_file" in result
            assert os.path.exists(result["instructions_file"])
            
            # Read the generated file
            with open(result["instructions_file"], "r") as f:
                content = f.read()
            
            # Verify the content
            assert "REQUIREMENTS:" in content
            assert req in content
            assert "CONTEXT:" in content
            assert context in content
            assert "LANGUAGE: java" in content
            
            logger.info(f"Generated instructions file: {result['instructions_file']}")
            logger.info(f"Content preview: {content[:200]}...")

@pytest.mark.asyncio
async def test_generate_llm_instructions_default_location():
    """Test the generation of LLM instructions file with default location."""
    req = TEST_REQUIREMENTS[0]
    context = TEST_CONTEXTS[0]
    
    # Create an agent state
    state = AgentState(
        requirements=req,
        processed_requirements={
            "intent": "code_generation",
            "language": "java",
            "original_text": req
        },
        combined_context=context
    )
    
    # Generate the instructions file with default location
    result = await generate_llm_instructions(state)
    
    # Verify the result
    assert "instructions_file" in result
    assert os.path.exists(result["instructions_file"])
    assert "llm_instructions.txt" in result["instructions_file"]
    
    # Read the generated file
    with open(result["instructions_file"], "r") as f:
        content = f.read()
    
    # Verify the content
    assert "REQUIREMENTS:" in content
    assert req in content
    assert "CONTEXT:" in content
    assert context in content
    assert "LANGUAGE: java" in content
    
    # Clean up
    os.remove(result["instructions_file"])
    
    # Log the location
    logger.info(f"Default instructions file location: {result['instructions_file']}")

if __name__ == "__main__":
    # Run the test directly
    import asyncio
    asyncio.run(test_generate_llm_instructions())
