"""
Text utilities for NLP processing.

This module provides utility functions for text preprocessing and analysis.
"""

import logging
import re
from typing import List, Dict, Any, Optional

import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)

def preprocess_text(text: str) -> str:
    """Preprocess text for NLP analysis.
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters that might interfere with parsing
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\-\'\"\`]', ' ', text)
    
    # Normalize quotes
    text = re.sub(r'[\u2018\u2019]', "'", text)
    text = re.sub(r'[\u201C\u201D]', '"', text)
    
    return text

def extract_sentences(text: str, nlp: Optional[Language] = None) -> List[Dict[str, Any]]:
    """Extract sentences from text.
    
    Args:
        text: Input text
        nlp: Optional spaCy NLP model
        
    Returns:
        List of sentence dictionaries
    """
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("Downloading spaCy model en_core_web_sm")
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
    
    doc = nlp(text)
    
    sentences = []
    for sent in doc.sents:
        sentences.append({
            "text": sent.text,
            "start": sent.start_char,
            "end": sent.end_char
        })
    
    return sentences

def extract_keywords(text: str, nlp: Optional[Language] = None, max_keywords: int = 20) -> List[str]:
    """Extract keywords from text.
    
    Args:
        text: Input text
        nlp: Optional spaCy NLP model
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("Downloading spaCy model en_core_web_sm")
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
    
    doc = nlp(text)
    
    # Extract keywords (nouns and proper nouns that are not stop words)
    keywords = []
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop and len(token.text) > 1:
            keywords.append(token.lemma_.lower())
    
    # Remove duplicates and limit the number of keywords
    keywords = list(dict.fromkeys(keywords))
    return keywords[:max_keywords]


