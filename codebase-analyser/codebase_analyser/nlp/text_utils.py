"""
Text utility functions for NLP processing.

This module provides utility functions for text preprocessing and analysis.
"""

import re
import logging
from typing import List, Set, Optional

import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)

def preprocess_text(text: str) -> str:
    """Preprocess text for NLP analysis.
    
    Args:
        text: Input text to preprocess
        
    Returns:
        Preprocessed text
    """
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_sentences(text: str, nlp: Language) -> List[str]:
    """Extract sentences from text using spaCy.
    
    Args:
        text: Input text
        nlp: spaCy language model
        
    Returns:
        List of sentences
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences

def extract_keywords(text: str, nlp: Language, pos_tags: Optional[List[str]] = None) -> List[str]:
    """Extract keywords from text based on part-of-speech tags.
    
    Args:
        text: Input text
        nlp: spaCy language model
        pos_tags: List of POS tags to include (default: NOUN, PROPN, VERB)
        
    Returns:
        List of keywords
    """
    if pos_tags is None:
        pos_tags = ['NOUN', 'PROPN', 'VERB']
    
    doc = nlp(text)
    keywords = [token.lemma_ for token in doc if token.pos_ in pos_tags and not token.is_stop]
    
    # Remove duplicates while preserving order
    seen: Set[str] = set()
    unique_keywords = [kw for kw in keywords if not (kw in seen or seen.add(kw))]
    
    return unique_keywords

def clean_code_references(text: str) -> str:
    """Clean text by removing code-specific syntax.
    
    Args:
        text: Input text that may contain code references
        
    Returns:
        Cleaned text
    """
    # Remove common code syntax patterns
    patterns = [
        r'```[\s\S]*?```',  # Markdown code blocks
        r'`[^`]*`',         # Inline code
        r'<.*?>',           # HTML tags
        r'#\w+',            # Hashtags/anchors
    ]
    
    cleaned_text = text
    for pattern in patterns:
        cleaned_text = re.sub(pattern, ' ', cleaned_text)
    
    # Normalize whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text
