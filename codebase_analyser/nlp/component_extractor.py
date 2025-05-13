"""
Component extractor for code-related components.

This module provides functionality to extract code-related components from
requirements text, such as actions, objects, and constraints.
"""

import logging
from typing import Dict, List, Any

import spacy
from spacy.tokens import Doc

logger = logging.getLogger(__name__)

class ComponentExtractor:
    """Extracts code-related components from requirements text."""
    
    def __init__(self, nlp=None):
        """Initialize the component extractor.
        
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
            
        logging.info("Initialized ComponentExtractor")
    
    def extract_components(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract code-related components from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with extracted components by type
        """
        doc = self.nlp(text)
        
        # Extract components
        components = {
            "actions": self._extract_actions(doc),
            "objects": self._extract_objects(doc),
            "constraints": self._extract_constraints(doc)
        }
        
        return components
    
    def _extract_actions(self, doc: Doc) -> List[Dict[str, Any]]:
        """Extract actions (verbs) from the document.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of action dictionaries
        """
        actions = []
        
        for token in doc:
            if token.pos_ == "VERB" and not token.is_stop:
                actions.append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                })
        
        return actions
    
    def _extract_objects(self, doc: Doc) -> List[Dict[str, Any]]:
        """Extract objects (direct objects of verbs) from the document.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of object dictionaries
        """
        objects = []
        
        for token in doc:
            if token.dep_ in ("dobj", "pobj") and token.pos_ in ("NOUN", "PROPN"):
                objects.append({
                    "text": token.text,
                    "verb": token.head.text if token.head.pos_ == "VERB" else None,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                })
        
        return objects
    
    def _extract_constraints(self, doc: Doc) -> List[Dict[str, Any]]:
        """Extract constraints (conditional clauses) from the document.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of constraint dictionaries
        """
        constraints = []
        
        # Look for conditional markers
        condition_markers = ["if", "when", "unless", "until", "provided", "assuming"]
        
        for token in doc:
            if token.lower_ in condition_markers or token.dep_ == "mark":
                # Find the clause that contains this token
                clause_start = token.i
                clause_end = token.i + 1
                
                # Find the head of the clause
                head = token.head
                
                # Find all tokens that depend on the head
                clause_tokens = [token]
                for t in doc:
                    if t.head == head and t.i != token.i:
                        clause_tokens.append(t)
                
                # Find the start and end of the clause
                if clause_tokens:
                    clause_start = min(t.i for t in clause_tokens)
                    clause_end = max(t.i for t in clause_tokens) + 1
                
                # Extract the clause text
                clause_text = doc[clause_start:clause_end].text
                
                constraints.append({
                    "text": clause_text,
                    "marker": token.text,
                    "start": doc[clause_start].idx,
                    "end": doc[clause_end-1].idx + len(doc[clause_end-1].text)
                })
        
        return constraints