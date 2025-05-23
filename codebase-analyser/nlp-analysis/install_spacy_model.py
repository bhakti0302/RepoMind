#!/usr/bin/env python3

"""
Install the required spaCy model.

This script installs the required spaCy model for the NLP analysis pipeline.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def install_spacy_model(model_name="en_core_web_sm"):
    """Install the specified spaCy model.
    
    Args:
        model_name: Name of the spaCy model to install
    """
    try:
        logger.info(f"Installing spaCy model: {model_name}")
        
        # Use subprocess to run the command
        result = subprocess.run(
            [sys.executable, "-m", "spacy", "download", model_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Successfully installed spaCy model: {model_name}")
        logger.info(f"Output: {result.stdout}")
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing spaCy model: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

if __name__ == "__main__":
    # Install the small English model
    success = install_spacy_model("en_core_web_sm")
    
    if success:
        print("Successfully installed spaCy model: en_core_web_sm")
    else:
        print("Failed to install spaCy model. Please check the logs for details.")
