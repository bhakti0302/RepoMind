"""
Entity recognition module for code-related entities.

This module provides functionality to recognize and extract code-related entities
from text using spaCy and custom patterns.
"""

import logging
from typing import Dict, List, Any

import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc

logger = logging.getLogger(__name__)

class EntityRecognizer:
    """Recognizes code-related entities in text."""
    
    def __init__(self, nlp=None):
        """Initialize the entity recognizer.
        
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
            
        logging.info("Initialized EntityRecognizer")
        
        # Initialize matchers
        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab)
        
        # Add patterns for code entities
        self._add_patterns()
        
    def _add_patterns(self):
        """Add patterns for recognizing code entities."""
        # Class patterns
        self.matcher.add("CLASS", [
            [{"LOWER": "class"}, {"POS": "PROPN"}],
            [{"LOWER": "create"}, {"LOWER": "a"}, {"LOWER": "class"}, {"POS": "PROPN"}],
            [{"LOWER": "implement"}, {"LOWER": "a"}, {"LOWER": "class"}, {"POS": "PROPN"}]
        ])
        
        # Method patterns
        self.matcher.add("METHOD", [
            [{"LOWER": "method"}, {"POS": "PROPN"}],
            [{"LOWER": "function"}, {"POS": "PROPN"}],
            [{"LOWER": "create"}, {"LOWER": "a"}, {"LOWER": "method"}, {"POS": "PROPN"}],
            [{"LOWER": "implement"}, {"LOWER": "a"}, {"LOWER": "method"}, {"POS": "PROPN"}]
        ])
        
        # Interface patterns
        self.matcher.add("INTERFACE", [
            [{"LOWER": "interface"}, {"POS": "PROPN"}],
            [{"LOWER": "create"}, {"LOWER": "an"}, {"LOWER": "interface"}, {"POS": "PROPN"}],
            [{"LOWER": "implement"}, {"LOWER": "an"}, {"LOWER": "interface"}, {"POS": "PROPN"}]
        ])
        
        # Add programming terms to phrase matcher
        programming_terms = [
            "class", "method", "function", "variable", "interface", "module",
            "component", "service", "controller", "model", "view", "api",
            "database", "table", "field", "column", "key", "value", "object",
            "array", "list", "map", "set", "dictionary", "enum", "constant"
        ]
        self.programming_terms = programming_terms
        terms = [self.nlp(term) for term in programming_terms]
        self.phrase_matcher.add("PROGRAMMING_TERMS", None, *terms)
    
    def recognize_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Recognize code-related entities in text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with recognized entities by type
        """
        doc = self.nlp(text)
        
        # Extract entities using matcher
        matches = self.matcher(doc)
        phrase_matches = self.phrase_matcher(doc)
        
        # Process matches
        entities = {
            "classes": [],
            "methods": [],
            "interfaces": [],
            "variables": [],
            "general": []
        }
        
        # Process matcher matches
        for match_id, start, end in matches:
            match_type = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            
            # Extract the actual entity name
            entity_name = None
            for token in span:
                if token.pos_ in ("PROPN", "NOUN") and token.text.lower() not in self.programming_terms:
                    entity_name = token.text
                    break
            
            if entity_name:
                entity = {
                    "name": entity_name,
                    "text": span.text,
                    "start": span.start_char,
                    "end": span.end_char
                }
                
                if match_type == "CLASS":
                    entities["classes"].append(entity)
                elif match_type == "METHOD":
                    entities["methods"].append(entity)
                elif match_type == "INTERFACE":
                    entities["interfaces"].append(entity)
        
        return entities
