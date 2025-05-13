"""
Natural Language Processing module for analyzing business requirements.

This module provides functionality for parsing and analyzing business requirements
using spaCy and other NLP techniques.
"""

from .requirements_parser import RequirementsParser
from .entity_recognition import EntityRecognizer
from .component_extractor import ComponentExtractor
from .text_utils import preprocess_text, extract_sentences, extract_keywords

__all__ = [
    'RequirementsParser',
    'EntityRecognizer',
    'ComponentExtractor',
    'preprocess_text',
    'extract_sentences',
    'extract_keywords',
]
