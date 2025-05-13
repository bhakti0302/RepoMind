"""
Requirements Parser module.

This module provides functionality for parsing business requirements using NLP.
"""

import os
import logging
import spacy
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class RequirementsParser:
    """Parser for business requirements documents."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the requirements parser.

        Args:
            model_name: Name of the spaCy model to use
        """
        self.model_name = model_name
        self.nlp = None
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.warning(f"Model {model_name} not found. Downloading...")
            try:
                os.system(f"python3 -m spacy download {model_name}")
                self.nlp = spacy.load(model_name)
                logger.info(f"Downloaded and loaded spaCy model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to download model: {e}")
                # Create a blank English model as a last resort
                logger.info("Creating a blank English model as fallback")
                self.nlp = spacy.blank("en")
                logger.info("Created blank English model")

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse business requirements text.

        Args:
            text: Business requirements text

        Returns:
            Dictionary containing parsed requirements
        """
        if not self.nlp:
            logger.error("No spaCy model loaded. Cannot parse text.")
            return {"error": "No spaCy model loaded"}

        try:
            # Process the text with spaCy
            doc = self.nlp(text)

            # Extract sentences
            sentences = [sent.text.strip() for sent in doc.sents]

            # Extract entities
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                }
                for ent in doc.ents
            ]

            # Extract noun phrases
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]

            # Extract verbs (actions)
            actions = [
                token.lemma_
                for token in doc
                if token.pos_ == "VERB"
            ]

            # Return parsed data
            return {
                "sentences": sentences,
                "entities": entities,
                "noun_phrases": noun_phrases,
                "actions": actions,
                "full_text": text
            }

        except Exception as e:
            logger.error(f"Error parsing text: {e}")
            return {"error": str(e)}

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse business requirements from a file.

        Args:
            file_path: Path to the requirements file

        Returns:
            Dictionary containing parsed requirements
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            logger.info(f"Parsing file: {file_path}")
            return self.parse(text)

        except Exception as e:
            logger.error(f"Error reading or parsing file {file_path}: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    parser = RequirementsParser()

    # Example text
    example_text = """
    The system should allow users to create new accounts with email verification.
    Users should be able to reset their passwords via email.
    The application must support OAuth login with Google and Facebook.
    """

    result = parser.parse(example_text)
    print("Parsed Requirements:")
    print(f"Sentences: {result['sentences']}")
    print(f"Entities: {result['entities']}")
    print(f"Noun Phrases: {result['noun_phrases']}")
    print(f"Actions: {result['actions']}")
