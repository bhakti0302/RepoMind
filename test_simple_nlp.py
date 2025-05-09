#!/usr/bin/env python3
"""
Simple test script for NLP processing functionality without requiring LLM.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import codebase_analyser
sys.path.append(str(Path(__file__).parent))

from codebase_analyser.agent.nodes.nlp_nodes import simple_process_requirements

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_simple_nlp_processing():
    """Test the simple NLP processing with various requirements."""
    test_requirements = [
        "Implement a new feature that allows users to export data to CSV format.",
        "Create a RESTful API endpoint for user authentication using JWT tokens.",
        "Fix the bug in the UserService class that causes null pointer exceptions when processing empty inputs.",
        "Refactor the DatabaseConnector to use connection pooling for better performance.",
        "Add validation for email addresses in the registration form component."
    ]
    
    for req in test_requirements:
        logger.info(f"\n\n=== Testing requirement: {req} ===")
        
        # Process the requirement using the simple processor
        processed = simple_process_requirements(req)
        
        # Print the processed requirements in a readable format
        logger.info(f"Intent: {processed['intent']}")
        logger.info(f"Language: {processed['language']}")
        
        logger.info("Entities:")
        for entity_type, entities in processed["entities"].items():
            if entities:
                logger.info(f"  {entity_type}: {', '.join(entities)}")
        
        logger.info(f"Key phrases: {', '.join(processed['key_phrases'])}")
        logger.info(f"File path: {processed.get('file_path', 'Not determined')}")
        
        logger.info("=" * 50)

if __name__ == "__main__":
    # Force using the simple processor by setting USE_MOCK_IMPLEMENTATIONS
    os.environ["USE_MOCK_IMPLEMENTATIONS"] = "1"
    test_simple_nlp_processing()