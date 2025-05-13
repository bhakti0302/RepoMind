
"""
Enhanced requirements parser for code generation.

This module extends the basic requirements parser with additional functionality
for extracting information needed for code generation.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Set

import spacy
from spacy.language import Language

# Import from existing codebase
from codebase_analyser.nlp.requirements_parser import RequirementsParser as BaseRequirementsParser
from codebase_analyser.nlp.text_utils import preprocess_text, extract_sentences, extract_keywords

logger = logging.getLogger(__name__)

class RequirementsParser(BaseRequirementsParser):
    """Enhanced parser for business requirements with code generation focus."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the enhanced requirements parser.
        
        Args:
            model_name: Name of the spaCy model to use
        """
        super().__init__()
        logger.info(f"Initialized RequirementsParser with model: {model_name}")
        
        # Patterns for identifying code-related requirements
        self.code_patterns = [
            r"implement(?:ing|ed)?\s+(?:a|an)?\s+(\w+)",
            r"creat(?:e|ing|ed)\s+(?:a|an)?\s+(\w+)",
            r"add(?:ing|ed)?\s+(?:a|an)?\s+(\w+)",
            r"develop(?:ing|ed)?\s+(?:a|an)?\s+(\w+)",
            r"build(?:ing)?\s+(?:a|an)?\s+(\w+)",
            r"(?:should|must|will)\s+(?:have|include|contain)\s+(?:a|an)?\s+(\w+)",
        ]
        
    def parse_text(self, text: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Parse requirements text with enhanced extraction.
        
        Args:
            text: Requirements text to parse
            file_path: Optional path to the source file
            
        Returns:
            Dictionary containing parsed requirements data with code-specific information
        """
        # Get basic parsing results from parent class
        result = self.parse_requirements(text)
        
        # Add enhanced parsing results
        result.update(self._extract_enhanced_information(text))
        
        return result
    
    def _extract_enhanced_information(self, text: str) -> Dict[str, Any]:
        """Extract enhanced information for code generation.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Dictionary with enhanced information
        """
        # Process the text with spaCy
        doc = self.nlp(text)
        
        # Extract code-related components
        components = self._extract_components(doc)
        
        # Extract actions (verbs that indicate what needs to be done)
        actions = self._extract_actions(doc)
        
        # Extract constraints (conditions that must be met)
        constraints = self._extract_constraints(doc)
        
        # Extract potential code patterns using regex
        code_elements = self._extract_code_elements(text)
        
        # Extract keywords for search
        keywords = extract_keywords(text, self.nlp, max_keywords=20)
        
        return {
            "components": components,
            "actions": actions,
            "constraints": constraints,
            "code_elements": code_elements,
            "keywords": keywords,
            "priority_keywords": keywords[:5]  # Top 5 keywords for search
        }
    
    def _extract_components(self, doc) -> List[Dict[str, Any]]:
        """Extract components (nouns that could be classes, methods, etc.).
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of component dictionaries
        """
        components = []
        
        # Extract noun chunks as potential components
        for chunk in doc.noun_chunks:
            # Skip very common or stop words
            if not all(token.is_stop for token in chunk):
                components.append({
                    "text": chunk.text,
                    "root": chunk.root.text,
                    "root_lemma": chunk.root.lemma_,
                    "start": chunk.start_char,
                    "end": chunk.end_char
                })
        
        return components
    
    def _extract_actions(self, doc) -> List[Dict[str, Any]]:
        """Extract actions (verbs that indicate what needs to be done).
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of action dictionaries
        """
        actions = []
        
        # Find verbs that could indicate actions
        for token in doc:
            if token.pos_ == "VERB" and not token.is_stop:
                # Get the subject and object if available
                subject = None
                direct_object = None
                
                # Look for subject and object
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject = child.text
                    elif child.dep_ in ("dobj", "pobj"):
                        direct_object = child.text
                
                actions.append({
                    "verb": token.text,
                    "lemma": token.lemma_,
                    "subject": subject,
                    "object": direct_object,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                })
        
        return actions
    
    def _extract_constraints(self, doc) -> List[Dict[str, Any]]:
        """Extract constraints (conditions that must be met).
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of constraint dictionaries
        """
        constraints = []
        
        # Look for modal verbs and negations
        for token in doc:
            if token.pos_ == "AUX" and token.dep_ == "aux" and token.text.lower() in ("must", "should", "will", "shall"):
                # Get the main verb
                main_verb = None
                for child in token.head.children:
                    if child.pos_ == "VERB":
                        main_verb = child.text
                        break
                
                if main_verb is None and token.head.pos_ == "VERB":
                    main_verb = token.head.text
                
                # Check for negation
                is_negated = any(child.dep_ == "neg" for child in token.head.children)
                
                constraints.append({
                    "modal": token.text,
                    "verb": main_verb,
                    "negated": is_negated,
                    "start": token.idx,
                    "end": token.idx + len(token.text)
                })
        
        return constraints
    
    def _extract_code_elements(self, text: str) -> List[Dict[str, Any]]:
        """Extract potential code elements using regex patterns.
        
        Args:
            text: Input text
            
        Returns:
            List of potential code elements
        """
        code_elements = []
        
        # Apply each pattern
        for pattern in self.code_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if match.group(1):
                    code_elements.append({
                        "text": match.group(1),
                        "pattern": pattern,
                        "start": match.start(1),
                        "end": match.end(1)
                    })
        
        return code_elements

