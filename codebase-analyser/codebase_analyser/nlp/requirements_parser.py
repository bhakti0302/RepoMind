"""
Requirements parser module.

This module provides functionality for parsing business requirements using spaCy.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import spacy
from spacy.language import Language

from .models import load_model
from .text_utils import preprocess_text, extract_sentences

logger = logging.getLogger(__name__)

class RequirementsParser:
    """Parser for business requirements documents."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the requirements parser.
        
        Args:
            model_name: Name of the spaCy model to use
        """
        self.model_name = model_name
        self.nlp = load_model(model_name)
        logger.info(f"Initialized RequirementsParser with model: {model_name}")
    
    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse a requirements file.
        
        Args:
            file_path: Path to the requirements file
            
        Returns:
            Dictionary containing parsed requirements data
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        # Read the file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
        
        # Parse the content
        return self.parse_text(content, file_path=str(file_path))
    
    def parse_text(self, text: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Parse requirements text.
        
        Args:
            text: Requirements text to parse
            file_path: Optional path to the source file
            
        Returns:
            Dictionary containing parsed requirements data
        """
        # Preprocess the text
        preprocessed_text = preprocess_text(text)
        
        # Extract sentences
        sentences = extract_sentences(preprocessed_text, self.nlp)
        
        # Process the text with spaCy
        doc = self.nlp(preprocessed_text)
        
        # Extract basic information
        result = {
            "source": file_path,
            "text": text,
            "sentences": sentences,
            "tokens": [token.text for token in doc],
            "entities": [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                }
                for ent in doc.ents
            ]
        }
        
        return result
