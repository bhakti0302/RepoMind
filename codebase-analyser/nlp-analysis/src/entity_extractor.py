# Create a new file with the fixed implementation
"""
Entity Extractor module.

This module provides functionality for extracting entities from text.
"""

import os
import sys
import logging
import spacy
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class EntityExtractor:
    """Entity extractor for requirements text."""
    
    def __init__(self, nlp=None, model_name="en_core_web_sm"):
        """Initialize the entity extractor.
        
        Args:
            nlp: spaCy NLP model
            model_name: Name of the spaCy model to use
        """
        self.nlp = nlp
        self.model_name = model_name
        
        if not self.nlp:
            try:
                self.nlp = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load spaCy model: {e}")
                raise
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary of entity types and lists of entities
        """
        try:
            # Process the text with spaCy
            doc = self.nlp(text)
            
            # Initialize entity categories
            entities = {
                "nouns": [],
                "technical_terms": [],
                "actions": []
            }
            
            # Extract nouns (common nouns and proper nouns)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"]:
                    # Clean the token text
                    clean_text = token.text.strip()
                    # Only add if not empty and not already in the list
                    if clean_text and clean_text.lower() not in [n.lower() for n in entities["nouns"]]:
                        entities["nouns"].append(clean_text)
            
            # Extract technical terms (noun phrases with 2+ words)
            for chunk in doc.noun_chunks:
                # Only consider multi-word phrases as technical terms
                if len(chunk.text.split()) > 1:
                    # Clean the chunk text
                    clean_text = chunk.text.strip()
                    # Only add if not empty and not already in the list
                    if clean_text and clean_text.lower() not in [t.lower() for t in entities["technical_terms"]]:
                        entities["technical_terms"].append(clean_text)
            
            # Extract actions (verbs)
            for token in doc:
                if token.pos_ == "VERB":
                    # Use the lemma (base form) of the verb
                    clean_text = token.lemma_.strip()
                    # Only add if not empty and not already in the list
                    if clean_text and clean_text.lower() not in [a.lower() for a in entities["actions"]]:
                        entities["actions"].append(clean_text)
            
            logger.info(f"Extracted {len(entities['nouns'])} nouns, {len(entities['technical_terms'])} technical terms, and {len(entities['actions'])} actions")
            
            return entities
        
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {"nouns": [], "technical_terms": [], "actions": []}

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract entities from text")
    parser.add_argument("--text", help="Text to extract entities from")
    parser.add_argument("--file", help="File containing text to extract entities from")
    args = parser.parse_args()
    
    # Get the text from either the command line or a file
    if args.text:
        text = args.text
    elif args.file:
        with open(args.file, 'r') as f:
            text = f.read()
    else:
        text = """
        # Sample Requirements
        
        The system should allow users to search for books by author or title.
        Each book should have attributes like title, author, and publication date.
        Users should be able to check the availability status of each book.
        """
    
    # Initialize entity extractor
    entity_extractor = EntityExtractor()
    
    # Extract entities
    entities = entity_extractor.extract_entities(text)
    
    # Print the results
    print("\nExtracted Entities:")
    for entity_type, entity_list in entities.items():
        print(f"\n{entity_type.capitalize()}:")
        for entity in entity_list:
            print(f"  - {entity}")
