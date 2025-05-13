"""
Requirements parser for code-related requirements.

This module provides functionality to parse and analyze code-related requirements
using spaCy and custom patterns.
"""

import logging
from typing import Dict, List, Any, Optional

import spacy
from spacy.language import Language

from .text_utils import preprocess_text, extract_sentences, extract_keywords
from .entity_recognition import EntityRecognizer
from .component_extractor import ComponentExtractor

logger = logging.getLogger(__name__)

class RequirementsParser:
    """Parses and analyzes code-related requirements."""
    
    def __init__(self, nlp=None):
        """Initialize the requirements parser.
        
        Args:
            nlp: Optional spaCy NLP model
        """
        if nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logging.warning("Downloading spaCy model en_core_web_sm")
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
        else:
            self.nlp = nlp
            
        logging.info("Initialized RequirementsParser")
        
        # Initialize entity recognizer and component extractor
        self.entity_recognizer = EntityRecognizer(self.nlp)
        self.component_extractor = ComponentExtractor(self.nlp)
    
    def parse_requirements(self, text: str) -> Dict[str, Any]:
        """Parse and analyze requirements text.
        
        Args:
            text: Requirements text
            
        Returns:
            Dictionary with parsed requirements
        """
        # Preprocess text
        preprocessed_text = preprocess_text(text)
        
        # Extract sentences
        sentences = extract_sentences(preprocessed_text, self.nlp)
        
        # Extract keywords
        keywords = extract_keywords(preprocessed_text, self.nlp)
        
        # Recognize entities
        entities = self.entity_recognizer.recognize_entities(preprocessed_text)
        
        # Extract components
        components = self.component_extractor.extract_components(preprocessed_text)
        
        # Combine results
        result = {
            "text": text,
            "preprocessed_text": preprocessed_text,
            "sentences": sentences,
            "keywords": keywords,
            "entities": entities,
            "components": components
        }
        
        return result
    
    def extract_code_elements(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract code-related elements from requirements text.
        
        Args:
            text: Requirements text
            
        Returns:
            Dictionary with extracted code elements by type
        """
        # Parse requirements
        parsed = self.parse_requirements(text)
        
        # Extract code elements
        code_elements = {
            "classes": parsed["entities"]["classes"],
            "methods": parsed["entities"]["methods"],
            "interfaces": parsed["entities"]["interfaces"],
            "actions": parsed["components"]["actions"],
            "objects": parsed["components"]["objects"],
            "constraints": parsed["components"]["constraints"]
        }
        
        return code_elements
