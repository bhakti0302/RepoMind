
"""
Entity extractor for code-related entities in requirements.

This module provides functionality to extract code-related entities from
requirements text, such as classes, methods, variables, and other components.
"""

import logging
import re
from typing import Dict, List, Set, Optional, Any, Tuple

import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, Span

logger = logging.getLogger(__name__)

class CodeEntityExtractor:
    """Extracts code-related entities from requirements text."""
    
    def __init__(self, nlp=None):
        """Initialize the code entity extractor.
        
        Args:
            nlp: Optional spaCy NLP model
        """
        if nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("Downloading spaCy model en_core_web_sm")
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
        else:
            self.nlp = nlp
            
        logger.info("Initialized CodeEntityExtractor")
        
        # Initialize matchers
        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab)
        
        # Common programming terms - define this BEFORE calling _add_patterns()
        self.programming_terms = {
            "class", "method", "function", "variable", "interface", "module",
            "component", "service", "controller", "model", "view", "api",
            "database", "table", "field", "column", "key", "value", "object",
            "array", "list", "map", "set", "dictionary", "enum", "constant",
            "parameter", "argument", "return", "input", "output", "endpoint"
        }
        
        # Add patterns for code entities
        self._add_patterns()
        
    def _add_patterns(self):
        """Add patterns for extracting code entities."""
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
        terms = [self.nlp(term) for term in self.programming_terms]
        self.phrase_matcher.add("PROGRAMMING_TERMS", None, *terms)
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract code-related entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with extracted entities by type
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
        
        # Extract potential variable names (camelCase or snake_case)
        for token in doc:
            if (token.is_alpha and 
                not token.is_stop and 
                token.text not in self.programming_terms and
                (re.match(r'^[a-z][a-zA-Z0-9]*$', token.text) or  # camelCase
                 re.match(r'^[a-z][a-z0-9_]*$', token.text))):    # snake_case
                
                entities["variables"].append({
                    "name": token.text,
                    "text": token.text,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                })
        
        # Extract general programming terms
        for match_id, start, end in phrase_matches:
            span = doc[start:end]
            entities["general"].append({
                "name": span.text,
                "text": span.text,
                "start": span.start_char,
                "end": span.end_char
            })
        
        return entities
    
    def extract_search_terms(self, text: str) -> List[str]:
        """Extract terms that can be used for code search.
        
        Args:
            text: Input text
            
        Returns:
            List of search terms
        """
        entities = self.extract_entities(text)
        
        # Collect all entity names
        search_terms = []
        for category in entities:
            for entity in entities[category]:
                search_terms.append(entity["name"])
        
        # Add additional terms from the text
        doc = self.nlp(text)
        for token in doc:
            if (token.pos_ in ("NOUN", "PROPN", "VERB") and 
                not token.is_stop and 
                len(token.text) > 2 and
                token.text.lower() not in self.programming_terms):
                search_terms.append(token.text)
        
        # Remove duplicates and normalize
        search_terms = list(set([term.lower() for term in search_terms if term]))
        
        return search_terms

