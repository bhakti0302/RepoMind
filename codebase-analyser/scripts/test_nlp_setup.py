#!/usr/bin/env python3
"""
Test script for NLP setup.

This script tests that spaCy is properly installed and configured.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_spacy_installation():
    """Test that spaCy is properly installed."""
    try:
        import spacy
        logger.info(f"spaCy version: {spacy.__version__}")
        return True
    except ImportError:
        logger.error("spaCy is not installed")
        return False

def test_model_loading():
    """Test that a spaCy model can be loaded."""
    try:
        import spacy
        model_name = "en_core_web_sm"
        
        try:
            nlp = spacy.load(model_name)
            logger.info(f"Successfully loaded model: {model_name}")
            
            # Test basic functionality
            doc = nlp("This is a test sentence for spaCy. It contains entities like Google and Microsoft.")
            logger.info(f"Tokens: {[token.text for token in doc[:5]]}")
            logger.info(f"Entities: {[(ent.text, ent.label_) for ent in doc.ents]}")
            
            return True
        except OSError:
            logger.warning(f"Model {model_name} not found. Try running setup_nlp.py first.")
            return False
    except Exception as e:
        logger.error(f"Error testing model loading: {e}")
        return False

def test_requirements_parser():
    """Test that the RequirementsParser can be initialized."""
    try:
        from codebase_analyser.nlp.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        logger.info("Successfully initialized RequirementsParser")
        
        # Test parsing a simple text
        result = parser.parse_text("The system shall allow users to login with their credentials.")
        logger.info(f"Parsed {len(result['sentences'])} sentences and found {len(result['entities'])} entities")
        
        return True
    except Exception as e:
        logger.error(f"Error testing RequirementsParser: {e}")
        return False

def main():
    """Main entry point for the script."""
    logger.info("Testing NLP setup...")
    
    # Test spaCy installation
    if not test_spacy_installation():
        logger.error("spaCy installation test failed")
        sys.exit(1)
    
    # Test model loading
    if not test_model_loading():
        logger.warning("Model loading test failed")
    
    # Test requirements parser
    if not test_requirements_parser():
        logger.error("RequirementsParser test failed")
        sys.exit(1)
    
    logger.info("All tests passed successfully")

if __name__ == "__main__":
    main()
