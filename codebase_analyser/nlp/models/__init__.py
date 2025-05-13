"""
Models module for NLP processing.

This module provides functionality for loading and managing spaCy models.
"""

import logging
import os
from typing import Dict, Optional

import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)

# Cache for loaded models
_loaded_models: Dict[str, Language] = {}

def load_model(model_name: str) -> Language:
    """Load a spaCy model, downloading it if necessary.
    
    Args:
        model_name: Name of the spaCy model to load
        
    Returns:
        Loaded spaCy model
    """
    # Check if model is already loaded
    if model_name in _loaded_models:
        logger.debug(f"Using cached spaCy model: {model_name}")
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
