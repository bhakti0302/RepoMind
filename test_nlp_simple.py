"""
Simplified test script for the NLP processing.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import only what we need for testing
from codebase_analyser.agent.state import AgentState
from codebase_analyser.agent.nodes.nlp_nodes import process_requirements

async def test_nlp_processing():
    """Test the NLP processing with various requirements."""
    test_requirements = [
        "Implement a new feature that allows users to export data to CSV format.",
        "Create a RESTful API endpoint for user authentication using JWT tokens.",
        "Fix the bug in the UserService class that causes null pointer exceptions when processing empty inputs.",
        "Refactor the DatabaseConnector to use connection pooling for better performance.",
        "Add validation for email addresses in the registration form component."
    ]
    
    for req in test_requirements:
        logger.info(f"\n\n=== Testing requirement: {req} ===")
        state = AgentState(requirements=req)
        result = await process_requirements(state)
        
        # Print the processed requirements in a readable format
        processed = result["processed_requirements"]
        logger.info(f"Intent: {processed['intent']}")
        
        logger.info("Entities:")
        for entity_type, entities in processed["entities"].items():
            if entities:
                logger.info(f"  {entity_type}: {', '.join(entities)}")
        
        logger.info(f"Key phrases: {', '.join(processed['key_phrases'])}")
        logger.info(f"Code references: {', '.join(processed['code_references'])}")
        
        logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_nlp_processing())