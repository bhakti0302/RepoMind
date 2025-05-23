"""
Text Processor module.

This module provides functionality for processing and cleaning text.
"""

import re
import logging
import spacy
from typing import List, Dict, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TextProcessor:
    """Processor for cleaning and normalizing text."""
    
    def __init__(self, nlp=None):
        """Initialize the text processor.
        
        Args:
            nlp: spaCy NLP model (if None, will load en_core_web_sm)
        """
        self.nlp = nlp
        if self.nlp is None:
            try:
                # Use the smaller model for text processing
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded spaCy model: en_core_web_sm")
            except OSError:
                logger.error("Failed to load spaCy model")
                raise
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text by cleaning and normalizing.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Remove special characters but keep punctuation
            text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)
            
            # Normalize whitespace again
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        try:
            # Process the text with spaCy
            doc = self.nlp(text)
            
            # Extract sentences
            sentences = [sent.text.strip() for sent in doc.sents]
            
            return sentences
        
        except Exception as e:
            logger.error(f"Error extracting sentences: {e}")
            return [text]
    
    def extract_keywords(self, text: str, pos_tags: List[str] = None) -> List[str]:
        """Extract keywords based on part-of-speech tags.
        
        Args:
            text: Input text
            pos_tags: List of POS tags to extract (default: NOUN, PROPN, VERB)
            
        Returns:
            List of keywords
        """
        if pos_tags is None:
            pos_tags = ["NOUN", "PROPN", "VERB"]
        
        try:
            # Process the text with spaCy
            doc = self.nlp(text)
            
            # Extract keywords based on POS tags
            keywords = [
                token.lemma_
                for token in doc
                if token.pos_ in pos_tags and not token.is_stop
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_keywords = [
                keyword for keyword in keywords
                if not (keyword in seen or seen.add(keyword))
            ]
            
            return unique_keywords
        
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def clean_code_references(self, text: str) -> str:
        """Clean code references in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with cleaned code references
        """
        try:
            # Clean Java-style references (com.example.Class.method)
            text = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*\.)+[a-zA-Z_][a-zA-Z0-9_]*', 
                          lambda m: m.group(0).replace('.', ' . '), text)
            
            # Clean camelCase and PascalCase
            text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
            
            # Clean snake_case
            text = re.sub(r'([a-zA-Z])_([a-zA-Z])', r'\1 \2', text)
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        
        except Exception as e:
            logger.error(f"Error cleaning code references: {e}")
            return text
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary containing processed text data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Processing file: {file_path}")
            
            # Preprocess the text
            preprocessed_text = self.preprocess_text(text)
            
            # Extract sentences
            sentences = self.extract_sentences(preprocessed_text)
            
            # Extract keywords
            keywords = self.extract_keywords(preprocessed_text)
            
            # Clean code references
            cleaned_text = self.clean_code_references(preprocessed_text)
            
            return {
                "original_text": text,
                "preprocessed_text": preprocessed_text,
                "cleaned_text": cleaned_text,
                "sentences": sentences,
                "keywords": keywords
            }
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    processor = TextProcessor()
    
    # Example text
    example_text = """
    The UserService.authenticate() method should verify credentials.
    The system must implement com.example.auth.AuthenticationManager for OAuth.
    Users_with_invalid_credentials should receive a clear error message.
    """
    
    # Preprocess the text
    preprocessed_text = processor.preprocess_text(example_text)
    print("Preprocessed Text:")
    print(preprocessed_text)
    
    # Extract sentences
    sentences = processor.extract_sentences(preprocessed_text)
    print("\nSentences:")
    for sentence in sentences:
        print(f"  - {sentence}")
    
    # Extract keywords
    keywords = processor.extract_keywords(preprocessed_text)
    print("\nKeywords:")
    print(keywords)
    
    # Clean code references
    cleaned_text = processor.clean_code_references(preprocessed_text)
    print("\nCleaned Text:")
    print(cleaned_text)
