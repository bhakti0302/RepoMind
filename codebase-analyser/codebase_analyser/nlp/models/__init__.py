"""
Models module for spaCy NLP models.

This module provides functionality for loading and managing spaCy models.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Union

import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)

# Default model to use if not specified
DEFAULT_MODEL = "en_core_web_sm"

# Dictionary to cache loaded models
_loaded_models: Dict[str, Language] = {}

def get_model_path(model_name: str) -> Path:
    """Get the path where a model should be stored.
    
    Args:
        model_name: Name of the spaCy model
        
    Returns:
        Path to the model directory
    """
    # Use the data directory in the project root
    base_dir = Path(__file__).parent.parent.parent.parent.parent / "data" / "nlp_models"
    return base_dir / model_name

def load_model(model_name: str = DEFAULT_MODEL) -> Language:
    """Load a spaCy model, downloading it if necessary.
    
    Args:
        model_name: Name of the spaCy model to load
        
    Returns:
        Loaded spaCy model
    """
    # Check if model is already loaded
    if model_name in _loaded_models:
        return _loaded_models[model_name]
    
    try:
        # Try to load the model
        logger.info(f"Loading spaCy model: {model_name}")
        nlp = spacy.load(model_name)
        _loaded_models[model_name] = nlp
        return nlp
    except OSError:
        # Model not found, try to download it
        logger.warning(f"Model {model_name} not found. Attempting to download...")
        try:
            spacy.cli.download(model_name)
            nlp = spacy.load(model_name)
            _loaded_models[model_name] = nlp
            return nlp
        except Exception as e:
            logger.error(f"Failed to download model {model_name}: {e}")
            raise

def unload_model(model_name: str) -> None:
    """Unload a spaCy model to free memory.
    
    Args:
        model_name: Name of the spaCy model to unload
    """
    if model_name in _loaded_models:
        logger.info(f"Unloading spaCy model: {model_name}")
        del _loaded_models[model_name]
