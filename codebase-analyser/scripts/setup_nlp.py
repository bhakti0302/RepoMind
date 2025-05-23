#!/usr/bin/env python3
"""
Setup script for NLP components.

This script downloads and configures spaCy models needed for requirements analysis.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Available spaCy models
AVAILABLE_MODELS = {
    "small": "en_core_web_sm",  # Small English model (~12MB)
    "medium": "en_core_web_md",  # Medium English model with word vectors (~43MB)
    "large": "en_core_web_lg",   # Large English model with word vectors (~560MB)
    "trf": "en_core_web_trf"     # Transformer-based model (~440MB)
}

def setup_data_directory() -> Path:
    """Create the data directory for storing NLP models.
    
    Returns:
        Path to the data directory
    """
    # Create the data directory in the project root
    data_dir = Path(__file__).parent.parent.parent / "data" / "nlp_models"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def download_models(models: list) -> None:
    """Download the specified spaCy models.
    
    Args:
        models: List of model names to download
    """
    for model_name in models:
        if model_name in AVAILABLE_MODELS:
            model_id = AVAILABLE_MODELS[model_name]
            logger.info(f"Downloading model: {model_id} ({model_name})")
            try:
                # Use spacy.cli to download the model
                import spacy.cli
                spacy.cli.download(model_id)
                logger.info(f"Successfully downloaded model: {model_id}")
                
                # Verify the model can be loaded
                import spacy
                nlp = spacy.load(model_id)
                logger.info(f"Successfully loaded model: {model_id}")
            except Exception as e:
                logger.error(f"Failed to download model {model_id}: {e}")
        else:
            logger.warning(f"Unknown model: {model_name}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Setup NLP components")
    parser.add_argument(
        "--models", 
        nargs="+", 
        choices=list(AVAILABLE_MODELS.keys()),
        default=["small"],
        help="spaCy models to download (default: small)"
    )
    
    args = parser.parse_args()
    
    # Setup data directory
    data_dir = setup_data_directory()
    logger.info(f"Using data directory: {data_dir}")
    
    # Download models
    download_models(args.models)
    
    logger.info("NLP setup completed successfully")

if __name__ == "__main__":
    main()
