#!/usr/bin/env python3
"""
Script to install all required dependencies for the codebase analyzer.
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

def install_package(package):
    """Install a package using pip."""
    try:
        logger.info(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        logger.info(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}: {e}")
        return False

def install_dependencies():
    """Install all required dependencies."""
    # Core dependencies from requirements.txt
    core_packages = [
        "tree-sitter==0.20.1",
        "tree-sitter-languages==1.5.0",
        "lancedb>=0.4.0",
        "numpy==1.24.3",
        "pydantic==2.4.2",
        "networkx==3.1",
        "pandas==2.2.3",
        "transformers==4.34.0",
        "torch==2.0.1",
        "sentence-transformers==2.2.2",
        "scikit-learn==1.3.0",
        "matplotlib==3.7.2",
        "plotly==5.18.0",
        "pyarrow==14.0.1",
        "spacy>=3.7.0",
        "tqdm==4.66.1",
        "requests==2.31.0"
    ]
    
    # LangGraph dependencies
    langgraph_packages = [
        "langgraph>=0.3.25",
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "langchain-openai>=0.1.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0"
    ]
    
    # Combine all packages
    all_packages = core_packages + langgraph_packages
    
    # Install each package
    for package in all_packages:
        install_package(package)
    
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