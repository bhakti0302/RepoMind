#!/usr/bin/env python3
"""
Script to install required dependencies for the codebase analyzer.
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install the required dependencies."""
    # List of required packages
    required_packages = [
        "langchain",
        "langchain-openai",
        "openai",
        "python-dotenv",
        "sentence-transformers",
        "spacy",
        "lancedb",
        "pydantic",
        "langsmith"
    ]
    
    logger.info("Installing required packages...")
    
    # Install each package
    for package in required_packages:
        try:
            logger.info(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
    
    # Install spaCy model
    try:
        logger.info("Installing spaCy model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
        logger.info("Successfully installed spaCy model")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install spaCy model: {e}")
    
    logger.info("All dependencies installed successfully")

if __name__ == "__main__":
    install_dependencies()