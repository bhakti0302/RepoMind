"""
Test the Natural Language Processing setup with spaCy.

This test verifies that the basic NLP functionality is working correctly,
including Named Entity Recognition, key component extraction, and text processing.
"""

import pytest
import os
import sys
import logging
from typing import Dict, Any

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions to test
from codebase_analyser.agent.nodes.nlp_nodes import process_requirements, simple_process_requirements
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
    "Implement a REST API endpoint for user authentication using Spring Boot",
    "Add error handling to the database connection module",
    "Create a function to process JSON data and extract customer information",
    "Implement a caching mechanism for frequently accessed database queries"
]

@pytest.mark.asyncio
async def test_process_requirements():
    """Test the process_requirements function."""
    for req in TEST_REQUIREMENTS:
        logger.info(f"Testing requirement: {req}")
        
        # Create an agent state with the requirement
        state = AgentState(requirements=req)
        
        # Process the requirement
        result = await process_requirements(state)
        
        # Verify the result
        assert "processed_requirements" in result
        processed = result["processed_requirements"]
        
        # Check that the basic fields are present
        assert "intent" in processed
        assert "entities" in processed
        assert "key_phrases" in processed
        assert "code_references" in processed
        
        # Log the processed requirements
        logger.info(f"Intent: {processed['intent']}")
        logger.info(f"Entities: {processed['entities']}")
        logger.info(f"Key phrases: {processed['key_phrases']}")
        logger.info(f"Code references: {processed['code_references']}")
        
        # Verify that the intent is not empty
        assert processed["intent"] != "unknown", f"Intent should not be unknown for: {req}"
        
        # Verify that at least some entities were extracted
        has_entities = False
        for entity_type, entities in processed["entities"].items():
            if entities:
                has_entities = True
                break
        assert has_entities, f"No entities were extracted for: {req}"

def test_simple_process_requirements():
    """Test the simple_process_requirements function."""
    for req in TEST_REQUIREMENTS:
        logger.info(f"Testing simple requirement processing: {req}")
        
        # Process the requirement using the simple processor
        processed = simple_process_requirements(req)
        
        # Verify the result
        assert "intent" in processed
        assert "entities" in processed
        assert "key_phrases" in processed
        
        # Log the processed requirements
        logger.info(f"Intent: {processed['intent']}")
        logger.info(f"Entities: {processed['entities']}")
        logger.info(f"Key phrases: {processed['key_phrases']}")
        
        # Verify that some key phrases were extracted
        assert len(processed["key_phrases"]) > 0, f"No key phrases were extracted for: {req}"

if __name__ == "__main__":
    # Run the tests directly
    import asyncio
    asyncio.run(test_process_requirements())
    test_simple_process_requirements()